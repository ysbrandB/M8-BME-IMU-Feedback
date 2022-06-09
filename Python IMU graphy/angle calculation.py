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
    xs.append([])
    ys.append([])

limit = 500
counter = 0
figs, axs = plt.subplots(3, len(sensors), figsize=(10, 6))


def take_measurement():
    while True:
        global counter
        for i, sensor in enumerate(sensors):
            xs[i].append(counter)
            ys[i].append(1)

            if len(xs[i]) > limit:
                xs[i].pop(0)
            if len(ys[i]) > limit:
                ys[i].pop(0)
        counter += 1


            # measurement = sensor.take_measurement()
            # for j, measure in enumerate(measurement):
            #     xs[i][j].append(counter)
            #     ys[i][j].append(measure)
            #     if len(xs[i][j]) > limit:
            #         xs[i][j].pop(0)
            #     if len(ys[i][j]) > limit:
            #         ys[i][j].pop(0)
            #
            #     if j == 3:
            #         calculate_value(measurement, counter, i)


# def calculate_value(gyro_x, counter, sensor_num):
#     angle = gyro_x
#
#     xs[sensor_num][6].append(counter)
#     ys[sensor_num][6].append(angle)
#     if len(xs[sensor_num][6]) > limit:
#         xs[sensor_num][6].pop(0)
#     if len(ys[sensor_num][6]) > limit:
#         ys[sensor_num][6].pop(0)


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
            for j in range(6, 7):
                axs[2][i].plot(xs[i][j], ys[i][j])
    else:
        axs[0].clear()
        axs[1].clear()
        axs[1].set_ylim([-500, 500])
        axs[0].set_ylim([-5, 5])
        # for i in range(3):
        axs[0].plot(xs[0], ys[0])
        # for i in range(3, 6):
        #     axs[1].plot(xs[0][i], ys[0][i])
        # for i in range(6, 7):
        #     axs[2].plot(xs[0][i], ys[0][i])


if __name__ == '__main__':
    ani = animation.FuncAnimation(figs, update_graph, interval=1/frame_rate)
    thread = threading.Thread(target=take_measurement)
    thread.daemon = True
    thread.start()
    plt.show()
