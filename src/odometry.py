# !/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file

import math


class Odometry:
    """
    Odometry module
    """

    def __init__(self, logger, motor_right, motor_left):
        self.logger = logger

        self.line_of_sight = 0
        self.direction = 0
        self.coordinate_x = 0
        self.coordinate_y = 0

        self.angle = 0
        self.distance_cm_x = 0
        self.distance_cm_y = 0

        self.motor_right = motor_right
        self.motor_left = motor_left

        self.motor_position_left = self.motor_left.position
        self.motor_position_right = self.motor_right.position

        self.motor_stack = []

    def set_coord(self, coordinate, direction):
        if coordinate:
            self.coordinate_x = coordinate[0]
            self.coordinate_y = coordinate[1]
            self.distance_cm_x = 0
            self.distance_cm_y = 0

        if direction:
            self.angle = direction
            self.direction = direction
            self.line_of_sight = direction / 57.2958  # angle -> arc

        # self.logger.debug("LOS: %s" % self.line_of_sight)

    def reset(self):
        self.motor_position_right = self.motor_right.position
        self.motor_position_left = self.motor_left.position
        self.clear_motor_stack()

    def calc_coord(self):
        distance_tire = 12

        delta_x = 0
        delta_y = 0

        self.line_of_sight = -self.line_of_sight % 6.28319

        for i in range(len(self.motor_stack)):
            d_r = self.distance_per_tick(self.motor_stack[i][1])
            d_l = self.distance_per_tick(self.motor_stack[i][0])

            angle_alpha = (d_r - d_l) / distance_tire
            angle_beta = angle_alpha / 2

            if 0 <= angle_alpha <= 0.174533 or angle_alpha >= -0.174533:  # when the way is straight
                distance_s = d_l
                #if 0 <= self.line_of_sight % 6.28319 < 0.785398 or 6.28319 > self.line_of_sight % 6.28319 > 5.49778:  # maybe better to work with arc // precise values better
                    #delta_y = delta_y + distance_s
                #elif 2.35619 <= self.line_of_sight % 6.28319 < 3.92699:
                    #delta_y = delta_y - distance_s
                #elif 0.785398 <= self.line_of_sight % 6.28319 < 2.35619:
                    #delta_x = delta_x + distance_s
                #elif 3.92699 <= self.line_of_sight % 6.28319 < 5.49779:
                    #delta_x = delta_x - distance_s
                delta_x = delta_x + -math.sin(self.line_of_sight) * distance_s
                delta_y = delta_y + math.cos(self.line_of_sight) * distance_s
            else:
                distance_s = (d_r + d_l) / angle_alpha * math.sin(angle_beta)
                delta_x = delta_x + -math.sin(self.line_of_sight + angle_beta) * distance_s
                delta_y = delta_y + math.cos(self.line_of_sight + angle_beta) * distance_s
            self.line_of_sight += angle_alpha

            self.logger.debug("LOS: %s, Angle: %s, X: %s, Y: %s, Distance: %s, d_r: %s, d_l: %s" % (self.line_of_sight, angle_alpha, delta_x, delta_y, distance_s, d_r, d_l))

        #self.line_of_sight = -self.line_of_sight % 360

        self.coordinate_x = self.coordinate_x + round(delta_x / 50)
        self.coordinate_y = self.coordinate_y + round(delta_y / 50)
        self.angle = round(-self.line_of_sight * 57.2958) % 360

        self.distance_cm_x += round(delta_x)
        self.distance_cm_y += round(delta_y)

        self.direction = self.angle_to_direction(self.angle)

        return (self.coordinate_x, self.coordinate_y), self.direction

    @staticmethod
    def angle_to_direction(angle):
        if 0 <= angle < 45 or 360 >= angle > 315:
            return 0
        elif 45 <= angle < 135:
            return 90
        elif 135 <= angle < 225:
            return 180
        elif 225 <= angle < 315:
            return 270
        else:
            return 0

    @staticmethod
    def distance_per_tick(motor_spin):
        radius = 2.8
        circumference = 2 * radius * math.pi
        motor_spin = motor_spin * (circumference / 360)

        return motor_spin

    def update_motor_stack(self):
        delta_motor_left = abs(abs(self.motor_left.position) - abs(self.motor_position_left))
        delta_motor_right = abs(abs(self.motor_right.position) - abs(self.motor_position_right))

        if delta_motor_left >= 270 or delta_motor_right >= 270:
            self.motor_stack.append([delta_motor_left, delta_motor_right])
            self.motor_position_left = self.motor_left.position
            self.motor_position_right = self.motor_right.position
            self.logger.debug("pos_left: %s, pos_right: %s, delta_left: %s, delta_right: %s" % (self.motor_position_left, self.motor_position_right, delta_motor_left, delta_motor_right))

    def clear_motor_stack(self):
        self.motor_stack.clear()
