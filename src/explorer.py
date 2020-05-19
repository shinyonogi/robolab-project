import time


def round_ten(number, down=False):
    """
    Round a number to a multiple of ten.

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
    """
    Convert RGB to a greyscale value (luminance)
    """
    return 0.3 * red + 0.59 * green + 0.11 * blue


class Explorer:
    """
    This class controls the robots movements as well as the majority of planet exploration.
    """

    def __init__(
        self,
        logger,
        communication,
        odometry,
        planet,
        sound,
        motor_right,
        motor_left,
        color_sensor,
        gyro_sensor,
        us_sensor
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
        self.sound = sound

        self.target_power = 30  # Power target level for motors in percent

        # Hard-Coded default color ranges
        self.red_rb_range = ((110, 140), (10, 30))
        self.blue_rb_range = ((20, 50), (80, 110))

    def start_calibration(self):
        """
        Start a kind of color sensor calibration.

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
        """
        Record the min, average and max RGB values recorded for the time period given by the run_for argument

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

    def run_motors(self, tp_right, tp_left, repeat=3):
        """
        Run the two motors with the provided duty cycle speed (in percent).

        This method ensures that the provided duty cycle values are in the valid range of -100 to 100.
        The parameter repeat specifies the number of times the command is sent to the motors, which is a fix for the
        phenomenon that sometimes only one motor is starting.
        """
        tp_right = -100 if tp_right < -100 else 100 if tp_right > 100 else tp_right
        tp_left = -100 if tp_left < -100 else 100 if tp_left > 100 else tp_left
        for i in range(repeat):
            self.motor_right.duty_cycle_sp = tp_right
            self.motor_left.duty_cycle_sp = tp_left
            self.motor_right.command = "run-direct"
            self.motor_left.command = "run-direct"

    def stop_motors(self, repeat=3):
        """
        Stop the motors by braking (specified in reset_motors().

        The parameter repeat specifies the number of times the command is sent to the motors.
        """
        for i in range(repeat):
            self.motor_right.stop()
            self.motor_left.stop()

    def reset_motors(self):
        """
        Reset motors, mainly used for resetting the motor position.
        """
        self.stop_motors()
        self.motor_right.reset()
        self.motor_left.reset()
        self.motor_right.stop_action = "brake"
        self.motor_left.stop_action = "brake"

    def rotate_to_path(self, start_direction, target_direction):
        """
        Rotate the robot to a path at target_direction. Calls rotate_by_degrees to path after a small calculation.
        """
        rotate_degrees = (start_direction - target_direction) % 360
        self.logger.debug("Rotating by %s degrees" % rotate_degrees)
        return self.rotate_by_degrees_to_path(rotate_degrees)

    def rotate_by_degrees_to_path(self, degrees):
        """
        Rotate the robot to the path found after specified degrees.

        Uses the gyro sensor until a degrees - 45 rotation is reached, from where the color sensor is used to stop
        the rotation at the next detected (black) path.
        """
        self.color_sensor.mode = "COL-COLOR"
        self.reset_gyro()
        target_angle = self.gyro_sensor.angle - degrees + 45

        self.run_motors(self.target_power - 5, -(self.target_power - 5))

        while self.gyro_sensor.angle > target_angle:
            pass

        while self.color_sensor.value() != 1:
            pass

        self.stop_motors()
        self.color_sensor.mode = "RGB-RAW"

    def reset_gyro(self):
        """
        Reset and calibrate the gyro sensor.

        Before calling this method, make sure the robot is standing still.
        """
        self.gyro_sensor.mode = "GYRO-RATE"
        self.gyro_sensor.mode = "GYRO-ANG"
        time.sleep(1)

    def sound_beep(self):
        return self.sound.beep()

    def sound_end_communication(self):
        return self.sound.tone([(200, 100, 100), (500, 200)])

    def sound_warning(self):
        return self.sound.tone([(200, 300, 500), (200, 300, 500), (200, 300)])

    def sound_star_wars_short(self):
        return self.sound.play_song((
            ('D4', 'e3'),
            ('D4', 'e3'),
            ('D4', 'e3'),
            ('G4', 'h'),
            ('D5', 'h')
        ))

    def start_exploration(self, is_first_point=True):
        """
        This method contains the main exploration and mechanical routine.
        """
        self.logger.info("Explorer starting")
        prev_coords = None
        prev_arrive_direction = None
        prev_start_direction = prev_arrive_direction
        while True:
            blocked, color = self.drive_to_next_point()  # Follow the path to the next point

            if is_first_point:  # Run if this is our "entry" point
                self.logger.info("Sending ready-signal to mothership")

                planet_data = self.ready_message()

                self.logger.info("Our planet is called %s" % planet_data.get("planetName"))
                self.planet.set_name(planet_data.get("planetName"))
                self.odometry.set_coord(
                    planet_data.get("startX"), planet_data.get("startY"), planet_data.get("startOrientation")
                )  # Set our odometry coordinates to the data we just received from the mothership
                self.odometry.clear_motor_stack()

            if blocked:  # If the path was blocked we're back on the same point we're coming from
                coords, direction = prev_coords, (prev_start_direction - 180) % 360
            else:
                coords, direction = self.odometry.calc_coord()  # Calculate current coordinates and direction

            self.odometry.clear_motor_stack()

            self.logger.debug(
                "Coords: %s, Direction: %s"
                % (
                    coords,
                    direction
                )
            )

            if not is_first_point:
                path = self.path_message(
                    (prev_coords[0],
                     prev_coords[1],
                     prev_start_direction,
                     coords[0],
                     coords[1],
                     (direction - 180) % 360,
                     "blocked" if blocked else "free")
                )

                coords = path[1][0]  # Get corrected (end) coordinates
                direction = (path[1][1] - 180) % 360   # Get corrected direction
                self.logger.debug("Coords: %s" % str((coords, direction)))
                self.odometry.set_coord(coords[0], coords[1], direction)  # Apply corrected coordinates and direction

                self.communication.reset_path()

            self.drive_off_point()  # Drive off the square for rotation

            if not self.planet.check_if_scanned(coords):  # Scan for paths if we haven't on this point before.
                paths = self.scan_for_paths(self.odometry.get_mm_coord()[1])  # Do a 360* scan for outgoing paths
                self.planet.add_andre(coords)  # Add this point to scanned points
                self.reset_motors()
                self.odometry.update_motor_positions()

                if is_first_point:
                    remove_path = (direction - 180) % 360
                    if remove_path in paths:
                        paths.remove(remove_path)  # Remove the "entry" path from the list of paths
                    is_first_point = False

                self.logger.debug("Paths in directions: %s" % paths)

                for p in paths:
                    self.planet.depth_first_add_stack(coords, p)  # Add paths to DFS stack

            target_direction = None  # This will be the next direction to drive
            last_message_at = time.time()
            done = False  # Helper variable to break out of outer loop
            while last_message_at + 3 > time.time():  # Three seconds after the last sent / received message
                communication_target = self.communication.target
                path_select = self.communication.path_select
                paths_unveiled = self.communication.paths_unveiled

                if target_direction is None or self.planet.target != communication_target or paths_unveiled:
                    if communication_target and self.planet.target != communication_target:
                        self.logger.debug("Got new target from mothership: %s" % str(communication_target))

                    # It's possible that we get a target for the point we're currently on
                    # If that's the case, we set the target AFTER we've done our DFS stuff, to avoid finishing to early
                    # TODO: actually, what happens when we arrive on a target and get a new one?
                    if coords != communication_target:
                        self.planet.set_target(communication_target)

                    dfs_direction = self.dfs_get_direction(coords)

                    if coords == self.planet.target:  # Reached target
                        self.logger.info("Target %s reached" % str(coords))
                        self.communication.target_reached_message()

                        done = self.complete()
                        if done:
                            break
                        else:
                            pass  # TODO: do something
                    elif dfs_direction is None:  # Nothing left to explore, at least that the DFS knows of
                        self.logger.info("Exploration completed")
                        self.communication.exploration_completed_message()

                        done = self.complete
                        if done:
                            break
                        else:
                            pass  # TODO: do something
                    else:
                        target_direction = int(dfs_direction)

                    if coords == communication_target:
                        self.planet.set_target(communication_target)

                    self.communication.path_select_message(coords[0], coords[1], target_direction)  # Send path choice

                if path_select:  # In case the server chose a path for us
                    self.logger.debug("Server chose direction: %s" % target_direction)
                    target_direction = path_select
                    self.communication.reset_path_select()

                if paths_unveiled:
                    self.communication.reset_paths_unveiled()

                time.sleep(0.25)
                last_message_at = self.communication.last_message_at

            if done:
                break

            self.logger.debug("End of transmission for this point")

            if self.sound:
                self.sound_end_communication().wait()

            self.logger.debug("Chosen direction: %s" % target_direction)
            self.planet.depth_first_add_reached(coords, target_direction)  # Inform DFS about chosen direction

            if target_direction != direction:  # If the path isn't in front of us, rotate to it
                self.rotate_to_path(direction, target_direction)
                self.odometry.set_coord(direction=target_direction)
                self.reset_motors()
                self.odometry.update_motor_positions()

            self.logger.debug("--------------------------------------------------")

            prev_coords, prev_arrive_direction, prev_start_direction = coords, direction, target_direction

    def dfs_get_direction(self, coords):
        """
        Call the DFS implemented in Planet to determine the next direction to drive to.
        """
        dfs = self.planet.depth_first_search(coords)  # Search which path to drive next with DFS

        self.logger.debug("DFS: %s" % str(dfs))

        if type(dfs) is list:
            result = dfs[0][1]
        else:
            result = None

        return result

    def ready_message(self):
        """
        Send ready message to the mothership and wait for a response. Repeat if no response was received for 2 seconds.
        """
        planet_data = None
        while not planet_data:
            self.communication.ready_message()

            for j in range(10):  # Wait for answer from mothership
                planet_data = self.communication.planet_data
                if planet_data:
                    break
                time.sleep(0.2)

            time.sleep(3)
        return planet_data

    def path_message(self, payload):
        """
        Send path message to the mothership and wait for a response. Repeat if no response was received for 2 seconds.
        """
        path = None
        while not path:  # Send path to server and wait for confirmation / correction
            self.communication.path_message(*payload)  # Send the discovered path to the mothership

            for j in range(10):  # Wait for answer from mothership
                path = self.communication.path
                if path:
                    break
                time.sleep(0.2)

            time.sleep(1)
        return path

    def complete(self):
        """
        Wait for a done message from the server after sending a explorationCompleted or targetReached message.

        Returns a bool, if message was received. If it's False, we screwed up somewhere.
        """
        done = False
        while self.communication.last_message_at + 5 > time.time():  # Wait for confirmation
            done = self.communication.is_done
            if done:
                self.logger.info("Got confirmation from server, celebrating...")
                if self.sound:
                    self.sound_star_wars_short()
                break

        return done

    def drive_off_point(self):
        """
        Drive off a colored square.
        """
        self.run_motors(self.target_power - 3, self.target_power)
        time.sleep(0.75)
        self.stop_motors()

    def drive_to_next_point(self):
        """
        Drive the robot along the path using a PD controller, until it reaches a colored square.

        Returns a tuple of properties, if the path was blocked and what color the target square is.
        """
        # These are the return values, expand as necessary
        blocked = False
        square_color = None

        # Setup hardware
        self.color_sensor.mode = "RGB-RAW"  # Measure RGB values
        self.us_sensor.mode = "US-DIST-CM"  # Measure distance in cm

        # See http://www.inpharmix.com/jps/PID_Controller_For_Lego_Mindstorms_Robots.html for documentation
        k_p = 0.14  # Proportional constant
        offset = 170  # Light sensor offset
        k_i = 0  # Integral constant, we disable this component because it ruins everything
        integral = 0  # Integral
        k_d = 0.055  # Derivative constant
        last_error = 0  # Error value of last loop

        while True:
            self.odometry.update_motor_stack()

            if self.us_sensor.distance_centimeters < 20:  # Path is blocked, so do a 180 rotation and drive back
                blocked = True
                self.logger.debug("Path blocked")
                self.stop_motors()
                if self.sound:
                    self.sound_warning().wait()
                self.rotate_by_degrees_to_path(180)
                self.odometry.update_motor_positions()
                new_angle = (self.odometry.get_mm_coord()[1] - 180) % 360
                self.odometry.set_coord(direction=self.odometry.angle_to_direction(new_angle))
                continue

            r, g, b = self.color_sensor.bin_data("hhh")  # Read RGB values from sensor
            gs = rgb_to_grayscale(r, g, b)  # Convert RGB to grayscale

            r_rb_range = self.red_rb_range
            b_rb_range = self.blue_rb_range
            if (
                r_rb_range[0][0] <= r <= r_rb_range[0][1]
                and r_rb_range[1][0] <= b <= r_rb_range[1][1]
            ):
                self.logger.debug("Detected RED")
                # if not self.check_if_on_point():
                #     self.logger.debug("Not on point, continuing")
                #     pass
                square_color = "red"
                self.stop_motors()
                break
            elif (
                b_rb_range[0][0] <= r <= b_rb_range[0][1]
                and b_rb_range[1][0] <= b <= b_rb_range[1][1]
            ):
                self.logger.debug("Detected BLUE")
                # if not self.check_if_on_point():
                #     self.logger.debug("Not on point, continuing")
                #     pass
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

            self.run_motors(power_right, power_left, 1)  # Apply motor powers

            time.sleep(0.03)  # 50 ms between loops seems to be optimal

        return blocked, square_color

    def check_if_on_point(self):
        """
        Rotate the robot to the left and right and scan the detected color while doing it, to check if we're actually
        on a point.
        """
        self.color_sensor.mode = "COL-COLOR"
        self.reset_gyro()  # Calibrate gyro sensor
        time.sleep(1)
        colors = []
        gyro_start_angle = self.gyro_sensor.angle

        self.run_motors(self.target_power - 5, -(self.target_power - 5))
        while self.gyro_sensor.angle > gyro_start_angle - 25:
            colors.append(self.color_sensor.value())
            time.sleep(0.01)

        self.run_motors(-(self.target_power - 5), self.target_power - 5)
        while self.gyro_sensor.angle < gyro_start_angle + 25:
            colors.append(self.color_sensor.value())
            time.sleep(0.01)

        self.stop_motors()
        return colors.count(1) + colors.count(6) < colors.count(2) + colors.count(5)

    def scan_for_paths(self, start_direction):
        """
        Do a 360-ish degree rotation and detect outgoing paths.

        The result is returned as a list of directions.
        """
        self.color_sensor.mode = "COL-COLOR"
        self.reset_gyro()
        gyro_start_angle = self.gyro_sensor.angle
        target_angle = gyro_start_angle - 360 + 45  # Rotate to this angle using the gyro sensor
        max_angle = gyro_start_angle - 360 - 15  # Use the color sensor to find a path in between target_angle and this

        self.run_motors(self.target_power - 5, -(self.target_power - 5))

        path_at_angles = []  # Angles at which we detected black are saved in here
        while self.gyro_sensor.angle > target_angle:
            if self.color_sensor.value() == 1:  # black
                path_at_angles.append(self.gyro_sensor.angle)

        # Continue the rotation until we detect black (which means the edge of a path) or the max angle is reached.
        while self.color_sensor.value() != 1 and self.gyro_sensor.angle > max_angle:
            pass

        self.stop_motors()

        paths = []
        # Convert the raw angles to directions (0, 90, 180, 270)
        for a in path_at_angles:
            a -= gyro_start_angle
            direction = self.odometry.angle_to_direction((start_direction - abs(a)) % 360)
            if direction not in paths:
                paths.append(direction)

        return paths
