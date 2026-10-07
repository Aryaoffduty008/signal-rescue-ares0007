import numpy as np


def sine_wave(t, amplitude=1.0, frequency=1.0, phase=0.0):
    """
    x(t) = A sin(2πft + φ)
    """
    return amplitude * np.sin(
        2 * np.pi * frequency * t + phase
    )


def cosine_wave(t, amplitude=1.0, frequency=1.0, phase=0.0):
    """
    x(t) = A cos(2πft + φ)
    """
    return amplitude * np.cos(
        2 * np.pi * frequency * t + phase
    )


def exponential_signal(t, amplitude=1.0, rate=1.0):
    """
    x(t) = A e^(at)
    """
    return amplitude * np.exp(rate * t)


def unit_step(t):
    """
    u(t)
    """
    return np.where(t >= 0, 1.0, 0.0)


def unit_impulse(t, tolerance=1e-6):
    """
    Approximation of δ(t) for numerical simulation.
    """
    return np.where(np.abs(t) < tolerance, 1.0, 0.0)


def ramp(t):
    """
    r(t) = t u(t)
    """
    return np.where(t >= 0, t, 0.0)