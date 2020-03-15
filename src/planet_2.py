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
        self.allnodes = []
        self.visitednodes = []
        self.alternativ = None
        self.weg = []

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

        print (self.allpathes)

   # def shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> Union[None, List[Tuple[Tuple[int, int], Direction]]]
#Union = Vereinigung von 2 Listen z.B. Input [1,2,3] und [4,5,6] > ouput [1,2,3,4,5,6]

#Hilfsmittel: https://de.wikipedia.org/wiki/Dijkstra-Algorithmus und AUD-Skript

#1. Initialsierung von distance und predecessor mit Zuweisung, das bei allen Knoten des Graphen: Distanz = unendlich, Vorgänger = 0
    def init_distance_predecessor (self, distance, predecessor):
        for i in self.allpathes:
            self.allnodes[i]=[math.inf, 0]
        for i  in self.allpathes:
            self.allnodes[i]=[0,i]
            break

# 1  Methode distanz_update(u,v,abstand[],vorgänger[]):
# 2      alternativ:= abstand[u] + abstand_zwischen(u, v)   // Weglänge vom Startknoten nach v über u
# 3      falls alternativ < abstand[v]:
# 4          abstand[v]:= alternativ
# 5          vorgänger[v]:= u

    def distance_update(self, start, target,weight, u):
        alternativ =  self.allpathes[start[0] ][start[u](weight)] + self.allpathes[target[0]][target[u](weight)]
        if alternativ <  self.allpathes[target[0]][target[u](weight)]:  #Liste für Abstand und Predecessor wahrscheinlich weniger falsch als das hier!
            self.allnodes[target] = [alternativ, u]

#1  Funktion erstelleKürzestenPfad(Zielknoten,vorgänger[])
#2   Weg[]:= [Zielknoten]
#3   u:= Zielknoten
#4   solange vorgänger[u] nicht null:   // Der Vorgänger des Startknotens ist null
#5       u:= vorgänger[u]
#6       füge u am Anfang von Weg[] ein
#7   return Weg[]

    def way(self, start, target, u):
        self.weg = [target]
        while self.allnodes [target[1]] != 0:
            self.allnodes [target[1]] = target
            self.weg.insert (0, target)
        return self.weg

#Solange es noch unbesuchte Knoten gibt, wähle darunter denjenigen mit minimaler Distanz aus und
# Speichere, dass dieser Knoten schon besucht wurde.
# Berechne für alle noch unbesuchten Nachbarknoten die Summe des jeweiligen Kantengewichtes und der Distanz im aktuellen Knoten.
# Ist dieser Wert für einen Knoten kleiner als die dort gespeicherte Distanz, aktualisiere sie und setze den aktuellen Knoten als Vorgänger.

 #1  Funktion Dijkstra(Graph, Startknoten):
 #2      initialisiere(Graph,Startknoten,abstand[],vorgänger[],Q)
 #3      solange Q nicht leer:                       // Der eigentliche Algorithmus
 #4          u:= Knoten in Q mit kleinstem Wert in abstand[]
 #5          entferne u aus Q                                // für u ist der kürzeste Weg nun bestimmt
 #6          für jeden Nachbarn v von u:
 #7              falls v in Q:                            // falls noch nicht berechnet
 #8                 distanz_update(u,v,abstand[],vorgänger[])   // prüfe Abstand vom Startknoten zu v
 #9      return vorgänger[]
    def djikstra(self, target):
        init_distance_predecessor()
        for i in self.allpathes:
            for d in Direction:
                try:
                    self.visitednodes.append (self.allpathes[i][d][0])
                except KeyError as e:
                    continue
        for i in self.allpathes:
            del self.allnodes[i]

        if target in self.allnodes:
            distance_update()




