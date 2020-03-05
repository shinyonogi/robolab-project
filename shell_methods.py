"""
This script provides methods that can be tested on the interactive Python shell.
It can be pasted directly into the shell.
"""

import ev3dev.ev3 as ev3
import time

m_right = ev3.LargeMotor(ev3.OUTPUT_A)
m_left = ev3.LargeMotor(ev3.OUTPUT_D)
m_right.stop_action = ev3.LargeMotor.STOP_ACTION_COAST
m_left.stop_action = ev3.LargeMotor.STOP_ACTION_COAST

cs = ev3.ColorSensor(ev3.INPUT_1)
cs.mode = ev3.ColorSensor.MODE_RGB_RAW

us = ev3.UltrasonicSensor(ev3.INPUT_4)
cs.mode = ev3.UltrasonicSensor.MODE_US_DIST_CM


def reset():
    # Reset motors
    m_right.reset()
    m_left.reset()


def stop():
    # Stop motors
    m_left.stop()
    m_right.stop()


def drive(sp_left=100, sp_right=100):
    # Drive using speed_sp
    m_left.speed_sp = sp_left
    m_right.speed_sp = sp_right
    m_left.command = "run-forever"
    m_right.command = "run-forever"


def drive_dc(sp_left=30, sp_right=30):
    # Drive using duty cycle
    m_left.duty_cycle_sp = sp_left
    m_right.duty_cycle_sp = sp_right
    m_left.command = "run-direct"
    m_right.command = "run-direct"


def rgb_to_grayscale(red, green, blue):
    # Convert RGB to grayscale
    return (0.3 * red) + (0.59 * green) + (0.11 * blue)


def test_color_gs():
    # Output current sensor grayscale value every second
    while True:
        rgb = cs.bin_data("hhh")
        r = rgb[0]
        g = rgb[1]
        b = rgb[2]
        gs = rgb_to_grayscale(r, g, b)
        print("grayscale %s, error %s" % (int(gs), int(gs - 170)))
        time.sleep(1)


def test_color():
    # Detect every second, if current color sensor value is red or blue, if not convert to grayscale.
    while True:
        rgb = cs.bin_data("hhh")
        r = rgb[0]
        g = rgb[1]
        b = rgb[2]
        if r > 100 > g and b < 100:
            print("red")
        elif g > 100 > r and b < 100 or b > 100 > r and g < 100:
            print("blue")
        else:
            print("grayscale %s" % rgb_to_grayscale(r, g, b))
        time.sleep(1)


reset()
