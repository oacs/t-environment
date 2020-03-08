import cv2
from PySimpleGUI import Graph, Window
graph = Graph((600, 450), (0, 450), (600, 0), key='GRAPH',
              enable_events=True, drag_submits=True, metadata={
        "a_id": None
    })


def graph_events(event, values, window: Window, read):
    frame = read()
    img_bytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
    if window["GRAPH"].metadata["a_id"]:
        # delete previous image
        window["GRAPH"].delete_figure(window["GRAPH"].metadata["a_id"])
    a_id = window["GRAPH"].draw_image(
        data=img_bytes, location=(0, 0))    # draw new image
    # move image to the "bottom" of all other drawings
    window["GRAPH"].TKCanvas.tag_lower(a_id)

    if event == 'GRAPH':
        window["GRAPH"].draw_circle(
            values['GRAPH'], 5, fill_color='red', line_color='red')
