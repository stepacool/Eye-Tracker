from typing import Protocol

import numpy


class Capture(Protocol):
    def detect_eyes(self):
        ...

    def detect_face(self):
        ...

    def process(self, frame: numpy.ndarray, threshold: int):
        ...
