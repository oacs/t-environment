''' action bar '''
from xml.etree.ElementTree import Element, ElementTree, SubElement

from PySimpleGUI import Button, Window

# from opencv.main import EnvProcess
from theme import WHITE

ACTION_LAYOUT = [
    Button(
        button_text="",
        tooltip="Play the simulation",
        # bind_return_key="p",
        button_color=[WHITE, WHITE],
        image_filename="assets/img/play.png",
        image_size=[35, 35],
        border_width=0,
        key="action_play_pause",
        disabled=False,
        metadata={
            "status": "play"
        }
    ),
    Button(
        button_text="",
        tooltip="Save the simulation",
        # bind_return_key="space",
        button_color=[WHITE, WHITE],
        image_filename="assets/img/save.png",
        image_size=[35, 35],
        border_width=0,
        key="action_save"
    ),
]

ACTION_KEYS = ["action_play_pause", "action_save"]


def action_events(event: str, _values: dict, window: Window, env_process):
    ''' handle all action bar events '''
    if event == "action_play_pause":
        if window["action_play_pause"].metadata["status"] == "pause":
            window["action_play_pause"].metadata["status"] = "play"
            env_process.run = False
        else:
            window["action_play_pause"].metadata["status"] = "pause"
            env_process.run = True

        window["action_play_pause"].update(
            image_filename="assets/img/" +
            window["action_play_pause"].metadata["status"] + ".png")

    if event == "action_save":
        simulation = Element('simulation')

        # comment = Comment('Generated for PyMOTW')
        # simulation.append(comment)

        boxes = SubElement(simulation, 'boxes')
        for box in env_process.boxes:
            box_el = SubElement(boxes, 'box')
            box_el.set('x', str(box.pos[0]))
            box_el.set('y', str(box.pos[1]))
            box_el.set('r', str(box.radius))
            box_el.set('w', str(box.weigh))
            box_el.set('id', str(box.id))

        walls = SubElement(simulation, 'walls')
        for wall in env_process.walls:
            wall_el = SubElement(walls, 'wall')
            pnt_1 = SubElement(wall_el, "pnt")
            pnt_1.set('x', str(wall.pos[0][0]))
            pnt_1.set('y', str(wall.pos[0][1]))

            pnt_2 = SubElement(wall_el, "pnt")
            pnt_2.set('x', str(wall.pos[1][0]))
            pnt_2.set('y', str(wall.pos[1][1]))

            wall_el.set('id', str(wall.id))
        ElementTree(simulation).write("state.xml")
