import matplotlib.pyplot as plt
import numpy as np

points_count = 10000
width = 10


def calculate_coordinates_harmonic(frequency):
    global points_count, width
    x = np.linspace(0, width * np.pi, points_count)
    y = 2 * np.cos(frequency * x)
    return x, y


def calculate_coordinates_digital(frequency):
    global points_count, width
    x = np.linspace(0, width * np.pi, 10000)
    y = np.sign(np.cos(frequency * x))
    return x, y


x, y = calculate_coordinates_digital(8)
plt.plot(x, y, marker=None, linestyle='-')


plt.title("Пример графика")
plt.xlabel("Амплисюда")
plt.ylabel("Амплитуда")
plt.grid()
plt.show()
