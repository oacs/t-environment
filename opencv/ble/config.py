from bluepy.btle import Scanner, Peripheral
from uuid import UUID
SENSOR_SERVICE = UUID("218EE492-8AFB-4CA6-93B6-2D0DBF2F00FE")
POSSIBLE_ANTS = ["d9:da:40:61:51:42", "cf:95:c4:15:a6:05", "c2:4d:ee:21:f3:6a"]
GROUP_CHAR = "5ad56076-88c1-4e11-bd31-7d4f1e99f32c"
CONFIG_CHAR = "79606e8e-0b90-4ade-8c21-2a8fe1e64217"
COLOR_CHAR = "c2a76563-3af7-4640-82be-1c841f228e6c"
POSITION_CHAR = "19B10001-E8F2-537E-4F6C-D104768A1214"
ROTATION_CHAR = "cd185314-5651-4eb9-b8cd-16e035d88bc4"
DEBUG_CHAR = "645e1252-55dd-4604-8d35-add29319725b"
COM_CHAR = "a6f2eee3-d71e-4e77-a9fa-66fb946c4e96"


def find_ant(know_ants):
    """ Find ants by color and connect to it"""
    for ant in POSSIBLE_ANTS:
        try:
            know_ants.index(ant)
            print(ant)
        except ValueError:
            return ant


def connect(ant_address, color):
    """ Connecto to ant and se the config """
    print("Connecting")

    ant = Peripheral(deviceAddr=ant_address)
    print("Connected")
    services = ant.getServices()
    print("Fetched services")
    for serv in services:
        print(serv)
        if (serv.uuid == SENSOR_SERVICE):
            print("Found sensor service")
            chars = serv.getCharacteristics()
            print("Found chars", chars)
            for char in chars:
                print(char, char.getHandle())
                if (char.uuid == POSITION_CHAR):
                    position_char = char.getHandle()
                    continue
                if (char.uuid == CONFIG_CHAR):
                    config_char = char.getHandle()
                    continue
                if (char.uuid == COLOR_CHAR):
                    readed_color = ant.readCharacteristic(
                        char.getHandle()).decode()
                if (char.uuid == DEBUG_CHAR):
                    debug_char = char.getHandle()
                if (char.uuid == COM_CHAR):
                    com_char = char.getHandle()
                if (char.uuid == ROTATION_CHAR):
                    rotation_char = char.getHandle()
    if (color == readed_color):

        print("setting cng")
        ant.writeCharacteristic(
            config_char, str.encode("cng"), withResponse=True)
        print("setted cng")
        chars = {
            "position": position_char,
            "debug": debug_char,
            "rotation": rotation_char,
            "com": com_char,
        }

        return True, color, ant, chars


# connect("cf:95:c4:15:a6:05", "R")