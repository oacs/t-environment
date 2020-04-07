from typing import Tuple

import cv2


class Box:
    pos: tuple
    id: int
    weigh: int
    radius: float

    def __init__(self, pos, identifier, weigh=1, radius=25):
        self.pos = pos
        self.id = identifier
        self.weigh = weigh
        self.radius = radius

    def draw(self, frame, offset: Tuple[int] = (0, 0)):
        color = (74, 200, 244)

        cv2.circle(frame, tuple(map(sum, zip(self.pos, offset))), self.radius, color, -1)
        cv2.putText(frame, str(self.weigh),
                    tuple(map(sum, zip(
                        (int(self.pos[0] - (self.radius * 3 / 8)), int(self.pos[1] + (self.radius / 3))), offset))),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
        return frame
