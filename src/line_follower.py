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

        self.target_power = 20

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
        k_p = 1/6  # Proportional constant
        offset = 170  # Light sensor offset
        target_power = self.target_power  # Target power cycle level (20%)
        k_i = 0  # Integral constant
        integral = 0  # Integral
        k_d = 0.1  # Derivative constant
        last_error = 0

        red_counter = 0
        blue_counter = 0

        while not self.stop_cmd:
            if self.us_sensor.distance_centimeters < 15:
                self.motor_left.duty_cycle_sp = 0
                self.motor_right.duty_cycle_sp = 0
                self.warning()
                self.motor_right.duty_cycle_sp = target_power
                self.motor_left.duty_cycle_sp = -target_power
                time.sleep(5)
                continue
                # add Odometry!!!!!

            rgb = self.color_sensor.bin_data("hhh")  # Read RGB values from sensor
            r = rgb[0]
            g = rgb[1]
            b = rgb[2]
            gs = self.rgb_to_grayscale(r, g, b)  # Convert RGB to grayscale

            if r > 100 > g and b < 100:
                if red_counter > 5:
                    self.warning()  # for testing
                    red_counter = 0
                else:
                    red_counter += 1
            elif g > 100 > r and b < 100 or b > 100 > r and g < 100:
                if blue_counter > 5:
                    self.warning()  # for testing
                    blue_counter = 0
                else:
                    blue_counter += 1

            # Calculate error, turn and motor powers
            error = gs - offset
            integral = 2/3 * integral + error
            derivative = error - last_error
            last_error = error
            turn = k_p * error + k_i * integral + k_d * derivative
            power_right = target_power + turn
            power_left = target_power - turn

            # Apply motor powers
            self.motor_left.duty_cycle_sp = power_left
            self.motor_right.duty_cycle_sp = power_right
            self.motor_left.command = "run-direct"
            self.motor_right.command = "run-direct"

        time.sleep(0.05)

        self.is_running = False

    def warning(self):
        # TODO: maybe also do something with LEDs here?
        self.speaker.tone([(200, 100, 100), (500, 200)])

    def found_square(self):
        pass

    def found_path(self):
        pass

    def scan_for_paths(self):
        started_at_degrees = 1  # Add odometry stuff here

        # Slowly rotate with half the target power
        self.motor_right.duty_cycle_sp = self.target_power / 2
        self.motor_left.duty_cycle_sp = -self.target_power / 2

        self.color_sensor.mode = "COL-COLOR"

        current_degrees = 1  # This is a placeholder for some odometry method call inside the while condition

        # We don't technically have to do a full 360, 270 degrees would be enough
        while current_degrees < started_at_degrees + 360:
            color = self.color_sensor.value()

            if color == 1:
                # black -> path
                pass
            elif color == 6:
                # white -> nothing
                pass
            elif color == 2 or color == 5:
                # blue or red -> square
                pass

            time.sleep(0.1)

        self.motor_right.duty_cycle_sp = 0
        self.motor_left.duty_cycle_sp = 0
        self.color_sensor.mode = "RGB-RAW"

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
