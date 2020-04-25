# Conbee II deconz API and websocket access

This is an effort to connect Zigbee sensors to the Adaptive City platform. A particular challenge is the
usual tight integration between Zigbee networking and the 'application layer', i.e. all software
available for Zigbee hardware seems to need to include a configuration for every single device type
that is connected to the network (WTF?). We will try and ease this restriction, i.e. be more permissive
about allowing devices to connect to the network, and defer dealing with the application-level issues (like
whether the device is a switch or a light bulb) until later in the software stack.
