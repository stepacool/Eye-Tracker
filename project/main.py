import argparse
import sys

from PyQt6.QtWidgets import QApplication

from capturers.haar_blob import HaarCascadeBlobCapture
from gui.application_window import Window
from video_source import (
    OpenCVCameraVideoSource,
    FolderOpenCVImageSource,
    StaticFileOpenCVImageFile,
)

FRAME_SOURCES = {
    "camera": OpenCVCameraVideoSource,
    "folder": FolderOpenCVImageSource,
    "file": StaticFileOpenCVImageFile,
}


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-fs",
        "--frame-source",
        action="store",
        dest="frame_source",
        choices=FRAME_SOURCES.keys(),
        default="camera",
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = get_args()
    frame_source = FRAME_SOURCES[args.frame_source]()

    capture = HaarCascadeBlobCapture()

    app = QApplication(sys.argv)

    window = Window(frame_source, capture)
    window.setWindowTitle("Eye Tracking")
    window.show()
    sys.exit(app.exec())
