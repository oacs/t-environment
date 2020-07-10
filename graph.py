import cv2
from PySimpleGUI import Graph, Window, Text, Input, Tab, TabGroup, OK, Column, Button

from opencv.box import Box
from opencv.wall import Wall
from theme import PRIMARY

from opencv.agent.agent import Agent, Pheromone
from opencv.forms.borders import get_rect_borders
from opencv.forms.color import ColorFilter, Colors
from opencv.forms.triangle import distance
from opencv.main import EnvProcess

main_graph = Graph((600, 450), (0, 450), (600, 0), key='MAIN-GRAPH',
                   enable_events=True, drag_submits=True, metadata={
        "a_id": None,
        "x": 0,
        "y": 0
    })

colors_graph = Graph((600, 450), (0, 450), (600, 0), key='COLORS-GRAPH',
                     enable_events=True, drag_submits=True, metadata={
        "color": None, "a_id": None,

    })

borders_graph = Graph((600, 450), (0, 450), (600, 0), key='BORDERS-GRAPH',
                      enable_events=True, drag_submits=True,
                      metadata={
                          "a_id": None,
                      })

graph_keys = ["MAIN-GRAPH", "GRAPH-MOUSE-MOTION", "-TAB-GROUP-"]


def process_click(type: int, coord: tuple, env_process: EnvProcess, window: Window):
    x, y = coord
    ant: Agent
    x_offset = min(env_process.borders[1][0], env_process.borders[0][0]);
    y_offset = min(env_process.borders[1][1], env_process.borders[0][1]);

    for i, ant in enumerate(env_process.ants):
        size = distance(ant.triangle.center, ant.triangle.top)
        ax, ay = ant.xy
        ax += x_offset
        ay += y_offset
        if (ax - (size / 2)) <= x <= (ax + (size / 2)) and (ay - (size / 2)) <= y <= (ay + (size / 2)):
            window["agent-column"].metadata = i
            return

    if (x_offset < x < max(env_process.borders[1][0],
                           env_process.borders[0][0]) and
            y_offset < y < max(env_process.borders[1][1],
                               env_process.borders[0][1])):

        if window["GRAPH-BOX"].metadata == "activated":
            env_process.boxes.append(Box((x- x_offset, y- y_offset), len(env_process.boxes)))
        elif window["GRAPH-WALL"].metadata == "activated":
            if type == 1:
                window.metadata["tempPos"] = (x- x_offset, y- y_offset)
            else:
                env_process.walls.append(Wall(window.metadata["tempPos"], (x- x_offset, y- y_offset), len(env_process.walls)))
        else:
            env_process.pheromones.append(
                Pheromone(x - x_offset,
                          y - y_offset, 5, b"0x12"))


