#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import IntEnum, unique
from typing import List, Tuple, Dict, Union


@unique
class Direction(IntEnum):
    """ Directions in shortcut """

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
        self.path_dictionary = {}  # All paths get saved in this dictionary

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

        if not (start[0] in self.path_dictionary):  # if the key (coordinate) doesn't exist
            self.path_dictionary[start[0]] = dict([(start[1], (target[0], target[1], weight))])
        else:  # if the key already exists
            self.path_dictionary[start[0]][start[1]] = (target[0], target[1], weight)

        if not (target[0] in self.path_dictionary):  # the path from target to start also get added
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

    def shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> Union[
        None, List[Tuple[Tuple[int, int], Direction]]]:
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

        for d in Direction:  # Case: if the shortest path is only a way between two coordinates
            try:
                if self.path_dictionary[start][d][0] == target:
                    return [(start, d)]
            except KeyError as e:  # Also to prevent KeyError
                continue

        number_of_coordinates = len(self.path_dictionary)
        matrix = [[0] * number_of_coordinates for i in range(number_of_coordinates)]

        matrix_column = 0
        matrix_row = 0

        for i in self.path_dictionary:  # First: goes through the dictionary/coordinates (First key)
            for s in Direction:  # Second: goes through the direction (Second key)
                for t in self.path_dictionary:  # Third: goes through the coordinates again
                    try:
                        if self.path_dictionary[i][s][0] == t and matrix_row != matrix_column:
                            matrix[matrix_row][matrix_column] = self.path_dictionary[i][s][2]  # Add the distance when there's a way
                        elif matrix_row == matrix_column:
                            matrix[matrix_row][matrix_column] = 0  # The way to coordinate itself
                        else:
                            if matrix[matrix_row][matrix_column] == 0:
                                matrix[matrix_row][
                                    matrix_column] = 9999  # 9999 stands for Infinity (unreachable coordinates)
                        matrix_column += 1
                    except KeyError as e:  # To avoid KeyError
                        continue
                matrix_column = 0
            matrix_row += 1

        shortest_path_dictionary = {}

        for i in self.path_dictionary:
            for j in self.path_dictionary:
                shortest_path_dictionary[(i, j)] = dict([(0, [])])

        for i in self.path_dictionary:
            for j in self.path_dictionary:
                for n in range(2):
                    shortest_path_dictionary[(i, j)][n] = []

        for i in self.path_dictionary:
            for d in Direction:
                try:
                    j = self.path_dictionary[i][d][0]
                    if i != j:
                        shortest_path_dictionary[(i, j)][0].append((i, d))
                except:
                    continue

        shortest_path_dictionary[(i, j)][2] = "HEllo"
        print(shortest_path_dictionary[(i, j)][2])

        i_1 = 0
        k_1 = 0
        j_1 = 0

        for k in self.path_dictionary:
            for i in self.path_dictionary:
                for j in self.path_dictionary:
                    if matrix[i_1][k_1] + matrix[k_1][j_1] < matrix[i_1][j_1]:
                        matrix[i_1][j_1] = min(matrix[i_1][j_1], matrix[i_1][k_1] + matrix[k_1][j_1])
                        Planet.calc_shortest_path(i, k, j, shortest_path_dictionary, 0)
                    elif matrix[i_1][k_1] + matrix[k_1][j_1] == matrix[i_1][j_1] and matrix[i_1][j_1] != 9999:
                        Planet.calc_shortest_path(i, k, j, shortest_path_dictionary, 1)
                        #print(shortest_path_dictionary[(i, j)])
                    j_1 += 1
                j_1 = 0
                i_1 += 1
            i_1 = 0
            k_1 += 1

        print(shortest_path_dictionary[((1, 1), (3, 5))])

        for i in shortest_path_dictionary:
            if (start, target) == i and shortest_path_dictionary[i][0] != []:
                shortest_path_dictionary[i][0] = Planet.sort_shortest_path(start, target,
                                                                           shortest_path_dictionary[i][0],
                                                                           self.path_dictionary)
                return shortest_path_dictionary[i][0]
        return []

    def calc_shortest_path(i, k, j, shortest_path_dictionary, version):
        iterator_counter = 0

        print(shortest_path_dictionary[(i, j)])

        if(shortest_path_dictionary[(i, j)][0] == []):
            iterator_counter_2 = 0
        elif(shortest_path_dictionary[(i, j)][1] == []):
            iterator_counter_2 = 1
        else:
            iterator_counter_2 = len(shortest_path_dictionary) + 1

        if version == 0:
            if shortest_path_dictionary[(i, k)][1] != [] and shortest_path_dictionary[(k, j)][1] != []:
                for m in range(len(shortest_path_dictionary[(i, k)])):
                    for n in range(len(shortest_path_dictionary[(k, j)])):
                        shortest_path_dictionary[(i, j)][iterator_counter] = shortest_path_dictionary[(i, k)][m] + \
                                                                             shortest_path_dictionary[(k, j)][n]
                        iterator_counter += 1
            elif shortest_path_dictionary[(i, k)][1] != [] and shortest_path_dictionary[(k, j)][1] == []:
                for m in range(len(shortest_path_dictionary[(i, k)])):
                    shortest_path_dictionary[(i, j)][iterator_counter] = shortest_path_dictionary[(i, k)][m] + shortest_path_dictionary[(k, j)][0]
                    iterator_counter += 1
            elif shortest_path_dictionary[(i, k)][1] == [] and shortest_path_dictionary[(k, j)][1] != []:
                for m in range(len(shortest_path_dictionary[(i, k)])):
                    shortest_path_dictionary[(i, j)][iterator_counter] = shortest_path_dictionary[(i, k)][0] + shortest_path_dictionary[(k, j)][m]
                    iterator_counter += 1
            else:
                shortest_path_dictionary[(i, j)][0] = shortest_path_dictionary[(i, k)][0] + \
                                                      shortest_path_dictionary[(k, j)][0]

        if(version == 1):
            print(shortest_path_dictionary[(i, k)][1], shortest_path_dictionary[(k, j)][1], iterator_counter)
            if(shortest_path_dictionary[(i, k)][1] != [] and shortest_path_dictionary[(k, j)][1] != []):
                for m in range(len(shortest_path_dictionary[(i, k)])):
                    for n in range(len(shortest_path_dictionary[(k, j)])):
                        shortest_path_dictionary[(i, j)][iterator_counter_2] = shortest_path_dictionary[(i, k)][m] + shortest_path_dictionary[(k, j)][n]
                        iterator_counter_2 += 1
            elif shortest_path_dictionary[(i, k)][1] != [] and shortest_path_dictionary[(k, j)][1] == []:
                for m in range(len(shortest_path_dictionary[(i, k)])):
                    shortest_path_dictionary[(i, j)][iterator_counter_2] = shortest_path_dictionary[(i, k)][m] + shortest_path_dictionary[(k, j)][0]
                    iterator_counter_2 += 1
            elif shortest_path_dictionary[(i, k)][1] == [] and shortest_path_dictionary[(k, j)][1] != []:
                for m in range(len(shortest_path_dictionary[(i, k)])):
                    shortest_path_dictionary[(i, j)][iterator_counter_2] = shortest_path_dictionary[((i, k))][0] + shortest_path_dictionary[(k, j)][m]
                    iterator_counter_2 += 1
            else:
                shortest_path_dictionary[(i, j)][iterator_counter_2] = shortest_path_dictionary[((i, k))][0] + shortest_path_dictionary[(k, j)][0]

    
    def sort_shortest_path(self, start, target, shortest_path_list, path_dictionary):  # just in case ;)
        sorted_shortest_path = []

        for i in range(len(shortest_path_list)):
            for j in range(len(shortest_path_list)):
                if start == shortest_path_list[j][0]:
                    sorted_shortest_path.append(shortest_path_list[j])
                    for d in Direction:
                        if d == shortest_path_list[j][1]:
                            start = path_dictionary[start][d][0]

        return sorted_shortest_path
