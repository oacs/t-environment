""" Contains the color code """
from enum import Enum
import cv2
import numpy as np


class Colors(Enum):
    """ Colors enums """
    red = "R"
    green = "G"
    blue = "B"
    purple = "P"
    yellow = "Y"
    unset = "unset"


class ColorFilter:
    """ Values for color filter """
    low_hsb = np.array(0)
    max_hsb = np.array(0)
    arc: int
    min_area: int
    max_area: int
    color: Colors

    def __init__(self, color,  low_hue, max_hue, low_sat, max_sat, low_bri, max_bri, arc, min_area, max_area):
        self.low_hsb = np.array([low_hue, low_sat, low_bri])
        self.max_hsb = np.array([max_hue, max_sat, max_bri])
        self.arc = arc
        self.min_area = min_area
        self.max_area = max_area
        self.color = color

    def get_mask(self, frame, debug=False):
        """ Get the mask for the color """
        # Define min and max values
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Create mask
        mask = cv2.inRange(hsv, self.low_hsb, self.max_hsb)
        if debug:
            cv2.imshow(self.color.value + " mask", mask)
        return mask


GREEN_CONF = ColorFilter(Colors.green, low_hue=35, max_hue=75,
                         low_sat=50, max_sat=190,
                         low_bri=90, max_bri=160,
                         arc=8,
                         min_area=190, max_area=900
                         )

PURPLE_CONF = ColorFilter(Colors.purple, low_hue=90, max_hue=180,
                          low_sat=50, max_sat=130,
                          low_bri=50, max_bri=140,
                          arc=8,
                          min_area=190, max_area=900
                          )
YELLOW_CONF = ColorFilter(Colors.yellow, low_hue=0, max_hue=50,
                          low_sat=50, max_sat=255,
                          low_bri=140, max_bri=210,
                          arc=8,
                          min_area=190, max_area=900
                          )
