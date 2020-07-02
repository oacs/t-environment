import json
from opencv.forms.color import Colors, YELLOW_CONF, GREEN_CONF


def read_config():
    with open('config.json') as json_file:
        data = json.load(json_file)
        possible_colors = list()
        for color in data['possible_colors']:
            if color is Colors.green.value:
                possible_colors.append(GREEN_CONF)
            elif color is Colors.yellow.value:
                possible_colors.append(YELLOW_CONF)
            # elif color is Colors.blue:
            #     possible_colors.append(BLUE_CONF)
        print(possible_colors)
    return data
