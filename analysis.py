import numpy as np


def energy(signal):
    """
    Calculate discrete-time signal energy.

    E = Σ |x[n]|²
    """
    return np.sum(np.abs(signal) ** 2)


def average_power(signal):
    """
    Calculate average power.

    P = (1/N) Σ |x[n]|²
    """
    return np.mean(np.abs(signal) ** 2)


def rms(signal):
    """
    Calculate RMS value.

    RMS = sqrt((1/N) Σ |x[n]|²)
    """
    return np.sqrt(average_power(signal))


def peak_amplitude(signal):
    """
    Find the maximum absolute amplitude.
    """
    return np.max(np.abs(signal))


def mean_value(signal):
    """
    Calculate the mean/DC value.
    """
    return np.mean(signal)