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

    # TODO: ask tutors if hooking into the logger is an issue, in that case we have to use our own
    logger.addHandler(logging.StreamHandler(sys.stdout))

    # Config variables
    group_id = "004"
    group_pwd = "vexyOo1M27"

    # Declare hardware components
    screen = ev3.Screen()
    led = ev3.Led()
    speaker = ev3.Sound
    button = ev3.Button()
    motor_right = ev3.LargeMotor(ev3.OUTPUT_A)
    motor_left = ev3.LargeMotor(ev3.OUTPUT_D)
    motor_right.reset()
    motor_left.reset()
    color_sensor = ev3.ColorSensor(ev3.INPUT_1)
    us_sensor = ev3.UltrasonicSensor(ev3.INPUT_4)

    planet = Planet()
    communication = Communication(client, logger, planet, group_id)
    odometry = Odometry(logger, motor_right, motor_left)
    expression = Expression(logger, screen, led, speaker)
    explorer = Explorer(logger, communication, odometry, planet, expression, motor_right, motor_left, color_sensor, us_sensor)

    communication.connect(group_id, group_pwd)

    while True:
        logger.info("Available commands: s to start, t to set test planet, c to calibrate, q to quit")
        cmd = input("Please enter command: ")
        if cmd == "s":
            communication.ready_message()  # Ask mothership for planet data
            logger.info("Waiting for planet data")

            planet_data = None
            while not planet_data:
                planet_data = communication.planet_data
                time.sleep(0.1)

            logger.info("Our planet is called %s" % planet_data["planetName"])

            odometry.set_start_coord((planet_data["startX"], planet_data["startY"]), planet_data["startOrientation"])

            explorer.start_exploration()
        elif cmd == "t":
            planet_name = input("Enter planet name: ")
            communication.testplanet_message(planet_name)
        elif cmd == "c":
            explorer.start_calibration()
        elif cmd == "q":
            break
        else:
            continue


# DO NOT EDIT
if __name__ == '__main__':
    run()
