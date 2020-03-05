class LineFollower:
    """
    Class that controls the robots movements.
    """

    def __init__(self, logger, communication, odometry, planet, motor_right, motor_left, color_sensor, us_sensor):
        self.logger = logger
        self.communication = communication
        self.odometry = odometry
        self.planet = planet
        self.motor_right = motor_right
        self.motor_left = motor_left
        self.color_sensor = color_sensor
        self.us_sensor = us_sensor

        self.stop = False

    @staticmethod
    def rgb_to_grayscale(red, green, blue):
        return 0.3 * red + 0.59 * green + 0.11 * blue
