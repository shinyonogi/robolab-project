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
        return self.speaker.beep()

    def speak(self, text):
        return self.speaker.speak(text)

    def tone_end_communication(self):
        # Three second warning tone
        return self.speaker.tone([(200, 100, 100), (500, 200)])

    def tone_warning(self):
        return self.speaker.tone([(200, 300, 500), (200, 300, 500), (200, 300)])

    def song_star_wars_short(self):
        return self.speaker.play_song((
            ('D4', 'e3'),
            ('D4', 'e3'),
            ('D4', 'e3'),
            ('G4', 'h'),
            ('D5', 'h')
        ))
