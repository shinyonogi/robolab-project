#!/usr/bin/env python3

from odometry import Odometry
import unittest


class DummyMotor:
    def __init__(self, start_position=0):
        self.position = start_position

    def set_position(self, position):
        self.position = position


class OdometryTest(unittest.TestCase):
    def setUp(self):
        self.motor_right = DummyMotor()
        self.motor_left = DummyMotor()
        self.odometry = Odometry(None, self.motor_right, self.motor_left)

    def test_straight_path(self):
        self.odometry.set_coord(x_coord=0, y_coord=0, direction=0)

        for i in range(1000):  # "move" 1000 ticks (degrees), which is very close to 50 cm with our robot
            self.motor_right.set_position(i)
            self.motor_left.set_position(i)
            self.odometry.update_motor_stack()

        coords = self.odometry.calc_coord()
        self.assertEqual(((0, 1), 0), coords)

    def test_right_curve(self):
        self.odometry.set_coord(x_coord=0, y_coord=0, direction=0)

        for i in range(500):  # "move" 500 ticks on the left motor, which is about 80 degrees to the right
            self.motor_left.set_position(i)
            self.odometry.update_motor_stack()

        coords = self.odometry.calc_coord()
        self.assertEqual(((0, 0), 90), coords)

    def test_left_curve(self):
        self.odometry.set_coord(x_coord=0, y_coord=0, direction=0)

        for i in range(500):  # "move" 500 ticks on the right motor, which is about 80 degrees to the left
            self.motor_right.set_position(i)
            self.odometry.update_motor_stack()

        coords = self.odometry.calc_coord()
        self.assertEqual(((0, 0), 270), coords)


if __name__ == "__main__":
    unittest.main()
