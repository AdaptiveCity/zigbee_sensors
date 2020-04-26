# Phoscon Web App deconz rest API calls

With test usage of PWA: startup, select `Sensors`, select `Sensor #2`, 
PWA makes the following calls to the deconz REST API:

```
/api/<apikey>/config?_=1587834781941
/api/<apikey>/config?_=1587834781942
/api/<apikey>/sensors/new
/api/<apikey>/sensors?_=1587834781943
/api/<apikey>/sensors?_=1587834781944
ws://<hostaddress>:443/
/api/<apikey>/sensors/new?_=1587834781945
/api/<apikey>/sensors?_=1587834781946     (repeats 5 seconds)
/api/<apikey>/sensors/new?_=1587834781947 (repeats 5 seconds)
```

API calls while idle on home page:

```
/api/<apikey>/groups?_=1587914100421
/api/<apikey>/lights?_=1587914100422
/api/<apikey>/sensors?_=1587914100423
/api/<apikey>/config?_=1587914100424
```
(repeating at 15 seconds)

API calls while viewing Sensor 2 and opening sensor:
```
GET /api/<apikey>/sensors?_=1587914812744
GET /api/<apikey>/sensors/new?_=1587914812745
GET /api/<apikey>/sensors/2
GET /api/<apikey>/sensors?_=1587914812746
GET /api/<apikey>/sensors/new?_=1587914812747
```

API calls while "Add new sensor"
```
"GET /api/<apikey>/sensors/new?_=1587915444273"
"GET /api/<apikey>/sensors?_=1587915444274"
"POST /api/<apikey>/sensors"
"GET /api/<apikey>/sensors/new?_=1587915444275"
...
"GET /api/<apikey>/sensors/new?_=1587915444282"
"PUT /api/<apikey>/config"
"GET /api/<apikey>/sensors/new?_=1587915444283"
"GET /api/<apikey>/sensors?_=1587915444284"
"PUT /api/<apikey>/config"
"GET /api/<apikey>/sensors/new?_=1587915444285"
```
Detail of each API call is listed below:

