from pathlib import Path

from cv2 import cv2
from settings import settings


class FrameSource:
    """
    Allows to go over files in a folder file-by-file, frame-by-frame as if they are a video
    """

    def __init__(self, location: Path = settings.DEBUG_DUMP_LOCATION):
        self.location = location
        self.path_list = None
        self.idx = 0

    def start(self):
        self.path_list = list(self.location.glob("*.png"))
        if not self.path_list:
            raise FileNotFoundError(f"Path: {self.location} is empty")

    def next_frame(self):
        if self.idx >= len(self.path_list):
            self.idx = 0
        img = cv2.imread(str(self.path_list[self.idx]))
        self.idx += 1
        return img

    def stop(self):
        ...
