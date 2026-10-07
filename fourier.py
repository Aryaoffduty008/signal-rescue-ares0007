import numpy as np


def fft_analysis(signal, sampling_rate):
    """
    Perform FFT analysis on a signal.

    Returns:
        frequencies
        magnitude
        phase
    """

    N = len(signal)

    # Fourier Transform
    spectrum = np.fft.fft(signal)

    # Frequency axis
    frequencies = np.fft.fftfreq(N, d=1 / sampling_rate)

    # Magnitude
    magnitude = np.abs(spectrum) / N

    # Phase
    phase = np.angle(spectrum)

    return frequencies, magnitude, phase


def dominant_frequency(signal, sampling_rate):
    """
    Find the strongest frequency component.
    """

    frequencies, magnitude, _ = fft_analysis(
        signal,
        sampling_rate
    )

    # Only look at positive frequencies
    positive = frequencies >= 0

    frequencies = frequencies[positive]
    magnitude = magnitude[positive]

    # Ignore DC component
    if len(magnitude) > 1:
        index = np.argmax(magnitude[1:]) + 1
    else:
        index = 0

    return frequencies[index], magnitude[index]