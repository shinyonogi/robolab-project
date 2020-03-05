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

        self.line_of_sight = line_of_sight
        self.coordinate_x = coordinate_x
        self.coordinate_y = coordinate_y

    def calc_coord(self, d_l, d_r):

        angle_alpha = (d_r - d_l) / self.distance_tire 

        if(angle_alpha == 0): #when the way is straight
            angle_beta = angle_alpha / 2
            distance_s = (d_r + d_l)/angle_alpha * math.sin(angle_beta)
        else:
            distance = d_l

        delta_x = -math.sin(self.line_of_sight + angle_beta) * distance_s
        delta_y = math.cos(self.line_of_sight + angle_beta) * distance_s

        self.line_of_sight += angle_alpha 
        self.coordinate_x += delta_x
        self.coordinate_y += delta_y

    def reset(self, direction, coordinate_x, coordinate_y):

        self.direction = direction 
        self.coordinate_x = coordinate_x
        self.coordinate_y = coordinate_y


    def get_cord(self):

        return (self.coordinate_x, self.coordinate_y)


    def get_direction(self):

        return self.direction 
        