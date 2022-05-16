import sys
import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import numpy as np

from CreaTeBME import connect

frame_rate = 60
sensors = connect()
sensor = sensors[0]
xs = [[] for x in range(6)]
ys = [[] for x in range(6)]
limit = 500
counter = 0
figs, axs = plt.subplots(2)


def take_measurement():
    while True:
        loop_time = time.perf_counter()
        global sensor, counter
        measurement = sensor.take_measurement()
        for i, measure in enumerate(measurement):
            xs[i].append(counter)
            ys[i].append(measure)
            if len(xs[i]) > limit:
                xs[i].pop(0)
            if len(ys[i]) > limit:
                ys[i].pop(0)
        counter += 1



def update_graph(counter):
    axs[0].clear()
    axs[1].clear()
    axs[1].set_ylim([-500, 500])
    axs[0].set_ylim([-5, 5])
    for i in range(3):
        axs[0].plot(xs[i], ys[i])
    for i in range(3, 6):
        axs[1].plot(xs[i], ys[i])


ani = animation.FuncAnimation(figs, update_graph, interval=1/frame_rate)
thread = threading.Thread(target=take_measurement)
thread.daemon = True
thread.start()
plt.show()