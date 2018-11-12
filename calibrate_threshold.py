import cv2
import numpy as np


class Calib:
    """
    Creates a window with trackbars on top, which you can adjust so that only pupils are visible.
    """

    def __init__(self, gray, threshold):
        self.gray = gray
        self.threshold = threshold

    def _nothing(self, _):
        pass

    def _switch(self, _):
        self.gray = not self.gray

    def setup(self):
        self.cap = cv2.VideoCapture(0)
        _, self.img = self.cap.read()

        cv2.imshow("Camera", self.img)
        cv2.createTrackbar("Threshold", "Camera", self.threshold, 255, self._nothing)
        cv2.createTrackbar("Grayscale ON/OFF", "Camera", 0, 1, self._switch)

        while(1):
            _, self.img = self.cap.read()
            if self.gray:
                self.img = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)
            self.k = cv2.waitKey(1) & 0xFF
            if self.k == 27:
                break
            self.threshold = cv2.getTrackbarPos('Threshold', 'Camera')
            _, self.img = cv2.threshold(self.img, self.threshold, 255, cv2.THRESH_BINARY)
            cv2.imshow('Camera', self.img)

        cv2.destroyAllWindows()

        print("Your settings are:\nThreshold:{}\nGrayscale:{}".format(self.threshold, self.gray))


if __name__ == "__main__":
    ebosh = Calib(False, 100)
    ebosh.setup()
