from pathlib import Path

from cv2 import cv2
from settings import settings


class FrameSource:
    """
    Go over video frame-by-frame. Location is specified with ENV var STATIC_FILE_PATH
    """

    def __init__(self, location: Path = settings.STATIC_FILE_PATH):
        self.location = location
        self.capture = None

    def start(self):
        self.capture = cv2.VideoCapture(str(self.location))
        if self.capture is None or not self.capture.read()[0]:
            raise FileNotFoundError(f"Couldn't open and read video: {self.location}")

    def next_frame(self):
        return self.capture.read()

    def stop(self):
        self.capture.release()
