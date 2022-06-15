import sys
import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import requests
import atexit

from scipy import signal
import numpy as np
from CreaTeBME import connect
import Wifi
from Logging import print_error, print_waring, print_green, print_blue, print_cyan

# acc: x, y, z. Gyro: x, y, z

log = []

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
            print_cyan(f"send to esp: {url}")
            requests.get(f"http://192.168.4.1/{url}", timeout=0.2)  # , timeout=0.0000000001)
        except requests.exceptions.ReadTimeout:
            print_waring(f"couldn't send to sensor")
            pass
    except requests.exceptions.ConnectTimeout:
        print_error(f"NOT CONNECT TO ESP")


def calc_stride_freq(i):
    global filteredImpact, peaks, stride_freq, calibration, calibrating
    filteredImpact = [xs[i][3].copy(), filterLow(ys[i][3])]
    deltaTime = timeImpact[-1] - timeImpact[0]
    # print(deltaTime)
    peaks = signal.find_peaks(filteredImpact[1], height=2.5, distance=10)
    stride_freq = (len(peaks[0])) / deltaTime * 60
    # print(f"{stride_freq = }")

    # first get the average stride freq of the user for a minute
    if calibrationStartTime + calibrationTime < time.perf_counter() and calibration:
        calibration = False
        with open("log.txt", "w") as file1:  # Writing data to log file
            file1.writelines(log)
        # log.clear()
        log.append("------------ Recording ------------\n")
        log.append(f"average stride freq = {sum(stride_freqs) / len(stride_freqs)}\n")
        print_blue("------------ Recording ------------")

    if calibration:
        if not calibrating:
            print_blue("------------ Calibrating ------------")

        calibrating = True
        stride_freqs.append(stride_freq)
        log.append(f"time: {time.perf_counter()},\tstride_freqs:{stride_freqs}\n")
        print(f"{-int(time.perf_counter() - (calibrationStartTime + calibrationTime))}")  # , {stride_freqs}")

    else:  # then give feedback on it
        #  compare the current stride_freq with the sum(stride_freq)/len(stride_freq). als het 10% verschil heeft dan feedback.
        average_impact_calibration = sum(stride_freqs) / len(stride_freqs)  # np.average(np.asarray(stride_freqs))
        log.append(f"time: {time.perf_counter()},\tESP message:{'     ' if not abs(average_impact_calibration - stride_freq) > average_impact_calibration * 0.1 else ('bigger' if average_impact_calibration < stride_freq else 'smaller')},\t{stride_freq = },\t{average_impact_calibration = }\n")
        print(f"{average_impact_calibration = }, {stride_freq = }, {average_impact_calibration * 0.1 = }")
        if abs(average_impact_calibration - stride_freq) > average_impact_calibration * 0.1:
            url = 'smaller'
            if average_impact_calibration < stride_freq:
                url = 'bigger'
            httpRequest(url)


def impact_attenuation():
    global foot_peaks, head_peaks
    foot_peaks = signal.find_peaks(ys[0][3], height=2.5)
    head_peaks = signal.find_peaks(ys[1][3], height=1.5)

    att_list = []
    for leg, hip in zip(foot_peaks[0], head_peaks[0]):
        sAtt = (1 - hip / leg) * 100

        if sAtt > 0:
            att_list.append(sAtt)

    att_average = 0
    if len(att_list) > 0:
        att_average = sum(att_list) / len(att_list)

    if calibration:  # first find the average
        attCalibration_list.append(att_average)
        log.append(f"time: {time.perf_counter()},\tattenuation: {sum(attCalibration_list) / len(attCalibration_list)},\tarray: {attCalibration_list}\n")
    else:  # then give feedback on it
        calibration_avg = sum(attCalibration_list) / len(attCalibration_list)
        print(f"attenuation: {att_average = }, calibration average = {calibration_avg}")
        log.append(f"time: {time.perf_counter()},\tESP message:{'WARN' if att_average < calibration_avg * 0.8 else '     '},\tattenuation: {att_average = },\tcalibration average = {calibration_avg}\n")
        if att_average < calibration_avg * 0.8:  # if the average is smaller than 10 of the calibration average
            # httpRequest('warn')
            pass


def take_measurement():
    old_time = time.perf_counter()

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

            array = np.array(measurement[:3])
            normalized_vector = np.linalg.norm(array)

            ys[i][3].append(normalized_vector)
            xs[i][3].append(counter)

            timeImpact.append(time.perf_counter())
            if len(xs[i][3]) > limit:
                xs[i][3].pop(0)
            if len(ys[i][3]) > limit:
                ys[i][3].pop(0)
            if len(timeImpact) > limit:
                timeImpact.pop(0)

        if old_time + 5 < time.perf_counter() and time.perf_counter() - startTime >= startDelay:
            old_time = time.perf_counter()
            # calculate the impact attenuation between waist and foot
            impact_attenuation()
            # low pass filter and calculate step freq
            calc_stride_freq(0)
        elif time.perf_counter() - startTime < startDelay and old_time + 5 < time.perf_counter():
            # visual count down for in the console, per every 5 sec
            old_time = time.perf_counter()
            print(int(startDelay - (time.perf_counter() - startTime)))

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
                axs[0][i].plot(xs[i][j][::], ys[i][j][::])

        axs[1][0].plot(xs[0][3], ys[0][3])
        axs[1][0].plot(filteredImpact[0], filteredImpact[1])
        axs[1][1].plot(xs[1][3], ys[1][3])

        for i in peaks[0]:
            axs[1][0].plot(filteredImpact[0][i], filteredImpact[1][i], ls="", marker="o", label="points", color=(1, 0, 1))
            # axs[1][0].plot(vals, poly, markevery=mark, ls="", marker="o", label="points")
            # p = axs[1][0].add_patch(plt.Circle((filteredImpact[0][i], filteredImpact[1][i]), 0.5, alpha=1))
            # p.set_color((1, 0, 1))

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
            axs[1].plot(filteredImpact[0][i], filteredImpact[1][i], ls="", marker="o", label="points", color=(1, 0, 1))


if __name__ == '__main__':
    print_green("Connecting to WiFi.")
    Wifi.connectToWifi()

    print_green("Connecting to Sensors..")
    sensors = connect()

    print_green("Setting up variables...")

    frame_rate = 60
    xs = []
    ys = []

    filteredImpact = [[0], [0]]
    timeImpact = []

    for sensor in sensors:
        xs.append([[] for i in range(4)])
        ys.append([[] for x in range(4)])

    limit = 500
    peaks = [[], []]
    foot_peaks = [[], []]
    head_peaks = [[], []]
    attCalibration_list = []

    counter = 0
    stride_freq = 0

    stride_freqs = []

    startTime = time.perf_counter()
    startDelay = 30
    calibrationTime = 30  # 60*3
    calibration = True
    calibrating = False
    calibrationStartTime = time.perf_counter() + startDelay
    httpRequest('calibrate')
    log.append("------------ Calibration ------------\n")

    figs, axs = plt.subplots(2, len(sensors), figsize=(10, 6))

    ani = animation.FuncAnimation(figs, update_graph, interval=1 / frame_rate)
    print_green("Starting thread....")
    thread = threading.Thread(target=take_measurement, daemon=True)
    thread.start()
    print_green("Starting graph.....")
    print_blue("------------ Starting up ------------")
    plt.show()


@atexit.register
def endProgram():  # called when the red cross has been pressed
    with open("log.txt", "w") as file1:  # Writing data to log file
        file1.writelines(log)
    print_green("stored log")

    Wifi.connectToWifi('eduroam')
    print_green("reconecting to eduroam")
