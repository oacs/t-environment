import PySimpleGUI as sg
import cv2
import tool as get_config_file
import threading
import queue
from agent import agent_gui, agent_gui_event
from cli import cli, cli_events, cli_keys
from menu.menu import menu_el
from actions.action import action_layout, action_events, action_keys
from theme import DARK, WHITE
from graph import graph, graph_events, graph_keys
from opencv.main import EnvProcess

sg.theme('DarkBlack1')  # Add a touch of color
# All the stuff inside your window.

actions = sg.Column(layout=[action_layout],
                    background_color=WHITE, pad=(0, 0))

layout = [
    [menu_el],
    [actions],
    [graph, agent_gui],
    [cli],
]

# Create the Window
window = sg.Window('UCAB-Bot Environment', layout, location=(0, 0), margins=(0, 0),
                   size=(1500, 900), resizable=True, background_color=DARK, metadata={
        "last_update": 0
    }).Finalize()

graph_elem = window['GRAPH']  # type sg.Graph
main_queue = queue.Queue()
env_process = EnvProcess(0, 0, 4, max_ants=1)
env_process.start_thread(main_queue)
actions.expand(expand_x=True, expand_y=False, expand_row=False)
cli.expand(expand_y=True)
cli_output: sg.Multiline = window["cli-output"]
cli_output.expand(expand_x=True, expand_row=True, expand_y=True)


def process_events(event: str, values: list, window: sg.Window) -> None:
    if event in action_keys:
        action_events(event, values, window)
    if event in cli_keys:
        cli_events(event, values, window)


# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read(timeout=20)
    # print(event)

    process_events(event, values, window)
    graph_events(event, values, window, env_process)
    agent_gui_event(event, values, window, env_process)
    # print(main_queue.qsize())
    try:  # see if something has been posted to Queue
        message = main_queue.get_nowait()
    except queue.Empty:  # get_nowait() will get exception when Queue is empty
        # print("queue empty")
        message = None
        # break from the loop if no more messages are queued up
        # if message received from queue, display the message in the Window
    if message is not None:
        if message["event"] is not None and message["values"] is not None:
            process_events(message["event"], message["values"], window)
            # graph_events(message["event"], message["values"], window, env_process)
            # agent_gui_event(message["event"], message["values"], window, env_process)
        # window.refresh()
        # print(message)
    # print(event)
    if event not in ("__TIMEOUT__", "graph", "agent-base-speed"):
        print('You entered ', values, event)
    # if event in (None, 'Cancel'):  # if user closes window or clicks cancel
    #     break
    else:
        continue

window.close()
