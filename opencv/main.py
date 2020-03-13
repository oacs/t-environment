import time
import struct
import queue
import threading
from typing import List, Any

import bluepy
import cv2
import numpy as np
from PySimpleGUI import Window, Multiline

from cli import send_info_message, output_message
from opencv.ble.config import find_ant
from opencv.forms.borders import get_rect_borders, crop_frame
from opencv.forms.triangle import get_triangle, distance, Triangle
from opencv.forms.color import GREEN_CONF, Colors, PURPLE_CONF, ColorFilter
from opencv.agent.agent import Agent
from opencv.forms.utils import approx_xy


class VideoCapture:
    """ buffer-less VideoCapture """

    def __init__(self, name, auto, focus):
        self.cap = cv2.VideoCapture(name)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, auto)
        self.cap.set(cv2.CAP_PROP_FOCUS, focus)
        self.queue = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

    def _reader(self):
        """ read frames as soon as they are available, keeping only most recent one """
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.queue.empty():
                try:
                    self.queue.get_nowait()  # discard previous (unprocessed) frame
                except queue.Empty:
                    pass
            self.queue.put(frame)

    def read(self):
        """ Return a frame """
        return self.queue.get()


def is_inside_rect(point, rect):
    """ Check if a point is inside a rect"""
    return rect[0][1] <= point[1] <= rect[1][1] and rect[0][0] <= point[0] <= rect[1][0]


# from kinnect import capture
FONT = cv2.FONT_HERSHEY_COMPLEX


# app = Flask(__name__)
# VIDEO = VideoCapture(0, 0, 4)


def create_trackbar():
    low_hue = 0
    high_hue = 255
    low_sat = 0
    high_sat = 255
    low_bri = 0
    high_bri = 255
    blur = 0
    """ Create Trackbar window """
    cv2.namedWindow('image')

    cv2.createTrackbar('low_hue', 'image', low_hue, 255, callback)
    cv2.createTrackbar('high_hue', 'image', high_hue, 255, callback)

    cv2.createTrackbar('low_sat', 'image', low_sat, 255, callback)

    cv2.createTrackbar('high_sat', 'image', high_sat, 255, callback)

    cv2.createTrackbar('low_bri', 'image', low_bri, 255, callback)
    cv2.createTrackbar('high_bri', 'image', high_bri, 255, callback)

    cv2.createTrackbar('blur', 'image', blur, 255, callback)


def trackbars():
    """ Get trackbar data """
    # get trackbar positions
    t_low_hue = cv2.getTrackbarPos('low_hue', 'image')
    t_high_hue = cv2.getTrackbarPos('high_hue', 'image')
    t_low_sat = cv2.getTrackbarPos('low_sat', 'image')
    t_high_sat = cv2.getTrackbarPos('high_sat', 'image')
    t_low_bri = cv2.getTrackbarPos('low_bri', 'image')
    t_high_bri = cv2.getTrackbarPos('high_bri', 'image')
    t_blur = cv2.getTrackbarPos('blur', 'image')
    t_arc = cv2.getTrackbarPos('arc', 'image')

    return [t_low_hue, t_low_sat, t_low_bri], [t_high_hue, t_high_sat, t_high_bri], t_blur, t_arc


def callback(x):
    """ Do nothing """
    pass


