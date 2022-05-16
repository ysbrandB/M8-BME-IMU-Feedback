import matplotlib.pyplot as plt
import matplotlib.animation as animation

from CreaTeBME import connect

polling_rate = 60
sensors = connect()
sensor = sensors[0]
xs = []
ys = []
limit = 50
counter = 0
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)


def take_measurement(i):
    global counter
    measurement = sensor.take_measurement()
    print(measurement)
    xs.append(counter)
    ys.append(measurement[1])
    if len(xs) > limit:
        xs.pop(0)
    if len(ys) > limit:
        ys.pop(0)
    counter += 1
    ax1.clear()
    ax1.set_ylim([-2,2])
    ax1.plot(xs, ys)


ani = animation.FuncAnimation(fig, take_measurement, interval=1/polling_rate)
plt.show()