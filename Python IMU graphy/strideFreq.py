import sys
import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading

from scipy import signal
from scipy.signal import find_peaks
import numpy as np

from CreaTeBME import connect

# acc: x, y, z. Gyro: x, y, z


def filterLow(values):
    fs = 60  # Sampling frequency of the sensor
    fc = 5  # Cut-off frequency of the filter
    w = (2 * fc / fs)  # Normalize the frequency
    b, a = signal.butter(2, w, 'low')  # Create filter parameters
    filtered = signal.lfilter(b, a, values)
    return filtered


# def filtering():
#     global filteredImpact
#     old_time = time.perf_counter()
#     while True:
#         if old_time + 0.5 < time.perf_counter():
#             old_time = time.perf_counter()
#             # filteredImpact = [xs[0][3].copy(), filterLow(ys[0][3])]
#         # print(f"{len(filteredImpact[0]) = }, {len(filteredImpact[1]) = }")


def take_measurement():
    old_time = time.perf_counter()
    impacts_foot = []
    shock_attenuation = []

    while True:
        loop_time = time.perf_counter()
        global counter, stride_freq
        peaks = [[],[]]
        for i, sensor in enumerate(sensors):
            measurement = sensor.take_measurement()
            for j, measure in enumerate(measurement[:3:]):
                xs[i][j].append(counter)
                ys[i][j].append(measure)
                if len(xs[i][j]) > limit:
                    xs[i][j].pop(0)
                if len(ys[i][j]) > limit:
                    ys[i][j].pop(0)

            array = np.array(measurement[:2])
            normalizedVector = np.linalg.norm(array)

            ys[i][3].append(normalizedVector)
            xs[i][3].append(counter)
            timeImpact.append(time.perf_counter())
            if len(xs[i][3]) > limit:
                xs[i][3].pop(0)
            if len(ys[i][3]) > limit:
                ys[i][3].pop(0)
            if len(timeImpact) > limit:
                timeImpact.pop(0)

            # low pass filter and calculate step freq
            if old_time + 5 < time.perf_counter() and i == 0:
                global filteredImpact
                old_time = time.perf_counter()
                filteredImpact = [xs[i][3].copy(), filterLow(ys[i][3])]
                deltaTime = timeImpact[-1] - timeImpact[0]
                # print(deltaTime)
                peaks = signal.find_peaks(filteredImpact[1], height=2.8, distance=25)
                stride_freq = (len(peaks[0])*2)/deltaTime * 60
                print(f"{stride_freq = }")

        # print(signal.find_peaks(ys[0][1])[0])  # , height=35, distance=0.3*512))
        impacts_foot = [ys[0][3][i] for i in peaks[0]]
        # average_impact_foot = sum(impacts_foot) / len(impacts_foot)

        impacts_waist = [ys[1][3][i] for i in peaks[0]]

        for i in impacts_foot:
            shock_attenuation = (1- impacts_waist[i] / impacts_foot[i]) *100
        # average_impact_waist = sum(impacts_waist) / len(impacts_waist)
        # impacts_waist = [normalizedVector for i in peaks[0][1::2]]
        # average_impact_waist = sum(impacts_waist)/len(impacts_waist)

        # impacts_head_z = [df_head['acc_z'][i] for i in peaks_head_z[0][1::2]]
        # average_impact_head_z = sum(impacts_head_z) / len(impacts_head_z)

        print(impacts_foot)
        # print(f"{impacts_waist = :0.4f} m/s^2")
        # print(shock_attenuation)

        # print(f"total impact head = {math.sqrt(math.pow(average_impact_head_x, 2) + math.pow(average_impact_head_z, 2)):0.4f} m/s^2")
        # print(signal.find_peaks(ys[0][1])[0])  # , height=35, distance=0.3*512))

        counter += 1

        # global filteredImpact

        # old_time = time.perf_counter()
        # while True:
        #     if old_time + 0.5 < time.perf_counter():
        #         old_time = time.perf_counter()
        #         filteredImpact = [filterLow([0][3]), filterLow(ys[0][3])]
        #     print(f"{len(filteredImpact[0]) = }, {len(filteredImpact[1]) = }")
def update_graph(counter):
    if len(sensors) > 1:
        for i in range (len(sensors)):
            axs[0][i].clear()
            axs[1][i].clear()
            axs[1][i].set_ylim([-500, 500])
            axs[0][i].set_ylim([-5, 5])
            for j in range(3):
                axs[0][i].plot(xs[i][j], ys[i][j])
            # for j in range(3, 6):
            #     axs[1][i].plot(xs[i][j], ys[i][j])
    else:
        axs[0].clear()
        axs[1].clear()
        axs[1].set_ylim([0, 10])
        axs[0].set_ylim([-5, 5])
        axs[1].grid(True)
        axs[0].grid(True)
        # for i in range(3):
        axs[0].plot(xs[0][1], ys[0][1])
        axs[0].plot(xs[0][0], ys[0][0])
        # print(filteredImpact)
        axs[1].plot(xs[0][3], ys[0][3])
        axs[1].plot(filteredImpact[0], filteredImpact[1])

        # peaks = signal.find_peaks(filteredImpact[1], height=3)
        for i in peaks[0]:
            p = axs[1].add_patch(plt.Circle((filteredImpact[0][i], filteredImpact[1][i]), 0.5, alpha=1))
            p.set_color((0, 1, 0))
        # for i in range(3, 6):
        #     axs[1].plot(xs[0][i], ys[0][i])


if __name__ == '__main__':
    frame_rate = 60
    sensors = connect()

    xs = []
    ys = []

    filteredImpact = [[0], [0]]
    timeImpact = []

    # impacts_foot = []
    # impacts_waist = []
    #
    # shock_attenuation = []

    for sensor in sensors:
        xs.append([[] for i in range(4)])
        ys.append([[] for x in range(4)])

    limit = 500
    peaks = [[],[]]
    counter = 0
    stride_freq = 0
    figs, axs = plt.subplots(2, len(sensors), figsize=(10, 6))

    ani = animation.FuncAnimation(figs, update_graph, interval=1/frame_rate)
    thread = threading.Thread(target=take_measurement, daemon=True)
    # thread_filtered = threading.Thread(target=filtering, daemon=True)
    # thread.daemon = True
    # thread_filtered.daemon = True

    # setup code:
    # weight = input("What is your weight? ")

    thread.start()
    # thread_filtered.start()
    plt.show()
