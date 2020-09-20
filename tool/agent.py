import time
from struct import unpack

import PySimpleGUI as sg
import cv2
from opencv.agent.agent import Agent
from opencv.main import EnvProcess

nav_graph = sg.Graph((600, 450), (0, 450), (600, 0), key='NAV-GRAPH',
                  enable_events=True, drag_submits=True,
                  metadata={
                      "a_id": None,
                  })
agent_gui = sg.Column([
    [sg.Text("Agent color: "), sg.Text("", key="agent-color")],
    [sg.Text("Agent pos: "), sg.Text("", key="agent-pos", size=(20, None))],
    [sg.Text("Agent speed: "), sg.Text(
        "", key="agent-speed", size=(20, None))],
    [sg.Text("Agent rotation: "), sg.Text(
        "", key="agent-rotation", size=(20, None))],
    [sg.Text("Agent destination: "), sg.Text(
        "", key="agent-destination", size=(20, None))],
    [sg.Text("Agent base speed clock: "),
     sg.InputText("", disabled=False,
                  key="agent-base-speed-c-input", size=(80, 20)),
     sg.Button(key='agent-base-speed-c', visible=True)],
    [sg.Text("Agent base speed reverse: "),
     sg.InputText("", disabled=False,
                  key="agent-base-speed-r-input", size=(80, 20)),
     sg.Button(key='agent-base-speed-r', visible=True)],
    [sg.Text("Agent base speed forward: "),
     sg.InputText("", disabled=False,
                  key="agent-base-speed-f-input", size=(80, 20)),
     sg.Button(key='agent-base-speed-f', visible=True)],
    [sg.Text("Agent debug msg: "),
     sg.Text("", key="agent-debug", size=(20, None))],
    [nav_graph]
], key="agent-column", metadata=-1)

last_update = 0

def update_image(frame, window, graph):
    img_bytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
    if window[graph].metadata["a_id"]:
        # delete previous image
        window[graph].delete_figure(window[graph].metadata["a_id"])
    window[graph].metadata["a_id"] = window[graph].draw_image(
        data=img_bytes, location=(0, 0))  # draw new image
    # move image to the "bottom" of all other drawings
    window[graph].TKCanvas.tag_lower(window[graph].metadata["a_id"])

def agent_gui_event(event: str, values: dict, window: sg.Window, env_process: EnvProcess):
    if window["agent-column"].metadata != -1:
        ant: Agent
        ant = env_process.ants[window["agent-column"].metadata]
        pos = "( " + str(ant.xy[0]) + " , " + str(ant.xy[1]) + " )"
        dest = (
            "( " + str(ant.destination[0]) + " , " + str(ant.destination[1]) + " )")
        window["agent-color"].update(ant.color)
        window["agent-pos"].update(str(pos))

        window["agent-speed"].update("%.2f" % ant.speed)
        if ant.rotation is not None:
            window["agent-rotation"].update("%.2f" % ant.rotation)
        window["agent-destination"].update(dest)
        # if int(round(time.time() * 1000)) - window.metadata["last_update"]  > 500:
        #     debug = ant.con.readCharacteristic(ant.chars.debug)
        #     window["agent-debug"].update(unpack("i", debug))
        #     window.metadata["last_update"] = int(round(time.time() * 1000))
        frame = env_process.ants[window["agent-column"].metadata].recognition.area
        update_image(frame, window, "NAV-GRAPH")
        if event in ("agent-base-speed-c", "agent-base-speed-r", "agent-base-speed-f"):
            ant: Agent
            ant = env_process.ants[window["agent-column"].metadata]
            ant.send_speed_base(
                int(values[event + "-input"]), event.split("agent-base-speed-")[1])
            # print(debug)
