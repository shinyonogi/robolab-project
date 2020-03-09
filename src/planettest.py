#!/usr/bin/env python3

import unittest
from planet import Direction, Planet


class ExampleTestPlanet(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        +--+
        |  |
        +-0,3------+
           |       |
          0,2-----2,2 (target)
           |      /
        +-0,1    /
        |  |    /
        +-0,0-1,0
           |
        (start)

        """
        # Initialize your data structure here
        self.planet = Planet()
        self.planet.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 1)
        self.planet.add_path(((0, 1), Direction.WEST), ((0, 0), Direction.WEST), 1)

    @unittest.skip('Example test, should not count in final test results')
    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        self.assertIsNone(self.planet.shortest_path((0, 0), (1, 2)))


class RoboLabPlanetTests(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        MODEL YOUR TEST PLANET HERE (if you'd like):

        (loop2)(1, 6) -  +   -   +
                                   |
              (1, 5)    +   -    (3, 5)
                 |      |        |
                 +      +        (3, 4)
                 |      |        |
        (loop)(1, 3) - (2, 3)    +
                        |        |
              (1, 2) - +       (3, 2)
                 |               |
              (1, 1) - (2, 1) -  +
                 |
                 (start)

        """
        # Initialize your data structure here
        self.planet = Planet()
        # self.planet.add_path(...)

        self.planet.add_path(((1, 1), Direction.EAST), ((2, 1), Direction.WEST), 1)
        self.planet.add_path(((1, 1), Direction.NORTH), ((1, 2), Direction.SOUTH), 1)
        self.planet.add_path(((2, 1), Direction.EAST), ((3, 2), Direction.SOUTH), 2)
        self.planet.add_path(((3, 2), Direction.NORTH), ((3, 4), Direction.SOUTH), 2)
        self.planet.add_path(((3, 4), Direction.NORTH), ((3, 5), Direction.SOUTH), 1)
        self.planet.add_path(((3, 5), Direction.NORTH), ((1, 6), Direction.EAST), 3)
        self.planet.add_path(((1, 6), Direction.WEST), ((1, 6), Direction.SOUTH), 2)
        self.planet.add_path(((1, 2), Direction.EAST), ((2, 3), Direction.SOUTH), 2)
        self.planet.add_path(((2, 3), Direction.WEST), ((1, 3), Direction.EAST), 1)
        self.planet.add_path(((1, 3), Direction.WEST), ((1, 3), Direction.SOUTH), 1)
        self.planet.add_path(((2, 3), Direction.NORTH), ((3, 5), Direction.WEST), 3)
        self.planet.add_path(((1, 3), Direction.NORTH), ((1, 5), Direction.SOUTH), 2)

    def test_add_get_paths(self):
        # print(self.planet.get_paths()) #prints all the paths (for us)
        return

    def test_shortest_path_opposite_path_1(self):
        #checks if two opposite ways return the same (opposite) shortest path 
        shortest_path = self.planet.shortest_path((1, 6), (1, 1))
        shortest_path = shortest_path[0]
        self.assertEqual(shortest_path[0], ((1, 6), Direction.EAST))
        self.assertEqual(shortest_path[1], ((3, 5), Direction.SOUTH))
        self.assertEqual(shortest_path[2], ((3, 4), Direction.SOUTH))
        self.assertEqual(shortest_path[3], ((3, 2), Direction.SOUTH))
        self.assertEqual(shortest_path[4], ((2, 1), Direction.WEST))


        shortest_path = self.planet.shortest_path((1, 1), (1, 6))
        shortest_path = shortest_path[0]
        self.assertEqual(shortest_path[0], ((1, 1), Direction.EAST))
        self.assertEqual(shortest_path[1], ((2, 1), Direction.EAST))
        self.assertEqual(shortest_path[2], ((3, 2), Direction.NORTH))
        self.assertEqual(shortest_path[3], ((3, 4), Direction.NORTH))
        self.assertEqual(shortest_path[4], ((3, 5), Direction.NORTH))

    def test_start_with_loop(self):
        #checks if the search for the shortest path doesn't stuck when it begins with a loop
        shortest_path = self.planet.shortest_path((1, 5), (2, 3))
        shortest_path = shortest_path[0]
        self.assertEqual(shortest_path[0], ((1, 5), Direction.SOUTH))
        self.assertEqual(shortest_path[1], ((1, 3), Direction.EAST))

        try:
            if shortest_path[2] is tuple:  # checks if there's a third element
                self.fail("FAIL")
        except:
            return

    def test_end_with_loop(self):
        #checks if the search for the shortest path doesn't stuck in a loop when it ends with a loop
        shortest_path = self.planet.shortest_path((2, 3), (1, 5))
        shortest_path = shortest_path[0]
        self.assertEqual(shortest_path[0], ((2, 3), Direction.WEST))
        self.assertEqual(shortest_path[1], ((1, 3), Direction.NORTH))

        try:
            if shortest_path[2] is tuple:  # checks if the loop stops
                self.fail("FAIL")
        except:
            return

    def test_integrity(self):
        """
        This test should check that the dictionary returned by "planet.get_paths()" matches the expected structure
        """
        test_get_paths = self.planet.get_paths()
        integrity = True
        direction_type = type(test_get_paths[(1, 1)][Direction.EAST][1])

        for i in test_get_paths:
            if type(i) is tuple:
                for j in test_get_paths[i]:
                    if ((type(j) is direction_type)
                            and (type(test_get_paths[i][j][0]) is tuple)
                            and (type(test_get_paths[i][j][1]) is direction_type)
                            and (type(test_get_paths[i][j][2]) is int)):
                        continue
                    else:
                        integrity = False
            else:
                integrity = False

        self.assertEqual(integrity, True)

    def test_empty_planet(self):
        """
        This test should check that an empty planet really is empty
        """
        empty_planet = Planet() #initializes an empty planet 

        self.assertEqual(empty_planet.get_paths(), {})

    def test_target(self):
        """
        This test should check that the shortest-path algorithm implemented works.

        Requirement: Minimum distance is three nodes (two paths in list returned)
        """
        test_shortest_path = self.planet.shortest_path((1, 1), (3, 4))
        test_shortest_path = test_shortest_path[0]

        if ((test_shortest_path[0] != ((1, 1), Direction.EAST))
                or (test_shortest_path[1] != ((2, 1), Direction.EAST))
                or (test_shortest_path[2] != ((3, 2), Direction.NORTH))):
            self.fail("FAIL")
    
    def test_target_not_reachable(self):
        """
        This test should check that a target outside the map or at an unexplored node is not reachable
        """
        test_shortest_path = self.planet.shortest_path((1, 1), (6, 5))

        self.assertIsNone(test_shortest_path)

    def test_same_length(self):
        """
        This test should check that the shortest-path algorithm implemented also can return alternatives with the
        same cost (weights)

        Requirement: Minimum of two paths with same cost exists, only one is returned by the logic implemented
        """

        test_shortest_path = self.planet.shortest_path((1, 1), (3, 5))

        test_shortest_path_1 = test_shortest_path[0]
        self.assertEqual(test_shortest_path_1[0], ((1, 1), Direction.EAST))     
        self.assertEqual(test_shortest_path_1[1], ((2, 1), Direction.EAST))
        self.assertEqual(test_shortest_path_1[2], ((3, 2), Direction.NORTH))
        self.assertEqual(test_shortest_path_1[3], ((3, 4), Direction.NORTH))

        test_shortest_path_2 = test_shortest_path[1]
        self.assertEqual(test_shortest_path_2[0], ((1, 1), Direction.NORTH))
        self.assertEqual(test_shortest_path_2[1], ((1, 2), Direction.EAST))
        self.assertEqual(test_shortest_path_2[2], ((2, 3), Direction.NORTH))


    def test_target_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target nearby

        Result: Target is reachable
        """
        test_shortest_path = self.planet.shortest_path((2, 3), (1, 5))
        test_shortest_path = test_shortest_path[0]

        if ((test_shortest_path[0] != ((2, 3), Direction.WEST))
                or (test_shortest_path[1] != ((1, 3), Direction.NORTH))):
            self.fail("FAIL")

    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        test_shortest_path = self.planet.shortest_path((1, 5), (6, 5))

        self.assertIsNone(test_shortest_path)


if __name__ == "__main__":
    unittest.main()
