
import aiohttp
import asyncio
import time
import simplejson as json

url = "http://192.168.1.118/api/B9FAF065F0/"

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

Zigbee device data:

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

class EndPoint(object):
    """ Represents an 'endpoint' in the ZigBee network, i.e. a sensor or
    actuator within a ZigBee device. A single device (which we call a Node)
    may contain multiple endpoints.
    """
    def __init__(self, node_id, endpoint_id, endpoint_dict):
        print("{} EndPoint __init__() {}/{}".format(ts_string(),node_id,endpoint_id))
        self.properties = endpoint_dict
        self.properties["endpoint_id"] = endpoint_id
        self.properties["node_id"] = node_id

class Node(object):
    """ Represents a ZigBee device which may contain multiple endpoints.
    """
    def __init__(self, node_id):
        self.node_id = node_id
        self.endpoints = {}

    def update(self, endpoint_id, endpoint):
        self.endpoints[endpoint_id] = endpoint

class ZigBeeData(object):
    """ Contains the collected state and metadata of all the Zigbee devices
    in the network. This data may be queried by "node name" or
    "endpoint_type:endpoint_id". The immediate need for this is because the
    sensor data from the deCONZ websocket *only* contains the
    "endpoint_type:endpoint_id" identifier and this needs enriching with a
    definitive 'sensor id'
    """
    def __init__(self):
        print("{} EndPoints __init__()".format(ts_string()))
        # endpoints will be referenced by self.nodes[node_id].endpoints[endpoint_id]
        self.nodes = {}
        # endpoints also referenced self.endpoints[endpoint_type][endpoint_id]
        self.endpoints = {}
        self.endpoints["sensors"] = {}
        self.endpoints["lights"] = {}
        self.endpoints["switches"] = {}

    # Update the Nodes data given a dictionary containing entries for multiple endpoints
    def update_all(self, r, endpoints_dict):
        for endpoint_id in endpoints_dict:
            endpoint = endpoints_dict[endpoint_id]
            endpoint["r"] = r
            endpoint["id"] = endpoint_id
            self.update(endpoints_dict[endpoint_id])

    # Update the Nodes data with info for a single endpoint.
    def update(self, endpoint_dict):
        node_id = endpoint_dict["name"]
        endpoint_r = endpoint_dict["r"]
        endpoint_id = endpoint_dict["id"]
        endpoint = EndPoint(node_id, endpoint_id, endpoint_dict)
        # Update reference in self.endpoints to this data
        self.endpoints[endpoint_r][endpoint_id] = endpoint
        if not node_id in self.nodes:
            self.nodes[node_id] = Node(node_id)
        # Update reference in self.nodes to same endpoint object
        self.nodes[node_id].update(endpoint_id, endpoint)

#####################################
# Return current timestamp as string
#####################################
def ts_string():
    return '{:.6f}'.format(time.time())

#####################################
# GET http
#####################################
async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

#####################################
# Async main()
#####################################
async def async_main():
    zigbee_data = ZigBeeData()
    async with aiohttp.ClientSession() as session:
        r = "sensors"
        json_response = await fetch(session, url+r)
        print("{} {}".format(ts_string(), json_response))
        endpoints_data = json.loads(json_response)
        zigbee_data.update_all("sensors", endpoints_data)

#####################################
# main()
#####################################
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_main())
