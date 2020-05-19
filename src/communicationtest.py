#!/usr/bin/env python3

import unittest
from planet import Planet
from communication import Communication

import logging
import os
import paho.mqtt.client as mqtt
import uuid


class CommunicationTest(unittest.TestCase):

    def setUp(self):
        client = mqtt.Client(client_id=str(uuid.uuid4()),
                             clean_session=False,
                             protocol=mqtt.MQTTv31
                             )
        log_file = os.path.realpath(__file__) + '/../../logs/project.log'
        logging.basicConfig(filename=log_file,
                            level=logging.DEBUG,
                            format='%(asctime)s: %(message)s'
                            )
        logger = logging.getLogger('RoboLab')

        
        self.planet = Planet()
        self.communication = Communication(client, logger, self.planet, "004")
        self.communication.planet
        self.communication.syntax_prove()

        self.communication.connect("004", "vexyOo1M27")

    def test_testplanet_message(self):
        self.communication.testplanet_message("Hasselhoff")

    def test_ready_message(self):
        self.communication.ready_message()

if __name__ == "__main__":
    unittest.main()
