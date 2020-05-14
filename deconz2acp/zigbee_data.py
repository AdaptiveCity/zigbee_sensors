"""
zigbee_data provides the ZigBeeData class to store metadata from the
deCONZ REST API and the most recent websocket message from each device endpoint.

The 'ZigBeeData.decode(msg_dict)' method injects additional properties
into the msg_dict (such as 'acp_id')

For examples of the device data from the REST interface and websocket
messages, see sensor_data/README.md.
"""

import aiohttp
import asyncio
import time
import simplejson as json
import sys

DEBUG = True

#####################################
# Return current timestamp as string
#####################################
def ts_string():
    return '{:.6f}'.format(time.time())

class EndPoint(object):
    """ Represents an 'endpoint' in the ZigBee network, i.e. a sensor or
    actuator within a ZigBee device. A single device (which we call a Node)
    may contain multiple endpoints. The EndPoint data serves two important
    functions: (1) we use it to map internal id's like "sensors/3" to the
    node identifier like "aqa-dw-05c688" and (2) the EndPoint keeps track of
    the state of the sensor so *events* (like a switch change from closed to
    open) can be marked as such.
    """
    def __init__(self, name, r, endpoint_id):
        print("{} EndPoint __init__() {} {}/{}".format(ts_string(),name,r,endpoint_id))
        self.rest_dict = {} # most recent REST API data for this endpoint
        self.rest_state = {} # some sensor data in the "state" property,
        self.rest_config = {} # other sensor data in the "config" property
        self.ws_dict = {} # most recent websocket message for this endpoint
        self.ws_state = {}
        self.ws_config = {}
        self.name = name # we are adding name, r, id to the endpoint_dict properties
        self.r = r
        self.id = endpoint_id

    # Store the latest data from the deCONZ REST API
    def handle_rest(self, endpoint_dict):
        self.rest_dict = endpoint_dict
        if "config" in endpoint_dict:
            self.rest_config = endpoint_dict["config"]
            # Handle name change (happens on install "Door/Window" to "aqa-wd-1a2b3c")
            if "name" in self.rest_config and self.rest_config["name"] != self.name:
                print("{} rest config sensor name change {} to {}".format(
                    ts_string(),
                    self.name,
                    self.rest_config["name"]), file=sys.stderr, flush=True)
                self.name = self.rest_config["name"]
        if "state" in endpoint_dict:
            self.rest_state = endpoint_dict["state"]

    # Store the latest incoming message from the deCONZ websocket
    def handle_ws(self, msg_dict):
        # Make a *copy* of the message
        msg_copy = json.loads(json.dumps(msg_dict))
        # Handle name change (happens on install "Door/Window" to "aqa-wd-1a2b3c")
        if "name" in msg_dict and msg_dict["name"] != self.name:
            print("{} ws sensor name change {} to {}".format(
                ts_string(),
                self.name,
                msg_dict["name"]), file=sys.stderr, flush=True)
            self.name = msg_dict["name"]

        # These calls will add properties to msg_dict
        # add "acp_id" and "acp_ts"
        self.add_core_properties(msg_dict)
        # If appropriate, add "acp_event" and "acp_event_value" properties to
        self.add_event(msg_dict)
        # add ACP 'standardized' versions of data values
        self.decode(msg_dict)

        # We explictly store the most recent "state" and "config", because
        # alternate websocket messages from the same endpoint may contain
        # one or the other (e.g. see Xiaomi Door/Window)
        self.ws_dict = msg_copy
        if "config" in self.ws_dict:
            self.ws_config = self.ws_dict["config"]
        if "state" in self.ws_dict:
            self.ws_state = self.ws_dict["state"]

    # Add "acp_id" and "acp_ts" properties to the message
    def add_core_properties(self, msg_dict):
        # timestamp
        msg_dict["acp_ts"] = ts_string()
        # sensor identifier
        msg_dict["acp_id"] = self.name

    def decode_event(self, prop, prop_value):
        if prop == "open":
            return "openclose", "open" if prop_value else "close"
        return None,None

    # Try and work out if the websocket message implies an EVENT, e.g.
    # a message with state.open=True can be compared with the previous
    # state and if changed then we mark this as an event.
    def add_event(self, msg_dict):
        if "state" in msg_dict:
            msg_state = msg_dict["state"]
            for prop in msg_state:
                if prop in ["open"]:
                    if prop in self.ws_state and msg_state[prop] != self.ws_state[prop]:
                        event, value = self.decode_event(prop, msg_state[prop])
                        if event is not None:
                            msg_dict["acp_event"] = event
                            msg_dict["acp_event_value"] = value
                            if DEBUG:
                                print("{} state change {} to {}".format(
                                    ts_string(),
                                    event,
                                    value), flush=True)

    # decode(msg) interprets data fields to possible add ACP 'standard' versions
    def decode(self,msg_dict):
        # temperature
        temperature = self.acp_temperature(msg_dict)
        if temperature is not None:
            msg_dict["acp_temperature"] = temperature

    # If there is a "temperature" property, return value as degrees C
    def acp_temperature(self, msg_dict):
        try:
            #debug is this 'standard' or just Aqara / deCONZ ?
            return msg_dict["config"]["temperature"] / 100
        except KeyError:
            return None

