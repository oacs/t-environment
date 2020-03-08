import PySimpleGUI as sg
import cv2
import tool as get_config_file
from menu.menu import menu_el
from actions.action import action_layout, action_events
from theme import DARK, WHITE
from graph import graph, graph_events
from opencv.main import EnvProcess

sg.theme('DarkBlack1')  # Add a touch of color
# All the stuff inside your window.

actions = sg.Column(layout=[action_layout],
                    background_color=WHITE, pad=(0, 0))

layout = [
    [menu_el],
    [actions],
    []
]

# Create the Window
window = sg.Window('UCAB-Bot Environment', layout, location=(0, 0), margins=(0, 0),
                   size=(1500, 900), resizable=True, background_color=DARK).Finalize()

graph_elem = window['-GRAPH-']  # type sg.Graph
env_process = EnvProcess()
actions.expand(expand_x=True)

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read(timeout=20)

    action_events(event, values, window)
    graph_events(event, values, window, env_process.read)

    if event in (None, 'Cancel'):  # if user closes window or clicks cancel
        break

    if event not in ("__TIMEOUT__", "graph"):
        print('You entered ', values, event)

window.close()
