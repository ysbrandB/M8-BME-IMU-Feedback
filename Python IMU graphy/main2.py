import sys
import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import numpy as np

from CreaTeBME import connect

frame_rate = 60
sensors = connect()

xs = []
ys = []

for sensor in sensors:
    xs.append([[] for x in range(6)])
    ys.append([[] for x in range(6)])

limit = 500
counter = 0
figs, axs = plt.subplots(2, len(sensors))


def take_measurement():
    while True:
        loop_time = time.perf_counter()
        global counter
        for i, sensor in enumerate(sensors):
            measurement = sensor.take_measurement()
            for j, measure in enumerate(measurement):
                xs[i][j].append(counter)
                ys[i][j].append(measure)
                if len(xs[i][j]) > limit:
                    xs[i][j].pop(0)
                if len(ys[i][j]) > limit:
                    ys[i][j].pop(0)
        counter += 1



def update_graph(counter):
    for i, sensor in enumerate(sensors):
        axs[0][i].clear()
        axs[1][i].clear()
        axs[1][i].set_ylim([-500, 500])
        axs[0][i].set_ylim([-5, 5])
        for j in range(3):
            axs[0][i].plot(xs[i][j], ys[i][j])
        for j in range(3, 6):
            axs[1][i].plot(xs[i][j], ys[i][j])


ani = animation.FuncAnimation(figs, update_graph, interval=1/frame_rate)
thread = threading.Thread(target=take_measurement)
thread.daemon = True
thread.start()
plt.show()
