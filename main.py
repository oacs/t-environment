import queue

import PySimpleGUI as sg

from actions.action import action_layout, action_events, action_keys
from tool.tools import tools_gui, tools_events
from cli import cli, cli_events, cli_keys
from graph import graph_tabs, graph_events
from menu.menu import menu_el
from opencv.main import EnvProcess
from theme import DARK, WHITE

sg.theme('DarkBlack1')  # Add a touch of color
# All the stuff inside your window.

actions = sg.Column(layout=[action_layout],
                    background_color=WHITE, pad=(0, 0))

layout = [
    [menu_el],
    [actions],
    [graph_tabs, tools_gui],
    [cli],
]

# Create the Window
window = sg.Window('UCAB-Bot Environment', layout, location=(0, 0), margins=(0, 0),
                   size=(1500, 900), resizable=True, background_color=DARK, metadata={
        "last_update": 0,
        "tempPos": (0,0)
    }).Finalize()

graph_elem = window['MAIN-GRAPH']  # type sg.Graph
graph_elem.bind('<Motion>', "-MOUSE-MOTION")
main_queue = queue.Queue()
env_process = EnvProcess(2, 0, 4, max_ants=1)
env_process.start_thread(main_queue)
# window["MAIN-GRAPH"].set_size((env_process.video.width, env_process.video.height))
# window["COLORS-GRAPH"].set_size((env_process.video.width, env_process.video.height))
# window["BORDERS-GRAPH"].set_size((env_process.video.width, env_process.video.height))
# print((env_process.video.width, env_process.video.height))

# cli.set_size((env_process.video.width, env_process.video.height))
actions.expand(expand_x=True, expand_y=False, expand_row=False)
# cli.expand(expand_y=True)
cli_output: sg.Multiline = window["cli-output"]
cli_output.expand(expand_x=True, expand_row=False, expand_y=True)


def process_events(event_type: str, event_values: dict, _window: sg.Window, process: EnvProcess) -> None:
    if event_type in action_keys:
        action_events(event_type, event_values, _window, process)
    if event_type in cli_keys:
        cli_events(event_type, event_values, _window, process)


# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read(timeout=20)
    # print(event)

    process_events(event, values, window, env_process)
    graph_events(event, values, window, env_process)
    tools_events(event, values, window, env_process)
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
            process_events(message["event"], message["values"], window, env_process)
            # graph_events(message["event"], message["values"], window, env_process)
            # agent_gui_event(message["event"], message["values"], window, env_process)
        # window.refresh()
        print(message)
    # print(event)
    if event not in ("__TIMEOUT__", "graph", "agent-base-speed", "MAIN-GRAPH-MOUSE-MOTION"):
        # print(window["MAIN-GRAPH"].user_bind_event)
        print('You entered ', event, values )
    # if event in (None, 'Cancel'):  # if user closes window or clicks cancel
    #     break
    else:
        continue

window.close()
