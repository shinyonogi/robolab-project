from enum import IntEnum, unique
from typing import List, Tuple, Dict, Union

import math 

@unique
class Direction(IntEnum):

    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270

Weight = int


class Planet_3:

    def __init__(self):

        self.path_dictionary = {}

    def add_path(self, start: Tuple[Tuple[int, int], Direction], target: Tuple[Tuple[int, int], Direction],weight: int):

        if not (start[0] in self.path_dictionary):  # if the key (coordinate) doesn't exist
            self.path_dictionary[start[0]] = dict([(start[1], (target[0], target[1], weight))])
        else:  # if the key already exists
            self.path_dictionary[start[0]][start[1]] = (target[0], target[1], weight)

        if not (target[0] in self.path_dictionary):  # the path from target to start also get added
            self.path_dictionary[target[0]] = dict([(target[1], (start[0], start[1], weight))])
        else:
            self.path_dictionary[target[0]][target[1]] = (start[0], start[1], weight)


    def get_paths(self) -> Dict[Tuple[int, int], Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]]:

        return self.path_dictionary

        #for i in self.path_dictionary:
            #print(i)


    def shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> Union[None, List[Tuple[Tuple[int, int], Direction]]]:

        if(start not in self.path_dictionary):
            return None

        if(target not in self.path_dictionary):
            return None

        n = 0

        for i in self.path_dictionary:
            if(i == start):
                break
            else:
                n += 1

        src = n

        self.number_of_coordinates = len(self.path_dictionary)
        self.graph = [[0 for column in range(self.number_of_coordinates)] for row in range(self.number_of_coordinates)]

        column = 0
        row = 0

        for i in self.path_dictionary: 
            for s in Direction:  
                for t in self.path_dictionary: 
                    try:
                        if self.path_dictionary[i][s][0] == t and row != column:
                            self.graph[row][column] = self.path_dictionary[i][s][2] 
                        else:
                            if self.graph[row][column] == 0:
                                self.graph[row][column] = 9999  
                        column += 1
                    except KeyError as e: 
                        continue
                column = 0
            row += 1

        shortest_path_dictionary = {}
        
        for i in self.path_dictionary: 
            for j in self.path_dictionary:
                shortest_path_dictionary[(i, j)] = []

        for i in self.path_dictionary: 
            for d in Direction:
                try:
                    j = self.path_dictionary[i][d][0]
                    if i != j:
                        shortest_path_dictionary[(i, j)].append((i, d))
                except:
                    continue

        #print(shortest_path_dictionary)

        dist = [math.inf] * self.number_of_coordinates
        dist[src] = 0
        sptSet = [False] * self.number_of_coordinates

        for cout in range(self.number_of_coordinates):

            u = self.calc_min_distance(dist, sptSet)
            sptSet[u] = True

            for v in range(self.number_of_coordinates): 
                if self.graph[u][v] > 0 and sptSet[v] == False and dist[v] > dist[u] + self.graph[u][v]: 
                    dist[v] = dist[u] + self.graph[u][v]
                    shortest_path_dictionary[(start, self.num_to_coord(v))] = shortest_path_dictionary[(start, self.num_to_coord(u))] + shortest_path_dictionary[(self.num_to_coord(u), self.num_to_coord(v))]

        #print(shortest_path_dictionary)

        #trg = 0
        #for i in self.path_dictionary:
            #if(i == target):
                #break
            #else:
                #trg += 1

        #return dist[trg]
        return shortest_path_dictionary[(start, target)]

    def calc_min_distance(self, dist, sptSet):

        min = math.inf

        for n in range(self.number_of_coordinates):
            if(dist[n] < min and sptSet[n] == False):
                min = dist[n]
                min_index = n

        return min_index

    def num_to_coord(self, n):

        number = 0
        for i in self.path_dictionary:
            if(number == n):
                return i
            else:
                number += 1


                
planet = Planet_3()

planet.add_path(((1, 1), Direction.EAST), ((2, 1), Direction.WEST), 1)
planet.add_path(((1, 1), Direction.NORTH), ((1, 2), Direction.SOUTH), 1)
planet.add_path(((2, 1), Direction.EAST), ((3, 2), Direction.SOUTH), 2)
planet.add_path(((3, 2), Direction.NORTH), ((3, 4), Direction.SOUTH), 2)
planet.add_path(((3, 4), Direction.NORTH), ((3, 5), Direction.SOUTH), 1)
planet.add_path(((3, 5), Direction.NORTH), ((1, 6), Direction.EAST), 3)
planet.add_path(((1, 6), Direction.WEST), ((1, 6), Direction.SOUTH), 2)
planet.add_path(((1, 2), Direction.EAST), ((2, 3), Direction.SOUTH), 2)
planet.add_path(((2, 3), Direction.WEST), ((1, 3), Direction.EAST), 1)
planet.add_path(((1, 3), Direction.WEST), ((1, 3), Direction.SOUTH), 1)
planet.add_path(((2, 3), Direction.NORTH), ((3, 5), Direction.WEST), 3)
planet.add_path(((1, 3), Direction.NORTH), ((1, 5), Direction.SOUTH), 2)

#planet.get_paths()

#shortest_path = planet.shortest_path((1, 1), (2, 1))
#print(shortest_path)

print(planet.shortest_path((1, 1), (1, 6)))
