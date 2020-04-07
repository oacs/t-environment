from PySimpleGUI import Menu, FileBrowse

menu_def = [
    ['File', ['z', 'Save', 'Exit', ]],
    ['Help', 'About...']
]

menu_el = Menu(menu_def)
