from typing import Protocol
from .camera import FrameSource as CameraFrameSource
from .file import FrameSource as FileFrameSource
from .folder import FrameSource as FolderFrameSource
from .video import FrameSource as VideoFrameSource


class FrameSource(Protocol):
    """
    Describes what methods are expected to be in a FrameSource
    """

    def next_frame(self):
        ...

    def start(self):
        ...

    def stop(self):
        ...

