import numpy as np
import cv2

from opencv.main import get_approx_xy

FONT = cv2.FONT_HERSHEY_SIMPLEX


def get_rect_borders(frame):
    """ Returns an array of borders(tuples with x and y) """
    # Turn no HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    config = {
        "low_hue": 0,
        "max_hue": 255,
        "low_sat": 0,
        "max_sat": 140,
        "low_bri": 0,
        "max_bri": 100,
        "arc": 8,
        # Ucab
        # "min_area": 400,
        # "max_area": 600,
        # Maria's house
        "min_area": 900,
        "max_area": 1400,
    }
    # min_x = 200
    # max_x = 500
    # min_y = 100
    # max_y = 400

    # Define min and max values
    lower_hsv = np.array(
        [config["low_hue"], config["low_sat"], config["low_bri"]])
    higher_hsv = np.array(
        [config["max_hue"], config["max_sat"], config["max_bri"]])
    # Create mask
    mask = cv2.inRange(hsv, lower_hsv, higher_hsv)
    # Blur image

    mask = cv2.GaussianBlur(mask, (5, 5), 1)

    contours, _ = cv2.findContours(
        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    rect_borders = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if config["min_area"] < area < config["max_area"]:
            approx = cv2.approxPolyDP(
                cnt, (config["arc"] / 100) * cv2.arcLength(cnt, True), True)
            pos = get_approx_xy(approx, area, mask)
            if len(approx) == 4:
                rect_borders.append(pos)
    # cv2.imshow('mas02k', mask)
    # cv2.imshow('frame', frame)

    return rect_borders


def crop_frame(frame, borders):
    min_x = min(borders[0][0], borders[1][0])
    max_x = max(borders[0][0], borders[1][0])
    min_y = min(borders[0][1], borders[1][1])
    max_y = max(borders[0][1], borders[1][1])
    return frame[min_y:max_y, min_x:max_x]
