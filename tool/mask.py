from PySimpleGUI import  Text, Slider, Column, Window, Combo

from opencv.forms.color import GREEN_CONF, YELLOW_CONF, ColorFilter, Colors
from opencv.main import EnvProcess

mask_gui = Column([
    [Text("Select default config: "), Combo(["Purple mask", "Green mask", "Empty mask"], key="mask-combo", enable_events=True)],
    [Text("Min Hue: "),
     Slider(range=(0, 255), orientation="h", disabled=False, key="mask-min-hue", size=(80, 20))],
    [Text("Max Hue: "),
     Slider(range=(0, 255), default_value=255, orientation="h", disabled=False, key="mask-max-hue", size=(80, 20))],
    [Text("Min Sat: "),
     Slider(range=(0, 255), orientation="h", disabled=False, key="mask-min-sat", size=(80, 20))],
    [Text("Max Sat: "),
     Slider(range=(0, 255), default_value=255, orientation="h", disabled=False, key="mask-max-sat", size=(80, 20))],
    [Text("Min Val: "),
     Slider(range=(0, 255), orientation="h", disabled=False, key="mask-min-val", size=(80, 20))],
    [Text("Max Val: "),
     Slider(range=(0, 255), default_value=255, orientation="h", disabled=False, key="mask-max-val", size=(80, 20))],

], key="mask-column", metadata=-1, visible=False)

last_update = 0


def mask_gui_event(event: str, values: dict, window: Window, env_process: EnvProcess):
    if event == "mask-combo":
        conf = ColorFilter(Colors.unset, 0, 255, 0, 255, 0, 255, 0, 0, 0)
        if values["mask-combo"] == "Purple mask":
            conf = YELLOW_CONF
        elif values["mask-combo"] == "Green mask":
            conf = GREEN_CONF
        window["mask-min-hue"].update(conf.low_hsb[0])
        window["mask-max-hue"].update(conf.max_hsb[0])
        window["mask-min-sat"].update(conf.low_hsb[1])
        window["mask-max-sat"].update(conf.max_hsb[1])
        window["mask-min-val"].update(conf.low_hsb[2])
        window["mask-max-val"].update(conf.max_hsb[2])
