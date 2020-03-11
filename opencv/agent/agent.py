""" This module is defined for the agent object """
import math
from enum import Enum
from uuid import UUID
import time
from struct import unpack, pack
import logging
import sys
import cv2
from bluepy.btle import Peripheral, BTLEException
from opencv.forms.color import Colors
from opencv.forms.triangle import Triangle, distance
from opencv.forms.utils import FONT, rotate_polygon
import numpy as np

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


class Characteristics():
    """ Characteristics that agents offer to write and read """

    position: int
    config: int
    color: int
    debug: int
    com: int
    rotation: int
    dest: int

    def __init__(self, chars):
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


def Rotate2D(pts, cnt, ang=math.pi / 4):
    """ pts = {} Rotates points(nx2) about center cnt(2) by angle ang(1) in radian """

    return np.dot(pts - cnt, np.array([(math.cos(ang), math.sin(ang)), (-math.sin(ang), math.cos(ang))]) + cnt)


class Service:
    """ Service that an agent offers """


class Updatable:
    """ Values that the server send to the agent """
    rotation = False

    def __init__(self):
        # self.radius is an instance variable
        self.rotation = False


class Agent:
    """ Agent with sensor values and methods to communicate """
    color: Colors
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
        self.triangle = Triangle()

    def connect(self):
        """ Connect to to ant and se the config """

        LOGGER.debug("Connecting")
        try:
            self.con = Peripheral(deviceAddr=self.address)
        except BTLEException:
            self.connected = False
            print("Failed to connect")
            return None
        LOGGER.debug("Connected")
        services = self.con.getServices()

        LOGGER.debug("Fetched services")
        for service in services:
            if service.uuid == SENSOR_SERVICE:
                LOGGER.debug("Found sensor service")
                chars = service.getCharacteristics()
                LOGGER.debug("Found chars:")
                LOGGER.debug(chars)
        chars = Characteristics(chars)

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
        LOGGER.debug("setted cng")

    def send_pos(self):
        """ Convert the position(tuple) to byte array and send via BLE """
        b_position = pack(
            "ii", self.triangle.position[0], self.triangle.position[1])
        self.con.writeCharacteristic(
            self.chars.position, b_position, withResponse=True)

    def send_rotation(self):
        """ Convert the rotation(float) to byte array and send via BLE """
        if self.sending.rotation:
            self.rotation = self.triangle.calc_rotation(
                self.destination)
            b_rotation = pack("ff", self.rotation, 0)
            self.con.writeCharacteristic(
                self.chars.rotation, b_rotation, withResponse=True)


    def send_dist(self, dest):
        """ Convert the dist(tuple) to byte array and send via BLE """
        b_dest = pack(
            "ii", dest[0], dest[1])
        self.con.writeCharacteristic(
            self.chars.dest, b_dest, withResponse=True)

    def send_speed_base(self, speed, type):
        """ Convert the dist(tuple) to byte array and send via BLE """
        b_dest = pack(
            "i", speed)
        print(type)
        print(("s"+type).encode() + b_dest, speed)
        self.con.writeCharacteristic(
            self.chars.config, ("s"+type).encode() + b_dest, withResponse=True)

    def update(self, frame, triangle, time_since_last_update):
        """ Update the sensors of the agent via BLE"""
        if triangle.is_valid() and self.triangle.is_valid():
            self.speed_rotation = distance(
                self.triangle.top, triangle.top) / time_since_last_update
        self.triangle = triangle

        # Calc speed
        self.speed = distance(
            self.triangle.center, self.xy) / time_since_last_update


        # update Time
        self.last_update = time.time()

        # update position
        self.xy = self.triangle.center

        self.read_message()
        self.send_rotation()
        self.send_pos()

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

            self.con.writeCharacteristic(
                self.chars.com, "0".encode(), withResponse=True)

    def draw_dest(self, frame, offset=(0, 0)):
        """ Draw the destination with a circle and a line from top to pnt """
        if self.destination[0] != -1 and self.triangle.is_valid():
            cv2.line(frame, tuple(map(sum, zip(self.triangle.center, offset))),
                     tuple(map(sum, zip(self.triangle.top, offset))), (200, 150, 50), 2)
            cv2.line(frame, tuple(map(sum, zip(self.triangle.top, offset))),
                     tuple(map(sum, zip(self.destination, offset))), (200, 150, 50), 2)
            cv2.circle(frame, tuple(map(sum, zip(self.destination, offset))), 5, 200, 1)

    def draw_distance(self, frame, offset=(0, 0)):
        """ Draw the distance with a circle and a line from top to pnt """
        if self.destination[0] != -1:
            cv2.line(frame, tuple(map(sum, zip(self.triangle.center, offset))),
                     tuple(map(sum, zip(self.triangle.top, offset))), (200, 150, 50), 2)
            cv2.putText(frame,
                        ('%.2f' % (distance(self.triangle.center, self.destination) / 5)) + " cm", self.destination,
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
                        ('%.2f' % self.rotation) + " C*", self.destination, FONT, 1,
                        255)

    def draw_claw(self, frame, offset=(0, 0)):
        # cv2.circle(frame, tuple(map(sum, zip(self.xy, offset))), 25, (128, 0, 128), 2);
        x, y = tuple(map(sum, zip(self.xy, offset)))
        forms = [np.array([
            (x - 12, y - 35), (13 + x, y - 35),
            (13 + x, y - 40), (x - 12, y - 40),
        ]),
            np.array([
                (x - 12, y - 45), (x - 6, y - 45),
                (x - 6, y - 65), (x - 12, y - 65),
            ]),
            np.array([
                (x + 6, y - 45), (x + 12, y - 45),
                (x + 12, y - 65), (x + 6, y - 65),
            ])
        ]
        for points in forms:
            b = rotate_polygon(points, 45, x, y)
            cv2.polylines(frame, [b], True, (128, 0, 128))
            cv2.fillPoly(frame, [b], (128, 0, 128))
