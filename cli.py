from typing import Any, Union

import PySimpleGUI as sg

from actions.action import action_events
from theme import DARK, WHITE, INFO, BLACK, DANGER

cli = sg.Column([
    [sg.Multiline("", disabled=True, key="cli-output", size=(20, 14), font=('Helvetica', 15, 'bold'),
                  background_color=BLACK, text_color=WHITE)],
    [sg.InputText("", disabled=False, key="cli-input", size=(80, 20)),
     sg.Button('enter-input', bind_return_key=True, visible=False)]
], size=(600, 450))

cli_keys = ["cli-output", "cli-input", "enter-input", "env-message"]


def cli_events(event: str, values: object, window: sg.Window) -> None:
    """
    Args:
        event:
        values:
        window:
    Returns:

    """
    cli_input: sg.InputText = window["cli-input"]
    cli_output: sg.Multiline = window["cli-output"]
    print((event, values))
    if event == "enter-input":
        send_user_message(values["cli-input"], cli_output)
        cli_input.update("")
        process_command(values["cli-input"], window)
    if event == "env-message":
        if values["type"] == "info":
            send_info_message(values["message"], cli_output)
        elif values["type"] == "error":
            send_error_message(values["message"], cli_output)
    return


def process_command(command: str, window: sg.Window):
    cli_output: sg.Multiline = window["cli-output"]
    if command == "start" or command == "play":
        if window["action_play_pause"].metadata["status"] == "pause":
            action_events("action_play_pause", {}, window)
            send_info_message("Successfully started", cli_output)
        else:
            send_error_message("Program already started", cli_output)
    elif command == "pause" or command == "stop":
        if window["action_play_pause"].metadata["status"] == "play":
            action_events("action_play_pause", {}, window)
            send_info_message("Simulation paused", cli_output)
        else:
            send_error_message("Program already paused", cli_output)
    else:
        send_error_message("Unknown command", cli_output)
    return


def send_user_message(text: str, output: sg.Multiline):
    output.update("\nUser: ", text_color_for_value=INFO, append=True, autoscroll=True)
    output.update(text, text_color_for_value=WHITE, append=True, autoscroll=True)
    return


def send_error_message(error: str, output: sg.Multiline):
    output.update("\nError: ", text_color_for_value=DANGER, append=True, autoscroll=True)
    output.update(error, text_color_for_value=DANGER, append=True, autoscroll=True)
    return


def send_info_message(info: str, output: sg.Multiline):
    output.update("\nEnv: ", text_color_for_value=INFO, append=True, autoscroll=True)
    output.update(info, text_color_for_value=INFO, append=True, autoscroll=True)
    return


def output_message(text: str, type_message: str):
    return {
        "event": "env-message",
        "values": {
            "message": text,
            "type": type_message
        }
    }
