"""
zigbee_data provides the ZigBeeData class to store metadata from the
deCONZ REST API.

The 'ZigBeeData.decode(msg_dict)' method injects additional properties
into the msg_dict (such as 'acp_id')
"""

import aiohttp
import asyncio
import time
import simplejson as json

DEBUG = True

"""
{
  "1": {
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
      "lastupdated": "2020-04-30T11:57:36",
      "status": 170,
      "sunrise": "2020-04-30T04:31:30",
      "sunset": "2020-04-30T19:23:33"
    },
    "swversion": "1.0",
    "type": "Daylight",
    "uniqueid": "00:21:2e:ff:ff:05:03:60-01"
  },
  "2": {
    "config": {
      "battery": 100,
      "on": true,
      "reachable": true,
      "temperature": 2400
    },
    "ep": 1,
    "etag": "043c902572c6a4fcb764b5ef1d1ca0b0",
    "manufacturername": "LUMI",
    "modelid": "lumi.sensor_magnet.aq2",
    "name": "aqa-wd-5c91b3",
    "state": {
      "lastupdated": "2020-04-30T12:07:30",
      "open": false
    },
    "swversion": "20161128",
    "type": "ZHAOpenClose",
    "uniqueid": "00:15:8d:00:04:5c:91:b3-01-0006"
  },
  "3": {
    "config": {
      "battery": 100,
      "on": true,
      "reachable": true,
      "temperature": 2300,
      "tholddark": 12000,
      "tholdoffset": 7000
    },
    "ep": 1,
    "etag": "578e96505df5c7487499d2b921d1ed3e",
    "manufacturername": "LUMI",
    "modelid": "lumi.sensor_motion.aq2",
    "name": "aqa-mot-6657d3",
    "state": {
      "dark": false,
      "daylight": false,
      "lastupdated": "2020-04-30T12:09:49",
      "lightlevel": 18130,
      "lux": 65
    },
    "swversion": "20170627",
    "type": "ZHALightLevel",
    "uniqueid": "00:15:8d:00:04:66:57:d3-01-0400"
  },
  "4": {
    "config": {
      "battery": 100,
      "duration": 90,
      "on": true,
      "reachable": true,
      "temperature": 2300
    },
    "ep": 1,
    "etag": "578e96505df5c7487499d2b921d1ed3e",
    "manufacturername": "LUMI",
    "modelid": "lumi.sensor_motion.aq2",
    "name": "aqa-mot-6657d3",
    "state": {
      "lastupdated": "2020-04-30T12:09:49",
      "presence": true
    },
    "swversion": "20170627",
    "type": "ZHAPresence",
    "uniqueid": "00:15:8d:00:04:66:57:d3-01-0406"
  }
}

Zigbee device data (delivered over websocket from deCONZ):

Note in this case (streamed sensor data) the payload includes
properties "r" and "id" which can be used to find the corresponding
ZigBeeData record with "name" (which is our definitive acp_id).

Xiaomi Door/Window:
{
    "config": {
        "battery": 100,
        "on": true,
        "reachable": true,
        "temperature": 2400
    },
    "e": "changed",
    "id": "2",
    "r": "sensors",
    "t": "event",
    "uniqueid": "00:15:8d:00:04:5c:91:b3-01-0006"
}
{
    "e": "changed",
    "id": "2",
    "r": "sensors",
    "state": {
        "lastupdated": "2020-04-30T13:44:47",
        "open": true
    },
    "t": "event",
    "uniqueid": "00:15:8d:00:04:5c:91:b3-01-0006"
}

Xiaomi Motion:
{
    "e": "changed",
    "id": "3",
    "r": "sensors",
    "state": {
        "dark": false,
        "daylight": true,
        "lastupdated": "2020-04-30T13:43:42",
        "lightlevel": 21173,
        "lux": 131
    },
    "t": "event",
    "uniqueid": "00:15:8d:00:04:66:57:d3-01-0400"
}
{
    "e": "changed",
    "id": "4",
    "r": "sensors",
    "state": {
        "lastupdated": "2020-04-30T13:43:42",
        "presence": true
    },
    "t": "event",
    "uniqueid": "00:15:8d:00:04:66:57:d3-01-0406"
}
"""
#####################################
# Return current timestamp as string
#####################################
def ts_string():
    return '{:.6f}'.format(time.time())

class EndPoint(object):
    """ Represents an 'endpoint' in the ZigBee network, i.e. a sensor or
    actuator within a ZigBee device. A single device (which we call a Node)
    may contain multiple endpoints.
    """
    def __init__(self, name, r, endpoint_id, endpoint_dict):
        print("{} EndPoint __init__() {} {}/{}".format(ts_string(),name,r,endpoint_id))
        self.properties = endpoint_dict
        self.properties["name"] = name # we are adding name, r, id to the endpoint_dict properties
        self.properties["r"] = r
        self.properties["id"] = endpoint_id

class Node(object):
    """ Represents a ZigBee device which may contain multiple endpoints.
    """
    def __init__(self, name):
        self.name = name
        self.endpoints = {}

    def update(self, endpoint):
        endpoint_id = endpoint.properties["id"]
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
        print("{} ZigBeeData __init__()".format(ts_string()))
        self.settings = settings
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
                    self.update_all(r, endpoints_dict)
                await asyncio.sleep(15)

    # decode(msg) will 'normalize' the properties,  e.g. copy 'name' into 'acp_id'
    # Returns True/False (and updates msg_dict) indicating a successful decode.
    # input is a dictionary
    def decode(self,msg_dict):
        # timestamp
        msg_dict["acp_ts"] = ts_string()

        # sensor identifier
        acp_id = self.acp_id(msg_dict)
        if acp_id is None:
            return False
        msg_dict["acp_id"] = self.acp_id(msg_dict)

        # temperature
        temperature = self.acp_temperature(msg_dict)
        if temperature is not None:
            msg_dict["acp_temperature"] = temperature

        return True

    # Try and extract a known identifier for the device
    def acp_id(self, msg_dict):
        try:
            return self.endpoints[msg_dict["r"]][msg_dict["id"]].properties["name"]
        except KeyError:
            return None

    # If there is a "temperature" property, return value as degrees C
    def acp_temperature(self, msg_dict):
        try:
            #debug is this 'standard' or just Aqara / deCONZ ?
            return msg_dict["config"]["temperature"] / 100
        except KeyError:
            return None

    # Update the Nodes data given a dictionary containing entries for multiple endpoints
    def update_all(self, r, endpoints_dict):
        for endpoint_id in endpoints_dict:
            endpoint_dict = endpoints_dict[endpoint_id]
            self.update(r, endpoint_id, endpoint_dict)

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
    def update(self, r, endpoint_id, endpoint_dict):
        name = endpoint_dict["name"]
        endpoint = EndPoint(name, r, endpoint_id, endpoint_dict)
        # Update reference in self.endpoints to this data
        self.endpoints[r][endpoint_id] = endpoint
        if not name in self.nodes:
            self.nodes[name] = Node(name)
        # Update reference in self.nodes to same endpoint object
        self.nodes[name].update(endpoint)

    #####################################
    # GET http from REST API
    #####################################
    async def http_get(self, session, url):
        async with session.get(url) as response:
            return await response.text()
