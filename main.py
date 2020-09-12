''' main module '''
import queue

import PySimpleGUI as sg

from actions.action import ACTION_KEYS, ACTION_LAYOUT, action_events
from cli import cli, cli_events, cli_keys
from graph import graph_events, graph_tabs
from menu.menu import MENU_EL
from opencv.main import EnvProcess
from theme import DARK, WHITE
from tool.tools import TOOLS_GUI, tools_events
from utils.json import read_config

sg.theme('DarkBlack1')  # Add a touch of color
# All the stuff inside your window.

ACTIONS = sg.Column(layout=[ACTION_LAYOUT],
                    background_color=WHITE, pad=(0, 0))

LAYOUT = [
    [MENU_EL],
    [ACTIONS],
    [graph_tabs, TOOLS_GUI],
    [cli],
]

# Create the Window
WINDOW = sg.Window('UCAB-Bot Environment', LAYOUT, location=(0, 0),
                   margins=(0, 0),
                   size=(1500, 900), resizable=True, background_color=DARK,
                   metadata={
                       "last_update": 0,
                       "tempPos": (0, 0)}
                   ).Finalize()

GRAPH_ELEM = WINDOW['MAIN-GRAPH']  # type sg.Graph
GRAPH_ELEM.bind('<Motion>', "-MOUSE-MOTION")
MAIN_QUEUE = queue.Queue()
ENV_PROCESS = EnvProcess(2, 0, 3, read_config())
ENV_PROCESS.start_thread(MAIN_QUEUE)

# window["MAIN-GRAPH"].set_size((env_process.video.width,
# env_process.video.height))
# window["COLORS-GRAPH"].set_size((env_process.video.width,
# env_process.video.height))
# window["BORDERS-GRAPH"].set_size((env_process.video.width,
# env_process.video.height))
# print((env_process.video.width, env_process.video.height))

# cli.set_size((env_process.video.width, env_process.video.height))
# actions.expand(expand_x=True, expand_y=False, expand_row=False)
# cli.expand(expand_y=True)
cli_output: sg.Multiline = WINDOW["cli-output"]
cli_output.expand(expand_x=True, expand_row=False, expand_y=True)


def process_events(event_type: str, event_values: dict,
                   _window: sg.Window, process: EnvProcess) -> None:
    ''' map the events and proccees them '''
    if event_type in ACTION_KEYS:
        action_events(event_type, event_values, _window, process)
    if event_type in cli_keys:
        cli_events(event_type, event_values, _window, process)


# Event Loop to process "events" and get the "values" of the inputs
while True:
    EVENT, VALUES = WINDOW.read(timeout=20)
    # print(event)

    process_events(EVENT, VALUES, WINDOW, ENV_PROCESS)
    graph_events(EVENT, VALUES, WINDOW, ENV_PROCESS)
    tools_events(EVENT, VALUES, WINDOW, ENV_PROCESS)
    # print(main_queue.qsize())
    try:  # see if something has been posted to Queue
        MESSAGE = MAIN_QUEUE.get_nowait()
    except queue.Empty:  # get_nowait() will get exception when Queue is empty
        # print("queue empty")
        MESSAGE = None
        # break from the loop if no more messages are queued up
        # if message received from queue, display the message in the Window
    if MESSAGE is not None:
        if MESSAGE["event"] is not None and MESSAGE["values"] is not None:
            process_events(MESSAGE["event"],
                           MESSAGE["values"], WINDOW, ENV_PROCESS)
            # graph_events(message["event"], message["values"],
            # window, env_process)
            # agent_gui_event(message["event"], message["values"],
            # window, env_process)
        # window.refresh()
        print(MESSAGE)
    # print(event)
    if EVENT not in ("__TIMEOUT__", "graph",
                     "agent-base-speed", "MAIN-GRAPH-MOUSE-MOTION"):
        # print(window["MAIN-GRAPH"].user_bind_event)
        print('You entered ', EVENT, VALUES)
    if EVENT in (None, 'Cancel'):  # if user closes window or clicks cancel
        break

WINDOW.close()
