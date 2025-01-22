import matplotlib.pyplot as plt
import numpy as np

points_count = 10000
width = 10
frequency = 8


def calculate_coordinates_harmonic(frequency):
    global points_count, width, points_count
    x = np.linspace(0, width * np.pi, points_count)
    y = 2 * np.cos(frequency * x)
    return x, y


def calculate_coordinates_digital(frequency):
    global points_count, width, points_count
    x = np.linspace(0, width * np.pi, points_count)
    y = np.sign(np.cos(frequency * x))
    return x, y


def calculate_coordinates_spectrum(frequency):
    global points_count, width, points_count
    signal = np.sin(2 * np.pi * frequency * np.arange(0, 1.0, 1/points_count))
    frequency_spectrum = np.fft.rfft(signal)
    frequencies = np.fft.rfftfreq(len(signal), d=1 / points_count)
    return frequencies, np.abs(frequency_spectrum)


x, y = calculate_coordinates_spectrum(frequency)
plt.plot(x, y, marker=None, linestyle='-')


plt.title(f'Пример графика {frequency} ГЦ')
plt.xlim(0, 30)
plt.grid()
plt.show()
