import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq, ifft
from scipy.signal import butter, filtfilt

# Параметры
frequency_sampling = 10000  # Частота дискретизации
T = 1  # Длительность сигнала, с
t = np.linspace(0, T, int(frequency_sampling * T), endpoint=False)  # Временная шкала
frequency2 = 50  # Частота несущей, Гц
frequency3 = 5   # Частота модулирующего сигнала, Гц
amplitude = 1   # Амплитуда модулирующего сигнала
amplitude2 = 1   # Амплитуда несущей

# Модулирующий сигнал
modulating_signal = amplitude * np.sign(np.sin(2 * np.pi * frequency3 * t))

# Генерация сигналов с модуляцией
amplitude_signal = (1 + modulating_signal) * amplitude2 * np.cos(2 * np.pi * frequency2 * t)  # Амплитудная модуляция
frequency_signal = amplitude2 * np.cos(2 * np.pi * frequency2 * t + modulating_signal)        # Частотная модуляция
phase_signal = amplitude2 * np.cos(2 * np.pi * frequency2 * t + np.pi * modulating_signal)  # Фазовая модуляция

# Вывод графиков модуляции
plt.figure(figsize=(12, 8))
plt.subplot(3, 1, 1)
plt.plot(t, amplitude_signal, label="AM Signal")
plt.title("Amplitude Modulation")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.grid()

plt.subplot(3, 1, 2)
plt.plot(t, frequency_signal, label="FM Signal")
plt.title("Frequency Modulation")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.grid()

plt.subplot(3, 1, 3)
plt.plot(t, phase_signal, label="PM Signal")
plt.title("Phase Modulation")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.grid()

plt.tight_layout()
plt.show()

# Расчет спектров
n = len(t)
freqs = fftfreq(n, 1 / frequency_sampling)
am_spectrum = np.abs(fft(amplitude_signal))

# Обрезка спектра
low_cutoff = frequency2 - 20
high_cutoff = frequency2 + 20
mask = (freqs > low_cutoff) & (freqs < high_cutoff)
filtered_spectrum = np.zeros_like(am_spectrum)
filtered_spectrum[mask] = am_spectrum[mask]

# Синтез сигнала из обрезанного спектра
synthesized_signal = np.real(ifft(filtered_spectrum))

# Фильтрация синтезированного сигнала
b, a = butter(4, frequency3 / (frequency_sampling / 2), btype='low')
filtered_signal = filtfilt(b, a, synthesized_signal)

# Графики спектра и синтезированного сигнала
plt.figure(figsize=(12, 8))

# Спектр амплитудной модуляции
plt.subplot(3, 1, 1)
plt.plot(freqs[:n // 2], am_spectrum[:n // 2])
plt.title("Spectrum of AM Signal")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.grid()

# Обрезанный спектр
plt.subplot(3, 1, 2)
plt.plot(freqs[:n // 2], filtered_spectrum[:n // 2])
plt.title("Filtered Spectrum")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.grid()

# Сравнение сигналов
plt.subplot(3, 1, 3)
plt.plot(t, filtered_signal, label="Filtered Synthesized Signal")
plt.plot(t, modulating_signal, label="Modulating Signal", linestyle='--')
plt.title("Comparison of Signals")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()

