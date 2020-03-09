import PySimpleGUI as sg

from opencv.agent.agent import Agent
from opencv.main import EnvProcess

agent_gui = sg.Column([
    [sg.Text("Agent color: "), sg.Text("", key="agent-color")],
    [sg.Text("Agent pos: "), sg.Text("", key="agent-pos", size=(20, None))],
    [sg.Text("Agent speed: "), sg.Text("", key="agent-speed", size=(20, None))],
    [sg.Text("Agent rotation: "), sg.Text("", key="agent-rotation", size=(20, None))],
    [sg.Text("Agent destination: "), sg.Text("", key="agent-destination", size=(20, None))],
], key="agent-column", metadata=-1)


def agent_gui_event(window: sg.Window, env_process: EnvProcess):
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
        print(pos, dest)
