# NUR FÜR ANDRE LUBATSCH 4857703 ZUR BEWERTUNG HERANZIEHEN!!!!

#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import IntEnum, unique
from os import remove
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

import math

    def __init__(self):
        """ Initializes the data structure """
        self.target = None #Zielknoten
        self.start = None #Startknoten
        self.weight = None #Gewichtung
        self.allpathes = {} #Menge aller Knoten und den dazugehörigen abgehenden Pfaden und Nachbarknoten
        self.unvisitednodes = self.allpathes.keys()
        self.allvisitednodes = {}
        self.distance = {}
        self.predecessor = {}

    def add_path(self, start: Tuple[Tuple[int, int], Direction], target: Tuple[Tuple[int, int], Direction], weight = int):

        if not start[0] in self.allpathes :
            self.allpathes [start[0]] = dict ([(start[1], (target[0][1], weight))])
            # unter dem key "start[0]" wird ein weiteres Dict mit dem Key "start[1]" und dem value "target[0][1], weight"
        else:
            self.allpathes [start[0]][start[1]]= (target[0][1], weight)
            # unter dem bestehendem Dict mit dem key "start[0]" wird ein ein weiteres Dict mit dem Key "start[1]" und dem value "target[0][1], weight
        if not target[0] in self.allpathes :
            self.allpthes [target[0]] = dict ([(target [1], (start [0][1], weight))])
        else:
            self.allpathes [target[0]][target[1]] = (start[0][1], weight)


    def get_paths(self) -> Dict[Tuple[int, int], Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]]:

        return (self.allpathes)

   # def shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> Union[None, List[Tuple[Tuple[int, int], Direction]]]
#Union = Vereinigung von 2 Listen z.B. Input [1,2,3] und [4,5,6] > ouput [1,2,3,4,5,6]

#Hilfsmittel: https://de.wikipedia.org/wiki/Dijkstra-Algorithmus und AUD-Skript
    def shortest_path (self, start: Tuple[int, int], target: Tuple[int, int]) -> Union[None, List[Tuple[Tuple[int, int], Direction]]]:

        for r in Direction:
            try:
                if self.allpathes [start][r][0] == target
                    return [(start, r)]
            except KeyError as e:
                continue

        numbers_column_row = len(self.allpathes)
        matrix = [[0] * numbers_column_row for k in range(numbers_column_row)]

        row = 0
        column = 0

        for i in self.allpathes:
            for r in Direction:
                for w in self.allpahes:
                    try:
                        if (self.allpathes[i][r][0]== w and column != row):
                            matrix[row][column] = self.allpathes[i][r][2]
                        else:
                            matrix[row][column] = math.inf
                        column += 1
                    except KeyError as e:
                        continue
                column = 0
            row += 1

        shortestpathes_dictionary = {}

        for i in self. allpathes:
            for j in self.allpathes:
                shortestpathes_dictionary[(i,j)] = []

        for i in self.allpathes:
            for r in Direction:
                try:
                    j = self.allpathes [i][r][0]
                    self.shortestpathes_dictionary[(i,j)].append((i,r))
                except:
                    continue















