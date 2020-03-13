from opencv.forms.triangle import get_triangle
import cv2
import queue
from opencv.main import EnvProcess

main_queue = queue.Queue()
env_process = EnvProcess(0, 0, 4, max_ants=1)
# env_process.start_thread(main_queue)

while True:
    frame = env_process.video.read()
    # t, frame2, mask =  get_triangle(frame)
    # cv2.imshow('mas02k', mask)
    cv2.imshow('frame-triangle', frame)

