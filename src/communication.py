#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
import json
import ssl

from planet import Planet 

class Communication:
    """
    Class to hold the MQTT client communication
    Feel free to add functions and update the constructor to satisfy your requirements and
    thereby solve the task according to the specifications
    """

    def __init__(self, mqtt_client, logger):
        """
        Initializes communication module, connect to server, subscribe, etc.
        :param mqtt_client: paho.mqtt.client.Client
        :param logger: logging.Logger
        """
        # DO NOT CHANGE THE SETUP HERE
        self.client = mqtt_client
        self.client.tls_set(tls_version=ssl.PROTOCOL_TLS)
        self.client.on_message = self.safe_on_message_handler
        # Add your client setup here

        self.logger = logger

        self.topic = "explorer/004"
        self.planet_name = ""
        
        self.client.connect("mothership.inf.tu-dresden.de", port = "8883")
        self.client.loop_start()

        self.testplanet_message()
        self.ready_message()

        self.target_determined = False

        self.planet = Planet()

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
        
        if(payload["from"] == "debug"):
            print("Message from Debug: ", payload)
        elif(payload["from"] == "server"):
            if(payload["type"] == "planet"):
                self.client.subscribe(f"planet/{payload['payload']['planetName']}/004")
                self.X = payload["payload"]["startX"]
                self.Y = payload["payload"]["startY"]

            elif(payload["type"] == "path"):
                Xs = payload["payload"]["startX"]
                Ys = payload["payload"]["startY"]
                Ds = payload["payload"]["startDirection"]
                self.Xc = payload["payload"]["endX"]
                self.Yc = payload["payload"]["endY"]
                self.Dc = payload["payload"]["endDirection"]
                self.path_status = payload["payload"]["pathstatus"]
                path_weight = payload["payload"]["weight"]

                self.planet.add_path(((Xs, Ys), Ds), ((self.Xc, self.Yc), self.Dc), path_weight)

            elif(payload["type"] == "pathselect"):
                self.Dc = payload["payload"]["startDirection"]

            elif(payload["type"] == "pathUnveiled"):
                Xs = payload["payload"]["startX"]
                Ys = payload["payload"]["startY"]
                Ds = payload["payload"]["startDirection"]
                Xe = payload["payload"]["endX"]
                Ye = payload["payload"]["endY"]
                De = payload["payload"]["endDirection"]
                path_status = payload["payload"]["pathstatus"]
                path_weight = payload["payload"]["weight"]

                self.planet.add_path(((Xs, Ys), Ds), ((Xe, Ye), De), path_weight)

            elif(payload["type"] == "target"):
                self.Xt = payload["payload"]["targetX"]
                self.Yt = payload["payload"]["targetY"]
                self.target_determined = True

            elif(payload["type"] == "done"):
                message = payload["payload"]["message"]
                print("Message from Mothership", message)

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
        self.client.send_message(self.topic, message, qos = 1)

    
    def ready_message(self):

        self.client.subscribe(self.explorer_name, qos = 1)
        message = {"from": "client", 
                   "type": "ready"}
        self.client.send_message(self.topic, message, qos = 1)
        self.client.subscribe(f"planet/{self.planet_name}/004", qos = 1)


    def path_message(self, Xs, Ys, Ds, Xe, Ye, De, path_status):

        message = {"from": "client",
                   "type": "path",
                   "payload": {
                       "startX": Xs,
                       "startY": Ys,
                       "startDirection": Ds.value,
                       "endX": Xe,
                       "endY": Ye,
                       "endDirection": De.value,
                       "pathStatus": path_status
                    }
        }
        self.client.send_message(self.topic, message, qos = 1)


    def path_select_message(self, Xs, Ys, Ds):

        message = {"from": "client", 
                   "type": "pathselect",
                   "payload": {
                       "startX": Xs,
                       "startY": Ys,
                       "startDirection": Ds.value
                   }
        }
        self.client.send_message(self.topic, message, qos = 1)


    def complete_message(self):

        message = {"from": "client",
                   "type": "targetReached",
                   "payload": {
                       "message": "Target Reached"
                   }
        }
        self.client.send_message(self.topic, message, qos = 1)

        message = {"from": "client", 
                   "type": "explorationCompleted", 
                   "payload": {
                       "message": "Exploration Completed"
                   }
        }
        self.client.send_message(self.topic, message, qos = 1)

        self.client.loop_stop()
        self.client.disconnect()


    def syntax_prove(self):

        self.client.subscribe("comtest/004", qos = 1)


    