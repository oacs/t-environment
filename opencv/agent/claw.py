''' claw module '''
from enum import Enum
from typing import List

import cv2
import numpy as np

from opencv.forms.utils import cart2pol, distance, rotate_polygon


class EnumClawState(Enum):
    """ Characteristics uuid enums """
    open = 0
    closing = 1
    closed = 2
    opening = 3


class Claw:
    ''' claw of agent '''
    # pylint: disable=too-many-instance-attributes
    state: EnumClawState
    pos: tuple
    separation: float
    rotation: float
    status: bytes
    box_id: int
    agent: str
    leader: str
    leader_pos: tuple
    length: int

    def __init__(self, pos, agent):
        self.state = EnumClawState.open
        self.pos = pos
        self.separation = 20
        self.rotation = 0
        self.status = b'\x01'
        self.agent = agent
        self.leader = ""
        self.leader_pos = (0, 0)
        self.length = 40

    def update(self, status, boxes, agent , ants: List):
        ''' update status of the claw '''
        # closed
        if (self.status == b'\x02') and (status == b'\x01'):
            self.status = b'\x01'
            self.separation -= 1
            return boxes
        elif self.status == b'\x01':
            if self.separation > 10:
                self.separation -= 1
            for box in boxes:
                distance_to_box = distance(box.pos, self.pos)
                if distance_to_box < 80:
                    self.status = b'\x04'
                    self.box_id = box.id
                    agent.con.writeCharacteristic(agent.chars.claw, b'\x04', withResponse=True)
                    agent.destination = (50, 50)
                    if box.leader is None:
                        box.leader = self.agent
                    else:
                        self.leader = box.leader
                        for ant in ants:
                            if ant.color == box.leader:
                                ant.con.writeCharacteristic(ant.chars.claw, b'\x06', withResponse=True)
                                self.leader_pos = ant.triangle.center
                    break
            return boxes

        if self.status == b'\x04':
            boxes = self.update_box_pos(boxes)
        return boxes

    def update_box_pos(self, boxes):
        ''' update box status '''
        new_boxes = list()
        for box in boxes:
            if box.id == self.box_id:
                if box.leader == self.agent:
                    new_pos = \
                        rotate_polygon(
                            [(self.pos[0], self.pos[1] - 30)],
                            self.rotation, self.pos[0], self.pos[1])[0]
                    box.pos = (new_pos[0], new_pos[1])
                else:
                    self.leader_pos = box.pos
            new_boxes.append(box)
        return new_boxes

    def draw_claw(self, frame: object, ants: List, offset: tuple = (0, 0)):
        ''' draw the claw on canvas '''
        x, y = tuple(map(sum, zip(self.pos, offset)))
        forms = [
            np.array([
                    (x - 12, y - 10),
                    (13 + x, y - 10),

                    (x, y - 5),
            ]),
            np.array([
                     (x - self.separation - 6, y - 15),
                     (x - self.separation, y - 15),
                     (x - self.separation, y - self.length),
                     ]),
            np.array([
                     (x + self.separation, y - 15),
                     (x + self.separation + 6, y - 15),
                     (x + self.separation, y - self.length),
                     ])
        ]
        try:
            if self.leader != self.agent and self.leader_pos != (0, 0):
                for ant in ants:
                    if ant.color == self.agent:
                        fixed_x = ant.triangle.center[0] - self.leader_pos[0]
                        fixed_y = ant.triangle.center[1] - self.leader_pos[1]
                        self.rotation = cart2pol(fixed_x, fixed_y
                                                 )[0]
                        self.rotation *= 180 / 3.1416 - 90
        except AttributeError:
            print()

        for points in forms:
            b = rotate_polygon(points, -self.rotation, x, y)
            cv2.polylines(frame, [b], True, (128, 0, 128))
            cv2.fillPoly(frame, [b], (128, 0, 128))
        return frame
