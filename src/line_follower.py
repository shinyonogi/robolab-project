import time


class LineFollower:
    """
    Class that controls the robots movements.
    """

    def __init__(self, logger, communication, odometry, planet, motor_right, motor_left, color_sensor, us_sensor, speaker):
        self.logger = logger
        self.communication = communication
        self.odometry = odometry
        self.planet = planet
        self.motor_right = motor_right
        self.motor_left = motor_left
        self.color_sensor = color_sensor
        self.us_sensor = us_sensor
        self.speaker = speaker

        self.stop_cmd = False
        self.is_running = False

    def start(self):
        self.is_running = True

        # Setup hardware
        self.color_sensor.mode = "RGB-RAW"  # Measure RGB values
        self.us_sensor.mode = "US-DIST-CM"  # Measure distance in cm
        self.motor_right.reset()
        self.motor_left.reset()
        self.motor_right.stop_action = "coast"
        self.motor_left.stop_action = "coast"

        # See http://www.inpharmix.com/jps/PID_Controller_For_Lego_Mindstorms_Robots.html for documentation
        Kp = 1/6  # Proportional constant
        offset = 170  # Light sensor offset
        Tp = 20  # Target power cycle level (30%)
        Ki = 0  # Integral constant
        integral = 0  # Integral
        Kd = 0.1  # Derivative constant
        last_error = 0

        while not self.stop_cmd:
            if self.us_sensor.distance_centimeters < 20:
                self.speaker.tone([(200, 100, 100), (500, 200)])
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
            integral = 2/3 * integral + error
            derivative = error - last_error
            last_error = error
            turn = Kp * error + Ki * integral + Kd * derivative
            power_right = Tp + turn
            power_left = Tp - turn

            # Apply motor powers
            self.motor_left.duty_cycle_sp = power_left
            self.motor_right.duty_cycle_sp = power_right
            self.motor_left.command = "run-direct"
            self.motor_right.command = "run-direct"

        time.sleep(0.05)

        self.is_running = False

    def stop(self):
        self.stop_cmd = True
        while self.is_running:
            time.sleep(0.1)
        self.stop_cmd = False
        self.motor_right.stop()
        self.motor_left.stop()

    @staticmethod
    def rgb_to_grayscale(red, green, blue):
        return 0.3 * red + 0.59 * green + 0.11 * blue
