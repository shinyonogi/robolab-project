#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
import json

# import ssl
import time


class Communication:
    """
    Class to hold the MQTT client communication
    Feel free to add functions and update the constructor to satisfy your requirements and
    thereby solve the task according to the specifications
    """

    def __init__(self, mqtt_client, logger, planet, group_id):
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

        self.topic = f"explorer/{group_id}"  # Used for: testplanet, ready, complete
        self.planet_topic = f"planet/none/{group_id}"  # Used for: path, pathSelect, pathUnveiled, target

        self.is_connected = False
        self.last_message_at = time.time()
        self.planet_data = None
        self.path = None
        self.path_select = None
        self.target = None
        self.is_done = False

    def connect(self, username, password):
        self.client.username_pw_set(username=username, password=password)

        while not self.is_connected:
            try:
                self.logger.debug("Connecting to mothership")
                self.client.connect("mothership.inf.tu-dresden.de", port=1883)
                self.is_connected = True
            except ConnectionRefusedError:
                self.logger.warning("Connection to mothership failed. Retrying...")
                time.sleep(3)

        self.client.loop_start()

    def disconnect(self):
        self.logger.debug("Disconnecting from mothership")
        self.client.loop_stop()
        self.client.disconnect()
        self.is_connected = False

    # DO NOT EDIT THE METHOD SIGNATURE
    def on_message(self, client, data, message):
        """
        Handles the callback if any message arrived
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        payload = json.loads(message.payload.decode("utf-8"))

        m_from = payload.get("from")
        m_type = payload.get("type")
        m_payload = payload.get("payload", {})

        if m_from == "debug" or m_from == "server":  # Don't log own messages
            self.logger.debug(json.dumps(payload, indent=2))

        self.last_message_at = time.time()

        if m_from == "debug":
            pass
        elif m_from == "server":
            if m_type == "planet":
                self.planet_topic = "planet/%s/%s" % (
                    m_payload.get("planetName"),
                    self.group_id,
                )
                self.client.subscribe(self.planet_topic)
                self.planet_data = m_payload
            elif m_type == "path" or m_type == "pathUnveiled":
                x_s = m_payload.get("startX")
                y_s = m_payload.get("startY")
                d_s = m_payload.get("startDirection")
                start = ((x_s, y_s), d_s)
                x_e = m_payload.get("endX")
                y_e = m_payload.get("endY")
                d_e = m_payload.get("endDirection")
                end = ((x_e, y_e), d_e)
                path_weight = m_payload.get("pathWeight")

                if m_type == "path":
                    self.path = (start, end)

                self.planet.add_path(start, end, path_weight)
            elif m_type == "pathSelect":
                self.path_select = m_payload.get("startDirection")
            elif m_type == "target":
                self.target = (m_payload.get("targetX"), m_payload.get("targetY"))
            elif m_type == "done":
                self.is_done = True
                message = m_payload.get("message")
                self.logger.info("Message from Mothership: %s" % message)

    def reset_path_select(self):
        self.path_select = None

    def reset_target(self):
        self.target = None

    def reset_path(self):
        self.path = None

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
        self.logger.debug("Send to: " + topic)
        self.logger.debug(json.dumps(message, indent=2))
        self.last_message_at = time.time()

        self.client.publish(topic, json.dumps(message))

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

    def testplanet_message(self, planet_name):
        message = {
            "from": "client",
            "type": "testplanet",
            "payload": {"planetName": planet_name},
        }

        self.send_message(self.topic, message)

    def ready_message(self):
        self.client.subscribe(self.topic, qos=1)

        message = {"from": "client", "type": "ready"}

        self.send_message(self.topic, message)

    def path_message(self, x_s, y_s, d_s, x_e, y_e, d_e, path_status):
        message = {
            "from": "client",
            "type": "path",
            "payload": {
                "startX": x_s,
                "startY": y_s,
                "startDirection": d_s,
                "endX": x_e,
                "endY": y_e,
                "endDirection": d_e,
                "pathStatus": path_status,
            },
        }

        self.send_message(self.planet_topic, message)

    def path_select_message(self, x_s, y_s, d_s):
        message = {
            "from": "client",
            "type": "pathSelect",
            "payload": {"startX": x_s, "startY": y_s, "startDirection": d_s},
        }

        self.send_message(self.planet_topic, message)

    def target_reached_message(self):
        message = {
            "from": "client",
            "type": "targetReached",
            "payload": {"message": "Target Reached"},
        }

        self.send_message(self.planet_topic, message)

    def exploration_completed_message(self):
        message = {
            "from": "client",
            "type": "explorationCompleted",
            "payload": {"message": "Exploration Completed"},
        }

        self.send_message(self.topic, message)

    def syntax_prove(self):
        self.client.subscribe("comtest/%s" % self.group_id, qos=1)
