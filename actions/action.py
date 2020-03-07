from PySimpleGUI import Button, TRANSPARENT_BUTTON
from theme import WHITE, DARK

on_play = False
action_layout = [
    Button(
        button_text="",
        tooltip="Play the simulation",
        bind_return_key="space",
        button_color=[DARK, DARK],
        image_filename="assets/img/play.png",
        image_size=[35, 35],
        border_width=0,
        key="action_play_pause",
        disabled=(on_play),
        metadata={
            "status": "play"
        }
    ),
    Button(
        button_text="",
        tooltip="Play the simulation",
        bind_return_key="space",
        button_color=[DARK, DARK],
        image_filename="assets/img/save.png",
        image_size=[35, 35],
        border_width=0,
        key="action_save"
    ),
]


def action_events(event, value, window):
    if (event == "action_play_pause"):
        print(window["action_play_pause"].metadata,
              )
        if window["action_play_pause"].metadata["status"] == "pause":
            window["action_play_pause"].metadata["status"] = "play"
        else:
            window["action_play_pause"].metadata["status"] = "pause"
        window["action_play_pause"].update(
            image_filename="assets/img/" + window["action_play_pause"].metadata["status"]+".png")
