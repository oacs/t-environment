from cv2 import putText, polylines, FONT_HERSHEY_COMPLEX

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
