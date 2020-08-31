""" This module is defined for the agent object """
import logging
import math
import queue
import sys
import time
from collections import OrderedDict
from struct import unpack, pack
from typing import List
from uuid import UUID

import bluepy
import cv2
import numpy as np
from bluepy.btle import Peripheral, BTLEException

from opencv.agent.claw import Claw
from opencv.forms.triangle import Triangle, distance
from opencv.forms.utils import FONT, pol2cart
from opencv.wall import Wall
from opencv.agent.pheromone import Pheromone, get_close_pheromones, get_pheromone_type
from opencv.agent.characteristics import Characteristics

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
LOGGER = logging.getLogger("agent")
SENSOR_SERVICE = UUID("218EE492-8AFB-4CA6-93B6-2D0DBF2F00FE")


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
    claw: Claw

    def __init__(self, address, color):
        # self.radius is an instance variable
        self.configured = False
        self.address = address
        self.connected = False
        self.last_update = time.time()
        self.chars = self.connect()
        if self.connected:
            # self.color = self.con.readCharacteristic(self.chars.color).decode()
            self.color = color
            self.set_config()
            self.claw_distance = 15
            self.claw = Claw((0, 0), self.color)
            self.claw.box_id = 0
            self.claw.status = b'\x04'
            self.claw.leader = "G"
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
            print("ERROR on GAT sending pos")
        except bluepy.btle.BTLEException as err:
            print("ERROR on sending pos"
                  "", err, err.message, err.emsg)
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

            cart_pos = pol2cart(angle, 150)
            cart_pos = (
                int(max(0, cart_pos[0] + self.xy[0])), int(max(cart_pos[1] + self.xy[1], 0)))
            temp_intercepts = False
            for wall in walls:
                intercepts, interception = wall.get_intersection(
                    [cart_pos, self.xy])
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

    def update(self, triangle, time_since_last_update, pheromones, walls: Wall, ):
        """ Update the sensors of the agent via BLE"""

        time_to_update = time.time()
        # if triangle.is_valid() and self.triangle.is_valid():
        #     self.speed_rotation = distance(
        #         self.triangle.top, triangle.top) / time_since_last_update
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
        # if abs(distance(prev_position, new_position)) > 6:
        self.xy = self.triangle.center
        self.send_pos()
        self.distance_sensor(walls)
        if self.collide:
            self.send_distance_lines()
        # else:
        #     self.xy = prev_position
        self.send_rotation()
        self.claw.pos = self.triangle.center
        time_to_update = time.time() - time_to_update
        # print(time_to_update)

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
                b_distance_lines += b'\x01'
            else:
                b_distance_lines += b'\x00'
        self.con.writeCharacteristic(
            self.chars.distance, b_distance_lines, withResponse=True)
        pass


def calc_bytes_of_length(array: list, min_length=20):
    length = min(min_length, len(array))
    b_length = pack("i", length)
    b_length = b_length[0:2]
    return b_length, length
