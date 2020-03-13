import math

from cv2 import putText, polylines, FONT_HERSHEY_COMPLEX, moments
import numpy as np

FONT = FONT_HERSHEY_COMPLEX


def approx_xy(approx, area: object, res: object) -> tuple:
    """
        Calculate the approximate position (x, y) of an object
    """
    polylines(res, approx, True, 255, 5)
    x: int = approx.ravel()[0]
    y: int = approx.ravel()[1]
    putText(res, "Rectangle " + str(area),
            (x, y), FONT, 1, 255)
    return x, y


def cart2pol(x, y):
    theta = np.arctan2(y, x)
    rho = np.hypot(x, y)
    return theta, rho


def pol2cart(theta, rho):
    x = rho * np.cos(theta)
    y = rho * np.sin(theta)
    return x, y


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
