"""
deconz2mqtt uses the deCONZ REST API to collect metadata for the connected
ZigBee devices and uses that to enhance data messages from the ZigBee devices
to be sent to a MQTT broker, for example to include a clear sensor identifer
in the MQTT message.

This code tested with Conbee II controller/gateway.
"""
import simplejson as json

import asyncio
import os
import sys
import signal
import time
import importlib
from datetime import datetime, timezone

import websockets

from gmqtt import Client as MQTTClient
from gmqtt.mqtt.constants import MQTTv311

from zigbee_data import ZigBeeData

# gmqtt compatible with uvloop
import uvloop

DEBUG = True

#import logging
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')


##################################################################
##################################################################
# Deconz2mqtt
##################################################################
##################################################################

class Deconz2mqtt():

    ###################
    # Sync class init
    ###################
    def __init__(self, settings):
        print("{} Deconz2mqtt __init__()".format(self.ts_string()),file=sys.stderr,flush=True)
        self.settings = settings

    #####################################
    # Signal handler for SIGINT, SIGTERM
    #####################################
    def ask_exit(self,*args):
        self.STOP.set()

    #####################################
    # Return current timestamp as string
    #####################################
    def ts_string(self):
        return '{:.6f}'.format(time.time())

    ###############################################################
    # Async initialization
    ###############################################################
    async def start(self, zigbee_data):

        self.zigbee_data = zigbee_data

        # Define async events for exit and reload (will set via signals)
        self.STOP = asyncio.Event()
        self.RELOAD = asyncio.Event()

        # connect output MQTT broker
        await self.connect_output_mqtt()

        # Connect input WebSocket
        asyncio.ensure_future(self.subscribe_input_ws())

    # Connect to input websocket
    async def subscribe_input_ws(self):
        ws_url = self.settings["input_ws"]["url"]

        connected = False

        while True:
            try:
                async with websockets.connect(ws_url) as ws:
                    connected = True
                    print("{} Deconz2mqtt connected to {}".format(self.ts_string(),ws_url),flush=True)
                    while connected:
                        try:
                            if DEBUG:
                                print("{} Deconz2mqtt awaiting msg from {}".format(self.ts_string(),ws_url),flush=True)
                            # Here we await & receive any websocket message
                            msg = await ws.recv()
                            if DEBUG:
                                pretty_msg = json.dumps(json.loads(msg), indent=4)
                                print("{} Deconz2mqtt msg received from {}:\n{}".format(
                                    self.ts_string(),
                                    ws_url,
                                    pretty_msg),flush=True)
                            #debug we're stuffing in a fake "zigbee" topic
                            self.handle_input_message("zigbee", msg)
                        except websockets.exceptions.ConnectionClosedError:
                            connected = False
                            print("{} Deconz2mqtt disconnected from {}".format(self.ts_string(),ws_url),flush=True)
                    print("{} Deconz2mqtt websocket read loop ended".format(self.ts_string()),flush=True)
            except ConnectionRefusedError:
                    print("{} Deconz2mqtt websocket connection refused from {}".format(self.ts_string(),ws_url),flush=True)
                    await asyncio.sleep(2) # sleep 2 seconds and retry

        print("{} Deconz2mqtt websocket connect loop ended".format(self.ts_string()),flush=True)

    # Connect to input MQTT broker
    async def connect_input_mqtt(self):
        self.input_client = MQTTClient(None) # auto-generate client id

        self.input_client.on_connect = self.input_on_connect
        self.input_client.on_message = self.input_on_message
        self.input_client.on_disconnect = self.input_on_disconnect
        self.input_client.on_subscribe = self.input_on_subscribe

        user = self.settings["input_mqtt"]["user"]
        password = self.settings["input_mqtt"]["password"]
        host = self.settings["input_mqtt"]["host"]
        port = self.settings["input_mqtt"]["port"]

        self.input_client.set_auth_credentials(user, password)

        await self.input_client.connect(host, port, keepalive=20, version=MQTTv311)

    async def connect_output_mqtt(self):
        self.output_client = MQTTClient(None) # auto-generate client id

        self.output_client.on_connect = self.output_on_connect
        self.output_client.on_message = self.output_on_message
        self.output_client.on_disconnect = self.output_on_disconnect
        self.output_client.on_subscribe = self.output_on_subscribe

        user = self.settings["output_mqtt"]["user"]
        password = self.settings["output_mqtt"]["password"]
        host = self.settings["output_mqtt"]["host"]
        port = self.settings["output_mqtt"]["port"]

        self.output_client.set_auth_credentials(user, password)

        await self.output_client.connect(host, port, keepalive=60, version=MQTTv311)

    ###############################################################
    # Sensor data message handler
    ###############################################################

    def handle_input_message(self, topic, msg_bytes):

        msg_dict = json.loads(msg_bytes)
        # Add required zigbee properties by updating msg_dict
        # send_data will be True if zigbee_data.decode decides this message should be sent via MQTT.
        send_data = self.zigbee_data.handle_ws_message(msg_dict)

        if send_data:
            self.send_output_message(topic, msg_dict)
        else:
            print("{} Incoming message not sent to MQTT\n{}\n".format(
                acp_ts,
                msg_bytes), flush=True)

    def send_output_message(self, topic, msg_dict):
        msg_bytes = json.dumps(msg_dict)
        #print("publishing {}".format(msg_bytes), flush=True)
        output_topic = self.settings["output_mqtt"]["topic_prefix"] + topic
        if DEBUG:
            pretty_msg = json.dumps(msg_dict, indent=4)
            print("{} MQTT publish disabled by DEBUG setting:\n{}".format(
                self.ts_string(),
                pretty_msg),flush=True)
        else:
            self.output_client.publish(output_topic, msg_bytes, qos=0)

    ###############################################################
    # WS INPUT
    ###############################################################

    def input_ws_connected(self, uri):
        print('{} INPUT Connected to {}'.format(
            self.ts_string(),
            uri), flush=True)

    ###############################################################
    # MQTT INPUT
    ###############################################################

    def input_on_connect(self, client, flags, rc, properties):
        print('{} INPUT Connected to {} as {}'.format(
            self.ts_string(),
            self.settings["input_mqtt"]["host"],
            self.settings["input_mqtt"]["user"]), flush=True)
        client.subscribe('#', qos=0)

    def input_on_message(self, client, topic, msg_bytes, qos, properties):
        # IMPORTANT! We avoid a loop by ignoring input messages with the output prefix
        if not topic.startswith(self.settings["output_mqtt"]["topic_prefix"]):
            if DEBUG:
                print('{} INPUT RECV MSG:\n{}'.format(
                    self.ts_string(),
                    msg_bytes), flush=True)
            self.handle_input_message(topic, msg_bytes)
        else:
            if DEBUG:
                print("{} INPUT RECV COOKED MSG SKIPPED".format(
                    self.ts_string()), flush=True)

    def input_on_disconnect(self, client, packet, exc=None):
        print("{} INPUT Disconnected\n".format(
            self.ts_string()),file=sys.stderr,flush=True)

    def input_on_subscribe(self, client, mid, qos, properties):
        print('{} INPUT SUBSCRIBED to {}'.format(
            self.ts_string(),
            self.settings["input_mqtt"]["topic"]), flush=True)

    ###############################################################
    # MQTT OUTPUT
    ###############################################################

    def output_on_connect(self, client, flags, rc, properties):
        print('{} OUTPUT Connected to {} as {}'.format(
            self.ts_string(),
            self.settings["output_mqtt"]["host"],
            self.settings["output_mqtt"]["user"]), flush=True)

    def output_on_disconnect(self, client, packet, exc=None):
        print("{} OUTPUT Disconnected\n".format(self.ts_string()),file=sys.stderr,flush=True)

    # These GMQTT methods here for completeness although not used

    def output_on_message(self, client, topic, msg_bytes, qos, properties):
        print('OUTPUT RECV MSG?:', msg_bytes, flush=True)

    def output_on_subscribe(self, client, mid, qos, properties):
        print('OUTPUT SUBSCRIBED? to {}', flush=True)

    ###############################################################
    # CLEANUP on EXIT SIGNAL (SIGINT or SIGTERM)
    ###############################################################

    async def finish(self):
        await self.STOP.wait()
        print("\n{} Deconz2mqtt interrupted - disconnecting\n".format(self.ts_string()),file=sys.stderr,flush=True)
        await self.output_client.disconnect()


###################################################################
# Async main - load settings.json and start coroutines
###################################################################
async def async_main():

    with open('settings.json', 'r') as sf:
        settings_data = sf.read()

    # parse file
    settings = json.loads(settings_data)

    # Instantiate a ZigBeeData to interface with deCONZ REST API
    zigbee_data = ZigBeeData(settings)

    # Instantiate a Deconz2mqtt
    deconz_2_mqtt = Deconz2mqtt(settings)

    # Add signal handlers for EXIT and RELOAD
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, deconz_2_mqtt.ask_exit)
    loop.add_signal_handler(signal.SIGTERM, deconz_2_mqtt.ask_exit)

    # Start the async coroutines.
    # Note we give deconz_2_mqtt a reference to zigbee_data
    done, pending = await asyncio.wait(
        [ deconz_2_mqtt.start(zigbee_data),
          zigbee_data.start()],
         return_when=asyncio.FIRST_COMPLETED)

    # This call to 'finish' awaits the 'STOP' event
    await deconz_2_mqtt.finish()

###################################################################
# Program main
# Sets up asyncio, runs async_main()
###################################################################
if __name__ == '__main__':

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    loop = asyncio.get_event_loop()

    loop.run_until_complete(async_main())
