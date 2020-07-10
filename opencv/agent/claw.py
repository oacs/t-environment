from enum import Enum
import cv2
import numpy as np
from opencv.forms.utils import rotate_polygon
from opencv.forms.utils import distance

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
    status: int
    box_id: int

    def __init__(self, pos):
        self.state = EnumClawState.open
        self.pos = pos
        self.separation = 20
        self.rotation = 0
        self.status = b'\x02'

    def update(self, status, boxes):

        if self.status == b'\x02':
            if status == b'\x01':
                self.status = b'\x01'
                self.separation -= 1
                return boxes
        if self.status == b'\x01':
            if self.separation > 10:
                self.separation -= 1
            for box in boxes:
                distance_to_box = distance(box.pos, self.pos)
                if  distance_to_box < 80:
                    self.status = b'\x04'
                    self.box_id = box.id
                    break
            return boxes

        if self.status == b'\x04':
            boxes = self.update_box_pos(boxes)
        return boxes

    def update_box_pos(self, boxes):
        new_boxes = list()
        for box in boxes:
            if box.id == self.box_id:
                new_pos = rotate_polygon([(self.pos[0], self.pos[1] -80)], self.rotation, self.pos[0], self.pos[1])[0]
                box.pos = (new_pos[0], new_pos[1])
            new_boxes.append(box)
        return  new_boxes

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
                (x - self.separation, y - 80),
            ]),
            np.array([
                (x + self.separation, y - 15),
                (x + self.separation + 6, y - 15),
                (x + self.separation, y - 80),
            ])
        ]
        for points in forms:
            b = rotate_polygon(points, self.rotation, x, y)
            cv2.polylines(frame, [b], True, (128, 0, 128))
            cv2.fillPoly(frame, [b], (128, 0, 128))
        return frame
