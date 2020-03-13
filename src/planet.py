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

        self.name = None
        self.target = None
        self.path_dictionary = {}  # All paths get saved in this dictionary

        self.depth_first_stack = {}
        self.depth_first_reached = {}

        self.andre = []

    def set_name(self, name: str):
        self.name = name

    def set_target(self, target: Tuple[int, int]):
        self.target = target

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


        self.depth_first_add_stack(start[0], start[1])
        self.depth_first_add_reached(start[0], start[1])
        self.depth_first_add_stack(target[0], target[1])
        self.depth_first_add_reached(target[0], target[1])

        #if not (start[0] in self.andre):
            #self.andre.append(start[0])
        
        #if not (start[0] in self.andre):
            #self.andre.append(target[0])


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

        for i in self.path_dictionary: #makes a dictionary of coordinates whic has 0 as a key and an empty list as a value
            for j in self.path_dictionary:
                shortest_path_dictionary[(i, j)] = dict([(0, [])])
                shortest_path_dictionary[(i, j)][1] = [] #adds an another key: 1 to the key: coordinate so that every coordinate has two values
 
        for i in self.path_dictionary: #adds the paths that are next to each other as shortest path 
            for d in Direction:
                try:
                    j = self.path_dictionary[i][d][0]
                    if i != j:
                        shortest_path_dictionary[(i, j)][0].append((i, d))
                except:
                    continue

        i_1 = 0
        k_1 = 0
        j_1 = 0

        for k in self.path_dictionary:
            for i in self.path_dictionary:
                for j in self.path_dictionary:
                    if matrix[i_1][k_1] + matrix[k_1][j_1] < matrix[i_1][j_1]: #if there's a shorter way
                        matrix[i_1][j_1] = min(matrix[i_1][j_1], matrix[i_1][k_1] + matrix[k_1][j_1]) #makes the matrix shorter
                        shortest_path_dictionary[(i, j)][1] = []
                        shortest_path_dictionary[(i, j)][0] = shortest_path_dictionary[(i, k)][0] + shortest_path_dictionary[(k, j)][0] #adds shortest path to key: 0
                        if(shortest_path_dictionary[(i, k)][1] != []): #eventually adds shortest path to key:1 so that it has alternatives 
                            shortest_path_dictionary[(i, j)][1] = shortest_path_dictionary[(i, k)][1] + shortest_path_dictionary[(k, j)][0] 
                        elif(shortest_path_dictionary[(k, j)][1] != []):
                            shortest_path_dictionary[(i, j)][1] = shortest_path_dictionary[(i, k)][0] + shortest_path_dictionary[(k, j)][1]
                    elif(matrix[i_1][k_1] + matrix[k_1][j_1] == matrix[i_1][j_1]): #if there's a way with same distance
                            shortest_path_dictionary[(i, j)][1] = shortest_path_dictionary[(i, k)][0] + shortest_path_dictionary[(k ,j)][0]
                    j_1 += 1
                j_1 = 0
                i_1 += 1
            i_1 = 0
            k_1 += 1


        for i in shortest_path_dictionary:
            if (start, target) == i and shortest_path_dictionary[i][0] != []: #returns two shortest paths (only the first one needed, the second one could eventually be empty)
                shortest_path_dictionary[i][0] = Planet.sort_shortest_path(start, target, shortest_path_dictionary[i][0], self.path_dictionary) 
                shortest_path_dictionary[i][1] = Planet.sort_shortest_path(start, target, shortest_path_dictionary[i][1], self.path_dictionary)
                return shortest_path_dictionary[i][0]
        return None #returns none if there aren't any paths

    
    def sort_shortest_path(start, target, shortest_path_list, path_dictionary):  # just in case ;)
        sorted_shortest_path = []

        for i in range(len(shortest_path_list)):
            for j in range(len(shortest_path_list)):
                if start == shortest_path_list[j][0]:
                    sorted_shortest_path.append(shortest_path_list[j])
                    for d in Direction:
                        if d == shortest_path_list[j][1]:
                            start = path_dictionary[start][d][0]

        return sorted_shortest_path 


    def coordinate_existent(self, start):

        if(start in self.path_dictionary):
            return self.path_dictionary[start]
        else:
            return None


    def depth_first_add_stack(self, start, direction):

        #print(start, direction)
        
        if start in self.depth_first_stack:
            direction_list = self.depth_first_stack[start]
            del self.depth_first_stack[start]
            self.depth_first_stack[start] = direction_list
            if not direction in self.depth_first_stack[start]:
                self.depth_first_stack[start].append(direction)
        else:
            self.depth_first_stack[start] = []
            self.depth_first_reached[start] = []
            self.depth_first_stack[start].append(direction)


    def depth_first_add_reached(self, start, direction):

        if not direction in self.depth_first_reached[start]:
            self.depth_first_reached[start].append(direction)
        
        
    def depth_first_search(self, start):

        if self.target:
            shortest_to_target = self.shortest_path(start, self.target)

            if shortest_to_target:
                return shortest_to_target

        target = ()

        for i in self.depth_first_stack:
            for d in Direction:
                if(d in self.depth_first_stack[i]):
                    if(d in self.depth_first_reached[i]):
                        continue
                    else:
                        target = ((i), d)
                        #if not(i in self.depth_first_reached):
                            #self.depth_first_reached[i] = []
                        #self.depth_first_reached[i].append(d)

                        break
                else:
                    continue

                    
        #print(target)

        if(target != ()):
            if(start == target[0]):
                return [target]
            else:
                return self.shortest_path(start, target[0])
        elif(target == ()):
            if(self.andre != []):
                return self.check_andre(start)
            else:
                return None


    def add_andre(self, coordinate):

        self.andre.append(coordinate)


    def check_andre(self, coordinate):

        for i in self.path_dictionary:
            if i in self.andre:
                continue
            else:
                #self.andre.append(i)
                return self.shortest_path(coordinate, i)


    def check_if_scanned(self, coordinate):

        if coordinate in self.andre:
            return True
        else: 
            return False
                

    #def delete_andre(self, coordinate):

        #self.andre = [d for d in self.andre if d != coordinate]

    

