#!/usr/bin/env python3

import unittest
from  communication import Communication

import logging
import os
import paho.mqtt.client as mqtt
import uuid

import json
import ssl

class CommunicationTest(unittest.Testcase):

    def __init__(self):
        
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


    def ready_message_test(self):
        
        self.communication.ready_message()
