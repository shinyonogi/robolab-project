#!/usr/bin/env python3

import unittest
from  communication import Communication

import logging
import os
import paho.mqtt.client as mqtt
import uuid

import json
import ssl

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

        self.communication = Communication(client, logger)
        self.communication.syntax_prove()

    def test_ready_message(self):

        self.communication.ready_message()


    def test_path_message(self):

        self.communication.path_message(0, 0, 0, 0, 0, 0, "blocked")


    def test_path_select_message(self):

        self.communication.path_select_message(0, 0, 0)


    def test_target_reached_message(self):

        self.communication.target_reached_message()


    def test_exploration_completed_message(self):

        self.communication.exploration_completed_message()


    def test_testplanet_message(self):

        self.communication.testplanet_message()


if __name__ == "__main__":
    unittest.main()