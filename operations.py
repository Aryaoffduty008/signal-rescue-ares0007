import numpy as np


def scale(signal, factor):
    """
    Amplitude scaling:
    y(t) = A x(t)
    """
    return factor * signal


def reverse(signal):
    """
    Time reversal:
    y(t) = x(-t)
    """
    return signal[::-1]


def shift(signal, shift_samples):
    """
    Discrete approximation of time shifting.

    Positive shift -> delay
    Negative shift -> advance
    """

    result = np.zeros_like(signal)

    if shift_samples > 0:
        result[shift_samples:] = signal[:-shift_samples]

    elif shift_samples < 0:
        shift_samples = abs(shift_samples)
        result[:-shift_samples] = signal[shift_samples:]

    else:
        result = signal.copy()

    return result


def add(signal_1, signal_2):
    return signal_1 + signal_2


def multiply(signal_1, signal_2):
    return signal_1 * signal_2