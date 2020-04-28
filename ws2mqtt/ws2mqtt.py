#!/usr/bin/env python

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

# gmqtt compatible with uvloop
import uvloop

DEBUG = False

#import logging
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')


##################################################################
##################################################################
# WS2MQTT
##################################################################
##################################################################

class WS2MQTT():

    ###################
    # Sync class init
    ###################
    def __init__(self):
        print("WS2MQTT __init__", flush=True)
        print("{} WS2MQTT started\n".format(self.ts_string()),file=sys.stderr,flush=True)

        self.settings = {}
        self.settings["decoders"] = []

    #####################################
    # Signal handler for SIGINT, SIGTERM
    #####################################
    def ask_exit(self,*args):
        self.STOP.set()

    #####################################
    # Signal handler for SIGALRM
    #####################################
    def reload(self,*args):
        self.load_decoders_file()

    #####################################
    # Return current timestamp as string
    #####################################
    def ts_string(self):
        return '{:.6f}'.format(time.time())

    ###############################################################
    # Async initialization
    ###############################################################
    async def start(self):
        # Define async events for exit and reload (will set via signals)
        self.STOP = asyncio.Event()
        self.RELOAD = asyncio.Event()

        # load settings.json into self.settings
        self.read_settings()

        # and output MQTT brokers (which can be same or different)
        await self.connect_output_mqtt()

        # Connect input WebSocket or MQTT
        #debug settings.json should be extended to support WS|MQTT
        if (True):
            self.protocol_in = "ws"
            asyncio.ensure_future(self.connect_input_ws())
        else:
            self.protocol_in = "mqtt"
            await self.connect_input_mqtt()
            
    # Connect to input websocket
    async def connect_input_ws(self):
        #debug still MQTT - add websocket code here
        #self.input_client = MQTTClient(None) # auto-generate client id

        #self.input_client.on_connect = self.input_on_connect
        #self.input_client.on_message = self.input_on_message
        #self.input_client.on_disconnect = self.input_on_disconnect
        #self.input_client.on_subscribe = self.input_on_subscribe

        #user = self.settings["input_ws"]["user"]
        #password = self.settings["input_ws"]["password"]
        host = self.settings["input_ws"]["host"]
        port = self.settings["input_ws"]["port"]

        uri = "ws://"+host+":"+str(port)
        
        #self.input_client.set_auth_credentials(user, password)

        #await self.input_client.connect(host, port, keepalive=20, version=MQTTv311)

        while True:
            async with websockets.connect(uri) as ws:
                print("ws2mqtt connected to {}".format(uri),flush=True)
                while True:
                    msg = await ws.recv()
                    if DEBUG:
                        print("{} ws2mqtt websocket message: {}".format(self.ts_string(),msg))
                    #debug topic?
                    self.handle_input_message("zigbee", msg)
                print("{} ws2mqtt disconnected to {}".format(self.ts_string,uri),flush=True)
        
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
    # Settings, including loading enabled decoders
    #
    # Builds self.settings from file "settings.json"
    # Then loads decoders listed in the setting "decoders_file"
    ###############################################################

    def read_settings(self):
        with open('settings.json', 'r') as sf:
            settings_data = sf.read()

            # parse file
        self.settings = json.loads(settings_data)

        self.load_decoders_file()

    def load_decoders_file(self):
        # getting settings filename for decoders list (json)
        decoders_file = self.settings["decoders_file"]

        # read the json file
        with open(decoders_file, 'r') as df:
            decoders_data = df.read()

        # parse to a python dictionary
        decoders_obj = json.loads(decoders_data)

        # store the new list of decoders as settings["decoders"]
        self.settings["decoders"] = decoders_obj["decoders"]

        # import/reload the decoders
        self.import_decoders(self.settings["decoders"])

    # import a list of decoder names
    def import_decoders(self, new_decoders):
        self.decoders = []
        for decoder_name in new_decoders:
            self.import_decoder(decoder_name)

    # import a decoder, given name
    # Will add { "name": , "decoder": } to self.decoders list
    def import_decoder(self, decoder_name):
        print("loading Decoder {}".format(decoder_name), flush=True)
        module_name = 'decoders.'+decoder_name
        # A new module can be imported with importlib.import_module()
        # BUT an already loaded module must use importlib.reload for update to work.
        if module_name in sys.modules:
            module = sys.modules[module_name]
            importlib.reload(module)
        else:
            module = importlib.import_module(module_name)
        # now we have the refreshed/new module, so put Decoder on list self.decoders
        decoder = module.Decoder(self.settings)
        print("    loaded Decoder {}".format(decoder_name), flush=True)
        self.decoders.append({"name": decoder_name, "decoder": decoder })

    ###############################################################
    # Sensor data message handler
    ###############################################################

    def handle_input_message(self, topic, msg_bytes):
        acp_ts = self.ts_string()
        msg_is_decoded = False
        for decoder in self.decoders:
            if decoder["decoder"].test(topic, msg_bytes):
                decoded = decoder["decoder"].decode(topic, msg_bytes)
                # If no acp_ts from decoder, insert from server time
                if not "acp_ts" in decoded:
                    decoded["acp_ts"] = acp_ts

                print("{} {} decoded by {}".format(acp_ts,decoded["acp_id"],decoder["name"]), flush=True)
                #debug testing timeout, disabled send:
                #self.send_output_message(topic, decoded)
                msg_is_decoded = True
                break # terminate the loop through decoders when first is found

        if msg_is_decoded:
            self.send_output_message(topic, decoded)
        else:
            print("{} Incoming message not decoded\n{}\n".format(acp_ts, msg_bytes), flush=True)

    def send_output_message(self, topic, decoded):
        msg_bytes = json.dumps(decoded)
        #print("publishing {}".format(msg_bytes), flush=True)
        output_topic = self.settings["output_mqtt"]["topic_prefix"] + topic
        self.output_client.publish(output_topic, msg_bytes, qos=0)

    ###############################################################
    # WS INPUT
    ###############################################################

    def input_ws_connected(self, uri):
        print('INPUT Connected to {}'.format(uri), flush=True)

    ###############################################################
    # MQTT INPUT
    ###############################################################

    def input_on_connect(self, client, flags, rc, properties):
        print('INPUT Connected to {} as {}'.format(self.settings["input_mqtt"]["host"],
                                                   self.settings["input_mqtt"]["user"]), flush=True)
        client.subscribe('#', qos=0)

    def input_on_message(self, client, topic, msg_bytes, qos, properties):
        # IMPORTANT! We avoid a loop by ignoring input messages with the output prefix
        if not topic.startswith(self.settings["output_mqtt"]["topic_prefix"]):
            if DEBUG:
                print('INPUT RECV MSG:', msg_bytes, flush=True)
            self.handle_input_message(topic, msg_bytes)
        else:
            if DEBUG:
                print('INPUT RECV COOKED MSG SKIPPED', flush=True)

    def input_on_disconnect(self, client, packet, exc=None):
        print('INPUT Disconnected', flush=True)
        print("{} INPUT Disconnected\n".format(self.ts_string()),file=sys.stderr,flush=True)

    def input_on_subscribe(self, client, mid, qos, properties):
        print('INPUT SUBSCRIBED to {}'.format(self.settings["input_mqtt"]["topic"]), flush=True)

    ###############################################################
    # MQTT OUTPUT
    ###############################################################

    def output_on_connect(self, client, flags, rc, properties):
        print('OUTPUT Connected to {} as {}'.format(self.settings["output_mqtt"]["host"],
                                                   self.settings["output_mqtt"]["user"]), flush=True)

    def output_on_disconnect(self, client, packet, exc=None):
        print('OUTPUT Disconnected', flush=True)
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
        print("\n{} WS2MQTT interrupted - disconnecting\n".format(self.ts_string()),file=sys.stderr,flush=True)
        if self.protocol_in == "mqtt":
            await self.input_client.disconnect()
        await self.output_client.disconnect()


###################################################################
# Async main
###################################################################
async def async_main():

    # Instantiate a WS2MQTT
    decoder_manager = WS2MQTT()

    # Add signal handlers for EXIT and RELOAD
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, decoder_manager.ask_exit)
    loop.add_signal_handler(signal.SIGTERM, decoder_manager.ask_exit)
    loop.add_signal_handler(signal.SIGALRM, decoder_manager.reload)

    await decoder_manager.start()

    # This call to 'finish' awaits the 'STOP' event
    await decoder_manager.finish()

###################################################################
# Program main
# Sets up asyncio, runs async_main()
###################################################################
if __name__ == '__main__':

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    loop = asyncio.get_event_loop()

    loop.run_until_complete(async_main())



