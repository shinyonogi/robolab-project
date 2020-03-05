#!/usr/bin/env python3

import ev3dev.ev3 as ev3
import logging
import os
import time
import paho.mqtt.client as mqtt
import uuid

from communication import Communication
from odometry import Odometry
from planet import Direction, Planet
from line_follower import LineFollower

client = None  # DO NOT EDIT


def run():
    # DO NOT CHANGE THESE VARIABLES
    #
    # The deploy-script uses the variable "client" to stop the mqtt-client after your program stops or crashes.
    # Your script isn't able to close the client after crashing.
    global client

    client = mqtt.Client(client_id=str(uuid.uuid4()),  # Unique Client-ID to recognize our program
                         clean_session=False,  # We want to be remembered
                         protocol=mqtt.MQTTv31  # Define MQTT protocol version
                         )
    log_file = os.path.realpath(__file__) + '/../../logs/project.log'
    logging.basicConfig(filename=log_file,  # Define log file
                        level=logging.DEBUG,  # Define default mode
                        format='%(asctime)s: %(message)s'  # Define default logging format
                        )
    logger = logging.getLogger('RoboLab')

    # THE EXECUTION OF ALL CODE SHALL BE STARTED FROM WITHIN THIS FUNCTION.
    # ADD YOUR OWN IMPLEMENTATION HEREAFTER.

    # Declare hardware components
    screen = ev3.Screen()
    speaker = ev3.Sound
    motor_right = ev3.LargeMotor(ev3.OUTPUT_A)
    motor_left = ev3.LargeMotor(ev3.OUTPUT_D)
    color_sensor = ev3.ColorSensor(ev3.INPUT_4)
    us_sensor = ev3.UltrasonicSensor(ev3.INPUT_1)

    line_follower = LineFollower(logger, None, None, None, motor_right, motor_left, color_sensor, us_sensor, speaker)
    line_follower.start()

    time.sleep(10)

    line_follower.stop()

    print("Hello World!")


# DO NOT EDIT
if __name__ == '__main__':
    run()
