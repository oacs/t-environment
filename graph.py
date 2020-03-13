import cv2
from PySimpleGUI import Graph, Window

from opencv.agent.agent import Agent
from opencv.forms.triangle import distance
from opencv.main import EnvProcess

graph = Graph((600, 450), (0, 450), (600, 0), key='GRAPH',
              enable_events=True, drag_submits=True, metadata={
        "a_id": None
    })

graph_keys = ["GRAPH"]


def process_click(coord: tuple, env_process: EnvProcess, window: Window):
    x, y = coord
    ant: Agent
    for i, ant in enumerate( env_process.ants):
        size = distance(ant.triangle.center, ant.triangle.top)
        ax, ay = ant.xy
        ax += env_process.borders[1][0]
        ay += env_process.borders[1][1]
        if (ax-(size/2)) <= x <= (ax+(size/2)) and (ay-(size/2)) <= y <= (ay+(size/2)):
            window["agent-column"].metadata = i
            return




def graph_events(event: str, values: dict, window: Window, env_process: EnvProcess) -> None:
    """
    Args:
        event: Event name
        values: values of the event
        env_process: process of CF
        window (Window):
    """
    frame = env_process.read()
    frame = env_process.draw_borders(frame)
    for ant in env_process.ants:
        ant.draw_dest(frame, env_process.borders[1])
    img_bytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
    if window["GRAPH"].metadata["a_id"]:
        # delete previous image
        window["GRAPH"].delete_figure(window["GRAPH"].metadata["a_id"])
    window["GRAPH"].metadata["a_id"] = window["GRAPH"].draw_image(
        data=img_bytes, location=(0, 0))  # draw new image
    # move image to the "bottom" of all other drawings
    window["GRAPH"].TKCanvas.tag_lower(window["GRAPH"].metadata["a_id"])

    if event == 'GRAPH':
        process_click(values["GRAPH"], env_process, window)

