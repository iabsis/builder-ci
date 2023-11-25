

from enum import Enum, auto


class Status(Enum):
    success = auto()
    failed = auto()
    duplicate = auto()
    running = auto()
