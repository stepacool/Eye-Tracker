import os
import cv2
import numpy as np


def init_cv():
    """loads all of cv2 tools"""
    face_detector = cv2.CascadeClassifier(
        os.path.join("Classifiers", "haar", "haarcascade_frontalface_default.xml"))
    eye_detector = cv2.CascadeClassifier(os.path.join("Classifiers", "haar", 'haarcascade_eye.xml'))
    detector_params = cv2.SimpleBlobDetector_Params()
    detector_params.filterByArea = True
    detector_params.maxArea = 1500
    detector = cv2.SimpleBlobDetector_create(detector_params)

    return face_detector, eye_detector, detector


def detect_face(img, img_gray, cascade):
    """
    Detects all faces, if multiple found, works with the biggest. Returns the following parameters:
    1. The face frame
    2. A gray version of the face frame
    2. Estimated left eye coordinates range
    3. Estimated right eye coordinates range
    5. X of the face frame
    6. Y of the face frame
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
        return None, None, None, None, None, None
    for (x, y, w, h) in biggest:
        frame = img[y:y + h, x:x + w]
        frame_gray = img_gray[y:y + h, x:x + w]
        lest = (int(w * 0.1), int(w * 0.45))
        rest = (int(w * 0.55), int(w * 0.9))
        X = x
        Y = y

    return frame, frame_gray, lest, rest, X, Y


def detect_eyes(img, img_gray, lest, rest, cascade):
    """

    :param img: image frame
    :param img_gray: gray image frame
    :param lest: left eye estimated position, needed to filter out nostril, know what eye is found
    :param rest: right eye estimated position
    :param cascade: Hhaar cascade
    :return: colored and grayscale versions of eye frames
    """
    leftEye = None
    rightEye = None
    leftEyeG = None
    rightEyeG = None
    coords = cascade.detectMultiScale(img_gray, 1.3, 5)

    if coords is None or len(coords) == 0:
        pass
    else:
        for (x, y, w, h) in coords:
            eyecenter = int(float(x) + (float(w) / float(2)))
            if lest[0] < eyecenter and eyecenter < lest[1]:
                leftEye = img[y:y + h, x:x + w]
                leftEyeG = img_gray[y:y + h, x:x + w]
                leftEye, leftEyeG = cut_eyebrows(leftEye, leftEyeG)
            elif rest[0] < eyecenter and eyecenter < rest[1]:
                rightEye = img[y:y + h, x:x + w]
                rightEyeG = img_gray[y:y + h, x:x + w]
                rightEye, rightEye = cut_eyebrows(rightEye, rightEyeG)
            else:
                pass  # nostril
    return leftEye, rightEye, leftEyeG, rightEyeG


def process_eye(img, threshold, detector, prevArea=None):
    """

    :param img: eye frame
    :param threshold: threshold value for threshold function
    :param detector:  blob detector
    :param prevArea: area of the previous keypoint(used for filtering)
    :return: keypoints
    """
    _, img = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
    img = cv2.erode(img, None, iterations=2)
    img = cv2.dilate(img, None, iterations=4)
    img = cv2.medianBlur(img, 5)
    keypoints = detector.detect(img)
    if keypoints and prevArea and len(keypoints) > 1:
        tmp = 1000
        for keypoint in keypoints:  # filter out odd blobs
            if abs(keypoint.size - prevArea) < tmp:
                ans = keypoint
                tmp = abs(keypoint.size - prevArea)
        keypoints = np.array(ans)

    return keypoints

def cut_eyebrows(img, imgG):
    height, width = img.shape[:2]
    img = img[15:height, 0:width]  # cut eyebrows out (15 px)
    imgG = imgG[15:height, 0:width]

    return img, imgG


def draw_blobs(img, keypoints):
    """Draws blobs"""
    cv2.drawKeypoints(img, keypoints, img, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)




