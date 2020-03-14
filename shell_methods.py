"""
This script provides methods that can be tested on the interactive Python shell.
It can be pasted directly into the shell.
"""

import ev3dev.ev3 as ev3
import time

m_right = ev3.LargeMotor(ev3.OUTPUT_A)
m_left = ev3.LargeMotor(ev3.OUTPUT_D)

cs = ev3.ColorSensor(ev3.INPUT_1)
cs.mode = ev3.ColorSensor.MODE_RGB_RAW

us = ev3.UltrasonicSensor(ev3.INPUT_4)
us.mode = ev3.UltrasonicSensor.MODE_US_DIST_CM

gs = ev3.GyroSensor(ev3.INPUT_3)
gs.mode = ev3.GyroSensor.MODE_GYRO_RATE
gs.mode = ev3.GyroSensor.MODE_GYRO_ANG


def reset():
    # Reset motors
    m_right.reset()
    m_left.reset()
    m_right.stop_action = ev3.LargeMotor.STOP_ACTION_BRAKE
    m_left.stop_action = ev3.LargeMotor.STOP_ACTION_BRAKE
    # Reset gyro sensor
    gs.mode = ev3.GyroSensor.MODE_GYRO_RATE
    gs.mode = ev3.GyroSensor.MODE_GYRO_ANG


reset()


def stop():
    # Stop motors
    m_left.stop()
    m_right.stop()


def drive(sp_right=25, sp_left=25):
    # Drive using duty cycle
    m_right.duty_cycle_sp = sp_right
    m_left.duty_cycle_sp = sp_left
    m_right.command = "run-direct"
    m_left.command = "run-direct"


def check():
    cs.mode = "COL-COLOR"
    reset()  # Calibrate gyro sensor
    time.sleep(1)
    colors = {}
    gyro_start_angle = gs.angle
    for i in [-1, 1]:
        drive(i * 30 - 5, - i * 30 - 5)
        while (gs.angle < gyro_start_angle + 25) if i == -1 else (gs.angle > gyro_start_angle - 25):
            c = cs.value()
            colors[c] = colors.get(c, 0) + 1
            time.sleep(0.01)
        stop()
    print(colors)
    return colors.get(1, 0) + colors.get(6, 0) < colors.get(2, 0) + colors.get(5, 0)


def rgb_to_grayscale(red, green, blue):
    # Convert RGB to grayscale
    return (0.3 * red) + (0.59 * green) + (0.11 * blue)


def follow(delay=0.1, k_p=0.15, offset=170, target_power=20, k_i=0, k_d=0.1):
    # PID controller method for tuning
    integral = 0
    last_error = 0
    red_counter = 0
    blue_counter = 0
    while True:
        rgb = cs.bin_data("hhh")  # Read RGB values from sensor
        r = rgb[0]
        g = rgb[1]
        b = rgb[2]
        gs = rgb_to_grayscale(r, g, b)  # Convert RGB to grayscale
        # Calculate error, turn and motor powers
        error = gs - offset
        integral = 2 / 3 * integral + error
        derivative = error - last_error
        last_error = error
        turn = k_p * error + k_i * integral + k_d * derivative
        power_right = target_power + turn
        power_left = target_power - turn
        # Apply motor powers
        m_left.duty_cycle_sp = power_left
        m_right.duty_cycle_sp = power_right
        m_left.command = "run-direct"
        m_right.command = "run-direct"
        # Sleep
        time.sleep(delay)