## POST `/api/<apikey>/sensors` (from Add New Sensor)
```
{
    "startedDateTime": "2020-04-26T16:01:56.351Z",
    "time": 4.205000004731119,
    "request": {
      "method": "POST",
      "url": "http://192.168.1.118/api/<apikey>/sensors",
      "httpVersion": "HTTP/1.1",
      "headers": "usual stuff",
      "queryString": [],
      "cookies": [],
      "headersSize": 598,
      "bodySize": 2,
      "postData": {
        "mimeType": "application/json",
        "text": "{}"
      }
    },
    "response": {
      "status": 200,
      "statusText": "OK",
      "httpVersion": "HTTP/1.1",
      "headers": "usual stuff",
      "cookies": [],
      "content": {
        "size": 77,
        "mimeType": "application/json",
        "compression": 0,
        "text": "[{\"success\":{\"/sensors\":\"Searching for new devices\",\"/sensors/duration\":60}}]"
      },
      "redirectURL": "",
      "headersSize": 117,
      "bodySize": 77,
      "_transferSize": 194
    },
    "cache": {},
    "timings": {
      "blocked": 2.7740000299215315,
      "dns": -1,
      "ssl": -1,
      "connect": -1,
      "send": 0.088,
      "wait": 0.9070000309348106,
      "receive": 0.43599994387477636,
      "_blocked_queueing": 2.6030000299215317
    },
    "serverIPAddress": "192.168.1.118",
    "_initiator": "usual stuff",
    "_priority": "High",
    "_resourceType": "xhr",
    "connection": "31781",
    "pageref": "page_2"
}
```
## PUT `/api/<apikey>/config` (Ending Add New Sensor)
```
 {
    "startedDateTime": "2020-04-26T16:01:59.876Z",
    "time": 13.6009999550879,
    "request": {
      "method": "PUT",
      "url": "http://192.168.1.118/api/B9FAF065F0/config",
      "httpVersion": "HTTP/1.1",
      "headers": "usual stuff",
      "queryString": [],
      "cookies": [],
      "headersSize": 597,
      "bodySize": 16,
      "postData": {
        "mimeType": "application/json",
        "text": "{\"permitjoin\":0}"
      }
    },
    "response": {
      "status": 200,
      "statusText": "OK",
      "httpVersion": "HTTP/1.1",
      "headers": "usual stuff",
      "cookies": [],
      "content": {
        "size": 38,
        "mimeType": "application/json",
        "compression": 0,
        "text": "[{\"success\":{\"/config/permitjoin\":0}}]"
      },
      "redirectURL": "",
      "headersSize": 158,
      "bodySize": 38,
      "_transferSize": 196
    },
    "cache": {},
    "timings": {
      "blocked": 11.242999921746552,
      "dns": -1,
      "ssl": -1,
      "connect": -1,
      "send": 0.20400000000000063,
      "wait": 0.9079999753236763,
      "receive": 1.246000058017671,
      "_blocked_queueing": 2.175999921746552
    },
    "serverIPAddress": "192.168.1.118",
    "_initiator": "usual stuff",
    "_priority": "High",
    "_resourceType": "xhr",
    "connection": "37112",
    "pageref": "page_2"
}
```
## GET `/api/<apikey>/sensors/2`
```
 {
    "startedDateTime": "2020-04-26T15:30:09.955Z",
    "time": 3.7360000424087048,
    "request": {
      "method": "GET",
      "url": "http://192.168.1.118/api/<apikey>/sensors/2",
      "httpVersion": "HTTP/1.1",
      "headers": "usual stuff",
      "queryString": [],
      "cookies": [],
      "headersSize": 518,
      "bodySize": 0
    },
    "response": {
      "status": 200,
      "statusText": "OK",
      "httpVersion": "HTTP/1.1",
      "headers": "usual stuff",
      "cookies": [],
      "content": {
        "size": 351,
        "mimeType": "application/json",
        "compression": 0,
        "text": {
            "config": {
                "battery":100,
                "on":true,
                "reachable":true,
                "temperature":2700},
            "ep":1,
            "etag":"96371585b06d87a977395cbe7fc589d1",
            "manufacturername":"LUMI",
            "modelid":"lumi.sensor_magnet.aq2",
            "name":"OpenClose 2",
            "state":{
                "lastupdated":"2020-04-26T15:29:57",
                "open":true},
            "swversion":"20161128",
            "type":"ZHAOpenClose",
            "uniqueid":"00:15:8d:00:04:5c:91:b3-01-0006"
        }
      },
      "redirectURL": "",
      "headersSize": 159,
      "bodySize": 351,
      "_transferSize": 510
    },
    "cache": {},
    "timings": {
      "blocked": 1.2760000858828424,
      "dns": -1,
      "ssl": -1,
      "connect": -1,
      "send": 0.11399999999999999,
      "wait": 1.7590000270158053,
      "receive": 0.586999929510057,
      "_blocked_queueing": 0.7910000858828425
    },
    "serverIPAddress": "192.168.1.118",
    "_initiator": "usual stuff",
    "_priority": "High",
    "_resourceType": "xhr",
    "connection": "29537",
    "pageref": "page_1"
}
```
## `/api/<apikey>/config?_=1587834781941`

