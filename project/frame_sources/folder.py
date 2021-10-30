from pathlib import Path

from settings import settings
from cv2 import cv2


class FrameSource:
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
