from pathlib import Path
from typing import Protocol
from cv2 import cv2

from settings import settings


class FrameSource(Protocol):
    """
    Describes what methods are expected to be in a FrameSource
    """

    def next_frame(self):
        ...

    def start(self):
        ...

    def stop(self):
        ...


class OpenCVCameraVideoSource:
    def __init__(self):
        self.camera_is_running = False

    def start(self):
        if not self.camera_is_running:
            for camera_device_index in range(0, 3000, 100):
                self.capture = cv2.VideoCapture(
                    camera_device_index
                )  # VideoCapture(0) sometimes drops error #-1072875772
                if self.capture is not None and self.capture.read()[0]:
                    self.camera_is_running = True
                    break

    def stop(self):
        if self.camera_is_running:
            self.capture.release()
            self.camera_is_running = False

    def next_frame(self):
        assert self.camera_is_running, "Start the camera first by calling the start() method"

        success, frame = self.capture.read()

        if not success:
            raise SystemError("Failed to capture a frame")

        return frame


class FolderOpenCVImageSource:
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


class StaticFileOpenCVImageFile:
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