def test_mask(frame):
    """ Get mask for trackbar """
    low, high, blur, arc = trackbars()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_hsv = np.array(low)
    higher_hsv = np.array(high)
    mask = cv2.inRange(hsv, lower_hsv,
                       higher_hsv)
    for i in range(blur):
        mask = cv2.GaussianBlur(mask, (5, 5), 1)

    # mask = cv2.inRange(hsv, lower_blue, upper_blue)
    res = cv2.bitwise_and(frame, frame)
    contours, _ = cv2.findContours(
        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 200 < area < 600:
            # if area < 10 or area > 100:
            #     break
            approx = cv2.approxPolyDP(
                cnt, (arc / 100) * cv2.arcLength(cnt, True), True)
            # cv2.drawContours(res, [approx], 0, (255), 5)
            pos = approx_xy(approx, area, res)
    return res, mask


def check_for_borders(video):
    """ ask for borders """
    frame = video.read()
    borders = get_rect_borders(frame)
    return borders


DEFAULT_COLORS = [GREEN_CONF, PURPLE_CONF]


class EnvProcess:
    """ buffer-less VideoCapture """
    unknown_triangles: List[Triangle]
    video: VideoCapture
    ants: List[Agent]
    possible_colors: List[ColorFilter]
    borders: List[tuple]
    max_ants: int
    output: Multiline
    started: bool
    queue: queue.Queue
    looking: bool

    def __init__(self, name, auto, focus, possible_colors=DEFAULT_COLORS, max_ants=2):
        self.queue = queue.Queue()
        self.video = VideoCapture(name, auto, focus)
        self.ants = list()
        self.unknown_triangles = list()
        self.possible_colors = possible_colors
        self.max_ants = max_ants
        self.borders = list()
        self.looking = False
        self.started = False

    def start_thread(self, main_queue: queue.Queue):
        t = threading.Thread(target=self._gen, args=[main_queue])
        main_queue.put(output_message("Process started", "info"))
        t.daemon = True
        self.started = True
        t.start()

    def _gen(self, main_queue):
        """ Main """

        frame = self.video.read()
        self.put_on_queue(frame)
        main_queue.put(output_message("Searching for borders", "info"))
        while len(self.borders) != 2:
            self.borders = check_for_borders(self.video)

        main_queue.put(output_message(
            "Setting config zone (" + str(self.borders[1][0] + 150) + ", " + str(self.borders[1][1] + 250) + ")",
            "info"))
        self.config_zone = [(0, 0), (self.borders[1][0] + 150, self.borders[1][1] + 250)]
        main_queue.put(output_message("Looking for ants", "info"))

        while True:
            frame = self.video.read()
            cropped = crop_frame(frame, self.borders)

            if len(self.ants) != self.max_ants and not self.looking:
                threading.Thread(target=self.look_for_new_ants, args=[cropped, main_queue]).start()
            self.put_on_queue(frame)

    def read(self):
        """ Return a frame """
        return self.queue.get()

    def look_for_new_ants(self, frame, main_queue):
        self.looking = True
        # print("Looking")
        color: ColorFilter
        for color in self.possible_colors:
            triangle = get_triangle(frame, color.color.value)
            if triangle.is_valid():
                if is_inside_rect(triangle.center, self.config_zone):
                    print(triangle.position)
                    self.possible_colors.remove(color)
                    new_ant: Agent
                    new_ant = find_ant(self.ants, color)
                    if new_ant is not None and new_ant.connected:
                        main_queue.put(output_message("New agent added " + new_ant.color, "info"))
                        self.ants.insert(0, new_ant)
                        self.update_agent(new_ant, new_ant.color == "P", main_queue)
                    else:
                        self.possible_colors.append(color)
        self.looking = False

    def update_agent(self, agent, following, main_queue):
        try:
            time_since_last_update = (time.time() - agent.last_update) * 1000
            frame = self.video.read()
            cropped = crop_frame(frame, self.borders)
            triangle = get_triangle(cropped, agent.color)
            if triangle.is_valid():
                if following:
                    dest = get_triangle(cropped, "G")
                    if dest.is_valid():
                        agent.destination = dest.center
                        agent.send_dist(dest.center)
                agent.update(cropped, triangle,
                             time_since_last_update)
        except bluepy.btle.BTLEDisconnectError:
            main_queue.put(output_message(f"Agent {agent.color} got disconnected. Trying to reconnect", "error"))
            agent.con.disconnect()
            # time.sleep(60)
            # agent.connect()
            # main_queue.put(output_message(f"Agent {agent.color} got reconnected.", "info"))

        except bluepy.btle.BTLEGattError:
            main_queue.put(output_message(f"Agent {agent.color} gatt error", "error"))
        except bluepy.btle.BTLEInternalError:
            main_queue.put(output_message(f"Agent {agent.color} BTLEInternalError", "error"))
        threading.Timer(0.2, function=self.update_agent, args=[agent, following, main_queue]).start()

    def draw_borders(self, frame):
        if len(self.borders) == 2:
            cv2.rectangle(
                frame, self.borders[0], self.borders[1], 200)
        return frame

    def put_on_queue(self, frame):
        if not self.queue.empty():
            try:
                self.queue.get_nowait()  # discard previous (unprocessed) frame
            except queue.Empty:
                pass
        # print("gen")
        self.queue.put(frame)

    def draw_xy(self, frame, x, y):
        if len(self.borders) == 2:
            frame = cv2.putText(frame, f"( {x}, {y} )", (self.borders[0][0] - 50, 50), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                                (140, 25, 78))
        return frame
