import sys
import os.path
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage
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
        self.load_cascades()
        self.load_blob_detector()
        self.startButton.clicked.connect(self.start_webcam)
        self.stopButton.clicked.connect(self.stop_webcam)
        self.nextButton.clicked.connect(self.next_page)
        self.oldRight = None
        self.oldLeft = None
        self.oldRightArea = None
        self.oldLeftArea = None

    def start_webcam(self):
        if not self.cameraRuns:
            self.capture = cv2.VideoCapture(cv2.CAP_DSHOW)  # VideoCapture(0) drops error# -1072875772
            if self.capture is None:
                self.capture = cv2.VideoCapture(0)
            self.cameraRuns = True
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(2)

        else:
            pass

    def update_frame(self):
        _, self.bImage = self.capture.read()
        if not self.pupilsCheckbox.isChecked():
            self.display_image(self.bImage, 1)
        if not self.pageTwo:  # first screen
            self.pImage = cv2.cvtColor(self.bImage, cv2.COLOR_RGB2GRAY)
            self.rightEyeThreshold = self.rightEyeThresholdSlider.value()
            self.leftEyeThreshold = self.leftEyeThresholdSlider.value()
            oldLeft = None
            oldRight = None
            face_frame, face_frame_gray, lest, rest, faceX, faceY = self.detect_face(self.bImage, self.pImage)
            if face_frame is not None:
                self.leyeframe, self.reyeframe, self.leyeframeG, self.reyeframeG = self.detect_eyes(face_frame, face_frame_gray, lest, rest)
                if self.leyeframe is not None:  # displays left eye
                    if self.leftEyeCheckbox.isChecked():  # draws a circle on left eye pupil
                        lheight, lwidth = self.leyeframe.shape[:2]
                        self.leyeframeG = self.leyeframeG[15:lheight, 0:lwidth]  # cut eyebrows out (15 px)
                        self.leyeframe = self.leyeframe[15:lheight, 0:lwidth]
                        self.lkeypoints = self.process_eye(self.leyeframeG, self.leftEyeThreshold)
                        if self.lkeypoints is not None:
                            cv2.drawKeypoints(self.leyeframe, self.lkeypoints, self.leyeframe, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
                            oldLeft = self.lkeypoints
                        else:
                            cv2.drawKeypoints(self.leyeframe, oldLeft, self.leyeframe, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
                    self.leyeframe = np.require(self.leyeframe, np.uint8, 'C')
                    self.display_image(self.leyeframe, 3)
                if self.reyeframe is not None:  # displays right eye
                    if self.rightEyeCheckbox.isChecked():  # draws a circle on right eye pupil
                        rheight, rwidth = self.reyeframe.shape[:2]
                        self.reyeframeG = self.reyeframeG[15:rheight, 0:rwidth] # cur eyebrows out (15 px)
                        self.reyeframe = self.reyeframe[15:rheight, 0:rwidth]
                        self.rkeypoints = self.process_eye(self.reyeframeG, self.rightEyeThreshold) # get blobs
                        self.draw_blobs(self.reyeframe, self.rkeypoints, side="right") # draw blobs

                    self.reyeframe = np.require(self.reyeframe, np.uint8, 'C')
                    self.display_image(self.reyeframe, 4)
            if self.pupilsCheckbox.isChecked():  # draws keypoints on pupils on main window
                self.display_image(self.bImage, 1)

        else:  # second screen
            pass

    def display_image(self, img, window):
        # Makes OpenCV images displayable on PyQT, displays them
        qformat = QImage.Format_Indexed8
        if len(img.shape) == 3:
            if img.shape[2] == 4:  # RGBA
                qformat = QImage.Format_RGBA8888
            else:  # RGB
                qformat = QImage.Format_RGB888

        outImage = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)  # BGR to RGB
        outImage = outImage.rgbSwapped()
        if window == 1:  # main window
            self.baseImage.setPixmap(QPixmap.fromImage(outImage))
            self.baseImage.setScaledContents(True)
        if window == 3:  # left eye window
            self.leftEyeBox.setPixmap(QPixmap.fromImage(outImage))
            self.leftEyeBox.setScaledContents(True)
        if window == 4:  # right eye window
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

    def process_eye(self, img, threshold):  # blob processing
        _, img = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
        img = cv2.erode(img, None, iterations=2)
        img = cv2.dilate(img, None, iterations=4)
        img = cv2.medianBlur(img, 5)
        keypoints = self.detector.detect(img)

        return keypoints

    def draw_blobs(self, img, keypoints, side="right"):
        """Draws blobs, uses a kwarg to determine which eye to draw (left or right)"""
        print(keypoints, self.oldRight, self.oldLeft)
        if len(keypoints) == 1:  # when one blob is found, we draw it and remember its position, area
            cv2.drawKeypoints(img, keypoints, img, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            if side == "right":
                self.oldRight = keypoints
                self.oldRightArea = keypoints[0].size
            else:
                self.oldLeft = keypoints
                self.oldLeftArea = keypoints
        elif len(keypoints) == 0 and self.oldRight is not None and side == "right":  # when no blobs are found, we draw the last remembered blob(right)
            cv2.drawKeypoints(img, self.oldRight, img, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        elif len(keypoints) == 0 and self.oldRight is not None and side == "left": # when no blobs are found, we draw the last remembered blob(left)
            cv2.drawKeypoints(img, self.oldLeft, img, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        elif len(keypoints) > 1:  # when multiple blobs are found the one whose area is the closest to the last detected blob's area is drawn
            tmp = 1000
            if side == "right":
                area = self.oldRightArea
            else:
                area = self.oldLeftArea
            for keypoint in keypoints: # filter out odd blobs
                if abs(keypoint.size - area) < tmp:
                    keypoint_to_draw = np.array(keypoint)
                    tmp = abs(keypoint.size - area)
            cv2.drawKeypoints(img, keypoint_to_draw, img, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    def process_pupil(self, img):  # pupil processing for conreal reflection
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.setWindowTitle("GUI test")
    window.show()
    sys.exit(app.exec_())
