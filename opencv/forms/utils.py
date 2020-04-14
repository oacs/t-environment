import math
from typing import List, Tuple

import numpy as np
from cv2 import putText, polylines, FONT_HERSHEY_COMPLEX
import math


FONT = FONT_HERSHEY_COMPLEX


def approx_xy(approx, area: object, res: object) -> tuple:
    """
        Calculate the approximate position (x, y) of an object
    """
    polylines(res, approx, True, 255, 5)
    x: int = approx.ravel()[0]
    y: int = approx.ravel()[1]
    # putText(res, "Rectangle " + str(area),
    #         (x, y), FONT, 1, 255)
    return x, y


def cart2pol(x, y):
    if x == 0:
        if y > 0:
            theta = 90
        else:
            theta = -90
    else:
        theta = np.arctan2(y, x)
    rho = np.hypot(x, y)
    return theta, rho


def pol2cart(theta, rho):
    x = rho * np.cos(np.deg2rad(theta))
    y = rho * np.sin(np.deg2rad(theta))
    return x, y


def line_line(points: List[tuple]):
    # calculate    the    direction    of    the    lines
    X1: int = points[0][0]
    X2: int = points[1][0]
    X3: int = points[2][0]
    X4: int = points[3][0]
    Y1: int = points[0][1]
    Y2: int = points[1][1]
    Y3: int = points[2][1]
    Y4: int = points[3][1]
    I1: int = [min(X1, X2), max(X1, X2)]
    I2: int = [min(X3, X4), max(X3, X4)]

    Ia = [max(min(X1, X2), min(X3, X4)),
          min(max(X1, X2), max(X3, X4))]

    if (max(X1, X2) < min(X3, X4)):
        return False, (-1, -1)  # There is no mutual abcisses

    A1: float = (Y1 - Y2) / (X1 - X2)  # Pay attention to not dividing by zero
    A2: float = (Y3 - Y4) / (X3 - X4)  # Pay attention to not dividing by zero
    b1 = Y1 - A1 * X1  # = Y2 - A1 * X2
    b2 = Y3 - A2 * X3  # = Y4 - A2 * X4

    if (A1 == A2):
        return False, (-1, -1)  # Parallel segments

    # Ya = A1 * Xa + b1
    # Ya = A2 * Xa + b2
    # A1 * Xa + b1 = A2 * Xa + b2
    # Once again, pay attention to not dividing by zero
    Xa = (b2 - b1) / (A1 - A2)

    if ((Xa < max(min(X1, X2), min(X3, X4))) or
            (Xa > min(max(X1, X2), max(X3, X4)))):
        return False  # intersection is out of bound
    else:
        return True
    #     return True, (intersection_x, intersection_y)
    #
    # return False, (-1, -1)


def line_rect(line_points, rect_points: List[tuple]):
    # check if the line has hit any of the rectangle's sides
    # uses the Line/Line function below
    hit_left, pnt_left = line_line(
        [line_points[0], line_points[1], rect_points[0], rect_points[1]])
    hit_right, pnt_right = line_line(
        [line_points[0], line_points[1], rect_points[3], rect_points[2]])
    hit_top, pnt_top = line_line(
        [line_points[0], line_points[1], rect_points[0], rect_points[3]])
    hit_bottom, pnt_bottom = line_line(
        [line_points[0], line_points[1], rect_points[1], rect_points[2]])

    possible_point = None
    if hit_left:
        if possible_point is None:
            possible_point = pnt_left

    if hit_right:
        if possible_point is None:
            possible_point = pnt_right
        else:
            right_distance = distance(line_points[1], pnt_right)
            if right_distance == min(right_distance, distance(line_points[1], possible_point)):
                possible_point = pnt_right
    if hit_top:
        if possible_point is None:
            possible_point = pnt_top
        else:
            top_distance = distance(line_points[1], pnt_top)
            if top_distance == min(top_distance, distance(line_points[1], possible_point)):
                possible_point = pnt_top

    if hit_bottom:
        if possible_point is None:
            possible_point = pnt_bottom
        else:
            bottom_distance = distance(line_points[1], pnt_bottom)
            if bottom_distance == min(bottom_distance, distance(line_points[1], possible_point)):
                possible_point = pnt_bottom

    # if ANY of the above are true, the line
    # has hit the rectangle
    if hit_left or hit_right or hit_top or hit_bottom:
        return True, (int(possible_point[0]), int(possible_point[1]))

    return False, (-1, -1)


def rotate_polygon(points, degrees, cx, cy):
    """ Rotate polygon the given angle about its center. """
    theta = math.radians(degrees)  # Convert angle to radians
    cos_ang, sin_ang = math.cos(theta), math.sin(theta)

    # find center point of Polygon to use as pivot

    new_points = []
    for p in points:
        x, y = p[0], p[1]
        tx, ty = x - cx, y - cy
        new_x = (tx * cos_ang + ty * sin_ang) + cx
        new_y = (-tx * sin_ang + ty * cos_ang) + cy
        new_points.append((int(new_x), int(new_y)))
    return np.array(new_points)


def slope(pt1, pt2):
    slope_value = 0
    try:
        slope_value = (pt1[1] - pt2[1]) / (pt1[0] - pt2[0])
    except ZeroDivisionError:
        slope_value = None
    return slope_value


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
    # print(dx, dy, pnt, m, pnt[0] < dx, pnt[1] < dy)
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


class Point:
    x: int
    y: int

    def __init__(self, x: int = None, y: int = None, arr: Tuple[int] = None):
        if x is not None and y is not None:
            self.x = int(x)
            self.y = int(y)
        elif arr is not None:
            self.x = int(arr[0])
            self.y = int(arr[1])

    def to_tuple(self):
        return self.x, self.y


class Segment:
    start_point: Point
    end_point: Point

    slope: float

    def __init__(self, start: Point, end: Point):
        self.start_point = start
        self.end_point = end
        self.slope = self.calc_slope()

    def length(self):
        return distance(self.start_point.to_tuple(), self.end_point.to_tuple())

    def calc_slope(self):
        return slope(self.start_point.to_tuple(), self.end_point.to_tuple())

    def intercepts(self, segment):

        self.start_point.x
        self.start_point.y
        self.end_point.x
        self.end_point.y
        segment.start_point.x
        segment.start_point.y
        segment.end_point.x
        segment.end_point.y

        s1_x = self.end_point.x - self.start_point.x
        s1_y = self.end_point.y - self.start_point.y
        s2_x = segment.end_point.x - segment.start_point.x
        s2_y = segment.end_point.y - segment.start_point.y
        ds = (-s2_x * s1_y + s1_x * s2_y)
        dt = (-s2_x * s1_y + s1_x * s2_y)

        if ds == 0 or dt == 0:
            return False, (-1, -1)

        s = (-s1_y * (self.start_point.x - segment.start_point.x) +
             s1_x * (self.start_point.y - segment.start_point.y)) / ds
        t = (s2_x * (self.start_point.y - segment.start_point.y) -
             s2_y * (self.start_point.x - segment.start_point.x)) / dt

        if 0 <= s <= 1 and 0 <= t <= 1:
            i_x = self.start_point.x + (t * s1_x)
            i_y = self.start_point.y + (t * s1_y)
            return True, (i_x, i_y)

        else:
            return False, (-1, -1)
