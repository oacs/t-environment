from typing import Tuple

import cv2

from opencv.forms.utils import line_rect, Segment, Point, distance


class Wall:
    pos: Tuple[tuple]
    id: int

    def __init__(self, pnt1, pnt2, identifier):
        self.pos = (pnt1, pnt2)
        self.id = identifier

    def draw(self, frame, offset: Tuple[int] = (0,0)):
        color = (30, 50, 30)
        cv2.rectangle(frame, tuple(map(sum, zip(self.pos[0], offset))), tuple(map(sum, zip(self.pos[1], offset))), color, -1)
        return frame

    def get_intersection(self, line_points):
        return self.line_rect(Segment(Point(arr=line_points[0]), Point(arr=line_points[1])))

    def get_all_points(self):
        return [
            Point(min(self.pos[0][0], self.pos[1][0]), min(self.pos[0][1], self.pos[1][1])),
            Point(min(self.pos[0][0], self.pos[1][0]), max(self.pos[0][1], self.pos[1][1])),
            Point(max(self.pos[0][0], self.pos[1][0]), max(self.pos[0][1], self.pos[1][1])),
            Point(max(self.pos[0][0], self.pos[1][0]), min(self.pos[0][1], self.pos[1][1])),
        ]

    def get_all_segments(self):
        points = self.get_all_points()
        return [
            Segment(points[0], points[1]),
            Segment(points[3], points[2]),
            Segment(points[0], points[3]),
            Segment(points[1], points[2])
        ]

    def line_rect(self, segment: Segment):
        # check if the line has hit any of the rectangle's sides
        # uses the Line/Line function below
        rect_segments = self.get_all_segments()

        hit_left, pnt_left = segment.intercepts(rect_segments[0])
        hit_right, pnt_right = segment.intercepts(rect_segments[1])
        hit_top, pnt_top = segment.intercepts(rect_segments[2])
        hit_bottom, pnt_bottom = segment.intercepts(rect_segments[3])

        intercep_point = None
        if hit_left:
            if intercep_point is None:
                intercep_point = pnt_left

        if hit_right:
            if intercep_point is None:
                intercep_point = pnt_right
            else:
                right_distance = distance(segment.end_point.to_tuple(), pnt_right)
                if right_distance == min(right_distance, distance(segment.end_point.to_tuple(), intercep_point)):
                    intercep_point = pnt_right
        if hit_top:
            if intercep_point is None:
                intercep_point = pnt_top
            else:
                top_distance = distance(segment.end_point.to_tuple(), pnt_top)
                if top_distance == min(top_distance, distance(segment.end_point.to_tuple(), intercep_point)):
                    intercep_point = pnt_top

        if hit_bottom:
            if intercep_point is None:
                intercep_point = pnt_bottom
            else:
                bottom_distance = distance(segment.end_point.to_tuple(), pnt_bottom)
                if bottom_distance == min(bottom_distance, distance(segment.end_point.to_tuple(), intercep_point)):
                    intercep_point = pnt_bottom

        # if ANY of the above are true, the line
        # has hit the rectangle
        if hit_left or hit_right or hit_top or hit_bottom:
            return True, (int(intercep_point[0]), int(intercep_point[1]))

        return False, (-1, -1)
