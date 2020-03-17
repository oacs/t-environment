import PySimpleGUI as sg

from opencv.forms.color import GREEN_CONF, PURPLE_CONF, ColorFilter, Colors
from opencv.main import EnvProcess

mask_gui = sg.Column([
    [sg.Text("Select default config: "), sg.Combo(["Purple mask", "Green mask", "Empty mask"], key="mask-combo", enable_events=True)],
    [sg.Text("Min Hue: "),
     sg.Slider(range=(0, 255), orientation="h", disabled=False, key="mask-min-hue", size=(80, 20))],
    [sg.Text("Max Hue: "),
     sg.Slider(range=(0, 255), orientation="h", disabled=False, key="mask-max-hue", size=(80, 20))],
    [sg.Text("Min Sat: "),
     sg.Slider(range=(0, 255), orientation="h", disabled=False, key="mask-min-sat", size=(80, 20))],
    [sg.Text("Max Sat: "),
     sg.Slider(range=(0, 255), orientation="h", disabled=False, key="mask-max-sat", size=(80, 20))],
    [sg.Text("Min Val: "),
     sg.Slider(range=(0, 255), orientation="h", disabled=False, key="mask-min-val", size=(80, 20))],
    [sg.Text("Max Val: "),
     sg.Slider(range=(0, 255), orientation="h", disabled=False, key="mask-max-val", size=(80, 20))],

], key="mask-column", metadata=-1)

last_update = 0


def mask_gui_event(event: str, values: dict, window: sg.Window, env_process: EnvProcess):
    if event == "mask-combo":
        conf = ColorFilter(Colors.unset, 0, 255, 0, 255, 0, 255, 0, 0, 0)
        if values["mask-combo"] == "Purple mask":
            conf = PURPLE_CONF
        elif values["mask-combo"] == "Green mask":
            conf = GREEN_CONF
        window["mask-min-hue"].update(conf.low_hsb[0])
        window["mask-max-hue"].update(conf.max_hsb[0])
        window["mask-min-sat"].update(conf.low_hsb[1])
        window["mask-max-sat"].update(conf.max_hsb[1])
        window["mask-min-val"].update(conf.low_hsb[2])
        window["mask-max-val"].update(conf.max_hsb[2])
