''' tools main '''
from PySimpleGUI import Column, Window

from opencv.main import EnvProcess
from tool.agent import agent_gui, agent_gui_event
from tool.mask import mask_gui, mask_gui_event

TOOLS_GUI = Column([[mask_gui, agent_gui]])


def tools_events(event: str, values: dict, window: Window,
                 env_process: EnvProcess):
    ''' map all events of tools '''
    agent_gui_event(event, values, window, env_process)
    mask_gui_event(event, values, window, env_process)
