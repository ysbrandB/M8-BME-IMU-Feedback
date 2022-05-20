from CreaTeBME import connect
import matplotlib.pyplot as plt
import time
import threading
import random

# AC:67:B2:38:77:86 WirelessIMU-7786
# AC:67:B2:38:87:32 WirelessIMU-8732

data = [[] for i in range(6)]
names = ['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z']
colors = ['red', 'green', 'blue', 'yellow', 'purple', 'black']
# This just simulates reading from a socket.
def data_listener():
    while True:
        global sensors, data
        for sensor in sensors:
            measurement = sensor.take_measurement()
            for i, measure in enumerate(measurement):
                data[i].append(measure)
                if len(data[i]) > 1000:
                    data[i].clear()


            # print(measurement)
            # Do something with the data
def update_graph():
    while True:
        plt.pause(0.001)
        # data_listener()
        for i, dataPoint in enumerate(data[::]):
            axs[0 if i < 3 else 1].plot(dataPoint, color=colors[i])
            axs[0 if i < 3 else 1].set_xlim([len(dataPoint)-1000, len(dataPoint)])

        # axs[0].legend(names[:3:])
        # axs[1].legend(names[3::])

        plt.draw()

if __name__ == '__main__':
    global sensors
    sensors = connect()
    thread = threading.Thread(target=data_listener)
    thread.daemon = True
    thread.start()
    #
    # initialize figure
    global fig, axs
    fig, axs = plt.subplots(2)

    # plt.figure()
    # ln, = plt.plot([])
    # plt.plot(data)
    plt.ion()
    plt.show()
    update_graph()