class Node(object):
    """ Represents a ZigBee device which may contain multiple endpoints.
    """
    def __init__(self, name):
        self.name = name
        self.endpoints = {}

    def update(self, endpoint):
        endpoint_id = endpoint.id
        self.endpoints[endpoint_id] = endpoint

class ZigBeeData(object):
    """ Contains the collected state and metadata of all the Zigbee devices
    in the network. This data may be queried by "node name" or
    "endpoint_type:endpoint_id". The immediate need for this is because the
    sensor data from the deCONZ websocket *only* contains the
    "endpoint_type:endpoint_id" identifier and this needs enriching with a
    definitive sensor identifier ('acp_id').
    """
    def __init__(self, settings):
        global DEBUG
        self.settings = settings
        if "DEBUG" in settings:
            DEBUG = settings["DEBUG"]
        print("{} ZigBeeData __init__() DEBUG={}".format(
            ts_string(),
            DEBUG),file=sys.stderr,flush=True)

        # endpoints will be referenced by self.nodes[name].endpoints[endpoint_id]
        self.nodes = {}
        # endpoints also referenced self.endpoints[endpoint_type][endpoint_id]
        self.endpoints = {}
        self.endpoints["sensors"] = {} # ZigBee devices (battery powered)
        self.endpoints["lights"] = {} # ZigBee devices (mains powered)

    #####################################
    # Async start()
    #####################################
    async def start(self):
        print("{} ZigBeeData start()".format(ts_string()))
        api_url = self.settings["deconz_api"]["url"]
        async with aiohttp.ClientSession() as session:
            while True:
                for r in ["sensors","lights"]:
                    #print("{} Getting {}".format(ts_string(), r))
                    json_response = await self.http_get(session, api_url+r)
                    if DEBUG:
                        print("{} REST API /{} response:\n{}".format(
                            ts_string(),
                            r,
                            json_response), flush=True)
                    endpoints_dict = json.loads(json_response)
                    self.handle_rest_response(r, endpoints_dict)
                #debug should put this refresh time in a constant
                await asyncio.sleep(15)

    # Deconz2mqqt has received websocket message and passed it to us
    def handle_ws_message(self, msg_dict):
        try:
            endpoint = self.endpoints[msg_dict["r"]][msg_dict["id"]]
            endpoint.handle_ws(msg_dict)
            return True # status
        except KeyError:
            return False

    # Update the Nodes data given a dictionary containing entries for multiple endpoints
    # r is "lights" or "sensors"
    # endpoints_dict is { "1": {...}, "2": {...} ...} with the info for each actual endpoint
    def handle_rest_response(self, r, endpoints_dict):
        for endpoint_id in endpoints_dict:
            endpoint_dict = endpoints_dict[endpoint_id]
            self.handle_endpoint_rest(r, endpoint_id, endpoint_dict)

    # Update the Nodes data with info for a single endpoint.
    """
    From http://host:port/api/<apikey>/sensors

    Note from this request we expand the dict with "sensors" (r) and
    "1" (endpoint_id) as sensors/1 is the unique local id of the sensor.

    { "1": {
          "config": {
            "configured": true,
            "on": true,
            "sunriseoffset": 30,
            "sunsetoffset": -30
          },
          "etag": "8bd046b9a5340839b658ed2696c1ea34",
          "manufacturername": "Philips",
          "modelid": "PHDL00",
          "name": "Daylight",
          "state": {
            "dark": false,
            "daylight": true,
            "lastupdated": "2020-05-01T05:17:36",
            "status": 160,
            "sunrise": "2020-05-01T04:29:35",
            "sunset": "2020-05-01T19:25:15"
          },
          "swversion": "1.0",
          "type": "Daylight",
          "uniqueid": "00:21:2e:ff:ff:05:03:60-01"
         }
    """
    def handle_endpoint_rest(self, r, endpoint_id, endpoint_dict):
        name = endpoint_dict["name"]
        try:
            endpoint = self.endpoints[r][endpoint_id]
        except KeyError:
            endpoint = EndPoint(name, r, endpoint_id)
            # Update reference in self.endpoints to this data
            self.endpoints[r][endpoint_id] = endpoint
        if not name in self.nodes:
            self.nodes[name] = Node(name)
            # Update reference in self.nodes to same endpoint object
            self.nodes[name].update(endpoint)
        # OK now update the Endpoint with the new data
        endpoint.handle_rest(endpoint_dict)

    #####################################
    # GET http from REST API
    #####################################
    async def http_get(self, session, url):
        async with session.get(url) as response:
            return await response.text()
