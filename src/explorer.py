import time


def round_ten(number, down=False):
    """This method rounds down a number to a multiple of ten"""
    r = int(round(number, -1))
    if down:
        return r if r <= number else r - 10
    else:
        return r if r >= number else r + 10


def rgb_to_grayscale(red, green, blue):
    """Converts RGB to a greyscale value using luminance"""
    return 0.3 * red + 0.59 * green + 0.11 * blue


class Explorer:
    """
    Class that controls the robots movements.
    """

    def __init__(self, logger, communication, odometry, planet, expression, motor_right, motor_left, color_sensor, us_sensor):
        self.logger = logger
        self.communication = communication
        self.odometry = odometry
        self.planet = planet
        self.motor_right = motor_right
        self.motor_left = motor_left
        self.color_sensor = color_sensor
        self.us_sensor = us_sensor
        self.expression = expression

        self.target_power = 20
        self.red_rb_range = ((120, 140), (10, 30))  # TODO: enter defaults (on test planet in E008)
        self.blue_rb_range = ((30, 50), (80, 110))

        self.logger.info("Explorer initialized and ready")

    def start_calibration(self):
        self.logger.info("Starting calibration")

        for color in ["red", "blue"]:
            input("Please place the robot's color sensor on a % square, then press enter and slightly move it around on the square for five seconds." % color)
            cal = self._calibrate()
            self.logger.debug(cal)
            rb_range = (
                    (round_ten(cal[0][0], True), round_ten(cal[0][2])),
                    (round_ten(cal[2][0], True), round_ten(cal[2][2]))
                )
            self.logger.debug(rb_range)
            if color == "red":
                self.red_rb_range = rb_range
            else:
                self.blue_rb_range = rb_range

        self.logger.info("Calibration done. Exploration can be started now.")

    def _calibrate(self):
        """Returns a tuple of the following structure:
        ( (Min Red, Avg Red, Max Red), ... green ... , ... blue ... )
        For completions sake we include green values, although they're useless af."""
        self.color_sensor.mode = "RGB-RAW"
        r = []
        g = []
        b = []
        for i in range(0, 50):
            rgb = self.color_sensor.bin_data("hhh")
            r.append(rgb[0])
            g.append(rgb[1])
            b.append(rgb[2])
            time.sleep(0.1)
        return (min(r), sum(r) / len(r), max(r)), (min(g), sum(g) / len(g), max(g)), (min(b), sum(b) / len(b), max(b))

    def start_exploration(self):
        self.logger.info("Explorer starting")
        while True:
            blocked, color = self.drive_to_next_square()
            self.logger.debug(self.odometry.calc_coord())
            self.scan_for_paths()

    def drive_to_next_square(self):
        blocked = False
        square_color = None
        # TODO: expand this as necessary

        # Setup hardware
        self.color_sensor.mode = "RGB-RAW"  # Measure RGB values
        self.us_sensor.mode = "US-DIST-CM"  # Measure distance in cm
        self.motor_right.reset()
        self.motor_left.reset()
        self.motor_right.stop_action = "coast"
        self.motor_left.stop_action = "coast"

        # See http://www.inpharmix.com/jps/PID_Controller_For_Lego_Mindstorms_Robots.html for documentation
        k_p = 0.11  # Proportional constant
        offset = 170  # Light sensor offset
        k_i = 0  # Integral constant, we disable this component because it ruins everything
        integral = 0  # Integral
        k_d = 0.04  # Derivative constant
        last_error = 0

        red_counter = 0
        blue_counter = 0

        while True:
            self.odometry.motorg_stack()

            if self.us_sensor.distance_centimeters < 15:
                blocked = True
                self.logger.debug("Path blocked")
                self.stop_motors()
                self.expression.tone_warning().wait()
                self.run_motors(self.target_power, -self.target_power)
                time.sleep(4)  # Replace with odometry stuff
                continue  # Drive back

            rgb = self.color_sensor.bin_data("hhh")  # Read RGB values from sensor
            r = rgb[0]
            g = rgb[1]
            b = rgb[2]
            gs = rgb_to_grayscale(r, g, b)  # Convert RGB to grayscale

            r_rb_range = self.red_rb_range
            b_rb_range = self.blue_rb_range
            if r_rb_range[0][0] <= r <= r_rb_range[0][1] and r_rb_range[1][0] <= b <= r_rb_range[1][1]:
                self.logger.debug("Detected RED")
                square_color = "red"
                self.stop_motors()
                break
            elif b_rb_range[0][0] <= r <= b_rb_range[0][1] and b_rb_range[1][0] <= b <= b_rb_range[1][1]:
                self.logger.debug("Detected BLUE")
                if blue_counter >= 2:
                    square_color = "blue"
                    self.stop_motors()
                    break
                else:
                    blue_counter += 1

            # Calculate error, turn and motor powers
            error = gs - offset
            integral = 2/3 * integral + error
            derivative = error - last_error
            last_error = error
            turn = k_p * error + k_i * integral + k_d * derivative
            power_right = self.target_power + turn
            power_left = self.target_power - turn

            self.run_motors(power_right, power_left)  # Apply motor powers

            time.sleep(0.05)

        return blocked, square_color

    def found_square(self):
        pass

    def found_path(self):
        pass

    def run_motors(self, tp_right, tp_left):
        self.motor_right.duty_cycle_sp = tp_right + 2
        self.motor_left.duty_cycle_sp = tp_left
        self.motor_left.command = "run-direct"
        self.motor_right.command = "run-direct"

    def stop_motors(self):
        self.logger.debug("Stopping motors")
        self.motor_right.stop()
        self.motor_left.stop()

    def scan_for_paths(self):
        self.logger.debug("Scanning for paths")

        self.color_sensor.mode = "COL-COLOR"

        # Drive until we detect either white or black, which means our robot sits directly on the square
        self.run_motors(self.target_power - 5, self.target_power - 5)

        color_val = 2
        while color_val == 2 or color_val == 5:
            # self.logger.debug(color_val)
            color_val = self.color_sensor.value()
            time.sleep(0.2)

        self.logger.debug("Oriented")
        self.stop_motors()
        time.sleep(0.75)

        started_at_degrees = 1  # Add odometry stuff here

        # Slowly rotate with half the target power
        self.run_motors(self.target_power - 5, - self.target_power - 5)

        current_degrees = 1  # This is a placeholder for some odometry method call inside the while condition

        counter = 0
        # We don't technically have to do a full 360, 270 degrees would be enough
        while current_degrees < started_at_degrees + 360:
            color = self.color_sensor.value()
            if color == 1:
                # print("black")
                counter += 1
            elif color == 2:
                # print("blue")
                counter += 1
            elif color == 5:
                # print("red")
                pass
            else:
                counter = 0
            current_degrees += 5
            if counter > 2:
                self.logger.debug("Path found at %s" % (current_degrees - started_at_degrees))
            time.sleep(0.1)

        self.stop_motors()
        self.color_sensor.mode = "RGB-RAW"

    def stop(self):
        self.stop_motors()
        self.logger.info("Explorer stopped")
