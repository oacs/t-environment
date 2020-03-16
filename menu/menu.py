from PySimpleGUI import Menu

menu_def = [
    ['File', ['Open', 'Save', 'Exit', ]],
    ['Help', 'About...']
]

menu_el = Menu(menu_def)
