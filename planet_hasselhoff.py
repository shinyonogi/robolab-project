from planet import Planet, Direction


class Hasselhoff(Planet):
    def __init__(self):
        super().__init__()
        # add_path( ((StartX, StartY), StartDir), ((EndX, EndY), EndDir), Weight )
        self.add_path(((0, 0), Direction.NORTH), ((1, 2), Direction.SOUTH), 4)
        self.add_path(((0, 1), Direction.EAST), ((1, 1), Direction.WEST), 1)
        self.add_path(((1, 1), Direction.SOUTH), ((2, 0), Direction.WEST), 2)
        self.add_path(((0, 2), Direction.NORTH), ((2, 2), Direction.SOUTH), 1)
        self.add_path(((2, 2), Direction.WEST), ((1, 2), Direction.EAST), 7)
        self.add_path(((1, 2), Direction.WEST), ((1, 0), Direction.NORTH), 10)
        self.add_path(((2, 2), Direction.NORTH), ((0, 3), Direction.WEST), 3)
        self.add_path(((0, 3), Direction.SOUTH), ((0, 3), Direction.WEST), 4)
