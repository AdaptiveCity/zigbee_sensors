# Conbee II deconz API and websocket access

This is an effort to connect Zigbee sensors to the Adaptive City platform.

The work does *not*
address the issue of seamless connectivity of ZigBee devices into a consumer-friendly home
automation service, in fact it does pretty much the opposite by trying collect the data from the
devices and send commands to them with as little 'application-level' software in the way
as possible.

A particular challenge is the
usual tight integration between Zigbee networking and the 'application layer', i.e. all software
available for Zigbee hardware seems to require a configuration for every single device type
that is connected to the network (WTF?). We will try and ease this restriction, i.e. be more permissive
about allowing devices to connect to the network, and defer dealing with the application-level issues (like
whether the device is a switch or a light bulb) until later in the software stack.

The work-in-progress tracing the `deCONZ REST API` calls is in [PWA API Calls](pwa_api_calls/README.md).

Below is an architectural diagram of how the Adaptive City components combine
to support Zigbee sensors.

![ACP Zigbee Support](images/deconz2mqtt.png)

## Decoders

See `acp_decoders` in [acp_local_mqtt](https://github.com/AdaptiveCity/acp_local_mqtt).

There are multiple reasons decoders are necessary in our system:

1. We want consistent reference to sensor identifiers and timestamps. Each sensor manufacturer
(and zigbee controller software) uses its own way of recording an identifier for the
sensor and the timestamp of the reading.

2. The deCONZ software is inconsistent in its use of identifiers for sensors. Each ZigBee device has a
`uniqueid` , the deCONZ REST API allows a `name` to be associated, and the devices are arbitrarily
categorized (a property called "r" as "sensors", "switches" or "lights" and given an integer "id"
within that category. The same device is `uniqueid: "00:15:8d:00:04:5c:91`, `name: "aqa-wd-5747f1"`
and `"r"/"id": "sensors"/"2"` with different identifiers used in different messages. The identifier
may be contained within the data payload, or embedded in the path used to reach the payload in an
aggregated data structure. `deconz2mqtt` normalizes these identifiers by including
them in the data messages and setting the `acp_id` property to the value of `name`.

3. Sensor providers are shockingly amateur in dealing with *events*. For example the Xiaomi Aqara Door/Window
sensor sends a periodic 'state' message (`open: true|false`) every 50 minutes, but sends the *same*
message when the door/window is actually opened or closed. This requires the *application* to maintain state in some
unique way for this sensor to work out if the door has just been opened.
Instead, we add properties `"acp_event": "openclose"`, `"acp_event_value": "open"` where
we believe an actual event has occurred.

## Example data messages
These messages are for the same device (a Xiaomi Aqara Motion Sensor), firstly as reported in the
REST API `sensors` query and secondly as the real-time sensor data provided via the deCONZ websocket.

### deCONZ REST API sensors information

The Xiaomi Aqara Motion sensor contains two ZigBee `endpoints`, for `ZHALightLevel` and `ZHAPresence`:

The information from the REST API is a combination of sensor metadata and the most recent `state` information. This
predated the websocket data 'push' so applications used to poll the REST API to get the sensor data (and probably
still do).

This metadata was received via a `GET` from `/api/<apikey>/sensors`, so the local `id`s are `sensors/3`
and `sensors/4`, with both of these mapping to the `name` `aqa-mot-6657d3`. For metadata for all devices
we also query `/api/<apikey>/lights` and `/api/<apikey>/switches`, but `deconz2mqtt` merges these into a
single internal lookup table.

```
{
  ...

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
    "etag": "7e68723348b522d4b381facbbd70ad2d",
    "manufacturername": "LUMI",
    "modelid": "lumi.sensor_motion.aq2",
    "name": "aqa-mot-6657d3",
    "state": {
      "dark": false,
      "daylight": true,
      "lastupdated": "2020-05-01T08:24:07",
      "lightlevel": 21644,
      "lux": 146
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
    "etag": "7e68723348b522d4b381facbbd70ad2d",
    "manufacturername": "LUMI",
    "modelid": "lumi.sensor_motion.aq2",
    "name": "aqa-mot-6657d3",
    "state": {
      "lastupdated": "2020-05-01T08:24:07",
      "presence": true
    },
    "swversion": "20170627",
    "type": "ZHAPresence",
    "uniqueid": "00:15:8d:00:04:66:57:d3-01-0406"
 }
}
```

### deCONZ websocket real-time streamed sensor data

Note the streamed sensor data is linked to the REST API `sensors` metadata and prior state via the `id` and `r` properties.

The `ZHALightLevel` reading:
```
{
    "e": "changed",
    "id": "3",
    "r": "sensors",
    "state": {
        "dark": false,
        "daylight": true,
        "lastupdated": "2020-04-30T09:56:51",
        "lightlevel": 20607,
        "lux": 115
    },
    "t": "event",
    "uniqueid": "00:15:8d:00:04:66:57:d3-01-0400"
}
```
The `ZHAPresence` reading:
```
{
    "e": "changed",
    "id": "4",
    "r": "sensors",
    "state": {
        "lastupdated": "2020-04-30T09:56:51",
        "presence": true
    },
    "t": "event",
    "uniqueid": "00:15:8d:00:04:66:57:d3-01-0406"
}
```
