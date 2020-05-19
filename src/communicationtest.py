#!/usr/bin/env python3

import unittest
from planet import Planet
from communication import Communication

import logging
import os
import paho.mqtt.client as mqtt
import uuid

import time


class CommunicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
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
        self.communication = Communication(client, logger, self.planet,  "004")
        self.communication.syntax_prove()

        self.communication.connect("004", "vexyOo1M27")


    def test_a_testplanet_message(self):
        self.communication.testplanet_message("Hasselhoff")

    def test_b_ready_message(self):
        self.communication.ready_message()
        time.sleep(3)
        self.assertEqual(self.communication.planet_data["planetName"], "Hasselhoff")
        self.assertEqual(self.communication.planet_data["startX"], 0)
        self.assertEqual(self.communication.planet_data["startY"], 0)
        self.assertEqual(self.communication.planet_data["startOrientation"], 0)

    def test_c_path_message(self):
        self.communication.path_message(0, 0, 0, 0, 1, 0, "free")
        time.sleep(3)
        self.assertEqual(self.communication.path, (((0, 0), 0), ((0, 1), 0)))


if __name__ == "__main__":
    unittest.main()
