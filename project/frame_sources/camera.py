from cv2 import cv2


class FrameSource:
    """
    Allows to capture images from camera frame-by-frame
    """

    def __init__(self, cam_id=None):
        self.camera_is_running = False
        self.cam_id = cam_id
        self.capture = None

    def _check_camera(self):
        return self.capture is not None and self.capture.read()[0]

    def start(self):
        if not self.camera_is_running:
            if self.cam_id is not None:
                self.capture = cv2.VideoCapture(self.cam_id)

                if not self._check_camera():
                    raise SystemError(f"Camera id={self.cam_id} not working")

                self.camera_is_running = True
                return
            for camera_device_index in range(0, 5000, 100):  # Try different camera IDs, they usually increment by 100
                self.capture = cv2.VideoCapture(camera_device_index)

                if self._check_camera():
                    self.camera_is_running = True
                    return
            raise SystemError("Couldn't find a camera on the device. shell \nls /dev/ | grep *video*\n might help")

    def stop(self):
        if self.camera_is_running:
            self.capture.release()
            self.camera_is_running = False

    def next_frame(self):
        assert self.camera_is_running, "Start the camera first by calling the start() method"

        success, frame = self.capture.read()

        if not success:
            raise SystemError("Failed to capture a frame")

        return frame
