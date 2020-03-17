from opencv.main import EnvProcess
from tool.agent import agent_gui_event, agent_gui
from tool.mask import mask_gui_event, mask_gui
from PySimpleGUI import Column, Window

tools_gui = Column([[mask_gui, agent_gui]])


def tools_events(event: str, values: dict, window: Window, env_process: EnvProcess):
    agent_gui_event(event, values, window, env_process)
    mask_gui_event(event, values, window, env_process)
