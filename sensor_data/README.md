# deCONZ REST API and Websocket Json

Metadata for all sensors can be retrieved with:

`/api/<apikey>/sensors`

or for an individual sensor (e.g. sensors/2):

`/api/<apikey>/sensors/2`

## Xiaomi Aqara Door/Window Sensor

### REST API
```
  "2":{
    "config":{
      "battery":100,
      "on":true,
      "reachable":true,
      "temperature":2500},
    "ep":1,
    "etag":"87355e3adaead72213862997bb887112",
    "manufacturername":"LUMI",
    "modelid":"lumi.sensor_magnet.aq2",
    "name":"aqa-wd-5c91b3",
    "state":{
      "lastupdated":"2020-04-29T10:26:56",
      "open":true},
    "swversion":"20161128",
    "type":"ZHAOpenClose",
    "uniqueid":"00:15:8d:00:04:5c:91:b3-01-0006"},
```
### Websocket
Periodic (50 mins):
```
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
```
This message sent periodically and also on switch change
```
{
    "e": "changed",
    "id": "2",
    "r": "sensors",
    "state": {
        "lastupdated": "2020-04-28T15:02:08",
        "open": true
    },
    "t": "event",
    "uniqueid": "00:15:8d:00:04:5c:91:b3-01-0006"
}
```

## Xiaomi Aqara Motion Sensor
Note that this sensor node has **two** entries in the `sensors` response, both
with the same `name` property.
### REST API
```
  "3":{
    "config":{
      "battery":100,
      "on":true,
      "reachable":true,
      "temperature":2400,
      "tholddark":12000,
      "tholdoffset":7000},
    "ep":1,
    "etag":"a7fd2d22656e4696b3a26086f3bacc62",
    "manufacturername":"LUMI",
    "modelid":"lumi.sensor_motion.aq2",
    "name":"aqa-mot-6657d3",
    "state":{
      "dark":false,
      "daylight":true,
      "lastupdated":"2020-04-29T10:42:48",
      "lightlevel":21336,
      "lux":136},
    "swversion":"20170627",
    "type":"ZHALightLevel",
    "uniqueid":"00:15:8d:00:04:66:57:d3-01-0400"},
  ```
  and
  ```
  "4":{
    "config":{
      "battery":100,
      "duration":90,
      "on":true,
      "reachable":true,
      "temperature":2400},
    "ep":1,
    "etag":"a7fd2d22656e4696b3a26086f3bacc62",
    "manufacturername":"LUMI",
    "modelid":"lumi.sensor_motion.aq2",
    "name":"aqa-mot-6657d3",
    "state":{
      "lastupdated":"2020-04-29T10:42:48",
      "presence":true},
    "swversion":"20170627",
    "type":"ZHAPresence",
    "uniqueid":"00:15:8d:00:04:66:57:d3-01-0406"}
  }
```
### Websocket
When added:

```
{
    "e": "added",
    "id": "3",
    "r": "sensors",
    "sensor": {
        "config": {
            "battery": 100,
            "on": true,
            "reachable": true,
            "temperature": 2400,
            "tholddark": 12000,
            "tholdoffset": 7000
        },
        "ep": 1,
        "etag": "42b55c52b596c5b7e309d15dc5b3c128",
        "id": "3",
        "manufacturername": "LUMI",
        "modelid": "lumi.sensor_motion.aq2",
        "name": "LightLevel 3",
        "state": {
            "dark": false,
            "daylight": false,
            "lastupdated": "2020-04-29T10:33:56",
            "lightlevel": 12788,
            "lux": 19
        },
        "type": "ZHALightLevel",
        "uniqueid": "00:15:8d:00:04:66:57:d3-01-0400"
    },
    "t": "event",
    "uniqueid": "00:15:8d:00:04:66:57:d3-01-0400"
}
```
and
```
{
    "e": "added",
    "id": "4",
    "r": "sensors",
    "sensor": {
        "config": {
            "battery": 100,
            "duration": 90,
            "on": true,
            "reachable": true,
            "temperature": 2400
        },
        "ep": 1,
        "etag": "c41a2fb7f2f1184835cf29ed523a7184",
        "id": "4",
        "manufacturername": "LUMI",
        "modelid": "lumi.sensor_motion.aq2",
        "name": "Presence 4",
        "state": {
            "lastupdated": "2020-04-29T10:34:04",
            "presence": true
        },
        "type": "ZHAPresence",
        "uniqueid": "00:15:8d:00:04:66:57:d3-01-0406"
    },
    "t": "event",
    "uniqueid": "00:15:8d:00:04:66:57:d3-01-0406"
}
```
Periodic:
```
{
    "config": {
        "battery": 100,
        "on": true,
        "reachable": true,
        "temperature": 2600,
        "tholddark": 12000,
        "tholdoffset": 7000
    },
    "e": "changed",
    "id": "3",
    "r": "sensors",
    "t": "event",
    "uniqueid": "00:15:8d:00:04:66:57:d3-01-0400"
}
```
On change:
```
  {
    "e": "changed",
    "id": "3",
    "r": "sensors",
    "state": {
        "dark": false,
        "daylight": true,
        "lastupdated": "2020-05-01T11:44:40",
        "lightlevel": 21106,
        "lux": 129
    },
    "t": "event",
    "uniqueid": "00:15:8d:00:04:66:57:d3-01-0400"
}
```
## Philips Hue Dimmer Switch

