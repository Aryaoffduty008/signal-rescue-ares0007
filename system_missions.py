import random
import numpy as np

from game.mission_engine import Mission


# ============================================================
# MISSION 10 — UNKNOWN SYSTEM
# ============================================================

def create_mission_10():
    pole = random.choice([-0.5, -1.0, -1.5, -2.0, -2.5, -3.0])

    mission = Mission(
        "10",
        "UNKNOWN SYSTEM",
        "We have identified a first-order transfer function but its exact pole is unknown.",
        "Estimate the pole and determine whether the continuous-time system is stable.",
        "For a continuous-time system, poles in the left half-plane correspond to stability.",
        lambda answer: validate_system_answer(answer, pole, 1),
    )

    mission.parameters = {
        "pole": pole,
        "stable": 1,
        "answer": [pole, 1],
    }
    return mission


# ============================================================
# MISSION 11 — SYSTEM FAILURE
# ============================================================

def create_mission_11():
    pole = random.choice([0.5, 1.0, 1.5, 2.0, 2.5])

    mission = Mission(
        "11",
        "SYSTEM FAILURE",
        "The spacecraft control system is amplifying disturbances instead of suppressing them.",
        "Estimate the pole and determine whether the system is stable.",
        "A right-half-plane pole produces an exponentially growing response.",
        lambda answer: validate_system_answer(answer, pole, 0),
    )

    mission.parameters = {
        "pole": pole,
        "stable": 0,
        "answer": [pole, 0],
    }
    return mission


def validate_system_answer(answer, target_pole, target_stable):
    if len(answer) != 2:
        return False, float("inf")

    try:
        pole = float(answer[0])
        stable = int(round(float(answer[1])))
    except (TypeError, ValueError):
        return False, float("inf")

    error = abs(pole - target_pole) * 0.6 + abs(stable - target_stable) * 0.4
    return error <= 0.08, float(error)


# ============================================================
# FINAL MISSION — SAVE ARES-7
# ============================================================

def create_final_mission():
    scale = random.choice([1.5, 1.75, 2.0, 2.25])
    delay = random.choice([0.05, 0.08, 0.10, 0.12, 0.15])
    reverse = 1
    frequency = random.choice([8.0, 9.0, 10.0, 11.0, 12.0])
    stable = 1

    mission = Mission(
        "12",
        "SAVE ARES-7",
        "Final transmission recovery: combine the signal operations with system-level reasoning.",
        "Match the corrupted telemetry using scale, delay, reversal, frequency and stability.",
        "Break the problem into five independent checks: amplitude, timing, orientation, frequency and system stability.",
        lambda answer: validate_final(
            answer,
            [scale, delay, reverse, frequency, stable],
        ),
    )

    mission.parameters = {
        "scale": scale,
        "delay": delay,
        "reverse": reverse,
        "frequency": frequency,
        "stable": stable,
        "answer": [scale, delay, reverse, frequency, stable],
    }
    return mission


def validate_final(answer, target):
    if len(answer) != 5:
        return False, float("inf")

    try:
        a = np.asarray(answer, dtype=float)
        t = np.asarray(target, dtype=float)
    except (TypeError, ValueError):
        return False, float("inf")

    error = (
        abs(a[0] - t[0]) * 0.25
        + abs(a[1] - t[1]) * 2.0
        + abs(a[2] - t[2]) * 0.25
        + abs(a[3] - t[3]) * 0.25
        + abs(a[4] - t[4]) * 0.25
    )

    return error <= 0.08, float(error)
