import threading
import time
from queue import Empty, Queue
from typing import List

import bluepy
import cv2
import numpy as np
from PySimpleGUI import Multiline

from cli import output_message
from opencv.agent.agent import Agent, State
from opencv.agent.pheromone import Pheromone
from opencv.agent.pheromone import __remove_pheromone as remove_pheromone
from opencv.agent.pheromone import __upt_pheromone as upt_pheromone
from opencv.ble.config import find_ant
from opencv.box import Box
from opencv.forms.borders import crop_frame, get_rect_borders
from opencv.forms.color import GREEN_CONF, YELLOW_CONF, ColorFilter
from opencv.forms.triangle import Triangle, get_triangle
from opencv.wall import Wall


class VideoCapture:
    """ buffer-less VideoCapture """

    def __init__(self, name, auto, focus):
        self.cap = cv2.VideoCapture(name)
        if self.cap.isOpened():
            self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)  # float
            self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, auto)
        self.cap.set(cv2.CAP_PROP_FOCUS, focus)
        self.queue = Queue()
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
                except Empty:
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


def callback():
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

    res: object = cv2.bitwise_and(frame, frame)
    contours, _ = cv2.findContours(
        mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return res, mask


def check_for_borders(video):
    """ ask for borders """
    frame = video.read()
    borders = get_rect_borders(frame)
    return borders


DEFAULT_COLORS: List[ColorFilter] = [GREEN_CONF, YELLOW_CONF]


class EnvProcess:
    """ buffer-less VideoCapture """
    # pylint: disable=too-many-instance-attributes
    unknown_triangles: List[Triangle]
    video: VideoCapture
    ants: List[Agent]
    possible_colors: List[ColorFilter]
    borders: List[tuple]
    max_ants: int
    output: Multiline
    started: bool
    queue: Queue
    looking: bool
    pheromones: list
    run: bool
    thread: threading.Thread
    boxes: List[Box]
    walls: List[Wall]
    config_zone: list
    possible_ants: list

    def __init__(self, name, auto, focus, config):

        if config['possible_colors'] is None:
            possible_colors = DEFAULT_COLORS
        else:
            possible_colors = config['possible_colors']
        self.possible_ants = config["ants"]
        self.queue = Queue()
        self.video = VideoCapture(name, auto, focus)
        self.ants: List[Agent] = list()
        self.unknown_triangles: List[Triangle] = list()
        self.possible_colors = possible_colors
        self.max_ants = config['max_ants']
        self.borders: List[tuple] = list()
        self.looking = False
        self.started = False
        self.pheromones: List[Pheromone] = list()
        self.run = False
        self.config_zone = None
        self.boxes = list()
        self.boxes.append(Box((150, 36), 0, None, 3))
        self.walls = list()

    def start_thread(self, main_queue: Queue):
        ''' statr a thread '''
        self.thread = threading.Thread(target=self._gen, args=[main_queue])
        main_queue.put(output_message("Process started", "info"))
        self.thread.daemon = True
        self.started = True
        self.thread.start()

    def _gen(self, main_queue):
        """ Main """

        while True:
            if self.run:
                frame = self.video.read()
                self.put_on_queue(frame)
                main_queue.put(output_message("Searching for borders", "info"))
                self.update_pheromones()
                while len(self.borders) != 2:
                    self.borders = check_for_borders(self.video)[0]

                main_queue.put(output_message(
                    "Setting config zone (" +
                    str(self.borders[1][0] + 150) + ", "
                    + str(
                        self.borders[0][1] + 250) + ")",
                    "info"))

                self.config_zone = [
                    (0, 0),
                    (max(self.borders[0][0], self.borders[1][0]),
                     max(self.borders[0][1],
                         self.borders[1][1]))]
                main_queue.put(output_message("Looking for ants", "info"))
                frame = self.video.read()
                cropped = crop_frame(frame, self.borders)
                if len(self.ants) != self.max_ants and not self.looking:
                    self.looking = True
                    threading.Timer(0, function=self.look_for_new_ants, args=[
                        cropped, main_queue]).start()
                while True:
                    frame = self.video.read()
                    cropped = crop_frame(frame, self.borders)

                    self.put_on_queue(frame)

                    if not self.run:
                        break
            else:
                frame = self.video.read()
                self.put_on_queue(frame)

    def read(self):
        """ Return a frame """
        return self.queue.get()

    def look_for_new_ants(self, frame, main_queue):
        ''' look_for_new_ants '''
        color: ColorFilter
        for color in self.possible_colors:
            triangle = get_triangle(frame, color)
            if triangle.is_valid():
                if is_inside_rect(triangle.center, self.config_zone):
                    main_queue.put(output_message(
                        "Possible agent added " + color, "info"))
                    new_ant: Agent
                    new_ant = find_ant(self.ants, color, self.possible_ants)
                    self.possible_colors.remove(color)
                    if new_ant is not None and new_ant.connected:
                        main_queue.put(output_message(
                            "New agent added " + new_ant.color, "info"))
                        self.ants.insert(0, new_ant)
                        self.update_agent(
                            new_ant, main_queue)
                    else:
                        self.possible_colors.append(color)
        frame = self.video.read()
        cropped = crop_frame(frame, self.borders)
        if len(self.ants) != self.max_ants:
            self.looking = True
            threading.Timer(2, function=self.look_for_new_ants,
                            args=[cropped, main_queue]).start()
        else:
            self.looking = False

    def update_agent(self, agent, main_queue):
        ''' update_agent '''

        time_since_last_update = (time.time() - agent.last_update) * 1000
        frame = self.video.read()
        cropped = crop_frame(frame, self.borders)
        triangle = get_triangle(cropped, agent.color)
        try:
            if triangle.is_valid():
                if agent.is_leader and agent.state == State.waiting_for_box:
                    agent.destination = self.boxes[0].pos
                    agent.state = State.going_to_box
                    agent.send_box_data(self.boxes[0])
                agent.update(triangle,
                             time_since_last_update,
                             self.pheromones, self.walls)
                self.boxes = agent.claw.update(agent.con.readCharacteristic(
                    agent.chars.claw), self.boxes, agent, self.ants)
                for event in agent.com_queue:
                    if event[0] == 33:
                        for ant in self.ants:
                            if ant.color != agent.color:
                                ant.send_help_call(agent.triangle.center)
                agent.com_queue.clear()
            pheromone = agent.pheromones.get_nowait()
            if pheromone is not None:
                self.pheromones.append(pheromone)

        except bluepy.btle.BTLEDisconnectError:
            main_queue.put(output_message(
                f"Agent {agent.color} got disconnected. Trying to reconnect", "error"))
            agent.con.disconnect()
        except bluepy.btle.BTLEGattError:
            main_queue.put(output_message(
                f"Agent {agent.color} gatt error", "error"))
        except bluepy.btle.BTLEInternalError:
            main_queue.put(output_message(
                f"Agent {agent.color} BTLEInternalError", "error"))
        except Empty:
            pass
        threading.Timer(0, function=self.update_agent, args=[
                        agent, main_queue]).start()

    def draw_borders(self, frame):
        ''' draw_borders '''
        if len(self.borders) == 2:
            cv2.rectangle(
                frame, self.borders[0], self.borders[1], 200)
        return frame

    def draw_config(self, frame):
        ''' draw_config '''
        if self.config_zone is not None and len(self.config_zone) == 2:
            cv2.rectangle(
                frame, self.config_zone[0], self.config_zone[1], 200)
        return frame

    def put_on_queue(self, frame):
        ''' put_on_queue '''

        if not self.queue.empty():
            try:
                self.queue.get_nowait()  # discard previous (unprocessed) frame
            except Empty:
                pass
        self.queue.put(frame)

    def draw_xy(self, frame, x, y):
        ''' draw_xy '''
        if len(self.borders) == 2:
            frame = cv2.putText(frame, f"( {x}, {y} )", (min(self.borders[0][0], self.borders[1][0]) - 50, 50), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                                (140, 25, 78))
        return frame

    def draw_pheromones(self, frame):
        ''' draw_pheromones '''
        for pheromone in self.pheromones:
            frame = cv2.circle(frame, (pheromone.x + min(self.borders[1][0], self.borders[0][0]),
                                       pheromone.y + min(self.borders[1][1], self.borders[0][1])),
                               pheromone.intense, (255, 140, 20))

        return frame

    def update_pheromones(self):
        ''' update_pheromones '''
        self.pheromones = list(map(upt_pheromone, self.pheromones))
        self.pheromones = list(filter(remove_pheromone, self.pheromones))

        threading.Timer(60, function=self.update_pheromones).start()
