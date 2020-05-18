# !/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file

import math


class Odometry:
    """
    Odometry module
    """

    def __init__(self, logger, motor_right, motor_left):
        self.logger = logger

        self.motor_right = motor_right
        self.motor_left = motor_left

        self.motor_position_left = self.motor_left.position
        self.motor_position_right = self.motor_right.position

        self.motor_stack = []

        self.wheel_circumference_mm = 2 * math.pi * 28
        self.wheel_distance_mm = 120

        self.angle_rad = 0
        self.x_position_mm = 0
        self.y_position_mm = 0

    def set_coord(self, x_coord=None, y_coord=None, direction=None):
        if x_coord is not None:
            self.x_position_mm = x_coord * 500

        if y_coord is not None:
            self.y_position_mm = y_coord * 500

        if direction is not None:
            self.angle_rad = math.radians(direction)

    def get_coord(self):
        return (
            (round(self.x_position_mm / 500), round(self.y_position_mm / 500)),
            self.angle_to_direction(math.degrees(self.angle_rad))
        )

    def get_mm_coord(self):
        return (
            (self.x_position_mm, self.y_position_mm),
            math.degrees(self.angle_rad)
        )

    def calc_coord(self):
        if len(self.motor_stack) == 0:
            return self.get_coord()

        prev_pos_right = self.motor_stack[0][0]
        prev_pos_left = self.motor_left[0][1]
        self.motor_stack.pop(0)

        while len(self.motor_stack) > 0:
            current_pos = self.motor_stack.pop(0)
            pos_right = current_pos[0]
            pos_left = current_pos[1]

            ticks_right = pos_right - prev_pos_right
            ticks_left = pos_left - prev_pos_left

            if not ticks_right and not ticks_left:
                continue

            prev_pos_right = pos_right
            prev_pos_left = pos_left

            rotations_right = float(ticks_right / 360)
            rotations_left = float(ticks_left / 360)

            mm_right = float(rotations_right * self.wheel_circumference_mm)
            mm_left = float(rotations_left * self.wheel_circumference_mm)

            mm = (mm_right + mm_left) / 2.0

            self.angle_rad += (mm_left - mm_right) / self.wheel_circumference_mm
            self.angle_rad %= 2 * math.pi

            self.x_position_mm += mm * math.sin(self.angle_rad)
            self.y_position_mm += mm * math.cos(self.angle_rad)

        return self.get_coord()

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

    def update_motor_stack(self):
        delta_motor_left = abs(abs(self.motor_left.position) - abs(self.motor_position_left))
        delta_motor_right = abs(abs(self.motor_right.position) - abs(self.motor_position_right))

        if delta_motor_left >= 0 or delta_motor_right >= 0:
            self.motor_stack.append([delta_motor_left, delta_motor_right])
            self.motor_position_left = self.motor_left.position
            self.motor_position_right = self.motor_right.position

    def update_motor_positions(self):
        self.motor_position_right = self.motor_right.position
        self.motor_position_left = self.motor_left.position
        self.clear_motor_stack()

    def clear_motor_stack(self):
        self.motor_stack.clear()
