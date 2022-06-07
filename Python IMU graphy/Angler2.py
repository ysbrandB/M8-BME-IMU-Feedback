import sys
import time
import math

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
    xs.append([[] for x in range(6+1)])
    ys.append([[] for x in range(6+1)])

limit = 500
counter = 0
figs, axs = plt.subplots(3, len(sensors), figsize=(10, 6))


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

            angle_calc(i, measurement)
            xs[i][6].append(counter)
            if len(xs[i][6]) > limit:
                xs[i][6].pop(0)
            if len(ys[i][6]) > limit:
                ys[i][6].pop(0)
        counter += 1


def angle_calc(sensor_id, measurement):
    base_x = 0
    base_y = 0
    base_z = 1
    acc_x = measurement[0] - base_x
    acc_y = measurement[1] - base_y
    acc_z = measurement[2] - base_z

    initial_x_angle = math.atan(acc_x / math.sqrt(acc_y ** 2 + acc_z ** 2))
    initial_y_angle = math.atan(acc_y / math.sqrt(acc_x ** 2 + acc_z ** 2))

    average_angle = []

    if len(average_angle) < 120:
        average_angle.append(initial_x_angle)
    else:
        average_angle.pop(0)

    average = 0
    for i in range(len(average_angle)):
        average += average_angle[i]
        average = average/len(average_angle)

    ys[sensor_id][6].append(average)
    # print(average)

def update_graph(counter):
    if len(sensors) > 1:
        for i in range (len(sensors)):
            axs[0][i].clear()
            axs[1][i].clear()
            axs[1][i].set_ylim([-500, 500])
            axs[0][i].set_ylim([-5, 5])
            for j in range(3):
                axs[0][i].plot(xs[i][j], ys[i][j])
            for j in range(3, 6):
                axs[1][i].plot(xs[i][j], ys[i][j])
    else:
        axs[0].clear()
        axs[1].clear()
        axs[2].clear()
        axs[1].set_ylim([-500, 500])
        axs[0].set_ylim([-5, 5])
        axs[2].set_ylim([-1, 1])
        for i in range(3):
            axs[0].plot(xs[0][i], ys[0][i])
        for i in range(3, 6):
            axs[1].plot(xs[0][i], ys[0][i])

        axs[2].plot(xs[0][6], ys[0][6])


ani = animation.FuncAnimation(figs, update_graph, interval=1/frame_rate)
thread = threading.Thread(target=take_measurement)
thread.daemon = True
thread.start()
plt.show()
