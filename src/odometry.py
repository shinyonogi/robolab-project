# !/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file

from planet import Planet
import math 

class Odometry:

    def __init__(self, coordinate, direction):
        """
        Initializes odometry module
        """

        # YOUR CODE FOLLOWS (remove pass, please!)

        self.line_of_sight = direction / 57.2958 #angle -> arc
        self.coordinate_x = coordinate[0]
        self.coordinate_y = coordinate[1]

    def calc_coord(self, motor_stack):

        distance_tire = 12

        for i in range(len(motor_stack)):

            d_r = Odometry.distance_per_tick(motor_stack[i][0])
            d_l = Odometry.distance_per_tick(motor_stack[i][1])

            delta_x = 0
            delta_y = 0

            angle_alpha = (d_r - d_l) / distance_tire 

            if(6.28319 >= angle_alpha >= 6.10865 or 0 <= angle_alpha <= 0.174533 ): #when the way is straight
                if(self.line_of_sight):
                    distance_s = d_l
                    delta_x = delta_x + distance_s
                    delta_y = delta_y + distance_s
            else:
                angle_beta = angle_alpha / 2
                distance_s = (d_r + d_l)/angle_alpha * math.sin(angle_beta)
                delta_x = delta_x + -math.sin(self.line_of_sight + angle_beta) * distance_s
                delta_y = delta_y + math.cos(self.line_of_sight + angle_beta) * distance_s

            self.line_of_sight += angle_alpha 
            self.coordinate_x += delta_x
            self.coordinate_y += delta_y


        self.coordinate_x = round(self.coordinate_x / 50)
        self.coordinate_y = round(self.coordinate_y / 50)
        self.direction = round(self.line_of_sight * 57.2958) % 360

        return ((self.coordinate_x, self.coordinate_y), self.direction)


    def distance_per_tick(motor_spin):

        radius = 2.8
        circumference = 2 * radius * math.pi
        motor_spin = motor_spin * (circumference / 360)

        return motor_spin 

    def reset(self, direction, coordinate_x, coordinate_y):

        self.direction = direction 
        self.coordinate_x = coordinate_x
        self.coordinate_y = coordinate_y
        