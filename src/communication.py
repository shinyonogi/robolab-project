#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
import json
# import ssl
import time

from planet import Planet


class Communication:
    """
    Class to hold the MQTT client communication
    Feel free to add functions and update the constructor to satisfy your requirements and
    thereby solve the task according to the specifications
    """

    def __init__(self, mqtt_client, logger, planet, group_id, planet_name):
        """
        Initializes communication module, connect to server, subscribe, etc.
        :param mqtt_client: paho.mqtt.client.Client
        :param logger: logging.Logger
        """
        # DO NOT CHANGE THE SETUP HERE
        self.client = mqtt_client
        # self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        self.client.on_message = self.safe_on_message_handler

        self.logger = logger
        self.planet = planet
        self.group_id = group_id

        self.topic = f"explorer/{group_id}"
        self.planet_name = planet_name

        self.target_determined = False

    def connect(self, username, password):
        self.client.username_pw_set(username=username, password=password)

        self.client.connect("mothership.inf.tu-dresden.de", port=1883)
        self.logger.debug("Connecting to mothership")

        self.client.loop_start()
        self.logger.debug("Starting communication loop")

    def disconnect(self):
        self.client.disconnect()

    # DO NOT EDIT THE METHOD SIGNATURE
    def on_message(self, client, data, message):
        """
        Handles the callback if any message arrived
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        payload = json.loads(message.payload.decode('utf-8'))
        self.logger.debug(json.dumps(payload, indent=2))

        # YOUR CODE FOLLOWS (remove pass, please!)

        if payload["from"] == "debug":
            self.logger.debug("Message from Debug: ", payload)
        elif payload["from"] == "server":
            if payload["type"] == "planet":
                self.client.subscribe(f"planet/{payload['payload']['planetName']}/{self.group_id}")
                self.X = payload["payload"]["startX"]
                self.Y = payload["payload"]["startY"]
            elif payload["type"] == "path":
                Xs = payload["payload"]["startX"]
                Ys = payload["payload"]["startY"]
                Ds = payload["payload"]["startDirection"]
                self.Xc = payload["payload"]["endX"]
                self.Yc = payload["payload"]["endY"]
                self.Dc = payload["payload"]["endDirection"]
                self.path_status = payload["payload"]["pathstatus"]
                path_weight = payload["payload"]["weight"]

                self.planet.add_path(((Xs, Ys), Ds), ((self.Xc, self.Yc), self.Dc), path_weight)
            elif payload["type"] == "pathselect":
                self.Dc = payload["payload"]["startDirection"]
            elif payload["type"] == "pathUnveiled":
                Xs = payload["payload"]["startX"]
                Ys = payload["payload"]["startY"]
                Ds = payload["payload"]["startDirection"]
                Xe = payload["payload"]["endX"]
                Ye = payload["payload"]["endY"]
                De = payload["payload"]["endDirection"]
                path_status = payload["payload"]["pathstatus"]
                path_weight = payload["payload"]["weight"]

                self.planet.add_path(((Xs, Ys), Ds), ((Xe, Ye), De), path_weight)
            elif payload["type"] == "target":
                self.Xt = payload["payload"]["targetX"]
                self.Yt = payload["payload"]["targetY"]
                self.target_determined = True
            elif payload["type"] == "done":
                message = payload["payload"]["message"]
                self.logger.debug("Message from Mothership", message)

        time.sleep(3)

    # DO NOT EDIT THE METHOD SIGNATURE
    #
    # In order to keep the logging working you must provide a topic string and
    # an already encoded JSON-Object as message.
    def send_message(self, topic, message):
        """
        Sends given message to specified channel
        :param topic: String
        :param message: Object
        :return: void
        """
        self.logger.debug('Send to: ' + topic)
        self.logger.debug(json.dumps(message, indent=2))

        # YOUR CODE FOLLOWS (remove pass, please!)
        self.client.publish(topic, json.dumps(message))

        time.sleep(3)

    # DO NOT EDIT THE METHOD SIGNATURE OR BODY
    #
    # This helper method encapsulated the original "on_message" method and handles
    # exceptions thrown by threads spawned by "paho-mqtt"
    def safe_on_message_handler(self, client, data, message):
        """
        Handle exceptions thrown by the paho library
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        try:
            self.on_message(client, data, message)
        except:
            import traceback
            traceback.print_exc()
            raise

    def testplanet_message(self):
        message = {"from": "client",
                   "type": "testplanet",
                   "payload": {"planetname": self.planet_name}}
        self.send_message(self.topic, message)

    def ready_message(self):
        self.client.subscribe(self.topic, qos=1)
        message = {"from": "client",
                   "type": "ready"}
        self.send_message(self.topic, message)
        self.client.subscribe(f"planet/{self.planet_name}/{self.group_id}", qos=1)

    def path_message(self, Xs, Ys, Ds, Xe, Ye, De, path_status):
        message = {"from": "client",
                   "type": "path",
                   "payload": {
                       "startX": Xs,
                       "startY": Ys,
                       "startDirection": Ds,
                       "endX": Xe,
                       "endY": Ye,
                       "endDirection": De,
                       "pathStatus": path_status
                   }
                   }
        self.send_message(self.topic, message)

    def path_select_message(self, Xs, Ys, Ds):
        message = {"from": "client",
                   "type": "pathselect",
                   "payload": {
                       "startX": Xs,
                       "startY": Ys,
                       "startDirection": Ds
                   }
                   }
        self.send_message(self.topic, message)

    def target_reached_message(self):
        message = {"from": "client",
                   "type": "targetReached",
                   "payload": {
                       "message": "Target Reached"
                   }
                   }
        self.send_message(self.topic, message)

    def exploration_completed_message(self):
        message = {"from": "client",
                   "type": "explorationCompleted",
                   "payload": {
                       "message": "Exploration Completed"
                   }
                   }
        self.send_message(self.topic, message)

        self.client.loop_stop()
        self.client.disconnect()

    def syntax_prove(self):
        self.client.subscribe(f"comtest/{self.group_id}", qos=1)
