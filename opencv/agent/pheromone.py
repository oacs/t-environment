from typing import List
from opencv.forms.triangle import distance


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


def get_pheromone_type(pheromone_type):
    if pheromone_type == 18:
        return "searching"
    elif pheromone_type == b"0x00":
        return "none"


def get_close_pheromones(dist: int, pos: tuple, pheromones: List[Pheromone]):
    close_pheromones = list(filter(lambda pheromone: distance(
        pos, (pheromone.x, pheromone.y)) < dist, pheromones))
    return close_pheromones


def __upt_pheromone(pheromone: Pheromone):
    pheromone.intense -= 1
    return pheromone


def __remove_pheromone(pheromone: Pheromone):
    return pheromone.intense > 0
