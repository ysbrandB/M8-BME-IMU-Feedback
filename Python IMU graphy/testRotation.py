import math
import sys
import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import numpy as np

from CreaTeBME import connect

def take_measurement():
    while True:
        loop_time = time.perf_counter()
        global counter, gyro_x, gyro_z
        for i, sensor in enumerate(sensors):
            measurement = sensor.take_measurement()
            for j, measure in enumerate(measurement):
                xs[i][j].append(counter)
                ys[i][j].append(measure)
                if len(xs[i][j]) > limit:
                    xs[i][j].pop(0)
                if len(ys[i][j]) > limit:
                    ys[i][j].pop(0)

            xss.append(counter)
        #     calculate angle from acc.
            gyro_x += measurement[3]
            gyro_z += measurement[5]
            rotations[2].append(gyro_x)
            rotations[3].append(gyro_z)

            r = math.sqrt(measurement[0]**2 + measurement[1]**2 + measurement[2]**2)
            angle_x = math.acos(measurement[2] / r)
            if measurement[0] == 0:
                if measurement[1] == 0:
                    angle_z = 0
                else:
                    angle_z = 360
            else:
                angle_z = math.atan(measurement[1]/measurement[0])
            rotations[0].append(angle_x)
            rotations[1].append(angle_z)

            for j in range(0, 2):
                if len(rotations[j]) > limit:
                    rotations[j].pop(0)
            if len(xss) > limit:
                xss.pop(0)

        counter += 1


def update_graph(counter):
    if len(sensors) > 1:
        for i in range (len(sensors)):
            axs[0][i].clear()
            axs[1][i].clear()
            axs[2][i].clear()
            axs[1][i].set_ylim([-500, 500])
            axs[0][i].set_ylim([-5, 5])
            axs[2][i].set_ylim([-180, 180])
            for j in range(3):
                axs[0][i].plot(xs[i][j], ys[i][j])
            for j in range(3, 6):
                axs[1][i].plot(xs[i][j], ys[i][j])
    else:
        axs[0].clear()
        axs[1].clear()
        axs[2].clear()
        axs[1].set_ylim([-500, 500])
        axs[0].set_ylim([-180, 180])
        axs[2].set_ylim([-180, 180])
        for i in range(3):
            axs[0].plot(xs[0][i], ys[0][i])
        # for i in range(3, 6):
        #     axs[1].plot(xs[0][i], ys[0][i])

        try:
            # axs[1].plot(xss, rotations[2])
            axs[1].plot(xss, rotations[0])
            # axs[2].plot(xss, rotations[3])
            axs[2].plot(xss, rotations[1])
        except ValueError:
            print(f"ValueError: x and y must have same first dimension, but have shapes {len(xss)}and {len(rotations[0])}")
            xss.pop(0)


if __name__ == '__main__':
    frame_rate = 60
    sensors = connect()

    xs = []
    ys = []

    rotations = [[] for i in range(6)]
    xss = []

    gyro_x = 0
    gyro_z = 0

    for sensor in sensors:
        xs.append([[] for x in range(6)])
        ys.append([[] for x in range(6)])

    limit = 500
    counter = 0
    figs, axs = plt.subplots(3, len(sensors), figsize=(10, 6))
    ani = animation.FuncAnimation(figs, update_graph, interval=1/frame_rate)
    thread = threading.Thread(target=take_measurement)
    thread.daemon = True
    thread.start()
    plt.show()
