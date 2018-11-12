import cv2
import os  # only here for path join
import numpy as np
import ctypes  # needed to get screen resolution

from calibrate_threshold import Calib


class Process:
    """
    Just a container for image processing functions
    """

    def __init__(self, faceCascade, eyeCascade, threshold):
        self.faceCascade = faceCascade
        self.eyeCascade = eyeCascade
        self.threshold = threshold

    @staticmethod
    def process(img, threshold=False, gray=False):
        """
        For now only serves for RGB-GRAY conversion, more functionality is to be added
        """
        if img.size == 0:
            return None
        if gray:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        if threshold:
            _, img = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
        return img

    @staticmethod
    def detect_face(img, cascade):
        """
        Detects all faces, if multiple found, works with the biggest. Returns the following parameters:
        1. Boolean saying wether any face could be found on the picture
        2. The face frame
        3. Estimated left eye coordinates range
        4. Estimated right eye coordinates range
        5. The face's X coordinate on the original picture
        6. The face's Y coordinate on the original picture
        """
        coords = cascade.detectMultiScale(img, 1.3, 5)

        if len(coords) > 1:
            biggest = (0, 0, 0, 0)
            for i in coords:
                if i[3] > biggest[3]:
                    biggest = i
            biggest = np.array([i], np.int32)
        elif len(coords) == 1:
            biggest = coords
        else:
            return False, None, None, None, None, None
        for (x, y, w, h) in biggest:
            faceX = x
            faceY = y
            frame = img[y:y + h, x:x + w]
            lest = (int(w * 0.1), int(w * 0.45))
            rest = (int(w * 0.55), int(w * 0.9))

        return True, frame, lest, rest, faceX, faceY

    @staticmethod
    def detect_eyes(img, cascade, lest, rest):
        """
        lest and rest are from detect_face method. Returns all geometrical information about eye frames.
        If eyes couldn't be found, returns False. If only one eye has been found, returns True but the missing
        eye's coordinates are set to 0.
        """
        coords = cascade.detectMultiScale(img, 1.3, 5)
        lX, lW = 0, 0
        lY, lH = 0, 0
        rX, rW = 0, 0
        rY, rH = 0, 0

        if coords is None or len(coords) == 0:
            return False, ((lX, lW), (rX, rW)), ((lY, lH), (rY, rH))
        elif len(coords) == 1:
            for(x, y, w, h) in coords:
                eyemiddle = int(float(x) + (float(w) / float(2)))
                if lest[0] < eyemiddle and eyemiddle < lest[1]:
                    eyeX = ((x, w), (0, 0))
                    eyeY = ((y, h), (0, 0))
                    return True, eyeX, eyeY
                if rest[0] < eyemiddle and eyemiddle < rest[1]:
                    eyeX = ((0, 0), (x, w))
                    eyeY = ((0, 0), (y, h))
                    return True, eyeX, eyeY
                else:
                    pass  # nostril case

        elif len(coords) >= 2:
            for(x, y, w, h) in coords:
                eyemiddle = int(float(x) + (float(w) / float(2)))
                if lest[0] < eyemiddle and eyemiddle < lest[1]:
                    lX, lW = x, w
                    lY, lH = y, h
                elif rest[0] < eyemiddle and eyemiddle < rest[1]:
                    rX, rW = x, w
                    rY, rH = y, h
                else:
                    pass  # nostril case
            return True, ((lX, lW), (rX, rW)), ((lY, lH), (rY, rH))

    @staticmethod
    def process_eye(frame, detector):
        frame = cv2.medianBlur(frame, 5)
        keypoints = detector.detect(frame)
        print(keypoints)
        marked = cv2.drawKeypoints(frame, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        return marked


if __name__ == "__main__":
    ####################################################
    """Calibrate threshold and other parameters for user's light conditions"""
    calib = Calib(False, 100)
    calib.setup()
    threshold = calib.threshold
    gray = calib.gray
    ####################################################
    """Get screen resolution"""
    user32 = ctypes.windll.user32
    screenW, screenH = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    ####################################################
    """Initiate cascade classifiers"""
    faceDetect = cv2.CascadeClassifier(os.path.join("Classifiers", "haar", "haarcascade_frontalface_default.xml"))
    eyeDetect = cv2.CascadeClassifier(os.path.join("Classifiers", "haar", 'haarcascade_eye.xml'))
    ####################################################
    """Initiate blob detector for pupil/iris tracking"""
    detector_params = cv2.SimpleBlobDetector_Params()
    detector = cv2.SimpleBlobDetector_create(detector_params)
    ####################################################
    """Select between working with a video/working with an image (The latter is for test purposes atm)"""
    mode = int(input("What would you like to process?\n1. Image\n2. Video\n"))
    if mode == 1:
        img = cv2.imread('AAAA.35.jpg', 1)
    elif mode == 2:
        cap = calib.cap
    ####################################################

    while True:
        eyesSuccess = False
        faceSuccess = False
        if mode == 2:
            _, img = cap.read()
        grayimg = Process.process(img, gray=True)
        faceSuccess, face_frame, lest, rest, faceX, faceY = Process.detect_face(grayimg, faceDetect)
        if faceSuccess:
            eyesSuccess, eyesX, eyesY = Process.detect_eyes(face_frame, eyeDetect, lest, rest)
        if eyesSuccess:
            print(faceX, eyesX)
            print(faceY, eyesY)
            lX, lW = faceX + eyesX[0][0], eyesX[0][1]
            rX, rW = faceX + eyesX[1][0], eyesX[1][1]
            lY, lH = faceY + eyesY[0][0], eyesY[0][1]
            rY, rH = faceY + eyesY[1][0], eyesY[1][1]
            leyeframe = img[lY:lY + lH, lX:lX + lW]  # colored
            reyeframe = img[rY:rY + rH, rX:rX + rW]  # colored
            leyeframe = Process.process(leyeframe, threshold=threshold, gray=gray)
            reyeframe = Process.process(reyeframe, threshold=threshold, gray=gray)
            if leyeframe is not None:
                pic = Process.process_eye(leyeframe, detector)
            cv2.imshow("Left eye", pic)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:         # wait for ESC key to exit
            cv2.destroyAllWindows()
            break
