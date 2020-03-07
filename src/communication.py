#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
import json
# import ssl


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

        self.planet_data = None
        self.path_select = None
        self.target = None

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

        m_from = payload.get("from")
        m_type = payload.get("type")
        m_payload = payload.get("payload")

        if m_from == "debug":
            pass
        elif m_from == "server":
            if m_type == "planet":
                self.planet_topic = f"planet/{m_payload['planetName']}/{self.group_id}"
                self.client.subscribe(self.planet_topic)
                self.planet_data = m_payload
            elif m_type == "path" or m_type == "pathUnveiled":
                Xs = m_payload["startX"]
                Ys = m_payload["startY"]
                Ds = m_payload["startDirection"]
                Xe = m_payload["endX"]
                Ye = m_payload["endY"]
                De = m_payload["endDirection"]
                path_status = m_payload["pathStatus"]  # TODO: do we add this to Planet?
                path_weight = m_payload["weight"]

                self.planet.add_path(((Xs, Ys), Ds), ((Xe, Ye), De), path_weight)
            elif m_type == "pathSelect":
                self.path_select = payload
            elif m_type == "target":
                self.target = payload
            elif m_type == "done":
                message = m_payload["message"]
                self.logger.info("Message from Mothership", message)

    def reset_path_select(self):
        self.path_select = None

    def reset_target(self):
        self.target = None

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
            "payload": {
                "planetName": planet_name
            }
        }

        self.send_message(self.topic, message)

    def ready_message(self):
        self.client.subscribe(self.topic, qos=1)

        message = {
            "from": "client",
            "type": "ready"
        }

        self.send_message(self.topic, message)

    def path_message(self, Xs, Ys, Ds, Xe, Ye, De, path_status):
        message = {
            "from": "client",
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
        message = {
            "from": "client",
            "type": "pathSelect",
            "payload": {
                "startX": Xs,
                "startY": Ys,
                "startDirection": Ds
            }
        }

        self.send_message(self.topic, message)

    def target_reached_message(self):
        message = {
            "from": "client",
            "type": "targetReached",
            "payload": {
                "message": "Target Reached"
            }
        }

        self.send_message(self.topic, message)

    def exploration_completed_message(self):
        message = {
            "from": "client",
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
