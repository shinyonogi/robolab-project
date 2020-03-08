# !/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file

import math


class Odometry:
    """
    Odometry module
    """

    def __init__(self, logger, motor_right, motor_left):
        self.logger = logger

        self.line_of_sight = None
        self.direction = None
        self.coordinate_x = None
        self.coordinate_y = None

        self.motor_right = motor_right
        self.motor_left = motor_left

        self.motor_position_left = self.motor_left.position
        self.motor_position_right = self.motor_right.position

        self.motor_stack = []

    def set_start_coord(self, coordinate, direction):
        self.coordinate_x = coordinate[0]
        self.coordinate_y = coordinate[1]
        self.direction = direction
        self.line_of_sight = direction / 57.2958  # angle -> arc

    def calc_coord(self):
        distance_tire = 12

        delta_x = 0
        delta_y = 0

        for i in range(len(self.motor_stack)):
            d_r = self.distance_per_tick(self.motor_stack[i][1])
            d_l = self.distance_per_tick(self.motor_stack[i][0])

            angle_alpha = (d_r - d_l) / distance_tire
            angle_beta = angle_alpha / 2

            if 6.28319 >= angle_alpha >= 6.10865 or 0 <= angle_alpha <= 0.174533:  # when the way is straight
                distance_s = d_l
                if self.direction == 0:  # maybe better to work with arc // precise values better
                    delta_y = delta_y + distance_s
                elif self.direction == 180:
                    delta_y = delta_y - distance_s
                elif self.direction == 90:
                    delta_x = delta_x + distance_s
                elif self.direction == 270:
                    delta_x = delta_x - distance_s
            else:
                distance_s = (d_r + d_l) / angle_alpha * math.sin(angle_beta)
                delta_x = delta_x + -math.sin(self.line_of_sight + angle_beta) * distance_s
                delta_y = delta_y + math.cos(self.line_of_sight + angle_beta) * distance_s
            self.line_of_sight += angle_alpha

            self.logger.debug("LOS: %s, Angle: %s" % (self.line_of_sight, angle_alpha))

        self.coordinate_x = self.coordinate_x + round(delta_x / 50)
        self.coordinate_y = self.coordinate_y + round(delta_y / 50)
        self.direction = round(self.line_of_sight * 57.2958) % 360

        if(0 <= self.direction < 45 or 360 >= self.direction > 315):
            self.direction = 0
        elif(45 <= self.direction < 135):
            self.direction = 90
        elif(135 <= self.direction < 225):
            self.direction = 180
        elif(225 <= self.direction < 315):
            self.direction = 270

        return ((self.coordinate_x, self.coordinate_y), self.direction)

    def distance_per_tick(self, motor_spin):
        radius = 2.8
        circumference = 2 * radius * math.pi
        motor_spin = motor_spin * (circumference / 360)

        return motor_spin

    def reset(self, direction, coordinate_x, coordinate_y):
        self.direction = direction
        self.coordinate_x = coordinate_x
        self.coordinate_y = coordinate_y
        self.motor_stack = []

    def motorg_stack(self):
        delta_motor_left = abs(abs(self.motor_left.position) - abs(self.motor_position_left))
        delta_motor_right = abs(abs(self.motor_right.position) - abs(self.motor_position_right))

        # print("delta motor left: ", delta_motor_left, self.motor_left.position, self.motor_position_left)
        # print("delta motor right: ", delta_motor_right, self.motor_right.position, self.motor_position_right)

        if delta_motor_left > 360:
            self.motor_stack.append([delta_motor_left, delta_motor_right])
            self.motor_position_left = self.motor_left.position 
            self.motor_position_right = self.motor_right.position 

    def clear_stack(self):
        self.motor_stack.clear()
