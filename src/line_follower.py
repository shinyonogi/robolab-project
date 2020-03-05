class LineFollower:
    """
    Class that controls the robots movements.
    """

    def __init__(self, logger, communication, odometry, planet):
        self.logger = logger
        self.communication = communication
        self.odometry = odometry
        self.planet = planet
