import cv2
import os
import numpy as np


method = "lbp"
if method == "lbp":
    faceDetect = cv2.CascadeClassifier(os.path.join("Classifiers", "lbp", "lbpcascade_frontalface_improved.xml"))
elif method == "haar":
    faceDetect = cv2.CascadeClassifier(os.path.join("Classifiers", "haar", "haarcascade_frontalface_default.xml"))

eyeDetect = cv2.CascadeClassifier(os.path.join("Classifiers", "haar", 'haarcascade_eye.xml'))

picnum = 0


def frame_process(img, clahe=False, blur=False, hist=False):
    frame = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return frame


def crop(img, coords):
    frame = img[y:y + h, x:x + w]
    return frame


while True:
    # ret, frame = cap.read()
    img = cv2.imread('Image.jpg', 1)
    height, width = map(float, img.shape[:2])
    coefficient = round(640 / max(height, width), 2)
    if coefficient < 1:
        img = cv2.resize(img, None, fx=coefficient, fy=coefficient)
    if True:  # if ret
        e1 = cv2.getTickCount()
        img = frame_process(img)

############################################

        # col = frame
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # pupilFrame = frame
        # clahe = frame  # histrogram equalization clahe
        # blur = frame  # median blur
        # edges = frame
        # eyes = cv2.CascadeClassifier(os.path.join("EyeClassifier", 'haarcascade_eye.xml'))
        # detected = eyes.detectMultiScale(frame, 1.3, 5)
        # for (x, y, w, h) in detected:
        #     cv2.rectangle(frame, (x, y), ((x + w), (y + h)), (0, 0, 255), 1)
        #     cv2.line(frame, (x, y), ((x + w, y + h)), (0, 0, 0), 1)
        #     cv2.line(frame, (x + w, y), ((x, y + h)), (0, 0, 0), 1)
        #     pupilFrame = cv2.equalizeHist(frame[y:(y + h), x:(x + w)])
        #     cl1 = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        #     clahe = cl1.apply(pupilFrame)
        #     blur = cv2.medianBlur(clahe, 7)
        #     circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=3, maxRadius=22)
        # cv2.imshow('image', pupilFrame)
        # cv2.imshow('clahe', clahe)
        # cv2.imshow('blur', blur)

        face_rect = faceDetect.detectMultiScale(img, 1.3, 5)
        for(x, y, w, h) in face_rect:
            face = crop(img, (x, y, w, h))
        eye_rects = eyeDetect.detectMultiScale(face, 1.3, 5)
        for(x, y, w, h) in eye_rects:
            eye = crop(face, (x, y, w, h))
            cv2.imwrite("testEyes\\" + str(picnum) + ".jpg", eye)
            picnum += 1
        cv2.imshow("IMAGE", eye)
        e2 = cv2.getTickCount()
        t = (e2 - e1) / cv2.getTickFrequency()
        print(t)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:         # wait for ESC key to exit
            cv2.destroyAllWindows()
            break
