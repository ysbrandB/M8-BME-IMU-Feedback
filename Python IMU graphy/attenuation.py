import sys
import time
import math
import scipy

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

            stride_length(i, measurement)
            xs[i][6].append(counter)
            if len(xs[i][6]) > limit:
                xs[i][6].pop(0)
            if len(ys[i][6]) > limit:
                ys[i][6].pop(0)
        counter += 1


def attenuation(s1, s2):
    sensorLeg = s1
    sensorHip = s2
    Satt = (1 - sensorLeg/sensorHip) * 100
    return Satt

att_list = []
def Danger(Satt):
    att_list.append(Satt)
    attAverage = 0
    for x in range(len(att_list)):
        attAverage += att_list[x]/len(att_list)
    if attAverage < 80:
        return True
    else:
        return False

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
        axs[2].set_ylim([-100, 100])
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