def graph_events(event: str, values: dict, window: Window, env_process: EnvProcess) -> None:
    """
    Args:
        event: Event name
        values: values of the event
        env_process: process of CF
        window (Window):
    """

    if event == "GRAPH-BOX":
        if window["GRAPH-BOX"].metadata == "activated":
            window["GRAPH-BOX"].metadata = "unactivated"
        else:
            window["GRAPH-WALL"].metadata = "unactivated"
            window["GRAPH-BOX"].metadata = "activated"
            window["GRAPH-WALL"].update(image_filename="assets/img/brick-" + window["GRAPH-WALL"].metadata + ".png")

        window["GRAPH-BOX"].update(image_filename="assets/img/box-" + window["GRAPH-BOX"].metadata + ".png")

    if event == "GRAPH-WALL":
        if window["GRAPH-WALL"].metadata == "activated":
            window["GRAPH-WALL"].metadata = "unactivated"
        else:
            window["GRAPH-BOX"].metadata = "unactivated"
            window["GRAPH-WALL"].metadata = "activated"
            window["GRAPH-BOX"].update(image_filename="assets/img/box-" + window["GRAPH-BOX"].metadata + ".png")

        window["GRAPH-WALL"].update(image_filename="assets/img/brick-" + window["GRAPH-WALL"].metadata + ".png")
    if values["-TAB-GROUP-"] == "-MAIN-TAB-":
        frame = env_process.read()
        if frame is not None:
            if event == 'MAIN-GRAPH':
                process_click(1, values["MAIN-GRAPH"], env_process, window)
            elif event == 'MAIN-GRAPH+UP':
                process_click(2, values["MAIN-GRAPH"], env_process, window)

            elif event == "MAIN-GRAPH-MOUSE-MOTION":
                window["MAIN-GRAPH"].metadata["x"] = window["MAIN-GRAPH"].user_bind_event.x
                window["MAIN-GRAPH"].metadata["y"] = window["MAIN-GRAPH"].user_bind_event.y
            if env_process.run:
                frame = env_process.draw_xy(frame, window["MAIN-GRAPH"].metadata["x"],
                                            window["MAIN-GRAPH"].metadata["y"])
                if len(env_process.borders) > 1:
                    offset = (min(env_process.borders[1][0], env_process.borders[0][0]),
                              min(env_process.borders[1][1], env_process.borders[0][1]))
                frame = env_process.draw_borders(frame)
                frame = env_process.draw_config(frame)
                frame = env_process.draw_pheromones(frame)

                if len(env_process.borders) > 1:
                    offset = (min(env_process.borders[1][0], env_process.borders[0][0]),
                              min(env_process.borders[1][1], env_process.borders[0][1]))
                    for box in env_process.boxes:
                        frame = box.draw(frame, offset)
                    for wall in env_process.walls:
                        frame = wall.draw(frame, offset)
                    for ant in env_process.ants:
                        frame = ant.claw.draw_claw(frame, offset)
                        ant.draw_dest(frame, offset)
                        # ant.draw_lines(frame, offset)
            update_image(frame, window, "MAIN-GRAPH")
    if values["-TAB-GROUP-"] == "-COLORS-TAB-":
        frame = env_process.read()
        frame = ColorFilter(
            Colors.unset,
            values["mask-min-hue"],
            values["mask-max-hue"],
            values["mask-min-sat"],
            values["mask-max-sat"],
            values["mask-min-val"],
            values["mask-max-val"],
            0, 0, 0
        ).get_mask(frame)
        update_image(frame, window, "COLORS-GRAPH")

    if values["-TAB-GROUP-"] == "-BORDERS-TAB-":
        frame = get_rect_borders(env_process.read())[1]
        update_image(frame, window, "BORDERS-GRAPH")

    if event == "-TAB-GROUP-":
        if values["-TAB-GROUP-"] == "-COLORS-TAB-":
            window["mask-column"].update(visible=True)
            window["agent-column"].update(visible=False)
        else:
            window["agent-column"].update(visible=True)
            window["mask-column"].update(visible=False)


def update_image(frame, window, graph):
    img_bytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
    if window[graph].metadata["a_id"]:
        # delete previous image
        window[graph].delete_figure(window[graph].metadata["a_id"])
    window[graph].metadata["a_id"] = window[graph].draw_image(
        data=img_bytes, location=(0, 0))  # draw new image
    # move image to the "bottom" of all other drawings
    window[graph].TKCanvas.tag_lower(window[graph].metadata["a_id"])


# The tab 1, 2, 3 layouts - what goes inside the tab
tab_main_layout = [[main_graph, Column([
    [
        Button(button_text="", button_color=[PRIMARY, PRIMARY],
               key="GRAPH-BOX",
               image_filename="assets/img/box-unactivated.png",
               image_size=[35, 35],
               border_width=0, )
    ],
    [
        Button(button_text="", button_color=[PRIMARY, PRIMARY],
               key="GRAPH-WALL",
               image_filename="assets/img/brick-unactivated.png",
               image_size=[35, 35],
               border_width=0, )
    ]
],
    metadata="unactivated",
    background_color=[PRIMARY])]]

tab_colors_layout = [[colors_graph]]
tab_border_layout = [[borders_graph]]

# The TabgGroup layout - it must contain only Tabs
tab_group_layout = [
    [Tab('Main', tab_main_layout, font='Courier 15', key='-MAIN-TAB-', pad=(0, 0), background_color=[PRIMARY]),
     Tab('Colors', tab_colors_layout, key='-COLORS-TAB-', pad=(0, 0), background_color=[PRIMARY]),
     Tab('Borders', tab_border_layout, key='-BORDERS-TAB-', pad=(0, 0), background_color=[PRIMARY]), ]]

# The window layout - defines the entire window
graph_tabs = TabGroup(tab_group_layout, enable_events=True, key='-TAB-GROUP-', background_color=[PRIMARY])
