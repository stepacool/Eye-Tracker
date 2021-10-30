import logging
from typing import Optional

import numpy
from cv2 import cv2
from cv2.data import haarcascades
from settings import settings

logger = logging.getLogger(__name__)


class CV2Error(Exception):
    pass


class HaarCascadeBlobCapture:
    """
    Class captures face and eyes using Haar Cascades.
    Detectes pupils using image processing with blob detection.
    Gaze estimation can be achieved by extracting x, y coordinates of the blobs
    Detailed description can be found here:
    https://medium.com/@stepanfilonov/tracking-your-eyes-with-python-3952e66194a6
    """

    face_detector = cv2.CascadeClassifier(haarcascades + "haarcascade_frontalface_default.xml")
    eye_detector = cv2.CascadeClassifier(haarcascades + "haarcascade_eye.xml")
    blob_detector = None

    def __init__(self):
        self.previous_left_blob_area = 1
        self.previous_right_blob_area = 1
        self.previous_left_keypoints = None
        self.previous_right_keypoints = None

    def init_blob_detector(self):
        detector_params = cv2.SimpleBlobDetector_Params()
        detector_params.filterByArea = True
        detector_params.maxArea = 1500
        self.blob_detector = cv2.SimpleBlobDetector_create(detector_params)

    def detect_face(self, img: numpy.ndarray) -> Optional[numpy.ndarray]:
        """
        Capture the biggest face on the frame, return it
        """

        coords = self.face_detector.detectMultiScale(img, 1.3, 5)

        if len(coords) > 1:
            biggest = (0, 0, 0, 0)
            for i in coords:
                if i[3] > biggest[3]:
                    biggest = i
            # noinspection PyUnboundLocalVariable
            biggest = numpy.array([i], numpy.int32)
        elif len(coords) == 1:
            biggest = coords
        else:
            return None

        for (x, y, w, h) in biggest:
            frame = img[y : y + h, x : x + w]
            return frame

    @staticmethod
    def _cut_eyebrows(img):
        """
        Primitively cut eyebrows out of an eye frame by simply cutting the top ~30% of the frame
        """
        if img is None:
            return img
        height, width = img.shape[:2]
        img = img[15:height, 0:width]  # cut eyebrows out (15 px)

        return img

    def detect_eyes(
        self, face_img: numpy.ndarray, cut_brows=True
    ) -> (Optional[numpy.ndarray], Optional[numpy.ndarray]):
        """
        Detect eyes, optionally cut the eyebrows out
        """
        coords = self.eye_detector.detectMultiScale(face_img, 1.3, 5)

        left_eye = right_eye = None

        if coords is None or len(coords) == 0:
            return left_eye, right_eye
        for (x, y, w, h) in coords:
            eye_center = int(float(x) + (float(w) / float(2)))
            if int(face_img.shape[0] * 0.1) < eye_center < int(face_img.shape[1] * 0.4):
                left_eye = face_img[y : y + h, x : x + w]
            elif int(face_img.shape[0] * 0.5) < eye_center < int(face_img.shape[1] * 0.9):
                right_eye = face_img[y : y + h, x : x + w]
            else:
                pass  # false positive - nostrill

            if cut_brows:
                return self._cut_eyebrows(left_eye), self._cut_eyebrows(right_eye)
            return left_eye, right_eye

    def blob_track(self, img, threshold, prev_area):
        _, img = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
        img = cv2.erode(img, None, iterations=2)
        img = cv2.dilate(img, None, iterations=4)
        img = cv2.medianBlur(img, 5)
        keypoints = self.blob_detector.detect(img)
        if keypoints and len(keypoints) > 1:
            tmp = 1000
            for keypoint in keypoints:  # filter out odd blobs
                if abs(keypoint.size - prev_area) < tmp:
                    ans = keypoint
                    tmp = abs(keypoint.size - prev_area)

            keypoints = (ans,)
        return keypoints

    def draw(self, source, keypoints, dest=None):
        try:
            if dest is None:
                dest = source
            return cv2.drawKeypoints(
                source,
                keypoints,
                dest,
                (0, 0, 255),
                cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
            )
        except cv2.error as e:
            raise CV2Error(str(e))

    def debug_dump(self, frame):
        """
        Dump the frame to a folder for future debug
        """
        cv2.imwrite(str(settings.DEBUG_DUMP_LOCATION / f"{id(frame)}.png"), frame)

    def process(self, frame: numpy.ndarray, l_threshold, r_threshold):
        if not self.blob_detector:
            self.init_blob_detector()

        try:
            face = self.detect_face(frame)
            if face is None:
                return frame, None, None
            face_gray = cv2.cvtColor(face, cv2.COLOR_RGB2GRAY)

            left_eye, right_eye = self.detect_eyes(face_gray)
            if left_eye is not None:
                left_key_points = self.blob_track(left_eye, l_threshold, self.previous_left_blob_area)

                kp = left_key_points or self.previous_left_keypoints
                left_eye = self.draw(left_eye, kp, frame)
                self.previous_left_keypoints = kp
            if right_eye is not None:
                right_key_points = self.blob_track(right_eye, r_threshold, self.previous_right_blob_area)

                kp = right_key_points or self.previous_right_keypoints
                right_eye = self.draw(right_eye, kp, frame)
                self.previous_right_keypoints = kp

            return frame, left_eye, right_eye
        except (cv2.error, CV2Error) as e:
            logger.error("error occurred: %s", str(e))
            logger.error(f"Thresholds: left: {l_threshold}, right: {r_threshold}")
            if settings.DEBUG_DUMP:
                self.debug_dump(frame)
            raise
