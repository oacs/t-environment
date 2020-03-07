import PySimpleGUI as sg
import tool as getConfigFile
from menu.menu import menu_el
sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.
layout = [
    [menu_el],
    [sg.Text('Some text on Row 1')],
    [sg.Text('Enter something on Row 2'), sg.InputText()],
    [sg.Button('Ok'), sg.Button('Cancel')]
]

# Create the Window
window = sg.Window('UCAB-Bot Environment', layout, location=(0, 0),
                   size=(800, 600), keep_on_top=True).Finalize()
window.Maximize()
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()

    if event in (None, 'Cancel'):   # if user closes window or clicks cancel
        break
    print('You entered ', values, event)

window.close()