```
{
  "startedDateTime": "2020-04-25T17:13:02.192Z",
  "time": 42.18999991111457,
  "request": {
    "method": "GET",
    "url": "http://192.168.1.53/api/<apikey>/config?_=1587834781941",
    "httpVersion": "HTTP/1.1",
    "headers": [
      {
        "name": "Host",
        "value": "192.168.1.53"
      },
      {
        "name": "Connection",
        "value": "keep-alive"
      },
      {
        "name": "Pragma",
        "value": "no-cache"
      },
      {
        "name": "Cache-Control",
        "value": "no-cache"
      },
      {
        "name": "Accept",
        "value": "vnd.ddel.v1"
      },
      {
        "name": "User-Agent",
        "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"
      },
      {
        "name": "X-Requested-With",
        "value": "XMLHttpRequest"
      },
      {
        "name": "Referer",
        "value": "http://192.168.1.53/pwa/devices-sensors.html?_v=fc464a7b5d2873c5b32080f1a825d315607bbe29,3,6,18&gwid=00212EFFFF050360"
      },
      {
        "name": "Accept-Encoding",
        "value": "gzip, deflate"
      },
      {
        "name": "Accept-Language",
        "value": "en-GB,en-US;q=0.9,en;q=0.8"
      }
    ],
    "queryString": [
      {
        "name": "_",
        "value": "1587834781941"
      }
    ],
    "cookies": [],
    "headersSize": 529,
    "bodySize": 0
  },
  "response": {
    "status": 200,
    "statusText": "OK",
    "httpVersion": "HTTP/1.1",
    "headers": [
      {
        "name": "Access-Control-Allow-Origin",
        "value": "*"
      },
      {
        "name": "Content-Type",
        "value": "application/json; charset=utf-8"
      },
      {
        "name": "Content-Length",
        "value": "3249"
      },
      {
        "name": "ETag",
        "value": "6a2509be57f40444524e9743d0c02510"
      }
    ],
    "cookies": [],
    "content": {
      "size": 3249,
      "mimeType": "application/json",
      "compression": 0,
      "text": 
      {
    "UTC":"2020-04-25T17:12:52",
    "announceinterval":45,
    "announceurl":"https://phoscon.de/discover",
    "apiversion":"2.05.74",
    "bridgeid":"00212EFFFF050360",
    "datastoreversion":"60",
    "devicename":"ConBee II",
    "dhcp":true,
    "discovery":true,
    "factorynew":false,
    "fwneedupdate":false,
    "fwupdatestate":"idle",
    "fwversion":"0x264a0700",
    "gateway":"192.168.1.1",
    "groupdelay":50,
    "homebridge":"not-managed",
    "homebridgepin":null,
    "homebridgeupdate":false,
    "homebridgeupdateversion":null,
    "homebridgeversion":null,
    "ipaddress":"192.168.1.53",
    "linkbutton":false,
    "localtime":"2020-04-25T18:12:52",
    "mac":"dc:a6:32:41:bf:10",
    "modelid":"deCONZ",
    "name":"Phoscon-GW-1.53",
    "netmask":"255.255.255.0",
    "networkopenduration":60,
    "otauactive":false,
    "otaustate":"off",
    "panid":11231,
    "permitjoin":0,
    "permitjoinfull":0,
    "port":80,
    "portalservices":false,
    "proxyaddress":"none",
    "proxyport":0,
    "replacesbridgeid":null,
    "rfconnected":true,
    "runmode":"systemd/gui",
    "starterkitid":",
    "swcommit":"fc464a7b5d2873c5b32080f1a825d315607bbe29",
    "swupdate":{"notify":false,"text":"","updatestate":0,"url":"","version":"2.04.35"},
    "swupdate2":{
        "autoinstall":{
            "on":false,
            "updatetime":"},
        "bridge":{
            "lastinstall":"2020-02-25T11:46:04",
            "state":"allreadytoinstall"},
        "checkforupdate":false,
        "install":false,
        "lastchange":",
        "lastinstall":",
        "state":"allreadytoinstall"},
    "swversion":"2.05.74",
    "system":"linux-gw",
    "timeformat":"24h",
    "timezone":"Europe/London",
    "updatechannel":"stable",
    "uuid":"c091859f-0ae1-4f67-90c3-ebe0802a213b",
    "websocketnotifyall":true,
    "websocketport":443,
    "whitelist":{
        "14FF97815B":{"create date":"2020-04-22T16:10:09","last use date":"2020-04-22T16:10:09","name":"Phoscon#B1133x817"},
        "1B85D49BBE":{"create date":"2020-04-23T08:39:27","last use date":"2020-04-23T08:40:04","name":"Phoscon#B1133x817"},
        "26566B5B76":{"create date":"2020-04-25T17:04:24","last use date":"2020-04-25T17:04:29","name":"Phoscon#B1299x762"},
        "4638AF7F91":{"create date":"2020-04-22T15:36:25","last use date":"2020-04-22T21:05:32","name":"Phoscon#B1073x819"},
        "49C806834E":{"create date":"2020-04-23T09:20:12","last use date":"2020-04-23T16:21:15","name":"Phoscon#B1073x868"},
        "61F1E18763":{"create date":"2020-04-25T17:06:28","last use date":"2020-04-25T17:11:49","name":"Phoscon#B1299x762"},
        "909DDC09DC":{"create date":"2020-04-23T08:40:04","last use date":"2020-04-23T08:40:06","name":"Phoscon#B1133x817"},
        "9D79C29584":{"create date":"2020-04-22T15:49:44","last use date":"2020-04-22T15:50:04","name":"Phoscon#B1133x817"},
        "<apikey>":{"create date":"2020-04-25T17:12:42","last use date":"2020-04-25T17:12:52","name":"Phoscon#B1299x762"},
        "B7FB9FC8DF":{"create date":"2020-04-22T15:34:00","last use date":"2020-04-22T15:34:00","name":"Phoscon#B1073x819"}},
    "wifi":"not-configured",
    "wifiavailable":[
        {"channel":1,"mac":"*","rssi":-53,"ssid":"Forster-Lewis"},
        {"channel":11,"mac":"*","rssi":-33,"ssid":"CSN_NODE"},
        {"channel":1,"mac":"5c:dc:96:51:4e:ec","rssi":-41,"ssid":"ianstudy"},
        {"channel":48,"mac":"5c:dc:96:51:4e:ed","rssi":-54,"ssid":"5GHz-ianstudy"},
        {"channel":1,"mac":"00:26:75:a4:50:bc","rssi":-71,"ssid":"Forster-Lewis"},
        {"channel":1,"mac":"*","rssi":-80,"ssid":"Forster-Lewis"}],
    "wifichannel":"1",
    "wificlientname":"Forster-Lewis",
    "wifiip":"192.168.1.53",
    "wifimgmt":8,
    "wifiname":null,
    "wifitype":"accesspoint",
    "zigbeechannel":15
}
    },
    "redirectURL": ",
    "headersSize": 160,
    "bodySize": 3249,
    "_transferSize": 3409
  },
  "cache": {},
  "timings": {
    "blocked": 4.511999941676855,
    "dns": 0.004999999999999893,
    "ssl": -1,
    "connect": 14.663,
    "send": 0.11799999999999855,
    "wait": 22.2369999878034,
    "receive": 0.6549999816343188,
    "_blocked_queueing": 0.4509999416768551
  },
  "serverIPAddress": "192.168.1.53",
  "_priority": "High",
  "_resourceType": "xhr",
  "connection": "115728",
  "pageref": "page_4"
}
```
## `/api/<apikey>/sensors/new`
```
{
  "startedDateTime": "2020-04-25T17:13:02.209Z",
  "time": 34.73899996335805,
  "request": {
    "method": "GET",
    "url": "http://192.168.1.53/api/<apikey>/sensors/new",
    "httpVersion": "HTTP/1.1",
    "headers": [
      {
        "name": "Host",
        "value": "192.168.1.53"
      },
      {
        "name": "Connection",
        "value": "keep-alive"
      },
      {
        "name": "Pragma",
        "value": "no-cache"
      },
      {
        "name": "Cache-Control",
        "value": "no-cache"
      },
      {
        "name": "Accept",
        "value": "vnd.ddel.v1"
      },
      {
        "name": "User-Agent",
        "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"
      },
      {
        "name": "X-Requested-With",
        "value": "XMLHttpRequest"
      },
      {
        "name": "Referer",
        "value": "http://192.168.1.53/pwa/devices-sensors.html?_v=fc464a7b5d2873c5b32080f1a825d315607bbe29,3,6,18&gwid=00212EFFFF050360"
      },
      {
        "name": "Accept-Encoding",
        "value": "gzip, deflate"
      },
      {
        "name": "Accept-Language",
        "value": "en-GB,en-US;q=0.9,en;q=0.8"
      }
    ],
    "queryString": [],
    "cookies": [],
    "headersSize": 518,
    "bodySize": 0
  },
  "response": {
    "status": 200,
    "statusText": "OK",
    "httpVersion": "HTTP/1.1",
    "headers": [
      {
        "name": "Access-Control-Allow-Origin",
        "value": "*"
      },
      {
        "name": "Content-Type",
        "value": "application/json; charset=utf-8"
      },
      {
        "name": "Content-Length",
        "value": "19"
      }
    ],
    "cookies": [],
    "content": {
      "size": 19,
      "mimeType": "application/json",
      "compression": 0,
      "text": { "lastscan": "none"}
    },
    "redirectURL": ",
    "headersSize": 117,
    "bodySize": 19,
    "_transferSize": 136
  },
  "cache": {},
  "timings": {
    "blocked": 0.9449999806135894,
    "dns": 0.007999999999999952,
    "ssl": -1,
    "connect": 13.383,
    "send": 0.12900000000000134,
    "wait": 19.932000056140126,
    "receive": 0.34199992660433054,
    "_blocked_queueing": 0.6089999806135893
  },
  "serverIPAddress": "192.168.1.53",
  "_priority": "High",
  "_resourceType": "xhr",
  "connection": "115734",
  "pageref": "page_4"
}
```
## `/api/<apikey>/sensors?_=1587834781943`

