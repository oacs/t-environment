import PySimpleGUI as sg

from opencv.agent.agent import Agent
from opencv.main import EnvProcess
from struct import unpack

agent_gui = sg.Column([
    [sg.Text("Agent color: "), sg.Text("", key="agent-color")],
    [sg.Text("Agent pos: "), sg.Text("", key="agent-pos", size=(20, None))],
    [sg.Text("Agent speed: "), sg.Text("", key="agent-speed", size=(20, None))],
    [sg.Text("Agent rotation: "), sg.Text("", key="agent-rotation", size=(20, None))],
    [sg.Text("Agent destination: "), sg.Text("", key="agent-destination", size=(20, None))],
    [sg.Text("Agent base speed: "),
     sg.Slider(range=(0, 255), default_value=50, key="agent-base-speed", enable_events=True, resolution=1,
               orientation="h")],
    [sg.Text("Agent debug msg: "),
     sg.Text("", key="agent-debug", size=(20, None))],
], key="agent-column", metadata=-1)


def agent_gui_event(event: str, values, window: sg.Window, env_process: EnvProcess):
    if window["agent-column"].metadata != -1:
        ant: Agent
        ant = env_process.ants[window["agent-column"].metadata]
        pos = "( " + str(ant.xy[0]) + " , " + str(ant.xy[1]) + " )"
        dest = ("( " + str(ant.destination[0]) + " , " + str(ant.destination[1]) + " )")
        window["agent-color"].update(ant.color)
        window["agent-pos"].update(str(pos))

        window["agent-speed"].update("%.2f" % ant.speed)
        window["agent-rotation"].update("%.2f" % ant.rotation)
        window["agent-destination"].update(dest)

        # print("debug", debug)
        # window["agent-debug"].update(unpack("i", debug))

        if event == "agent-base-speed":
            ant: Agent
            ant = env_process.ants[window["agent-column"].metadata]
            ant.send_speed_base(int(values["agent-base-speed"]))
            debug = ant.con.readCharacteristic(ant.chars.debug)
            window["agent-debug"].update(unpack("i", debug))
