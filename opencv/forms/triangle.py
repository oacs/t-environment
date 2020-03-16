""" Triangle module """
import math  # 'math' needed for 'sqrt'
import cv2
from opencv.forms.color import PURPLE_CONF, Colors, GREEN_CONF

FONT = cv2.FONT_HERSHEY_SIMPLEX
width = 103
height = 73


def slope(pt1, pt2):
    return (pt1[1] - pt2[1]) / (pt1[0] - pt2[0])


def offset_rect(pt1, m):
    """ Calc B of y = mx + B """
    return pt1[1] - (m * pt1[0])


def delta_x_y(m, b, pnt):
    """ calc  dx for y and dy for dx on a rect """
    try:
        dx = (pnt[1] - b) / m
    except ZeroDivisionError:
        dx = pnt[1]
    dy = ((m * pnt[0]) + b)
    return dx, dy


def up_or_down(dx, dy, pnt, m):
    """  Check if one point is upper or down an rect """
    # if(dx == 0 or dy == 0):
    #     return 0
    if m > 0:
        if pnt[0] < dx and pnt[1] > dy:
            return 1
        elif pnt[0] > dx and pnt[1] < dy:
            return -1
    else:
        if (pnt[0] < dx) and (pnt[1] < dy):
            return -1
        elif pnt[0] > dx and pnt[1] > dy:
            return 1
    print(dx, dy, pnt, m, pnt[0] < dx, pnt[1] < dy)
    return 0


def is_clockwise(m, orientation, top, pnt):
    """ check in which direction is need it to turn """
    if m < 0:
        if top[0] < pnt[0] and top[1] > pnt[1]:
            return -1 * orientation
        elif top[0] > pnt[0] and top[1] < pnt[1]:
            return 1 * orientation
    else:
        if top[0] < pnt[0] and top[1] < pnt[1]:
            return -1 * orientation
        elif top[0] > pnt[0] and top[1] > pnt[1]:
            return 1 * orientation
    return 1


def distance(p0, p1):
    """ Calculate the distance in px of two points"""
    return math.sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2)


def between_pt(p0, p1):
    """ Calculate the point between two points"""
    return int((p0[0] + p1[0]) / 2), int((p0[1] + p1[1]) / 2)


class Triangle:
    """ Class for triangle found on the environment """
    contours: list
    position: tuple
    center: tuple
    top: tuple
    color: Colors

    def __init__(self, contours=None, position=(-1, -1), color=None):
        self.contours = contours
        self.position = position
        if self.is_valid():
            self.top, self.center = self.calc_top_center()
        self.color = color

    def calc_top_center(self):
        """ Return the center and the top point of the triangle """
        distance1 = distance(self.contours[0][0], self.contours[1][0])
        distance2 = distance(self.contours[1][0], self.contours[2][0])
        distance3 = distance(self.contours[0][0], self.contours[2][0])
        minor = min(distance1, distance2, distance3)
        center = top = (-1, -1)

        if minor == distance1:
            top = self.contours[2][0]
            center = between_pt(self.contours[0][0], self.contours[1][0])
        elif minor == distance2:
            top = self.contours[0][0]
            center = between_pt(self.contours[2][0], self.contours[1][0])
        elif minor == distance3:
            top = self.contours[1][0]
            center = between_pt(self.contours[0][0], self.contours[2][0])
        top = (top[0], top[1])

        return top, center

    def is_valid(self):
        """ Check if the triangle is valid """
        return self.position[0] != -1 and self.position[1] != -1

    def calc_rotation(self, pnt):
        """ Calc the rotation of the triangle with another point"""
        triangle_line = distance(self.center, self.top)
        point_line = distance(self.center, pnt)

        aux_line = distance(pnt, self.top)

        if point_line == 0 or triangle_line == 0:
            return 0
        value = math.acos((point_line ** 2 - aux_line ** 2 + triangle_line **
                           2) / (2 * point_line * triangle_line)) * 180 / math.pi

        m = slope(self.top, pnt)
        b = offset_rect(self.top, m)
        dx, dy = delta_x_y(m, b, self.center)
        orientation = up_or_down(dx, dy, self.center, m)
        return value * is_clockwise(m, orientation, self.top, pnt) * -1


def get_triangle(frame, config=Colors.purple.value, prev_pos=False):
    """ Returns an array of borders(tuples with x and y) """
    # AREA = 100
    # # Turn no HSV
    if prev_pos:
        print(prev_pos)
    #     min_crop_y = max(0, prev_pos[1]-AREA)
    #     min_crop_x = max(0, prev_pos[0]-AREA)
    #     max_crop_y = min(np.size(frame, 0)-1, prev_pos[1]+AREA)
    #     max_crop_x = min(np.size(frame, 1)-1, prev_pos[0]+AREA)
    #     print(min_crop_y, max_crop_y, min_crop_x, max_crop_x)
    #     frame = frame[min_crop_y:max_crop_y, min_crop_x: max_crop_x]
    # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    if config == Colors.purple.value:
        config = PURPLE_CONF
    elif config == Colors.green.value:
        config = GREEN_CONF
    mask = config.get_mask(frame)
    # Blur image
    # mask = cv2.GaussianBlur(mask, (5, 5), 1)
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)
    triangle = Triangle([], (-1, -1), config.color)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        approx = cv2.convexHull(cnt)
        if config.min_area < area < config.max_area:
            x = approx.ravel()[0]
            y = approx.ravel()[1]
            approx = cv2.approxPolyDP(
                cnt, (config.arc / 100) * cv2.arcLength(cnt, True), True)
            cv2.polylines(frame, approx, True, 255, 5)
            if len(approx) == 3:
                # cv2.polylines(frame, approx, True, 255, 5)
                triangle = Triangle(
                    approx, (x, y), config.color)
                # cv2.circle(mask, triangle.top, 12, 255)

    # cv2.imshow('mas02k', mask)
    # cv2.imshow('frame-triangle', frame)
    return triangle
