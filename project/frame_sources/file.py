from pathlib import Path

from cv2 import cv2
from settings import settings


class FrameSource:
    """
    Allows to make a 'video' from a single static image - as if it's a static video
    """

    def __init__(self, location: Path = settings.STATIC_FILE_PATH):
        self.location = location
        self.img = None

    def start(self):
        self.img = cv2.imread(str(self.location))
        if self.img is None:
            raise FileNotFoundError(f"File not found: {self.location}")

    def next_frame(self):
        return self.img

    def stop(self):
        ...
