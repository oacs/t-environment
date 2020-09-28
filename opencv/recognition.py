import random

import cv2  # Not actually necessary if you just want to create an image.
import numpy as np

from opencv.forms.utils import distance


class Recognition:

    def __init__(self, screen_dimension, scan_radius=190):
        self.area = np.zeros((screen_dimension[1], screen_dimension[0], 3), np.uint8)
        # self.area = cv2.rectangle(self.area, (0, 0), (180, 350), (254, 254, 254))
        self.scan_radius = scan_radius
        self.screen_dimension = screen_dimension
        self.new_pos = (-1,-1)

    def update_vision(self, pos):
        self.area = cv2.circle(self.area, pos, self.scan_radius, (254, 254, 254), -1)

    def get_close_unknown_position(self, pos ):
        if self.new_pos[0] == -1  or  distance(pos, self.new_pos) < 30:
            new_pos = (-1, -1)
            min_dist = 9999
            contours, _ = cv2.findContours(
                cv2.cvtColor(self.area, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)
            for cnt in contours:
                area = cv2.contourArea(cnt)
                approx = cv2.convexHull(cnt)
                max_rand = len(cnt) -1
                rand = random.randint(0, max_rand)
                x = cnt[rand][0][0]
                y = cnt[rand][0][1]
                dist = min(distance(pos, (x, y)), min_dist)
                if dist < min_dist:
                    new_pos = (x, y)
                    min_dist = dist
            self.new_pos = new_pos
        return self.new_pos
