# !/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file

from planet import Planet

class Odometry:
    def __init__(self, line_of_sight, cooreinate_x, coordinate_y):
        """
        Initializes odometry module
        """

        # YOUR CODE FOLLOWS (remove pass, please!)
        distance_tire = 0
        radius = 0
        circumference = 2 * radius * math.pi

        self.d_l = 0 
        self.d_r = 0
        self.line_of_sight = line_of_sight
        self.coordinate_x = coordinate_x
        self.coordinate_y = coordinate_y
