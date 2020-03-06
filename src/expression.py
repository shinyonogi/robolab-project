class Expression:
    """
    This class allows our robot to express itself.
    Everyone deserves a voice.
    """

    def __init__(self, logger, screen, led, speaker):
        self.logger = logger
        self.screen = screen
        self.led = led
        self.speaker = speaker

    def beep(self):
        # Built-int beep
        self.speaker.beep()

    def speak(self, text):
        self.speaker.speak(text)

    def tone_signal(self):
        # Short tone
        self.speaker.tone([(200, 100, 100)])

    def tone_warning(self):
        # Three second warning tone
        self.speaker.tone([(200, 100, 100), (500, 200)])

    def song_star_wars_title(self):
        # Star Wars title song
        self.speaker.play_song((
            ('D4', 'e3'),
            ('D4', 'e3'),
            ('D4', 'e3'),
            ('G4', 'h'),
            ('D5', 'h'),
            ('C5', 'e3'),
            ('B4', 'e3'),
            ('A4', 'e3'),
            ('G5', 'h'),
            ('D5', 'q'),
            ('C5', 'e3'),
            ('B4', 'e3'),
            ('A4', 'e3'),
            ('G5', 'h'),
            ('D5', 'q'),
            ('C5', 'e3'),
            ('B4', 'e3'),
            ('C5', 'e3'),
            ('A4', 'h.'),
        ))

    def song_star_wars_imperial_march(self):
        # Start Wars Imperial March song
        self.speaker.tone([
            (392, 350, 100), (392, 350, 100), (392, 350, 100), (311.1, 250, 100),
            (466.2, 25, 100), (392, 350, 100), (311.1, 250, 100), (466.2, 25, 100),
            (392, 700, 100), (587.32, 350, 100), (587.32, 350, 100),
            (587.32, 350, 100), (622.26, 250, 100), (466.2, 25, 100),
            (369.99, 350, 100), (311.1, 250, 100), (466.2, 25, 100), (392, 700, 100),
            (784, 350, 100), (392, 250, 100), (392, 25, 100), (784, 350, 100),
            (739.98, 250, 100), (698.46, 25, 100), (659.26, 25, 100),
            (622.26, 25, 100), (659.26, 50, 400), (415.3, 25, 200), (554.36, 350, 100),
            (523.25, 250, 100), (493.88, 25, 100), (466.16, 25, 100), (440, 25, 100),
            (466.16, 50, 400), (311.13, 25, 200), (369.99, 350, 100),
            (311.13, 250, 100), (392, 25, 100), (466.16, 350, 100), (392, 250, 100),
            (466.16, 25, 100), (587.32, 700, 100), (784, 350, 100), (392, 250, 100),
            (392, 25, 100), (784, 350, 100), (739.98, 250, 100), (698.46, 25, 100),
            (659.26, 25, 100), (622.26, 25, 100), (659.26, 50, 400), (415.3, 25, 200),
            (554.36, 350, 100), (523.25, 250, 100), (493.88, 25, 100),
            (466.16, 25, 100), (440, 25, 100), (466.16, 50, 400), (311.13, 25, 200),
            (392, 350, 100), (311.13, 250, 100), (466.16, 25, 100),
            (392.00, 300, 150), (311.13, 250, 100), (466.16, 25, 100), (392, 700)
        ]).wait()