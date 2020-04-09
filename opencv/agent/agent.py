""" This module is defined for the agent object """
import logging
import math
import queue
import sys
import time
from collections import OrderedDict

from enum import Enum
from struct import unpack, pack
from typing import List
from uuid import UUID

import bluepy
import cv2
import numpy as np
from bluepy.btle import Peripheral, BTLEException

from opencv.forms.triangle import Triangle, distance
from opencv.forms.utils import FONT, rotate_polygon, cart2pol, pol2cart
from opencv.wall import Wall

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
LOGGER = logging.getLogger("agent")
SENSOR_SERVICE = UUID("218EE492-8AFB-4CA6-93B6-2D0DBF2F00FE")


class EnumChars(Enum):
    """ Characteristics uuid enums """
    group = "5ad56076-88c1-4e11-bd31-7d4f1e99f32c"
    config = "79606e8e-0b90-4ade-8c21-2a8fe1e64217"
    color = "c2a76563-3af7-4640-82be-1c841f228e6c"
    position = "19B10001-E8F2-537E-4F6C-D104768A1214"
    rotation = "cd185314-5651-4eb9-b8cd-16e035d88bc4"
    debug = "645e1252-55dd-4604-8d35-add29319725b"
    com = "a6f2eee3-d71e-4e77-a9fa-66fb946c4e96"
    dest = "403dc772-b887-44bd-9105-1215e7886112"
    pheromones = "5b3afbbc-c715-4d31-942d-e4d63bf04eae"
    distance = "f17ca917-e5af-4f0f-afab-0243fb59193c"


class Characteristics:
    """ Characteristics that agents offer to write and read """

    position: int
    config: int
    color: int
    debug: int
    com: int
    rotation: int
    dest: int
    pheromones: int

    def __init__(self, chars):
        self.pheromones = -1
        for char in chars:
            if char.uuid == EnumChars.position.value:
                self.position = char.getHandle()
                continue
            if char.uuid == EnumChars.config.value:
                self.config = char.getHandle()
                continue
            if char.uuid == EnumChars.color.value:
                self.color = char.getHandle()
                continue
            if char.uuid == EnumChars.debug.value:
                self.debug = char.getHandle()
                continue
            if char.uuid == EnumChars.com.value:
                self.com = char.getHandle()
                continue
            if char.uuid == EnumChars.rotation.value:
                self.rotation = char.getHandle()
                continue
            if char.uuid == EnumChars.dest.value:
                self.dest = char.getHandle()
                continue
            if char.uuid == EnumChars.pheromones.value:
                self.pheromones = char.getHandle()
                continue
            if char.uuid == EnumChars.distance.value:
                self.distance = char.getHandle()
                continue


def rotate_2d(pts, cnt, ang=math.pi / 4):
    """ pts = {} Rotates points(nx2) about center cnt(2) by angle ang(1) in radian """

    return np.dot(pts - cnt, np.array([(math.cos(ang), math.sin(ang)), (-math.sin(ang), math.cos(ang))]) + cnt)


class Service:
    """ Service that an agent offers """


class Updatable:
    """ Values that the server send to the agent """
    rotation = False
    pheromone = "none"

    def __init__(self):
        # self.radius is an instance variable
        self.rotation = False


