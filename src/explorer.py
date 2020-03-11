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

    def __init__(
        self,
        logger,
        communication,
        odometry,
        planet,
        expression,
        motor_right,
        motor_left,
        color_sensor,
        gyro_sensor,
        us_sensor,
    ):
        self.logger = logger
        self.communication = communication
        self.odometry = odometry
        self.planet = planet
        self.motor_right = motor_right
        self.motor_left = motor_left
        self.color_sensor = color_sensor
        self.us_sensor = us_sensor
        self.gyro_sensor = gyro_sensor
        self.expression = expression

        self.target_power = 20  # Our optimal target power level is 20%

        # Hard-Coded defaults recorded in daylight on Piech
        self.red_rb_range = ((120, 150), (10, 30))
        self.blue_rb_range = ((30, 50), (90, 110))

        # Hard-Coded defaults recorded on Hasselhoff
        # self.red_rb_range = ((100, 140), (10, 30))
        # self.blue_rb_range = ((20, 50), (80, 100))

        self.logger.info("Explorer initialized and ready")

    def start_calibration(self):
        """Start a kind of color sensor calibration.

        Record the min and max RGB color values using record_min_max_color(), after which appropriate color ranges
        for red and blue are calculated with round_ten() and saved.
        """

        self.logger.info("Starting calibration")

        for color in ["red", "blue"]:
            input(
                "Please place the robot's color sensor on a %s square, then press enter and slightly move it around on the square for five seconds."
                % color
            )
            cal = self.record_min_max_color()
            rb_range = (
                (round_ten(cal[0][0], True), round_ten(cal[0][2])),
                (round_ten(cal[2][0], True), round_ten(cal[2][2])),
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
        return (
            (min(r), sum(r) / len(r), max(r)),
            (min(g), sum(g) / len(g), max(g)),
            (min(b), sum(b) / len(b), max(b)),
        )

    def run_motors(self, tp_right, tp_left, check_dc=True):
        # Make sure the provided powers are in the range 0 - 100
        tp_right = -100 if tp_right < -100 else 100 if tp_right > 100 else tp_right
        tp_left = -100 if tp_left < -100 else 100 if tp_left > 100 else tp_left
        # TODO: sometimes only one of the motors is starting, figure out why and how to prevent that
        # I guess this is might be a fix for it... just send the command three times so the motors really get it
        for i in range(3 if check_dc else 1):
            self.motor_right.duty_cycle_sp = tp_right
            self.motor_left.duty_cycle_sp = tp_left
            self.motor_right.command = "run-direct"
            self.motor_left.command = "run-direct"

    def stop_motors(self):
        self.motor_right.stop()
        self.motor_left.stop()

    def reset_motors(self):
        self.motor_right.reset()
        self.motor_left.reset()
        self.motor_right.stop_action = "coast"
        self.motor_left.stop_action = "coast"

    def rotate(self, degrees):
        self.reset_gyro()
        time.sleep(1)
        gyro_start_angle = self.gyro_sensor.angle
        self.run_motors(self.target_power, -self.target_power)
        while self.gyro_sensor.angle > gyro_start_angle - degrees:
            time.sleep(0.1)
        self.stop_motors()

    def reset_gyro(self):
        """Reset and calibrate the gyro sensor.

        Before calling this method, make sure the robot is standing still.
        """
        # self.logger.debug("Resetting gyro sensor")
        self.gyro_sensor.mode = "GYRO-RATE"
        self.gyro_sensor.mode = "GYRO-ANG"

    def start_exploration(self, is_first_point=True):
        self.logger.info("Explorer starting")
        prev_coords = None
        prev_arrive_direction = None
        prev_start_direction = prev_arrive_direction
        while True:
            blocked, color = self.drive_to_next_point()  # Follow the path to the next point

            if is_first_point:  # Run if this is our "entry" point
                self.logger.info("Sending ready-signal to mothership")
                self.communication.ready_message()

                planet_data = None
                while not planet_data:  # Wait for answer from mothership
                    planet_data = self.communication.planet_data
                    time.sleep(0.1)

                self.logger.info("Our planet is called %s" % planet_data["planetName"])
                self.odometry.set_coord(
                    (planet_data.get("startX"), planet_data.get("startY")),
                    planet_data.get("startOrientation")
                )  # Set our odometry coordinates to the data we just received from the mothership
                self.odometry.clear_motor_stack()

            if blocked:  # If the path was blocked we're back on the same point we're coming from
                coords, direction = prev_coords, (prev_start_direction - 180) % 360
            else:
                coords, direction = self.odometry.calc_coord()  # Calculate current coordinates and direction
            self.odometry.clear_motor_stack()

            self.logger.debug(
                "Coords: %s, Direction: %s, DeltaX: %s, DeltaY: %s, Angle: %s"
                % (
                    coords,
                    direction,
                    self.odometry.distance_cm_x,
                    self.odometry.distance_cm_y,
                    self.odometry.angle,
                )
            )

            if not is_first_point:
                self.communication.path_message(
                    prev_coords[0],
                    prev_coords[1],
                    prev_start_direction,
                    coords[0],
                    coords[1],
                    (direction - 180) % 360 if not blocked else direction,
                    "blocked" if blocked else "free",
                )  # Send the discovered path to the mothership

                path_answer = None
                while not path_answer:  # Wait for answer from mothership
                    path_answer = self.communication.path
                    time.sleep(0.1)

                coords = (path_answer.get("endX"), path_answer.get("endY"))  # Get corrected coordinates
                direction = (path_answer.get("endDirection") - 180) % 360   # Get corrected direction
                self.logger.debug("Fixed coords %s" % str((coords, direction)))
                self.odometry.set_coord(coords, direction)  # Apply corrected coordinates and direction

                self.communication.reset_path()

            self.drive_off_point()  # Drive off the square for rotation

            point = self.planet.coordinate_existent(coords)  # Check if our planet already has the point
            paths = []  # Here we'll save all directions in which there are paths starting from the square
            if (not point or point and len(point.keys()) < 4) and prev_coords != coords:
                # Do a 360* scan, if we haven't discovered this point before, or we've discovered it before but
                # we have less than 4 paths from it saved (we might have had some paths revealed from the mothership),
                # or the previous coordinates aren't the same as the current one (otherwise we just drove a loop)
                # TODO: perhaps create a dict in planet with all the points we definitely have already scanned?
                paths = self.scan_for_paths(direction)  # Do a 360* scan for outgoing paths
                self.logger.debug("Paths in directions: %s" % paths)
                self.reset_motors()
                self.odometry.reset()
                # self.odometry.update_motor_stack()
                # self.logger.debug("Odometry coords after rotation: %s", str(self.odometry.calc_coord()))
                # self.odometry.clear_motor_stack()

                if is_first_point:
                    remove_path = (direction - 180) % 360
                    if remove_path in paths:
                        paths.remove(remove_path)  # Remove the "entry" path from the list of paths
                    is_first_point = False

            for p in paths:
                self.planet.depth_first_add_stack(coords, p)  # Add paths to DFS stack

            dfs = self.planet.depth_first_search(coords)  # Search which path to drive next with DFS

            chosen_path = int(dfs[0][1])  # Get search result TODO: check if None, in that case... what?

            self.logger.debug("DFS chosen path: %s" % chosen_path)

            self.communication.path_select_message(coords[0], coords[1], chosen_path)  # Send chosen path to mothership

            path_select_answer = None
            target = None
            self.logger.debug("Last message at: %s, Current time: %s" % (self.communication.last_message_at, time.time()))
            while self.communication.last_message_at + 3 > time.time():  # 3 second timeout after last message
                path_select_answer = self.communication.path_select
                target = self.communication.target
                time.sleep(0.25)

            self.logger.debug("End of communication for this point")

            # self.expression.song_star_wars_short().wait()

            if path_select_answer:
                chosen_path = path_select_answer.get("startDirection")  # Apply path direction
                self.logger.debug("Chosen path from server: %s" % chosen_path)
                self.communication.reset_path_select()

            if target:
                pass  # TODO: do something

            self.planet.depth_first_add_reached(coords, chosen_path)  # Inform DFS about chosen path

            if chosen_path != direction:  # If the path isn't in front of us, rotate to it
                self.rotate((direction - chosen_path) % 360)
                self.odometry.set_coord(None, chosen_path)
                self.reset_motors()
                self.odometry.reset()

            prev_coords, prev_arrive_direction, prev_start_direction = coords, direction, chosen_path

    def drive_off_point(self):
        """Drive off a colored square using the color sensor. The robot stops after when it only detects black or white.

        This method is called after a point was discovered.
        """
        self.run_motors(self.target_power - 6, self.target_power - 3)
        time.sleep(2)  # TODO: replace with odometry stuff
        self.stop_motors()

    def drive_to_next_point(self):
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

        while True:
            self.odometry.update_motor_stack()

            if self.us_sensor.distance_centimeters < 20:
                blocked = True
                self.logger.debug("Path blocked")
                self.stop_motors()
                self.expression.tone_warning().wait()
                self.rotate(180)
                self.odometry.update_motor_stack()
                self.odometry.clear_motor_stack()
                new_angle = (self.odometry.angle - 180) % 360  # TODO: try if odometry would calculate this correctly
                self.odometry.angle = new_angle
                self.odometry.set_coord(None, self.odometry.angle_to_direction(new_angle))
                continue  # Drive back

            r, g, b = self.color_sensor.bin_data("hhh")  # Read RGB values from sensor
            gs = rgb_to_grayscale(r, g, b)  # Convert RGB to grayscale

            r_rb_range = self.red_rb_range
            b_rb_range = self.blue_rb_range
            if r_rb_range[0][0] <= r <= r_rb_range[0][1] and r_rb_range[1][0] <= b <= r_rb_range[1][1]:
                self.logger.debug("Detected RED")
                # With a calibrated sensor we cas assume we're on a colored square after it was detected for two loops
                # TODO: instead, maybe stop and do a short (30 Degree) turn in each direction and scan for colors?
                square_color = "red"
                self.stop_motors()
                break
            elif (
                b_rb_range[0][0] <= r <= b_rb_range[0][1]
                and b_rb_range[1][0] <= b <= b_rb_range[1][1]
            ):
                self.logger.debug("Detected BLUE")
                square_color = "blue"
                self.stop_motors()
                break

            # Calculate error, turn and motor powers
            error = gs - offset
            integral = 2 / 3 * integral + error
            derivative = error - last_error
            last_error = error
            turn = k_p * error + k_i * integral + k_d * derivative
            power_right = self.target_power + turn
            power_left = self.target_power - turn

            self.run_motors(power_right, power_left, False)  # Apply motor powers

            time.sleep(0.05)  # 50 ms between loops seems to be optimal

        return blocked, square_color

    def scan_for_paths(self, start_direction):
        """Make the robot do a 360 degree rotation and detect outgoing paths.

        This method is called after we've detected a point.
        The result is returned as a list of directions.
        """
        self.color_sensor.mode = "COL-COLOR"

        self.reset_gyro()  # Calibrate gyro sensor
        time.sleep(1)

        path_at_angles = []
        gyro_start_angle = abs(self.gyro_sensor.angle)

        self.run_motors(self.target_power - 5, -self.target_power - 5)

        while abs(self.gyro_sensor.angle) < gyro_start_angle + 355:
            angle = abs(self.gyro_sensor.angle) - gyro_start_angle
            color = self.color_sensor.value()
            if color == 1:  # black
                path_at_angles.append(angle)
                # self.logger.debug("Path at %s" % ((start_direction - angle) % 360))
            time.sleep(0.05)

        self.stop_motors()

        paths = []
        for a in path_at_angles:
            direction = self.odometry.angle_to_direction((start_direction - a) % 360)
            if direction not in paths:
                paths.append(direction)

        return paths
