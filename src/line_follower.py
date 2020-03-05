import time


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

    def start(self):
        self.stop = False

        # Setup hardware
        self.color_sensor.mode = "RGB-RAW"  # Measure RGB values
        self.us_sensor.mode = "US-DIST-CM"  # Measure distance in cm
        self.motor_right.reset()
        self.motor_left.reset()

        # See http://www.inpharmix.com/jps/PID_Controller_For_Lego_Mindstorms_Robots.html for documentation
        Kp = 1/6  # Kp contant
        offset = 170  # Light sensor offset
        Tp = 30  # Target power cycle level (30%)

        while not self.stop:
            if self.us_sensor.distance_centimeters < 10:
                self.motor_right.duty_cycle_sp = Tp
                self.motor_right.command = "run-direct"
                self.motor_left.duty_cycle_sp = -Tp
                self.motor_left.command = "run-direct"
                # add Odometry!!!!!

            rgb = self.color_sensor.bin_data("hhh")  # Read RGB values from sensor
            r = rgb[0]
            g = rgb[1]
            b = rgb[2]
            gs = self.rgb_to_grayscale(r, g, b)  # Convert RGB to grayscale

            # TODO: this isn't reliable, find a better way to detect red/blue squares
            # if r > 100 > g and b < 100:
            #     print("red")
            # elif g > 100 > r and b < 100 or b > 100 > r and g < 100:
            #     print("blue")
            # else:
            #     print("grayscale")
            #     gs = self.rgb_to_grayscale(r, g, b)
            #     print(gs)

            # Calculate error, turn and motor powers
            error = gs - offset
            turn = Kp * error
            power_right = Tp + turn
            power_left = Tp - turn

            # Apply motor powers
            self.motor_left.duty_cycle_sp = power_left
            self.motor_right.duty_cycle_sp = power_right
            self.motor_left.command = "run-direct"
            self.motor_right.command = "run-direct"

        time.sleep(0.05)

    def stop(self):
        self.stop = True

    @staticmethod
    def rgb_to_grayscale(red, green, blue):
        return 0.3 * red + 0.59 * green + 0.11 * blue
