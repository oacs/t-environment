from enum import Enum
import cv2
import numpy as np
from opencv.forms.utils import distance, cart2pol, rotate_polygon
from typing import List

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
    status: bytes
    box_id: int
    agent: str
    leader: str
    leader_pos: tuple

    def __init__(self, pos, agent):
        self.state = EnumClawState.open
        self.pos = pos
        self.separation = 20
        self.rotation = 0
        self.status = b'\x02'
        self.agent = agent
        self.leader = ""
        self.leader_pos = (0, 0)

    def update(self, status, boxes, ants: List):

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
                if distance_to_box < 80:
                    self.status = b'\x04'
                    self.box_id = box.id
                    if box.leader is None:
                        box.leader = self.agent
                    else:
                        self.leader = box.leader
                        for ant in ants:
                            if ant.color == box.leader:
                                self.leader_pos = ant.triangle.center
                    break
            return boxes

        if self.status == b'\x04':
            boxes = self.update_box_pos(boxes)
        return boxes

    def update_box_pos(self, boxes):
        new_boxes = list()
        for box in boxes:
            if box.id == self.box_id :
                if box.leader == self.agent:
                    new_pos = rotate_polygon([(self.pos[0], self.pos[1] - 80)], self.rotation, self.pos[0], self.pos[1])[0]
                    box.pos = (new_pos[0], new_pos[1])
                else:
                    self.leader_pos = box.pos
            new_boxes.append(box)
        return new_boxes

    def draw_claw(self, frame: object, ants: List, offset: tuple = (0, 0)) -> object:
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
        try:
            if self.leader != self.agent and self.leader_pos is not (0, 0):
                for ant in ants:
                    if ant.color == self.agent:
                        self.rotation = cart2pol(ant.triangle.center[0] -self.leader_pos[0],ant.triangle.center[1] -self.leader_pos[1] )[0] *180 /3.1416 -90
        except AttributeError:
            print()

        for points in forms:
            b = rotate_polygon(points, -self.rotation, x, y)
            cv2.polylines(frame, [b], True, (128, 0, 128))
            cv2.fillPoly(frame, [b], (128, 0, 128))
        return frame
