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

        self.motor_stack = []

        self.wheel_circumference_mm = 2 * math.pi * 28
        self.wheel_distance_mm = 120

        # Current orientation in radians
        self.angle_rad = 0
        # Position in mm on the 50x50 cm planet grid
        self.x_position_mm = 0
        self.y_position_mm = 0

    def set_coord(self, x_coord=None, y_coord=None, direction=None):
        # Convert coordinates on 50x50 cm planet grid to mm positions
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
        if len(self.motor_stack) == 0:  # Skip calculation if stack is empty
            return self.get_coord()

        first_pos = self.motor_stack.pop(0)
        prev_pos_right = first_pos[0]
        prev_pos_left = first_pos[1]

        while len(self.motor_stack) > 0:
            # Get and delete first element from stack
            current_pos = self.motor_stack.pop(0)
            pos_right = current_pos[0]
            pos_left = current_pos[1]

            # Calculate number of ticks (motor degrees) since previous stack element
            ticks_right = pos_right - prev_pos_right
            ticks_left = pos_left - prev_pos_left

            # Skip if robot didn't move
            if not ticks_right and not ticks_left:
                continue

            prev_pos_right = pos_right
            prev_pos_left = pos_left

            # Number of motor rotations
            rotations_right = float(ticks_right / 360)
            rotations_left = float(ticks_left / 360)

            # Distance moved in mm on both wheels
            mm_right = float(rotations_right * self.wheel_circumference_mm)
            mm_left = float(rotations_left * self.wheel_circumference_mm)

            # Distance moved in mm by the robot
            mm = (mm_right + mm_left) / 2.0

            # Calculate new orientation and limit it to 0 to 2*Pi (0 to 360 degrees)
            self.angle_rad += (mm_right - mm_left) / self.wheel_circumference_mm
            self.angle_rad %= 2 * math.pi

            # Calculate new x and y positions
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
        self.motor_stack.append([self.motor_left.position, self.motor_right.position])

    def clear_motor_stack(self):
        self.motor_stack.clear()
