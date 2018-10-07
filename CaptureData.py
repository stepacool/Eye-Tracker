import cv2
import os
import numpy as np
from threading import Thread

cap = cv2.VideoCapture(0)
method = "haar"
if method == "lbp":
    faceDetect = cv2.CascadeClassifier(os.path.join("Classifiers", "lbp", "lbpcascade_frontalface_improved.xml"))
elif method == "haar":
    faceDetect = cv2.CascadeClassifier(os.path.join("Classifiers", "haar", "haarcascade_frontalface_default.xml"))

eyeDetect = cv2.CascadeClassifier(os.path.join("Classifiers", "haar", 'haarcascade_eye.xml'))

global picnum
picnum = 0


class ProcessImage:

    """
    Class contains all the functions that are required to be applied to an image
    in order to exract an eye/a pupil.
    By default it goes the following way: Image => Biggest face => Eyes => Pupils.
    By sending False some of the procedures can be turned off/skipped.(Not recommended)
    """

    def __init__(self, face=True, eyes=True, pupils=True):
        self.faceBool = face
        self.eyesBool = eyes
        self.pupilsBool = pupils

    @staticmethod
    def frame_process(img, clahe=False, blur=False, hist=False):
        """
        Resizes the image if any of its dimensions are bigger than 640px, makes it gray.
        Doesn't apply any additional filters/Doesn't morph the image in any additional way,
        unless True has been sent along with one or more parameters.
        """

        height, width = map(float, img.shape[:2])
        coefficient = round(640 / max(height, width), 2)
        if coefficient < 1:
            img = cv2.resize(img, None, fx=coefficient, fy=coefficient)
        frame = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        return frame

    @staticmethod
    def crop_face(img, cascade):
        """
        Takes biggest face as the face to work with
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
            return False, None, None, None
        for (x, y, w, h) in biggest:
            frame = img[y:y + h, x:x + w]
            lest = (int(w * 0.1), int(w * 0.45))
            rest = (int(w * 0.55), int(w * 0.9))
            # cv2.imwrite("testEyes\\Face." + str(picnum) + ".jpg", img)

        return True, frame, lest, rest

    @staticmethod
    def crop_eyes(img, cascade, lest, rest):
        """
        lest and rest are the left eye estimated location and the right eye estimated location respectively.
        Separate cases for 0, 1, 2 and 3+(nostrill) eyes detected.
        """
        coords = cascade.detectMultiScale(img, 1.3, 5)
        lefteye = None
        righteye = None
        cv2.imwrite("testEyes\\Face." + str(picnum) + ".jpg", img)
        if coords is None or len(coords) == 0:
            return False, (lefteye, righteye)
        elif len(coords) == 1:
            for(x, y, w, h) in coords:
                eyemiddle = int(float(x) + (float(w) / float(2)))
                if lest[0] < eyemiddle and eyemiddle < lest[1]:
                    lefteye = img[y:y + h, x:x + w]
                    return True, (lefteye, righteye)
                if rest[0] < eyemiddle and eyemiddle < rest[1]:
                    righteye = img[y:y + h, x:x + w]
                    return True, (lefteye, righteye)
                else:
                    pass  # nostril case

        elif len(coords) >= 2:
            for(x, y, w, h) in coords:
                eyemiddle = int(float(x) + (float(w) / float(2)))
                if lest[0] < eyemiddle and eyemiddle < lest[1]:
                    lefteye = img[y:y + h, x:x + w]
                elif rest[0] < eyemiddle and eyemiddle < rest[1]:
                    righteye = img[y:y + h, x:x + w]
                else:
                    pass  # nostril case
            return True, (lefteye, righteye)

    @staticmethod
    def detect_pupils(img):
        pupil = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT)
        print(pupil)


while True:
    ret, img = cap.read()
    # ret = True
    # img = cv2.imread('Face.188.jpg', 1)
    if ret:
        e1 = cv2.getTickCount()
        eyesSuccess = False
#################################################################################################

        image = ProcessImage.frame_process(img)
        faceSuccess, face, lest, rest = ProcessImage.crop_face(image, faceDetect)
        if faceSuccess:
            eyesSuccess, eyes = ProcessImage.crop_eyes(face, eyeDetect, lest, rest)
        if eyesSuccess:
            for i in eyes:
                if i is None:
                    pass
                else:
                    pass ####################
                    # pupilcoords =

        picnum += 1

#################################################################################################
        e2 = cv2.getTickCount()
        t = (e2 - e1) / cv2.getTickFrequency()
        print(t)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:         # wait for ESC key to exit
            cv2.destroyAllWindows()
            break
