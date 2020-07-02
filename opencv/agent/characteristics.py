from enum import Enum


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
            elif char.uuid == EnumChars.config.value:
                self.config = char.getHandle()
                continue
            elif char.uuid == EnumChars.color.value:
                self.color = char.getHandle()
                continue
            elif char.uuid == EnumChars.debug.value:
                self.debug = char.getHandle()
                continue
            elif char.uuid == EnumChars.com.value:
                self.com = char.getHandle()
                continue
            elif char.uuid == EnumChars.rotation.value:
                self.rotation = char.getHandle()
                continue
            elif char.uuid == EnumChars.dest.value:
                self.dest = char.getHandle()
                continue
            elif char.uuid == EnumChars.pheromones.value:
                self.pheromones = char.getHandle()
                continue
            elif char.uuid == EnumChars.distance.value:
                self.distance = char.getHandle()
                continue
            else:
                print("Unknown char", char.uuid)
        pass
