#!/usr/bin/env python3

import ev3dev.ev3 as ev3
import logging
import sys
import os
import time
import paho.mqtt.client as mqtt
import uuid

from communication import Communication
from expression import Expression
from odometry import Odometry
from planet import Direction, Planet
from explorer import Explorer

client = None  # DO NOT EDIT
explorer = None
logger = None


def run():
    # DO NOT CHANGE THESE VARIABLES
    #
    # The deploy-script uses the variable "client" to stop the mqtt-client after your program stops or crashes.
    # Your script isn't able to close the client after crashing.
    global client, explorer, logger

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

    logger.addHandler(logging.StreamHandler(sys.stdout))

    # Declare hardware components
    screen = ev3.Screen()
    led = ev3.Led()
    speaker = ev3.Sound
    button = ev3.Button()
    button.on_up = up_callback
    button.on_down = down_callback
    motor_right = ev3.LargeMotor(ev3.OUTPUT_A)
    motor_left = ev3.LargeMotor(ev3.OUTPUT_D)
    color_sensor = ev3.ColorSensor(ev3.INPUT_1)
    us_sensor = ev3.UltrasonicSensor(ev3.INPUT_4)

    communication = Communication(client, logger)
    odometry = Odometry(logger, None, None, motor_right, motor_left)
    planet = Planet()
    communication = Communication(client, logger, planet)
    expression = Expression(logger, screen, led, speaker)
    explorer = Explorer(logger, communication, odometry, planet, expression, motor_right, motor_left, color_sensor, us_sensor)

    logger.info("Robot ready!")

    while True:
        button.process()
        time.sleep(0.250)


def up_callback(state):
    logger.debug("Up-Button pressed" if state else "Up-Button released")
    # TODO: this doesn't work because the LineFollower start blocks the thread
    if explorer:
        if not explorer.is_running:
            explorer.start()
        else:
            explorer.stop()


def down_callback(state):
    logger.debug("Down-Button pressed" if state else "Down-Button released")
    sys.exit(0)


# DO NOT EDIT
if __name__ == '__main__':
    run()
