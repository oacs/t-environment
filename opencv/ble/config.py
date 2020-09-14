from uuid import UUID

from opencv.agent.agent import Agent
from opencv.forms.color import ColorFilter

SENSOR_SERVICE = UUID("218EE492-8AFB-4CA6-93B6-2D0DBF2F00FE")
# POSSIBLE_ANTS = ["d9:da:40:61:51:42", "CF:95:C4:15:A6:05", "c2:4d:ee:21:f3:6a"]
POSSIBLE_ANTS = ["c2:4d:ee:21:f3:6a"]
GROUP_CHAR = "5ad56076-88c1-4e11-bd31-7d4f1e99f32c"
CONFIG_CHAR = "79606e8e-0b90-4ade-8c21-2a8fe1e64217"
COLOR_CHAR = "c2a76563-3af7-4640-82be-1c841f228e6c"
POSITION_CHAR = "19B10001-E8F2-537E-4F6C-D104768A1214"
ROTATION_CHAR = "cd185314-5651-4eb9-b8cd-16e035d88bc4"
DEBUG_CHAR = "645e1252-55dd-4604-8d35-add29319725b"
COM_CHAR = "a6f2eee3-d71e-4e77-a9fa-66fb946c4e96"


def return_address(ant: Agent):
    return ant.address


def find_ant(know_ants: list, color: ColorFilter, possible_ants  ):
    """ Find ants by color and connect to it"""
    ant_address = map(return_address, know_ants)
    for ant in possible_ants:
        if ant["address"] not in ant_address and ant["color"] is color:
            ant_obj = Agent(ant["address"], color, ant["config"])
            if ant_obj.connected:
                return ant_obj

        # if ant not in ant_address:
        #     ant_obj = Agent(ant)
        #     if ant_obj.connected and ant_obj.color == color.color.value:
        #         return ant_obj
    return None


# def connect(ant_address, color):
#     """ Connect to to ant and se the config """
#     print("Connecting")
#     read_color
#     ant = Peripheral(deviceAddr=ant_address)
#     print("Connected")
#     services = ant.getServices()
#     print("Fetched services")
#     for service in services:
#         print(service)
#         if service.uuid == SENSOR_SERVICE:
#             print("Found sensor service")
#             chars = service.getCharacteristics()
#             print("Found chars", chars)
#             for char in chars:
#                 print(char, char.getHandle())
#                 if char.uuid == POSITION_CHAR:
#                     position_char = char.getHandle()
#                     continue
#                 if char.uuid == CONFIG_CHAR:
#                     config_char = char.getHandle()
#                     continue
#                 if char.uuid == COLOR_CHAR:
#                     read_color = ant.readCharacteristic(
#                         char.getHandle()).decode()
#                 if char.uuid == DEBUG_CHAR:
#                     debug_char = char.getHandle()
#                 if char.uuid == COM_CHAR:
#                     com_char = char.getHandle()
#                 if char.uuid == ROTATION_CHAR:
#                     rotation_char = char.getHandle()
#     if read_color != None and color == read_color:
#         print("setting cng")
#         ant.writeCharacteristic(
#             config_char, str.encode("cng"), withResponse=True)
#         print("set cng")
#         chars = {
#             "position": position_char,
#             "debug": debug_char,
#             "rotation": rotation_char,
#             "com": com_char,
#         }
#
#         return True, color, ant, chars

# connect("cf:95:c4:15:a6:05", "R")
