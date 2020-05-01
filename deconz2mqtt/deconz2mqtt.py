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

from deconzapi import ZigBeeData

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
    def __init__(self):
        print("{} Deconz2mqtt started\n".format(self.ts_string()),file=sys.stderr,flush=True)

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
    async def start(self, zigbee_data):

        self.zigbee_data = zigbee_data

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
            asyncio.ensure_future(self.subscribe_input_ws())
        else:
            self.protocol_in = "mqtt"
            await self.connect_input_mqtt()

    # Connect to input websocket
    async def subscribe_input_ws(self):
        host = self.settings["input_ws"]["host"]
        port = self.settings["input_ws"]["port"]

        uri = "ws://"+host+":"+str(port)

        connected = False

        while True:
            try:
                async with websockets.connect(uri) as ws:
                    connected = True
                    print("{} Deconz2mqtt connected to {}".format(self.ts_string(),uri),flush=True)
                    while connected:
                        try:
                            if DEBUG:
                                print("{} Deconz2mqtt awaiting msg from {}".format(self.ts_string(),uri),flush=True)
                            # Here we await & receive any websocket message
                            msg = await ws.recv()
                            if DEBUG:
                                pretty_msg = json.dumps(json.loads(msg), indent=4)
                                print("{} Deconz2mqtt msg received from {}:\n{}".format(self.ts_string(),uri,pretty_msg),flush=True)
                            #debug we're stuffing in a fake "zigbee" topic
                            self.handle_input_message("zigbee", msg)
                        except websockets.exceptions.ConnectionClosedError:
                            connected = False
                            print("{} Deconz2mqtt disconnected from {}".format(self.ts_string(),uri),flush=True)
                    print("{} Deconz2mqtt websocket read loop ended".format(self.ts_string()),flush=True)
            except ConnectionRefusedError:
                    print("{} Deconz2mqtt websocket connection refused from {}".format(self.ts_string(),uri),flush=True)
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

        #debug check if input is deconz websocket here
        if (True):
            msg_dict = json.loads(msg_bytes)
            # add required zigbee properties to message before passing it to decoders
            self.zigbee_data.decode(msg_dict)
            #debug a bit awkward to have to convert back to bytes
            msg_bytes = json.dumps(msg_dict)

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
        print("\n{} Deconz2mqtt interrupted - disconnecting\n".format(self.ts_string()),file=sys.stderr,flush=True)
        if self.protocol_in == "mqtt":
            await self.input_client.disconnect()
        await self.output_client.disconnect()


###################################################################
# Async main
###################################################################
async def async_main():

    # Instantiate a Deconz2mqtt
    deconz_2_mqtt = Deconz2mqtt()

    # Add signal handlers for EXIT and RELOAD
    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, deconz_2_mqtt.ask_exit)
    loop.add_signal_handler(signal.SIGTERM, deconz_2_mqtt.ask_exit)
    loop.add_signal_handler(signal.SIGALRM, deconz_2_mqtt.reload)

    zigbee_data = ZigBeeData()

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
