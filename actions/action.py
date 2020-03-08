from PySimpleGUI import Button, Window
from theme import WHITE

action_layout = [
    Button(
        button_text="",
        tooltip="Play the simulation",
        # bind_return_key="p",
        button_color=[WHITE, WHITE],
        image_filename="assets/img/play.png",
        image_size=[35, 35],
        border_width=0,
        key="action_play_pause",
        disabled=False,
        metadata={
            "status": "play"
        }
    ),
    Button(
        button_text="",
        tooltip="Play the simulation",
        # bind_return_key="space",
        button_color=[WHITE, WHITE],
        image_filename="assets/img/save.png",
        image_size=[35, 35],
        border_width=0,
        key="action_save"
    ),
]


def action_events(event: str, value: object, window: Window):
    if event == "action_play_pause":
        if window["action_play_pause"].metadata["status"] == "pause":
            window["action_play_pause"].metadata["status"] = "play"
        else:
            window["action_play_pause"].metadata["status"] = "pause"
        window["action_play_pause"].update(
            image_filename="assets/img/" + window["action_play_pause"].metadata["status"]+".png")
