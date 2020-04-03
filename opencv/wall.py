from typing import Tuple

import cv2


class Wall:
    pos: Tuple[tuple]
    id: int
    weigh: int
    radius: float

    def __init__(self, pnt1, pnt2, identifier):
        self.pos = (pnt1, pnt2)
        self.id = identifier

    def draw(self, frame):
        color = (30, 50, 30)
        cv2.rectangle(frame, self.pos[0], self.pos[1], color, -1)
        return frame
