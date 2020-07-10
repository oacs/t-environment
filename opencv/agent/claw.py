from enum import Enum
import cv2
import numpy as np
from opencv.forms.utils import rotate_polygon


class EnumClawState(Enum):
    """ Characteristics uuid enums """
    open = 0
    closing = 1
    closed = 2
    opening = 3


class Claw:
    state: EnumClawState
    pos: tuple
    separation: float
    rotation: float

    def __init__(self, pos):
        self.state = EnumClawState.open
        self.pos = pos
        self.separation = 1
        self.rotation = 0

    def draw_claw(self, frame: object, offset: tuple = (0, 0)) -> object:
        # cv2.circle(frame, tuple(map(sum, zip(self.xy, offset))), 25, (128, 0, 128), 2);
        x, y = tuple(map(sum, zip(self.pos, offset)))
        forms = [np.array([
            (x - 12, y - 10),
            (13 + x, y - 10),
            (x, y - 5),
        ]),
            np.array([
                (x - self.separation - 6, y - 15),
                (x - self.separation, y - 15),
                (x - self.separation, y - 40),
            ]),
            np.array([
                (x + self.separation, y - 15),
                (x + self.separation + 6, y - 15),
                (x + self.separation, y - 40),
            ])
        ]
        for points in forms:
            b = rotate_polygon(points, self.rotation, x, y)
            cv2.polylines(frame, [b], True, (128, 0, 128))
            cv2.fillPoly(frame, [b], (128, 0, 128))
        return frame
