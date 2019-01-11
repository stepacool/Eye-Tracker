import sys
import os.path
import cv2
import numpy as np
import process
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage
import time


class Window(QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        loadUi('GUImain.ui', self)
        with open("style.css", "r") as css:
            self.setStyleSheet(css.read())
        self.faceDetect, self.eyeDetect, self.detector, self.calibrateImage, self.pointer = process.init_cv()
        self.startButton.clicked.connect(self.start_webcam)
        self.stopButton.clicked.connect(self.stop_webcam)
        self.nextButton.clicked.connect(self.next_page)
        self.screenWidth = QDesktopWidget().screenGeometry().width()
        self.screenHeight = QDesktopWidget().screenGeometry().height()
        self.oldRight = None
        self.oldLeft = None
        self.oldRightArea = None
        self.oldLeftArea = None
        self.cameraRuns = False
        # args below are used for calibration
        self.pageTwo = False
        self.X = None
        self.Y = None
        self.xPool = []
        self.yPool = []
        self.calibrated = False
        self.centerX = 0
        self.leftX = 0
        self.righX = 0

    def start_webcam(self):  # main loop
        if not self.cameraRuns:
            self.capture = cv2.VideoCapture(cv2.CAP_DSHOW)  # VideoCapture(0) drops error# -1072875772
            if self.capture is None:
                self.capture = cv2.VideoCapture(0)
            self.cameraRuns = True
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(2)

    def update_frame(self):  # logic of the main loop

        _, bImage = self.capture.read()
        self.display_image(bImage, 1)
        pImage = cv2.cvtColor(bImage, cv2.COLOR_RGB2GRAY)
        rightEyeThreshold = self.rightEyeThresholdSlider.value()
        leftEyeThreshold = self.leftEyeThresholdSlider.value()
        face_frame, face_frame_gray, lest, rest, faceX, faceY = process.detect_face(bImage, pImage, self.faceDetect)
        if face_frame is not None:
            leyeframe, reyeframe, leyeframeG, reyeframeG = process.detect_eyes(face_frame, face_frame_gray, lest, rest, self.eyeDetect)

            if reyeframe is not None:
                if self.rightEyeCheckbox.isChecked():
                    reyeframe, reyeframeG = process.cut_eyebrows(reyeframe, reyeframeG)
                    rkeypoint = process.process_eye(reyeframeG, rightEyeThreshold, self.detector, prevArea=self.oldRightArea)
                    if rkeypoint:
                        self.oldRight = rkeypoint
                        self.oldRightArea = rkeypoint[0].size
                    else:
                        rkeypoint = self.oldRight
                    try:
                        self.X, self.Y = rkeypoint[0].pt[0], rkeypoint[0].pt[1]
                    except TypeError:
                        pass
                    process.draw_blobs(reyeframe, rkeypoint)
                reyeframe = np.require(reyeframe, np.uint8, 'C')
                self.display_image(reyeframe, 4)

            if leyeframe is not None:
                if self.leftEyeCheckbox.isChecked():
                    leyeframe, leyeframeG = process.cut_eyebrows(leyeframe, leyeframeG)
                    lkeypoint = process.process_eye(leyeframeG, leftEyeThreshold, self.detector,
                                                    prevArea=self.oldLeftArea)
                    if lkeypoint:
                        self.oldLeft = lkeypoint
                        self.oldRightArea = lkeypoint[0].size
                    else:
                        lkeypoint = self.oldLeft
                    process.draw_blobs(leyeframe, lkeypoint)
                leyeframe = np.require(leyeframe, np.uint8, 'C')
                self.display_image(leyeframe, 3)

        if self.pupilsCheckbox.isChecked():  # draws keypoints on pupils on main window
            self.display_image(bImage, 1)

        # calibration and gaze estimation part below
        # logic below can be put in DRY way, but I can't come up with a way for now, want to make it work at least
        # Code below works
        # if self.pageTwo and not self.calibrated:
        #     if len(self.xPool) < 50:
        #         self.xPool.append(self.X)
        #         self.yPool.append(self.Y)
        #     else:
        #         if self.centerX == 0:
        #             self.centerX = max(self.xPool)
        #             self.centerY = max(self.yPool)
        #             cv2.moveWindow('Look_here', 0, 0)
        #             self.xPool = []
        #             self.yPool = []
        #         elif self.leftX == 0:
        #             self.leftX = max(self.xPool)
        #             self.topY = max(self.yPool)
        #             cv2.moveWindow('Look_here', self.screenWidth - 260, self.screenHeight - 40)
        #             self.xPool = []
        #             self.yPool = []
        #         else:
        #             self.rightX = max(self.xPool)
        #             self.bottomY = max(self.yPool)
        #             cv2.destroyWindow('Look_here')
        #             self.calibrated = True
        #             self.xRange = abs(self.rightX - self.leftX) # range of your pupils' movement X
        #             self.yRange = abs(self.bottomY - self.topY) # Y
        #             print(self.xRange, self.yRange)
        #             cv2.imshow('Pointer', self.pointer)

        # # POINTER PART
        # elif self.pageTwo and self.calibrated:
        #     ratioX = (self.rightX - self.X) / self.xRange
        #     ratioY = (self.bottomY - self.Y) / self.yRange
        #     print(ratioX, ratioY)
        #     screenpositionX = int((self.screenWidth-150) * ratioX)
        #     screenpositionY = int((self.screenHeight-150) * ratioY)
        #     cv2.moveWindow('Pointer', screenpositionX, screenpositionY)

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
            self.nextButton.clicked.disconnect(self.next_page)
            self.backButton.setEnabled(True)
            self.backButton.clicked.connect(self.next_page)
            self.showFullScreen()
            self.rightEyeThreshold = self.rightEyeThresholdSlider.value()
            self.pageTwo = not self.pageTwo
            cv2.imshow('Look_here', self.calibrateImage)
            cv2.moveWindow('Look_here', self.screenWidth / 2 - 130, self.screenHeight / 2 - 20)

    def stop_webcam(self):
        if self.cameraRuns:
            self.timer.stop()
            self.cameraRuns = not self.cameraRuns

    def calibrate(self):
        pass
        # cv2.imshow('Look_here', self.calibrateImage)
        # cv2.moveWindow('Look_here', self.screenWidth / 2 - 130, self.screenHeight / 2 - 20)
        # centerX, centerY = self.matchPixToXY()
        # cv2.moveWindow('Look_here', 0, 0)
        # leftX, topY = self.matchPixToXY()
        # cv2.moveWindow('Look_here', self.screenWidth-260, self.screenHeight-40)
        # rightX, bottomY = self.matchPixToXY()

    def matchPixToXY(self):
        """
        Matches X, Y of blob to where you look(to where "Look_here" window is)
        :return:
        """
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.setWindowTitle("GUI test")
    window.show()
    sys.exit(app.exec_())
