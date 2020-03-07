import PySimpleGUI as sg
import cv2
import tool as getConfigFile
from menu.menu import menu_el
from actions.action import action_layout, action_events
from theme import DARK
from opencv.main import EnvProcess
sg.theme('DarkBlack1')   # Add a touch of color
# All the stuff inside your window.
layout = [
    [menu_el],
    action_layout,
    [sg.Image(filename='', key='image', size=(400, 400))]
]

# Create the Window
window = sg.Window('UCAB-Bot Environment', layout, location=(0, 0),
                   size=(1500, 900), resizable=True, background_color=DARK).Finalize()
# window.Maximize()
env_process = EnvProcess()
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read(timeout=20)

    action_events(event, values, window)
    frame = env_process.read()
    if window["action_play_pause"].metadata["status"] == "play":
        imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
        window['image'].update(data=imgbytes)
    if event in (None, 'Cancel'):   # if user closes window or clicks cancel
        break

    if event not in ("__TIMEOUT__"):
        print('You entered ', values, event)

window.close()
