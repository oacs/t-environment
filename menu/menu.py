''' top menu '''
from PySimpleGUI import Menu

MENU_DEF = [
    ['File', ['z', 'Save', 'Exit', ]],
    ['Help', 'About...']
]

MENU_EL = Menu(MENU_DEF)