class Agent:
    """ Agent with sensor values and methods to communicate """
    color: str
    chars: Characteristics
    triangle: Triangle
    sending: Updatable
    con: Peripheral
    address: str
    xy = (-1, -1)
    last_update: float
    # Destination info
    destination = (-1, -1)
    rotation: float
    distance: float
    connected: bool
    speed = 0
    speed_rotation = 0
    __configured: bool
    sensor_lines: List[tuple]
    collide: bool

    def __init__(self, address, ):
        # self.radius is an instance variable
        self.configured = False
        self.address = address
        self.connected = False
        self.last_update = time.time()
        self.chars = self.connect()
        if self.connected:
            self.color = self.con.readCharacteristic(self.chars.color).decode()
            self.set_config()
        self.sending = Updatable()
        # self.sending.pheromone = True
        self.triangle = Triangle()
        self.rotation = 360
        self.pheromones = queue.Queue()
        self.sensor_lines = list()

    def connect(self):
        """ Connect to to ant and se the config """

        LOGGER.debug("Connecting")
        try:
            self.con = Peripheral(deviceAddr=self.address)
            self.con.addr = self.address
        except BTLEException:
            self.connected = False
            print("Failed to connect", BTLEException)
            return None
        LOGGER.debug("Connected")
        services = self.con.getServices()

        LOGGER.debug("Fetched services")
        chars_list = list()
        for service in services:
            if service.uuid == SENSOR_SERVICE:
                LOGGER.debug("Found sensor service")
                chars_list = service.getCharacteristics()
                LOGGER.debug("Found chars:")
                # LOGGER.debug(chars)
        chars = Characteristics(chars_list)
        self.connected = True
        return chars

    def read_color(self):
        """ Read the color from the agent """
        self.color = self.con.readCharacteristic(self.chars.color)

    def set_config(self):
        """ Set the configuration on the agent """

        LOGGER.debug("setting cng")
        self.con.writeCharacteristic(
            self.chars.config, str.encode("cng"), withResponse=True)
        self.__configured = True
        LOGGER.debug("set cng")

    def send_pos(self):
        """ Convert the position(tuple) to byte array and send via BLE """
        try:
            b_position = pack(
                "ii", self.triangle.position[0], self.triangle.position[1])
            self.con.writeCharacteristic(
                self.chars.position, b_position, withResponse=True)
        except bluepy.btle.BTLEGattError:
            pass

    def send_rotation(self):
        """ Convert the rotation(float) to byte array and send via BLE """
        if self.destination:
            new_rotation = self.triangle.calc_rotation(
                self.destination)
            if self.rotation == 360 or abs(self.rotation - new_rotation) > 3:
                self.rotation = new_rotation
                b_rotation = pack("ff", self.rotation, 0)
                self.con.writeCharacteristic(
                    self.chars.rotation, b_rotation, withResponse=True)

    def send_dist(self, dest):
        """ Convert the dist(tuple) to byte array and send via BLE """
        b_dest = pack(
            "ii", dest[0], dest[1])
        self.con.writeCharacteristic(
            self.chars.dest, b_dest, withResponse=True)

    def distance_sensor(self, walls: List[Wall]):
        temp_sensor_lines = list()
        start_object = None
        end_object = None
        self.collide = False

        self.sensor_lines.clear()
        for angle in range(0, 360, 15):
            cart_pos = pol2cart(angle, 50)
            cart_pos = (int(max(0, cart_pos[0] + self.xy[0])), int(max(cart_pos[1] + self.xy[1], 0)))
            temp_intercepts = False
            for wall in walls:
                intercepts, interception = wall.get_intersection([cart_pos, self.xy])
                if intercepts:
                    if temp_intercepts:
                        if distance(cart_pos, self.xy) > distance(interception, self.xy):
                            cart_pos = interception
                    else:
                        cart_pos = interception
                        temp_intercepts = True

            if temp_intercepts:
                if start_object is None:
                    start_object = cart_pos
                else:
                    end_object = cart_pos
            else:
                if start_object is not None:
                    self.sensor_lines.append((start_object, "red"))
                    self.collide = True
                    if end_object is not None:
                        self.sensor_lines.append((end_object, "red"))
                        end_object = None
                    start_object = None
                self.sensor_lines.append((cart_pos, "blue"))

    def send_pheromones(self, pheromones):
        b_pheromones = b''
        pheromones = list(OrderedDict.fromkeys(
            pheromones))  # remove duplicates
        length = min(20, len(pheromones))
        b_length = pack("i", length)
        b_length = b_length[0:1]
        b_pheromones += b_length
        for i in range(0, length):
            temp_x = pack("i", pheromones[i].x)
            temp_y = pack("i", pheromones[i].y)
            temp_x = temp_x[0:3]
            temp_y = temp_y[0:3]
            b_pheromones += temp_x
            b_pheromones += temp_y


        self.con.writeCharacteristic(
            self.chars.pheromones, b_pheromones, withResponse=True)
        # debug = self.con.readCharacteristic(self.chars.debug)
        # print(unpack("i", debug))

    def send_speed_base(self, speed, speed_type: str):
        """ Convert the dist(tuple) to byte array and send via BLE """
        b_dest = pack(
            "i", speed)
        self.con.writeCharacteristic(
            self.chars.config, ("s" + speed_type).encode() + b_dest, withResponse=True)

    def update(self, triangle, time_since_last_update, pheromones, walls: Wall):
        """ Update the sensors of the agent via BLE"""
        if triangle.is_valid() and self.triangle.is_valid():
            self.speed_rotation = distance(
                self.triangle.top, triangle.top) / time_since_last_update
        self.triangle = triangle

        # Calc speed
        prev_speed = self.speed
        self.speed = distance(
            self.triangle.center, self.xy) / time_since_last_update

        # update Time
        self.last_update = time.time()

        # update position
        prev_position = self.xy
        new_position = self.triangle.center

        if self.sending.pheromone is not "none":
            self.send_pheromones(get_close_pheromones(
                12000, self.xy, pheromones))
            self.sending.pheromone = "none"

        self.read_message()
        if abs(distance(prev_position, new_position)) > 6:
            self.xy = self.triangle.center
            self.send_pos()
            self.distance_sensor(walls)
            if self.collide:
                self.send_distance_lines()
        else:
            self.xy = prev_position
        self.send_rotation()

    def read_message(self):
        """ Check the com char of the agent and process the msg """

        message = self.con.readCharacteristic(
            self.chars.com)

        # if have the format => number,number
        if message.find(0x2c) != -1:
            self.sending.rotation = True
            # Read dist
            self.destination = (
                unpack("i", message[0:4])[0], unpack("i", message[5:9])[0])

        # print(message[0], b'\x11', message, message[0] == b'\x11')
        if message[0] == 17:
            intense = unpack("i", message[2:6])[0]
            self.pheromones.put(
                Pheromone(self.xy[0], self.xy[1], intense, message[1]))
        if message[0] == 18:
            self.sending.pheromone = get_pheromone_type(message[1])

        self.con.writeCharacteristic(
            self.chars.com, "0".encode(), withResponse=True)
        return

    def draw_lines(self, frame, offset=(0, 0)):
        """ Draw the destination with a circle and a line from top to pnt """
        for (line, color) in self.sensor_lines:
            if line[0] != -1 and self.triangle.is_valid():
                if color is "red":
                    show_color = (20, 20, 200)
                else:
                    show_color = (200, 150, 50)
                cv2.line(
                    frame,
                    tuple(map(sum, zip(self.triangle.center, offset))),
                    tuple(map(sum, zip(line, offset))),
                    show_color,
                    2
                )

    def draw_dest(self, frame, offset=(0, 0)):
        """ Draw the destination with a circle and a line from top to pnt """
        if self.destination[0] != -1 and self.triangle.is_valid():
            cv2.line(frame, tuple(map(sum, zip(self.triangle.center, offset))),
                     tuple(map(sum, zip(self.triangle.top, offset))), (200, 150, 50), 2)
            cv2.line(frame, tuple(map(sum, zip(self.triangle.top, offset))),
                     tuple(map(sum, zip(self.destination, offset))), (200, 150, 50), 2)
            cv2.circle(frame, tuple(
                map(sum, zip(self.destination, offset))), 5, 200, 1)

    def draw_distance(self, frame, offset=(0, 0)):
        """ Draw the distance with a circle and a line from top to pnt """
        if self.destination[0] != -1:
            cv2.line(frame, tuple(map(sum, zip(self.triangle.center, offset))),
                     tuple(map(sum, zip(self.triangle.top, offset))), (200, 150, 50), 2)
            cv2.putText(frame,
                        ('%.2f' % (distance(self.triangle.center,
                                            self.destination) / 5)) + " cm", self.destination,
                        FONT, 1,
                        255)

    def draw_rotation(self, frame, offset=(0, 0)):
        """ Draw the rotation with a circle and a line from top to pnt """
        if self.destination[0] != -1:
            cv2.line(frame, tuple(map(sum, zip(self.triangle.center, offset))),
                     tuple(map(sum, zip(self.destination, offset))), (200, 150, 50), 2)
            cv2.line(frame, tuple(map(sum, zip(self.triangle.center, offset))),
                     tuple(map(sum, zip(self.triangle.top, offset))), (200, 150, 50), 2)
            cv2.putText(frame,
                        ('%.2f' % self.rotation) +
                        " C*", self.destination, FONT, 1,
                        255)

    def draw_claw(self, frame: object, offset: tuple = (0, 0)) -> object:
        # cv2.circle(frame, tuple(map(sum, zip(self.xy, offset))), 25, (128, 0, 128), 2);
        x, y = tuple(map(sum, zip(self.xy, offset)))
        forms = [np.array([
            (x - 12, y - 10), (13 + x, y - 10),
            (x, y - 5),
        ]),
            np.array([
                (x - 12, y - 15), (x - 6, y - 15),
                (x - 6, y - 40),
            ]),
            np.array([
                (x + 6, y - 15), (x + 12, y - 15),
                (x + 6, y - 40),
            ])
        ]
        for points in forms:
            b = rotate_polygon(points, 0, x, y)
            cv2.polylines(frame, [b], True, (128, 0, 128))
            cv2.fillPoly(frame, [b], (128, 0, 128))
        return frame

    def send_distance_lines(self):
        b_distance_lines = b''
        b_length, length = calc_bytes_of_length(self.sensor_lines, 23)
        b_distance_lines += b_length
        for i in range(0, length):
            ((temp_x, temp_y), intercepts) = self.sensor_lines[i]
            temp_x = pack("i", temp_x)
            temp_y = pack("i", temp_y)
            temp_x = temp_x[0:3]
            temp_y = temp_y[0:3]
            b_distance_lines += temp_x
            b_distance_lines += temp_y

            if intercepts == "red":
                b_distance_lines += b'0x01'
            else:
                b_distance_lines += b'0x00'
        self.con.writeCharacteristic(
            self.chars.distance, b_distance_lines, withResponse=True)
        pass


def get_pheromone_type(pheromone_type):
    if pheromone_type == 18:
        return "searching"
    elif pheromone_type == b"0x00":
        return "none"


def calc_bytes_of_length(array: list, min_length=20):
    length = min(min_length, len(array))
    b_length = pack("i", length)
    b_length = b_length[0:2]
    return b_length, length


class Pheromone:
    x: int
    y: int
    intense: int
    type: str

    def __init__(self, x, y, intense, pheromone_type):
        self.x = x
        self.y = y
        self.intense = intense
        self.type = get_pheromone_type(pheromone_type)

    def __eq__(self, other):
        return self.x == other.x \
               and self.y == other.y

    def __hash__(self):
        return hash(('x', self.x,
                     'y', self.y))


def get_close_pheromones(dist: int, pos: tuple, pheromones: List[Pheromone]):
    close_pheromones = list(filter(lambda pheromone: distance(
        pos, (pheromone.x, pheromone.y)) < dist, pheromones))
    return close_pheromones


def __upt_pheromone(pheromone: Pheromone):
    pheromone.intense -= 1
    return pheromone


def __remove_pheromone(pheromone: Pheromone):
    return pheromone.intense > 0