### REST API

```
  "5":{
    "config":{
      "group":"13070",
      "on":true,
      "reachable":true},
    "ep":2,
    "etag":"a5e9f2d7de2b6265b82fc0e2542b051a",
    "manufacturername":"Philips",
    "mode":1,
    "modelid":
    "RWL021",
    "name":"Dimmer Switch",
    "state":{
      "buttonevent":null,
      "eventduration":null,
      "lastupdated":"none"},
    "swversion":"5.45.1.17846",
    "type":"ZHASwitch",
    "uniqueid":"00:17:88:01:08:0e:10:d4-02-fc00"}
```
### Websocket
When added:
```
{
    "e": "added",
    "id": "5",
    "r": "sensors",
    "sensor": {
        "config": {
            "on": true,
            "reachable": true
        },
        "ep": 2,
        "etag": "0bf070db0ba020a39be22758eb441759",
        "id": "5",
        "manufacturername": "Philips",
        "mode": 1,
        "modelid": "RWL021",
        "name": "RWL021 5",
        "state": {
            "buttonevent": null,
            "eventduration": null,
            "lastupdated": "none"
        },
        "type": "ZHASwitch",
        "uniqueid": "00:17:88:01:08:0e:10:d4-02-fc00"
    },
    "t": "event",
    "uniqueid": "00:17:88:01:08:0e:10:d4-02-fc00"
}
```
```
{
    "config": {
        "group": "13070",
        "on": true,
        "reachable": true
    },
    "e": "changed",
    "id": "5",
    "r": "sensors",
    "t": "event",
    "uniqueid": "00:17:88:01:08:0e:10:d4-02-fc00"
}
```

