#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import IntEnum, unique
from typing import List, Tuple, Dict, Union


@unique
class Direction(IntEnum):
    """ Directions in shortcut """

    __order__ = 'NORTH SOUTH WEST EAST'

    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270


Weight = int
"""
Weight of a given path (received from the server)

Value:  -1 if blocked path
        >0 for all other paths
        never 0
"""


class Planet:
    """
    Contains the representation of the map and provides certain functions to manipulate or extend
    it according to the specifications
    """

    def __init__(self):
        """ Initializes the data structure """

        self.target = None
        self.path_dictionary = {} #all paths get saved in this dictionary

    def add_path(self, start: Tuple[Tuple[int, int], Direction], target: Tuple[Tuple[int, int], Direction],
                 weight: int):
        """
         Adds a bidirectional path defined between the start and end coordinates to the map and assigns the weight to it

        Example:
            add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST), 1)
        :param start: 2-Tuple
        :param target:  2-Tuple
        :param weight: Integer
        :return: void
        """

        # YOUR CODE FOLLOWS (remove pass, please!) 
        
        if((start[0] in self.path_dictionary) == False): #if the key (coordinate) doesn't exist
            self.path_dictionary[start[0]] = dict([(start[1], (target[0], target[1], weight))])
        else: #if the key already exists
            self.path_dictionary[start[0]][start[1]] = (target[0], target[1], weight)

        if((target[0] in self.path_dictionary) == False): #the path from target to start also get added
            self.path_dictionary[target[0]] = dict([(target[1], (start[0], start[1], weight))])
        else:
            self.path_dictionary[target[0]][target[1]] = (start[0], start[1], weight)


    def get_paths(self) -> Dict[Tuple[int, int], Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]]:
        """
        Returns all paths

        Example:
            {
                (0, 3): {
                    Direction.NORTH: ((0, 3), Direction.WEST, 1),
                    Direction.EAST: ((1, 3), Direction.WEST, 2)
                },
                (1, 3): {
                    Direction.WEST: ((0, 3), Direction.EAST, 2),
                    ...
                },
                ...
            }
        :return: Dict
        """

        # YOUR CODE FOLLOWS (remove pass, please!)
        
        return self.path_dictionary

    def shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> Union[None, List[Tuple[Tuple[int, int], Direction]]]:
        """
        Returns a shortest path between two nodes

        Examples:
            shortest_path((0,0), (2,2)) returns: [((0, 0), Direction.EAST), ((1, 0), Direction.NORTH)]
            shortest_path((0,0), (1,2)) returns: None
        :param start: 2-Tuple
        :param target: 2-Tuple
        :return: 2-Tuple[List, Direction]
        """

        # YOUR CODE FOLLOWS (remove pass, please!)

        for d in Direction: #Case: if the shortest path is only a way between two cooredinates
            try:
                if(self.path_dictionary[start][d][0] == target):
                    return [(start, d)]
            except KeyError as e: #Also to prevent KeyError
                continue
        
        number_of_coordinates = len(self.path_dictionary)
        matrix = [[0] * number_of_coordinates for i in range(number_of_coordinates)]  

        matrix_column = 0
        matrix_row = 0

        for i in self.path_dictionary: #First: goes through the dictionary/coordinates (First key)
            for s in Direction: #Second: goes through the direction (Second key)
                for t in self.path_dictionary: #Third: goes through the coordinates again 
                    try:
                        if(self.path_dictionary[i][s][0] == t and matrix_row != matrix_column):
                            matrix[matrix_row][matrix_column] = self.path_dictionary[i][s][2] #Add the distance when there's a way
                        elif(matrix_row == matrix_column):
                            matrix[matrix_row][matrix_column] = 0 #The way to coordinate itself 
                        else:
                            if(matrix[matrix_row][matrix_column] == 0):
                                matrix[matrix_row][matrix_column] = 9999 #9999 stands for Infinity (unreachable coordinates)
                        matrix_column += 1
                    except KeyError as e: #To avoid keyerror 
                        continue
                matrix_column = 0
            matrix_row += 1
