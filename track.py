import sys
import os.path
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage
from functools import reduce
from collections import deque
import cv2
import numpy as np


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        loadUi('GUImain.ui', self)
        with open("style.css", "r") as css:
            self.setStyleSheet(css.read())
        self.image = None
        self.cameraRuns = False
        self.pageTwo = False
        self.showPupils = False
        self.load_cascades()
        self.load_blob_detector()
        self.startButton.clicked.connect(self.start_webcam)
        self.stopButton.clicked.connect(self.stop_webcam)
        self.nextButton.clicked.connect(self.next_page)
        self.coordsQueueLeft = deque()
        self.coordsQueueRight = deque()

    def start_webcam(self):
        if not self.cameraRuns:
            self.capture = cv2.VideoCapture(cv2.CAP_DSHOW)  # VideoCapture(0) drops error# -1072875772
            self.cameraRuns = not self.cameraRuns
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(2)

        else:
            pass

    def update_frame(self):
        _, self.bImage = self.capture.read()
        if not self.showPupils:
            self.display_image(self.bImage, 1)
        if not self.pageTwo:  # first screen
            self.pImage = cv2.cvtColor(self.bImage, cv2.COLOR_RGB2GRAY)
            self.param1 = self.param1Slider.value()
            self.param2 = self.param2Slider.value()
            self.minRadius = self.minRadiusSlider.value()
            self.maxRadius = self.maxRadiusSlider.value()
            self.arg1 = self.arg1Slider.value()
            self.arg2 = self.arg2Slider.value()
            self.threshold = self.thresholdSlider.value()
            oldLeft = None
            oldRight = None
            face_frame, face_frame_gray, lest, rest, faceX, faceY = self.detect_face(self.bImage, self.pImage)
            if face_frame is not None:
                self.leyeframe, self.reyeframe, self.leyeframeG, self.reyeframeG = self.detect_eyes(face_frame, face_frame_gray, lest, rest)
                if self.leyeframe is not None:
                    if self.leftEyeCheckbox.isChecked():
                        if self.blobToggle.value():
                            lheight, lwidth = self.leyeframe.shape[:2]
                            self.leyeframeG = self.leyeframeG[15:lheight, 0:lwidth]  # cut eyebrows out
                            self.leyeframe = self.leyeframe[15:lheight, 0:lwidth]
                            self.lkeypoints = self.process_eye(self.leyeframeG)
                            if self.lkeypoints is not None:
                                cv2.drawKeypoints(self.leyeframe, self.lkeypoints, self.leyeframe, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
                                oldLeft = self.lkeypoints
                            else:
                                cv2.drawKeypoints(self.leyeframe, oldLeft, self.leyeframe, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
                        else:
                            lIris = self.process_eye1(self.leyeframeG)
                            if lIris is not None:
                                self.lx, self.ly, self.lradius = self.stabilizeLeft(lIris[0], lIris[1], lIris[2])
                                cv2.circle(self.leyeframe, (self.lx, self.ly), self.lradius, (0, 255, 0), 2)
                                cv2.circle(self.leyeframe, (self.lx, self.ly), 2, (0, 0, 255), 3)
                    self.leyeframe = np.require(self.leyeframe, np.uint8, 'C')
                    self.display_image(self.leyeframe, 3)
                if self.reyeframe is not None:
                    if self.rightEyeCheckbox.isChecked():
                        if self.blobToggle.value():
                            rheight, rwidth = self.reyeframe.shape[:2]
                            self.reyeframeG = self.reyeframeG[15:rheight, 0:rwidth]
                            self.reyeframe = self.reyeframe[15:rheight, 0:rwidth]
                            self.rkeypoints = self.process_eye(self.reyeframeG)
                            if self.rkeypoints is not None:
                                cv2.drawKeypoints(self.reyeframe, self.rkeypoints, self.reyeframe, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
                                oldRight = self.rkeypoints
                            else:
                                cv2.drawKeypoints(self.reyeframe, oldRight, self.reyeframe, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
                        else:
                            rIris = self.process_eye1(self.reyeframeG)
                            if rIris is not None:
                                self.x, self.y, self.radius = self.stabilizeRight(rIris[0], rIris[1], rIris[2])
                                cv2.circle(self.reyeframe, (self.x, self.y), self.radius, (0, 255, 0), 2)
                                cv2.circle(self.reyeframe, (self.x, self.y), 2, (0, 0, 255), 3)
                    self.reyeframe = np.require(self.reyeframe, np.uint8, 'C')
                    self.display_image(self.reyeframe, 4)
                if self.pupilsCheckbox.isChecked():
                    self.display_image(self.bImage, 1)

        else:  # second screen
            pass

    def display_image(self, img, window):
        # to do: Grayscale display
        qformat = QImage.Format_Indexed8
        if len(img.shape) == 3:
            if img.shape[2] == 4:  # RGBA
                qformat = QImage.Format_RGBA8888
            else:  # RGB
                qformat = QImage.Format_RGB888

        outImage = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)  # BGR to RGB
        outImage = outImage.rgbSwapped()
        if window == 1:
            self.baseImage.setPixmap(QPixmap.fromImage(outImage))
            self.baseImage.setScaledContents(True)
        if window == 3:
            self.leftEyeBox.setPixmap(QPixmap.fromImage(outImage))
            self.leftEyeBox.setScaledContents(True)
        if window == 4:
            self.rightEyeBox.setPixmap(QPixmap.fromImage(outImage))
            self.rightEyeBox.setScaledContents(True)

    def next_page(self):
        if self.cameraRuns:
            if not self.pageTwo:  # first to second screen
                self.nextButton.clicked.disconnect(self.next_page)
                self.backButton.setEnabled(True)
                self.backButton.clicked.connect(self.next_page)
                self.leftEyeBox.hide()
                self.rightEyeBox.hide()
                self.pageTwo = not self.pageTwo
            else:  # second to first screen
                self.nextButton.clicked.connect(self.next_page)
                self.backButton.setEnabled(False)
                self.leftEyeBox.show()
                self.rightEyeBox.show()
                self.pageTwo = not self.pageTwo

    def load_cascades(self):
        self.faceDetect = cv2.CascadeClassifier(os.path.join("Classifiers", "haar", "haarcascade_frontalface_default.xml"))
        self.eyeDetect = cv2.CascadeClassifier(os.path.join("Classifiers", "haar", 'haarcascade_eye.xml'))

    def load_blob_detector(self):
        detector_params = cv2.SimpleBlobDetector_Params()
        detector_params.filterByArea = True
        detector_params.maxArea = 1500
        self.detector = cv2.SimpleBlobDetector_create(detector_params)

    def stop_webcam(self):
        if self.cameraRuns:
            self.timer.stop()
            self.cameraRuns = not self.cameraRuns

    def detect_face(self, img, img_gray):
        """
        Detects all faces, if multiple found, works with the biggest. Returns the following parameters:
        1. The face frame
        2. A gray version of the face frame
        2. Estimated left eye coordinates range
        3. Estimated right eye coordinates range
        5. X of the face frame
        6. Y of the face frame
        """
        coords = self.faceDetect.detectMultiScale(img, 1.3, 5)

        if len(coords) > 1:
            biggest = (0, 0, 0, 0)
            for i in coords:
                if i[3] > biggest[3]:
                    biggest = i
            biggest = np.array([i], np.int32)
        elif len(coords) == 1:
            biggest = coords
        else:
            return None, None, None, None, None, None
        for (x, y, w, h) in biggest:
            frame = img[y:y + h, x:x + w]
            frame_gray = img_gray[y:y + h, x:x + w]
            lest = (int(w * 0.1), int(w * 0.45))
            rest = (int(w * 0.55), int(w * 0.9))
            X = x
            Y = y

        return frame, frame_gray, lest, rest, X, Y

    def detect_eyes(self, img, img_gray, lest, rest):
        """
        lest and rest are from detect_face method. Returns colored and grayscale eye frames.
        """
        leftEye = None
        rightEye = None
        leftEyeG = None
        rightEyeG = None
        coords = self.eyeDetect.detectMultiScale(img_gray, 1.3, 5)

        if coords is None or len(coords) == 0:
            pass
        else:
            for(x, y, w, h) in coords:
                eyecenter = int(float(x) + (float(w) / float(2)))
                if lest[0] < eyecenter and eyecenter < lest[1]:
                    leftEye = img[y:y + h, x:x + w]
                    leftEyeG = img_gray[y:y + h, x:x + w]
                elif rest[0] < eyecenter and eyecenter < rest[1]:
                    rightEye = img[y:y + h, x:x + w]
                    rightEyeG = img_gray[y:y + h, x:x + w]
                else:
                    pass  # nostril
        return leftEye, rightEye, leftEyeG, rightEyeG

    def process_eye(self, img):  # blob processing
        _, img = cv2.threshold(img, self.threshold, 255, cv2.THRESH_BINARY)
        img = cv2.erode(img, None, iterations=2)
        img = cv2.dilate(img, None, iterations=4)
        img = cv2.medianBlur(img, 5)
        keypoints = self.detector.detect(img)

        return keypoints

    def process_eye1(self, img):  # circular processing
        # kernel_sharpening = np.array([[-1, -1, -1], #maybe use later as an alternative to equalizeHist()
        #                               [-1, 9, -1],
        #                               [-1, -1, -1]])
        # sharpened = cv2.filter2D(img, -1, kernel_sharpening)
        equ = cv2.equalizeHist(img)
        circles = cv2.HoughCircles(equ, cv2.HOUGH_GRADIENT, self.arg1, self.arg2,
                                   param1=self.param1, param2=self.param2, minRadius=self.minRadius, maxRadius=self.maxRadius)
        smallest = 255
        if circles is None or circles[0, 0, 1] == 0 or circles[0, 0, 0] == 0:  # openCV bug, returns [0, 0, 0] instead of None when nothing is detected (sometimes)
            return None
        for i in circles[0, :]:  # filter the "blackest" circle out by comparing average pixel value in the circles
            X = int(i[0])
            Y = int(i[1])
            r = i[2]
            a = int(r / 1.7)  # pythagoras theorem (sqrt2)
            total = 0
            count = 0
            for y in range(Y - 2 * a, Y):
                for x in range(X, X + 2 * a):
                    if x < img.shape[1] and y < img.shape[0]:  # img.shape returns (Y, X), not (X, Y) lol
                        pixel = equ.item(x, y)
                        total += pixel
                        count += 1
            avg = total / count
            if avg < smallest:
                smallest = avg
                iris = i
                # circles = np.uint16(np.around(circles))
        return iris

    def stabilizeLeft(self, x, y, r):  # averages the last five X, Y and radius values with help of dequeue
        if len(self.coordsQueueLeft) == 5:
            self.coordsQueueLeft.popleft()
        else:
            for i in range(0, 5 - len(self.coordsQueueLeft)):
                self.coordsQueueLeft.append((x, y, r))
        stableX = reduce((lambda x, y: x + y), [iris[0] for iris in self.coordsQueueLeft]) / 5
        stableY = reduce((lambda x, y: x + y), [iris[1] for iris in self.coordsQueueLeft]) / 5
        stableRadius = reduce((lambda x, y: x + y), [iris[2] for iris in self.coordsQueueLeft]) / 5
        return int(stableX), int(stableY), int(stableRadius)

    def stabilizeRight(self, x, y, r):  # averages the last five X, Y and radius values with help of dequeue
        if len(self.coordsQueueRight) == 5:
            self.coordsQueueRight.popleft()
        else:
            for i in range(0, 5 - len(self.coordsQueueRight)):
                self.coordsQueueRight.append((x, y, r))
        stableX = reduce((lambda x, y: x + y), [iris[0] for iris in self.coordsQueueRight]) / 5
        stableY = reduce((lambda x, y: x + y), [iris[1] for iris in self.coordsQueueRight]) / 5
        stableRadius = reduce((lambda x, y: x + y), [iris[2] for iris in self.coordsQueueRight]) / 5
        return int(stableX), int(stableY), int(stableRadius)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.setWindowTitle("GUI test")
    window.show()
    sys.exit(app.exec_())