```
{
    "e": "changed",
    "id": "5",
    "name": "phi-dim-0e10d4",
    "r": "sensors",
    "t": "event",
    "uniqueid": "00:17:88:01:08:0e:10:d4-02-fc00"
}
```
Periodic (every 5 mins):
```
{
    "config": {
        "battery": 100,
        "group": "13070",
        "on": true,
        "reachable": true
    },
    "e": "changed",
    "id": "5",
    "r": "sensors",
    "t": "event",
    "uniqueid": "00:17:88:01:08:0e:10:d4-02-fc00"
}
```
```
{
    "e": "changed",
    "id": "5",
    "r": "sensors",
    "state": {
        "buttonevent": 1000,
        "eventduration": 0,
        "lastupdated": "2020-05-01T11:43:32"
    },
    "t": "event",
    "uniqueid": "00:17:88:01:08:0e:10:d4-02-fc00"
}
```
'On' button down/up:
```
{
    "e": "changed",
    "id": "5",
    "r": "sensors",
    "state": {
        "buttonevent": 1000,
        "eventduration": 0,
        "lastupdated": "2020-05-01T18:00:15"
    },
    "t": "event",
    "uniqueid": "00:17:88:01:08:0e:10:d4-02-fc00"
}
{
    "e": "changed",
    "id": "5",
    "r": "sensors",
    "state": {
        "buttonevent": 1002,
        "eventduration": 2,
        "lastupdated": "2020-05-01T18:00:15"
    },
    "t": "event",
    "uniqueid": "00:17:88:01:08:0e:10:d4-02-fc00"
}
```
'Off' button down/up:
```
{
    "e": "changed",
    "id": "5",
    "r": "sensors",
    "state": {
        "buttonevent": 4000,
        "eventduration": 0,
        "lastupdated": "2020-05-01T18:01:06"
    },
    "t": "event",
    "uniqueid": "00:17:88:01:08:0e:10:d4-02-fc00"
}
{
    "e": "changed",
    "id": "5",
    "r": "sensors",
    "state": {
        "buttonevent": 4002,
        "eventduration": 1,
        "lastupdated": "2020-05-01T18:01:06"
    },
    "t": "event",
    "uniqueid": "00:17:88:01:08:0e:10:d4-02-fc00"
}
```
4-second dimmer 'plus' press
```
{
    "e": "changed",
    "id": "5",
    "r": "sensors",
    "state": {
        "buttonevent": 2000,
        "eventduration": 0,
        "lastupdated": "2020-05-01T18:03:07"
    },
    "t": "event",
    "uniqueid": "00:17:88:01:08:0e:10:d4-02-fc00"
}
{
    "e": "changed",
    "id": "5",
    "r": "sensors",
    "state": {
        "buttonevent": 2001,
        "eventduration": 8,
        "lastupdated": "2020-05-01T18:03:07"
    },
    "t": "event",
    "uniqueid": "00:17:88:01:08:0e:10:d4-02-fc00"
}
{
    "e": "changed",
    "id": "5",
    "r": "sensors",
    "state": {
        "buttonevent": 2001,
        "eventduration": 16,
        "lastupdated": "2020-05-01T18:03:08"
    },
    "t": "event",
    "uniqueid": "00:17:88:01:08:0e:10:d4-02-fc00"
}
{
    "e": "changed",
    "id": "5",
    "r": "sensors",
    "state": {
        "buttonevent": 2001,
        "eventduration": 24,
        "lastupdated": "2020-05-01T18:03:09"
    },
    "t": "event",
    "uniqueid": "00:17:88:01:08:0e:10:d4-02-fc00"
}
{
    "e": "changed",
    "id": "5",
    "r": "sensors",
    "state": {
        "buttonevent": 2003,
        "eventduration": 26,
        "lastupdated": "2020-05-01T18:03:09"
    },
    "t": "event",
    "uniqueid": "00:17:88:01:08:0e:10:d4-02-fc00"
}
```
4-second dimmer 'minus' press:
```
{
    "e": "changed",
    "id": "5",
    "r": "sensors",
    "state": {
        "buttonevent": 3000,
        "eventduration": 0,
        "lastupdated": "2020-05-01T18:01:54"
    },
    "t": "event",
    "uniqueid": "00:17:88:01:08:0e:10:d4-02-fc00"
}
{
    "e": "changed",
    "id": "5",
    "r": "sensors",
    "state": {
        "buttonevent": 3001,
        "eventduration": 8,
        "lastupdated": "2020-05-01T18:01:55"
    },
    "t": "event",
    "uniqueid": "00:17:88:01:08:0e:10:d4-02-fc00"
}
{
    "e": "changed",
    "id": "5",
    "r": "sensors",
    "state": {
        "buttonevent": 3001,
        "eventduration": 16,
        "lastupdated": "2020-05-01T18:01:56"
    },
    "t": "event",
    "uniqueid": "00:17:88:01:08:0e:10:d4-02-fc00"
}
{
    "e": "changed",
    "id": "5",
    "r": "sensors",
    "state": {
        "buttonevent": 3001,
        "eventduration": 24,
        "lastupdated": "2020-05-01T18:01:56"
    },
    "t": "event",
    "uniqueid": "00:17:88:01:08:0e:10:d4-02-fc00"
}
{
    "e": "changed",
    "id": "5",
    "r": "sensors",
    "state": {
        "buttonevent": 3003,
        "eventduration": 28,
        "lastupdated": "2020-05-01T18:01:57"
    },
    "t": "event",
    "uniqueid": "00:17:88:01:08:0e:10:d4-02-fc00"
}
```

## deCONZ 'virtual sensor'
```
  {
    "1":{
      "config":{
        "configured":true,
        "on":true,
        "sunriseoffset":30,
        "sunsetoffset":-30},
      "etag":"8bd046b9a5340839b658ed2696c1ea34",
      "manufacturername":"Philips",
      "modelid":"PHDL00",
      "name":"Daylight",
      "state":{
        "dark":false,
        "daylight":true,
        "lastupdated":"2020-04-29T10:25:06",
        "status":160,
        "sunrise":"2020-04-29T04:33:27",
        "sunset":"2020-04-29T19:21:51"},
      "swversion":"1.0",
      "type":"Daylight",
      "uniqueid":"00:21:2e:ff:ff:05:03:60-01"},
  ```
