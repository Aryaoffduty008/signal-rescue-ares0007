import random
import numpy as np

from engine.convolution import manual_convolution
from game.mission_engine import Mission


# ============================================================
# SHARED HELPERS
# ============================================================

def _numeric_error(answer, target):
    try:
        a = np.asarray(answer, dtype=float)
        b = np.asarray(target, dtype=float)
    except (TypeError, ValueError):
        return False, float("inf")

    if a.shape != b.shape:
        return False, float("inf")

    error = float(np.mean(np.abs(a - b)))
    return error <= 0.05, error


def _bool_error(answer, target):
    if len(answer) != 1:
        return False, float("inf")
    try:
        value = int(round(float(answer[0])))
    except (TypeError, ValueError):
        return False, float("inf")

    error = 0.0 if value == int(target) else 1.0
    return error == 0.0, error


# ============================================================
# MISSION 01 — ESTABLISH CONTACT
# ============================================================

def generate_mission_01_parameters():
    amplitude = random.choice([0.75, 1.0, 1.25, 1.5, 1.75, 2.0])
    frequency = random.choice([3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
    phase = random.choice(
        [-np.pi / 2, -np.pi / 4, 0.0, np.pi / 4, np.pi / 2]
    )
    return amplitude, frequency, phase


def validate_mission_01(answer, target):
    if len(answer) != 3:
        return False, float("inf")

    try:
        a = np.asarray(answer, dtype=float)
        t = np.asarray(target, dtype=float)
    except (TypeError, ValueError):
        return False, float("inf")

    error = float(np.mean(np.abs(a - t)))
    return error <= 0.05, error


def create_mission_01():
    amplitude, frequency, phase = generate_mission_01_parameters()
    mission = Mission(
        "01",
        "ESTABLISH CONTACT",
        "ARES-7's beacon has been detected. Reconstruct the signal parameters.",
        "Tune amplitude, frequency and phase until your generated signal matches the reference.",
        "Start by comparing the height, spacing and horizontal shift of the waveform.",
        lambda answer: validate_mission_01(
            answer, [amplitude, frequency, phase]
        ),
    )
    mission.parameters = {
        "amplitude": amplitude,
        "frequency": frequency,
        "phase": phase,
        "answer": [amplitude, frequency, phase],
    }
    return mission


# ============================================================
# MISSION 02 — ALIGN THE TRANSMISSION
# ============================================================

def generate_mission_02_parameters():
    frequency = 4.0
    delay = random.choice([0.06, 0.08, 0.12, 0.16, 0.20])
    return frequency, delay


def validate_mission_02(answer, correct_delay, frequency):
    if len(answer) != 1:
        return False, float("inf")

    try:
        user_delay = float(answer[0])
    except (TypeError, ValueError):
        return False, float("inf")

    period = 1.0 / frequency
    raw_difference = user_delay - correct_delay

    # Delays differing by whole signal periods are equivalent for a
    # pure periodic sine wave.
    wrapped_difference = (
        (raw_difference + period / 2.0) % period
    ) - period / 2.0

    error = abs(wrapped_difference)
    return error <= 0.01, error


def create_mission_02():
    frequency, delay = generate_mission_02_parameters()
    mission = Mission(
        "02",
        "ALIGN THE TRANSMISSION",
        "The signal arrived late through the communication channel.",
        "Adjust the delay until the received waveform aligns with the reference.",
        "A positive delay shifts a signal to the right. Watch the peaks and zero crossings.",
        lambda answer: validate_mission_02(
            answer, delay, frequency
        ),
    )
    mission.parameters = {
        "frequency": frequency,
        "delay": delay,
        "answer": [delay],
    }
    return mission


# ============================================================
# MISSION 03 — RESTORE SIGNAL STRENGTH
# ============================================================

def generate_mission_03_parameters():
    weak_amplitude = random.choice([0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65])
    target_amplitude = random.choice([0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5])
    scale = target_amplitude / weak_amplitude
    return weak_amplitude, target_amplitude, scale


def create_mission_03():
    weak_amp, target_amp, scale = generate_mission_03_parameters()

    mission = Mission(
        "03",
        "RESTORE SIGNAL STRENGTH",
        "ARES-7's transmission is too weak to decode reliably.",
        "Scale the weak signal until its amplitude matches the recovery target.",
        "Signal scaling changes amplitude but does not change frequency.",
        lambda answer: _numeric_error(answer, [scale]),
    )

    mission.parameters = {
        "weak_amplitude": weak_amp,
        "target_amplitude": target_amp,
        "scale": scale,
        "answer": [scale],
    }
    return mission


# ============================================================
# MISSION 04 — CORRUPTED ORIENTATION
# ============================================================

def generate_mission_04_parameters():
    length = random.choice([4, 5, 6])
    original = random.sample(range(1, 9), length)
    return original, list(reversed(original))


def create_mission_04():
    original, reversed_signal = generate_mission_04_parameters()

    mission = Mission(
        "04",
        "CORRUPTED ORIENTATION",
        "The sampled telemetry arrived backwards in time.",
        "Reverse the received discrete-time sequence.",
        "Time reversal means x[n] becomes x[-n]. On the displayed samples, the order flips.",
        lambda answer: _bool_error(answer, 1),
    )

    mission.parameters = {
        "original": original,
        "received": reversed_signal,
        "answer": [1],
    }
    return mission


# ============================================================
# MISSION 05 — THE MIXER
# ============================================================

def generate_mission_05_parameters():
    amp_a = random.choice([0.8, 1.0, 1.2])
    freq_a = random.choice([4.0, 5.0, 6.0])

    amp_b = random.choice([0.3, 0.4, 0.5, 0.6, 0.7])
    freq_b = random.choice([15.0, 20.0, 25.0])

    return amp_a, freq_a, amp_b, freq_b


def create_mission_05():
    amp_a, freq_a, amp_b, freq_b = generate_mission_05_parameters()

    mission = Mission(
        "05",
        "THE MIXER",
        "Two transmissions are riding on the same communication link.",
        "Recover the amplitudes of the two component signals used in the mixer.",
        "The mixed waveform is the sum of both signals. Match both component amplitudes.",
        lambda answer: _numeric_error(answer, [amp_a, amp_b]),
    )

    mission.parameters = {
        "amp_a": amp_a,
        "freq_a": freq_a,
        "amp_b": amp_b,
        "freq_b": freq_b,
        "answer": [amp_a, amp_b],
    }
    return mission


# ============================================================
# MISSION 06 — CORRUPTED TRANSMISSION
# ============================================================

def generate_mission_06_parameters():
    scale = random.choice([1.5, 1.75, 2.0, 2.25, 2.5])
    delay = random.choice([0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20])
    reverse = 1
    return scale, delay, reverse


def create_mission_06():
    scale, delay, reverse = generate_mission_06_parameters()

    mission = Mission(
        "06",
        "CORRUPTED TRANSMISSION",
        "ARES-7 applied several transformations to the original signal.",
        "Undo the amplitude scaling, time delay and reversal.",
        "Treat the corruption as separate operations: scale, shift, then reverse.",
        lambda answer: validate_mission_06(answer, [scale, delay, reverse]),
    )

    # The values are the corruption parameters. The mission asks the
    # player to identify them; the GUI visualizes the corrupted signal.
    mission.parameters = {
        "scale": scale,
        "delay": delay,
        "reverse": reverse,
        "answer": [scale, delay, reverse],
    }
    return mission


def validate_mission_06(answer, target):
    if len(answer) != 3:
        return False, float("inf")

    try:
        a = np.asarray(answer, dtype=float)
        t = np.asarray(target, dtype=float)
    except (TypeError, ValueError):
        return False, float("inf")

    numeric_error = (
        abs(a[0] - t[0])
        + abs(a[1] - t[1]) * 4
        + abs(a[2] - t[2])
    ) / 6.0

    return numeric_error <= 0.035, float(numeric_error)


# ============================================================
# MISSION 07 — ENERGY CRISIS
# ============================================================

def generate_mission_07_parameters():
    amplitudes = random.sample([0.8, 1.0, 1.2, 1.5, 1.8], 3)
    threshold = 0.75

    viable = [
        (index, amp)
        for index, amp in enumerate(amplitudes, start=1)
        if amp >= threshold
    ]
    correct_index = min(viable, key=lambda item: item[1])[0]

    return amplitudes, threshold, correct_index


def create_mission_07():
    amplitudes, threshold, correct_index = generate_mission_07_parameters()

    mission = Mission(
        "07",
        "ENERGY CRISIS",
        "Power is limited. Choose the weakest signal that is still strong enough for reliable recovery.",
        f"Select the lowest-energy signal whose amplitude is at least {threshold:.2f}.",
        "For a sinusoid with the same duration and frequency, energy grows with amplitude squared.",
        lambda answer: _bool_error(answer, correct_index),
    )

    mission.parameters = {
        "amplitudes": amplitudes,
        "threshold": threshold,
        "correct_index": correct_index,
        "answer": [correct_index],
    }
    return mission


# ============================================================
# MISSION 08 — WHAT'S INSIDE?
# ============================================================

def generate_mission_08_parameters():
    frequencies = random.sample(
        [8.0, 10.0, 12.0, 20.0, 40.0, 50.0, 60.0, 80.0, 100.0, 120.0],
        3,
    )
    amplitudes = random.sample([1.0, 0.8, 0.6, 0.5, 0.4], 3)
    return frequencies, amplitudes


def create_mission_08():
    frequencies, amplitudes = generate_mission_08_parameters()
    sorted_frequencies = sorted(frequencies)

    mission = Mission(
        "08",
        "WHAT'S INSIDE?",
        "The waveform looks complicated, but hidden frequencies can be revealed with the FFT.",
        "Identify the three dominant frequencies hidden in the transmission.",
        "FFT converts a time-domain signal into frequency components. Look for the largest peaks.",
        lambda answer: validate_mission_08(answer, sorted_frequencies),
    )

    mission.parameters = {
        "frequencies": frequencies,
        "amplitudes": amplitudes,
        "answer": sorted_frequencies,
    }
    return mission


def validate_mission_08(answer, target):
    if len(answer) != 3:
        return False, float("inf")

    try:
        a = np.sort(np.asarray(answer, dtype=float))
        t = np.sort(np.asarray(target, dtype=float))
    except (TypeError, ValueError):
        return False, float("inf")

    error = float(np.mean(np.abs(a - t)))
    return error <= 2.0, error


# ============================================================
# MISSION 09 — THE CHANNEL
# ============================================================

def generate_mission_09_parameters():
    x = random.choice(
        [
            [1, 2, 1],
            [1, 1, 2],
            [2, 1, 1],
            [1, 2, 2],
        ]
    )
    h = random.choice(
        [
            [1, 1],
            [1, 2],
            [2, 1],
            [1, -1],
        ]
    )
    y = manual_convolution(np.asarray(x, dtype=float), np.asarray(h, dtype=float))
    return x, h, y.tolist()


def create_mission_09():
    x, h, target = generate_mission_09_parameters()

    mission = Mission(
        "09",
        "THE CHANNEL",
        "The channel itself is altering the signal. Model it with discrete convolution.",
        "Adjust the four output samples until they match x[n] * h[n].",
        "For each output sample, multiply overlapping samples and add the products.",
        lambda answer: validate_mission_09(answer, target),
    )

    mission.parameters = {
        "x": x,
        "h": h,
        "target": target,
        "answer": target,
    }
    return mission


def validate_mission_09(answer, target):
    if len(answer) != len(target):
        return False, float("inf")

    try:
        a = np.asarray(answer, dtype=float)
        t = np.asarray(target, dtype=float)
    except (TypeError, ValueError):
        return False, float("inf")

    error = float(np.mean(np.abs(a - t)))
    return error <= 0.10, error
