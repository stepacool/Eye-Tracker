import cv2
import os
import numpy as np

cap = cv2.VideoCapture(0)
method = "haar"
if method == "lbp":
    faceDetect = cv2.CascadeClassifier(os.path.join("Classifiers", "lbp", "lbpcascade_frontalface_improved.xml"))
elif method == "haar":
    faceDetect = cv2.CascadeClassifier(os.path.join("Classifiers", "haar", "haarcascade_frontalface_default.xml"))

eyeDetect = cv2.CascadeClassifier(os.path.join("Classifiers", "haar", 'haarcascade_eye.xml'))

picnum = 0


class ProcessImage:

    """Class contains all the functions that are required to be applied to an image in order to exract an eye/a pupil.
    By default it goes the following way: Image => Biggest face => Eyes => Pupils.
    By sending False some of the procedures can be turned off/skipped.(Not recommended)"""

    def __init__(self, face=True, eyes=True, pupils=True):
        self.faceBool = face
        self.eyesBool = eyes
        self.pupilsBool = pupils

    @staticmethod
    def frame_process(img, clahe=False, blur=False, hist=False):
        """Resizes the image if any of its dimensions are bigger than 640px, makes it gray
        Doesn't apply any additional filters/Doesn't morph the image in any additional way, unless True has been set
        along with one or more parameters."""

        height, width = map(float, img.shape[:2])
        coefficient = round(640 / max(height, width), 2)
        if coefficient < 1:
            img = cv2.resize(img, None, fx=coefficient, fy=coefficient)
        frame = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        return frame

    @staticmethod
    def crop_face(img, cascade):
        """Takes biggest face as the face to work with"""
        coords = cascade.detectMultiScale(img, 1.3, 5)
        if len(coords) > 1:
            biggest = (0, 0, 0, 0)
            for i in coords:
                if i[3] > biggest[3]:
                    biggest = i
        elif len(coords) == 1:
            biggest = coords
        else:
            return None
        for (x, y, w, h) in biggest:
            frame = img[y:y + h, x:x + w]
            lest = (int(w * 0.1), int(w * 0.4))
            rest = (int(w * 0.6), int(w * 0.9))
        return frame, lest, rest

    @staticmethod
    def crop_eyes(img, cascade, lest, rest):
        """
        lest and rest are the left eye estimated location and the right eye estimated location respectively.
        Update 2: Still thinking about how to deal with 1 eye detected/no eyes detected cases.
        """
        coords = cascade.detectMultiScale(img, 1.3, 5)

        for(x, y, w, h) in coords:
            eyemiddle = int(float(x) + (float(w) / float(2)))
            print(coords, lest, rest, eyemiddle)
            if lest[0] < eyemiddle and eyemiddle < lest[1]:
                lefteye = img[y:y + h, x:x + w]
            elif rest[0] < eyemiddle and eyemiddle < rest[1]:
                righteye = img[y:y + h, x:x + w]
        return lefteye, righteye

    @staticmethod
    def detect_pupils():
        pass


while True:
    ret, img = cap.read()
    # img = cv2.imread('Image.jpg', 1)
    if ret:
        e1 = cv2.getTickCount()
#################################################################################################

        image = ProcessImage.frame_process(img)
        face, lest, rest = ProcessImage.crop_face(image, faceDetect)  # left-eye estimate, right-eye estimate (location)
        eyes = ProcessImage.crop_eyes(face, eyeDetect, lest, rest)
        cv2.imshow("IMAGE", face)
        cv2.imwrite("testEyes\\" + "lefteye" + str(picnum) + ".jpg", face)
        picnum += 1

#################################################################################################
        e2 = cv2.getTickCount()
        t = (e2 - e1) / cv2.getTickFrequency()
        print(t)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:         # wait for ESC key to exit
            cv2.destroyAllWindows()
            break
