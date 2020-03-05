#!/usr/bin/env python3

from odometry import Odometry
import unittest

class OdometryTest(unittest.TestCase):
    
    def setUp(self):
        
        self.motor_stack = []
        self.motor_stack.append([360, 360])
        self.motor_stack.append([360, 360])
        self.motor_stack.append([360, 360])


    def test_straight_path(self):

        odometry = Odometry((0, 0), 0)
        coordinate = odometry.calc_coord(self.motor_stack)
        self.assertEqual(((1, 1), 0), coordinate)


    def test_straight_path_backwards(self):

        odometry = Odometry((0, 0), 90)
        odometry.calc_coord(self.motor_stack)
        #self.assertEqual((0, 0), (self.odometry.get_cord()))
        #self.assertEqual

if __name__ == "__main__":
    unittest.main()