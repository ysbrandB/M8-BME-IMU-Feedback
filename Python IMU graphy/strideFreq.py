import sys
import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import requests

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


def httpRequest(url):
    try:
        try:
            # requests.get(f"http://192.168.4.1/{url}", timeout=0.0000000001)
            pass
        except requests.exceptions.ReadTimeout:
            pass
    except requests.exceptions.ConnectTimeout:
        print(f"NOT CONNECT TO ESP")


def calc_stride_freq(i):
    global filteredImpact, peaks, stride_freq
    filteredImpact = [xs[i][3].copy(), filterLow(ys[i][3])]
    deltaTime = timeImpact[-1] - timeImpact[0]
    # print(deltaTime)
    peaks = signal.find_peaks(filteredImpact[1], height=2.8, distance=25)

    stride_freq = (len(peaks[0])) / deltaTime * 60
    # print(f"{stride_freq = }")

    # first get the average stride freq of the user for a minute
    if calibrationStartTime + calibrationTime > time.perf_counter():
        stride_freqs.append(stride_freq)
    else:  # then give feedback on it
        #  compare the current stride_freq with the sum(stride_freq)/len(stride_freq). als het 10% verschil heeft dan feedback.
        average_impact_calibration = np.average(np.asarray(stride_freqs))
        # print(f"{average_impact_calibration = }, {stride_freq = }, {average_impact_calibration * 0.1 = }")
        if abs(average_impact_calibration - stride_freq) > average_impact_calibration * 0.1:
            url = 'smaller'
            if average_impact_calibration < stride_freq:
                url = 'bigger'
            httpRequest(url)
            # print(f"http://192.168.4.1/{url}")


def calc_shock_attenuation(leg, hip):
    steps = 10
    # reference = 80
    sAtt = (1 - hip / leg) * 100
    if sAtt > 0:
        att_list.append(sAtt)
    if len(att_list) > steps:
        att_list.pop(0)

    attAverage = 0

    for x in range(len(att_list)):
        attAverage += att_list[x] / len(att_list)

    return attAverage

def impact_attenuation():
    global foot_peaks
    foot_peaks = signal.find_peaks(ys[0][3], height=2.5)
    for j in foot_peaks[0]:
        print(calc_shock_attenuation(ys[0][3][j], ys[1][3][j]))
        print(ys[0][3][j], ys[1][3][j])

def take_measurement():
    old_time = time.perf_counter()
    impacts_foot = []
    shock_attenuation = []

    while True:
        loop_time = time.perf_counter()
        global counter
        for i, sensor in enumerate(sensors):
            measurement = sensor.take_measurement()
            for j, measure in enumerate(measurement[:3:]):
                xs[i][j].append(counter)
                ys[i][j].append(measure)
                if len(xs[i][j]) > limit:
                    xs[i][j].pop(0)
                if len(ys[i][j]) > limit:
                    ys[i][j].pop(0)

            timeImpact.append(time.perf_counter())
            if len(xs[i][3]) > limit:
                xs[i][3].pop(0)
            if len(ys[i][3]) > limit:
                ys[i][3].pop(0)
            if len(timeImpact) > limit:
                timeImpact.pop(0)

            # low pass filter and calculate step freq
            if old_time + 5 < time.perf_counter() and i == 0 and time.perf_counter() - startTime >= 1:
                old_time = time.perf_counter()
                calc_stride_freq(i)

                # for j in peaks[0][1]:
                #     print(calc_shock_attenuation(ys[0][3][j], ys[1][3][j]))
                #     print(ys[0][3][j], ys[1][3][j])
                # print(peaks[1][j])
                impact_attenuation()
            array = np.array(measurement[:3])
            normalized_vector = np.linalg.norm(array)

            ys[i][3].append(normalized_vector)
            xs[i][3].append(counter)
        # print(peaks[0][1])

        counter += 1


def update_graph(counter):
    if len(sensors) > 1:
        for i in range(len(sensors)):
            axs[0][i].clear()
            axs[1][i].clear()
            axs[1][i].set_ylim([0, 10])
            axs[0][i].set_ylim([-5, 5])
            axs[1][i].grid(True)
            axs[0][i].grid(True)
            for j in range(3):
                axs[0][i].plot(xs[i][j][::5], ys[i][j][::5])

        axs[1][0].plot(xs[0][3], ys[0][3])
        axs[1][0].plot(filteredImpact[0], filteredImpact[1])
        axs[1][1].plot(xs[1][3], ys[1][3])
        for i in peaks[0]:
            p = axs[1][0].add_patch(plt.Circle((filteredImpact[0][i], filteredImpact[1][i]), 0.5, alpha=1))
            p.set_color((0, 1, 0))

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

        for i in peaks[0]:
            p = axs[1].add_patch(plt.Circle((filteredImpact[0][i], filteredImpact[1][i]), 0.5, alpha=1))
            p.set_color((0, 1, 0))


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
    peaks = [[], []]
    att_list = []
    counter = 0
    stride_freq = 0

    stride_freqs = []

    startTime = time.perf_counter()
    calibrationTime = 20  # 60*3
    calibrationStartTime = time.perf_counter()
    httpRequest('calibrate')

    figs, axs = plt.subplots(2, len(sensors), figsize=(10, 6))

    ani = animation.FuncAnimation(figs, update_graph, interval=1 / frame_rate)
    thread = threading.Thread(target=take_measurement, daemon=True)
    thread.start()
    plt.show()
