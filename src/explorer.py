import time


def round_ten(number, down=False):
    """Round a number to a multiple of ten

    This function is used for calculating the calibrated color ranges.

    If the down argument is False, the number will be rounded up (e.g. 42 becomes 50).
    If the down argument is True, the number will be rounded down (e.g. 69 becomes 60).
    """
    r = int(round(number, -1))
    if down:
        return r if r <= number else r - 10
    else:
        return r if r >= number else r + 10


def rgb_to_grayscale(red, green, blue):
    """Convert RGB to a greyscale value using luminance"""
    return 0.3 * red + 0.59 * green + 0.11 * blue


class Explorer:
    """This class controls the robots movements as well as the majority of planet exploration."""

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

        self.target_power = 20  # Our optimal target power level is 20%
        # self.red_rb_range = ((120, 140), (10, 30))  # Hard-Coded defaults recorded in daylight on Piech
        # self.blue_rb_range = ((30, 50), (80, 110))
        self.red_rb_range = ((100, 140), (10, 30))  # Hard-Coded defaults recorded on Hasselhoff
        self.blue_rb_range = ((20, 50), (80, 100))

        self.logger.info("Explorer initialized and ready")

    def start_calibration(self):
        """Start a kind of color sensor calibration.

        Record the min and max RGB color values using record_min_max_color(), after which appropriate color ranges
        for red and blue are calculated with round_ten() and saved.
        """

        self.logger.info("Starting calibration")

        for color in ["red", "blue"]:
            input("Please place the robot's color sensor on a %s square, then press enter and slightly move it around on the square for five seconds." % color)
            cal = self.record_min_max_color()
            rb_range = (
                    (round_ten(cal[0][0], True), round_ten(cal[0][2])),
                    (round_ten(cal[2][0], True), round_ten(cal[2][2]))
                )
            self.logger.debug("Range is: %s " % str(rb_range))
            if color == "red":
                self.red_rb_range = rb_range
            else:
                self.blue_rb_range = rb_range

        self.logger.info("Calibration done, exploration can be started now")

    def record_min_max_color(self, run_for=5):
        """Record the min, average and max RGB values recorded for the time period given by the run_for argument

        Returns a tuple of the following structure: ( (Min Red, Avg Red, Max Red), ... green ... , ... blue ... )
        For completions sake we include green values, although they're useless af
        """
        self.color_sensor.mode = "RGB-RAW"
        r, g, b = [], [], []
        for i in range(0, int(run_for) * 10):
            rgb = self.color_sensor.bin_data("hhh")
            r.append(rgb[0])
            g.append(rgb[1])
            b.append(rgb[2])
            time.sleep(0.1)
        return (min(r), sum(r) / len(r), max(r)), (min(g), sum(g) / len(g), max(g)), (min(b), sum(b) / len(b), max(b))

    def start_exploration(self):
        self.logger.info("Explorer starting")
        prev_coords, prev_direction = self.odometry.calc_coord()
        while True:
            blocked, color = self.drive_to_next_square()
            coords, direction = self.odometry.calc_coord()
            self.logger.debug((coords, direction))
            self.logger.debug("X: %s, Y: %s, Angle: %s" % (self.odometry.distance_cm_x, self.odometry.distance_cm_y, self.odometry.angle))
            self.odometry.clear_motor_stack()

            if True:  # TODO: check if square is not in planet
                self.drive_off_square()
                self.odometry.update_motor_stack()
                # path_at_angles = self.scan_for_paths(direction)
                # self.communication.path_message(prev_coords[0], prev_coords[1], prev_direction, coords[0], coords[1], direction, "blocked" if blocked else "free")
                #
                # path_answer = None
                # while not path_answer:
                #     path_answer = self.communication.path
                #     time.sleep(0.25)
                #
                # if path_answer.get("endX") != coords[0]:
                #     coords = (path_answer.get("endX"), coords[1])
                #
                # if path_answer.get("endY") != coords[1]:
                #     coords = (coords[0], path_answer.get("endY"))

            prev_coords, prev_direction = coords, direction

    def drive_off_square(self):
        """Drive off a colored square using the color sensor. The robot stops after when it only detects black or white.

        This method is called after a square was discovered.
        """
        self.run_motors(self.target_power - 5, self.target_power - 5)

        color_val = 2
        while color_val == 2 or color_val == 5:
            color_val = self.color_sensor.value()
            time.sleep(1)  # TODO: find a better way?

        self.stop_motors()

    def drive_to_next_square(self):
        """Drive the robot along the path using a PID controller, until it reaches a colored square.

        Returns a tuple of properties, e.g. if the path was blocked and what color the target square is.
        """
        # These are the return values, expand as necessary
        blocked = False
        square_color = None

        # Setup hardware
        self.color_sensor.mode = "RGB-RAW"  # Measure RGB values
        self.us_sensor.mode = "US-DIST-CM"  # Measure distance in cm

        # See http://www.inpharmix.com/jps/PID_Controller_For_Lego_Mindstorms_Robots.html for documentation
        k_p = 0.11  # Proportional constant
        offset = 170  # Light sensor offset
        k_i = 0  # Integral constant, we disable this component because it ruins everything
        integral = 0  # Integral
        k_d = 0.04  # Derivative constant
        last_error = 0  # Error value of last loop

        red_counter = 0  # Counts the amount of consecutive red-detections
        blue_counter = 0  # Does the same for blue

        while True:
            self.odometry.update_motor_stack()  # TODO: only call this in the exploration loop?

            if self.us_sensor.distance_centimeters < 15:
                blocked = True
                self.logger.debug("Path blocked")
                self.stop_motors()
                self.expression.tone_warning().wait()
                self.run_motors(self.target_power, -self.target_power)
                time.sleep(4)  # TODO: replace with odometry stuff
                continue  # Drive back

            r, g, b = self.color_sensor.bin_data("hhh")  # Read RGB values from sensor
            gs = rgb_to_grayscale(r, g, b)  # Convert RGB to grayscale

            r_rb_range = self.red_rb_range
            b_rb_range = self.blue_rb_range
            if r_rb_range[0][0] <= r <= r_rb_range[0][1] and r_rb_range[1][0] <= b <= r_rb_range[1][1]:
                self.logger.debug("Detected RED")
                # With a calibrated sensor we cas assume we're on a colored square after it was detected for two loops
                # TODO: instead, maybe stop and do a short (30 Degree) turn in each direction and scan for colors?
                # if red_counter >= 2:
                #     square_color = "red"
                #     self.stop_motors()
                #     break
                # else:
                #     red_counter += 1
                square_color = "red"
                self.stop_motors()
                break
            elif b_rb_range[0][0] <= r <= b_rb_range[0][1] and b_rb_range[1][0] <= b <= b_rb_range[1][1]:
                self.logger.debug("Detected BLUE")
                # if blue_counter >= 2:
                #     square_color = "blue"
                #     self.stop_motors()
                #     break
                # else:
                #     blue_counter += 1
                square_color = "blue"
                self.stop_motors()
                break

            # Calculate error, turn and motor powers
            error = gs - offset
            integral = 2/3 * integral + error
            derivative = error - last_error
            last_error = error
            turn = k_p * error + k_i * integral + k_d * derivative
            power_right = self.target_power + turn
            power_left = self.target_power - turn

            self.run_motors(power_right, power_left)  # Apply motor powers

            time.sleep(0.05)  # 50 ms between loops seems to be optimal

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

    def scan_for_paths(self, start_direction):
        """Make the robot do a 360 degree rotation and detect outgoing paths.

        This method is called after we've detected a (yet undiscovered) square.
        The result is returned as a list of directions.
        """
        self.logger.info("Scanning for paths")

        self.color_sensor.mode = "COL-COLOR"

        self.run_motors(self.target_power - 5, - self.target_power - 5)

        path_at_angles = []
        counter = 0
        current_coords, current_direction = self.odometry.calc_coord()
        while current_direction <= start_direction + 360:
            color = self.color_sensor.value()
            if color == 1:  # black
                counter += 1
            elif color == 2:  # blue, likely this is actually black
                # TODO: maybe only do this when we're on a red square, just to be safe?
                counter += 1
            elif color == 5:  # red
                pass
            else:
                counter = 0
            if counter >= 2:
                # TODO: make sure we don't add the same path twice with slightly different angles
                # self.logger.debug("Path found at %s" % (current_direction - start_direction))
                path_at_angles.append(current_direction - start_direction)
            self.odometry.update_motor_stack()
            current_coords, current_direction = self.odometry.calc_coord()
            time.sleep(0.1)  # TODO: this might be too high

        self.stop_motors()
        return path_at_angles