```
{
  "startedDateTime": "2020-04-25T17:13:02.256Z",
  "time": 45.940999989397824,
  "request": {
    "method": "GET",
    "url": "http://192.168.1.53/api/<apikey>/sensors?_=1587834781943",
    "httpVersion": "HTTP/1.1",
    "headers": "same as above",
    "queryString": [
      {
        "name": "_",
        "value": "1587834781943"
      }
    ],
    "cookies": [],
    "headersSize": 530,
    "bodySize": 0
  },
  "response": {
    "status": 200,
    "statusText": "OK",
    "httpVersion": "HTTP/1.1",
    "headers": "same as above",
    "cookies": [],
    "content": {
      "size": 776,
      "mimeType": "application/json",
      "compression": 0,
      "text": {
        "1":{
            "config":{
                "configured":true,
                "on":true,
                "sunriseoffset":30,
                "sunsetoffset":-30},
            "etag":"daf06e71e7b950b30d387a684648c296",
            "manufacturername":"Philips",
            "modelid":"PHDL00",
            "name":"Daylight",
            "state":{
                "dark":false,
                "daylight":true,
                "lastupdated":"2020-04-25T11:58:20",
                "status":170,
                "sunrise":"2020-04-25T04:41:24",
                "sunset":"2020-04-25T19:15:00"},
            "swversion":"1.0",
            "type":"Daylight",
            "uniqueid":"00:21:2e:ff:ff:05:03:60-01"},
        "2":{
            "config":{
                "battery":100,
                "on":true,
                "reachable":true,
                "temperature":2900},
            "ep":1,
            "etag":"5643dc6724cfc6df37d06ba417a12aa4",
            "manufacturername":"LUMI",
            "modelid":"lumi.sensor_magnet.aq2",
            "name":"OpenClose 2",
            "state":{
                "lastupdated":"2020-04-25T16:49:42",
                "open":false},
            "swversion":"20161128",
            "type":"ZHAOpenClose",
            "uniqueid":"00:15:8d:00:04:5c:91:b3-01-0006"}
        }
    },
    "redirectURL": ",
    "headersSize": 159,
    "bodySize": 776,
    "_transferSize": 935
  },
  "cache": {},
  "timings": {
    "blocked": 0.8380000503212214,
    "dns": -1,
    "ssl": -1,
    "connect": -1,
    "send": 0.04999999999999999,
    "wait": 44.68600005494058,
    "receive": 0.36699988413602114,
    "_blocked_queueing": 0.5570000503212214
  },
  "serverIPAddress": "192.168.1.53",
  "_priority": "High",
  "_resourceType": "xhr",
  "connection": "115722",
  "pageref": "page_4"
}
```
