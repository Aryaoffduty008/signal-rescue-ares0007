import numpy as np


def transfer_function_info(
    numerator,
    denominator
):
    """
    Calculate zeros and poles from transfer-function
    polynomial coefficients.

    Example:

        H(s) = 1 / (s + 2)

        numerator   = [1]
        denominator = [1, 2]
    """

    numerator = np.asarray(
        numerator,
        dtype=float
    )

    denominator = np.asarray(
        denominator,
        dtype=float
    )

    # Remove leading zeros
    numerator = np.trim_zeros(
        numerator,
        trim="f"
    )

    denominator = np.trim_zeros(
        denominator,
        trim="f"
    )

    zeros = np.roots(numerator) \
        if len(numerator) > 1 else np.array([])

    poles = np.roots(denominator) \
        if len(denominator) > 1 else np.array([])

    return zeros, poles


def is_stable(poles):
    """
    Continuous-time stability criterion:

    Stable if all poles have negative real parts.
    """

    poles = np.asarray(
        poles,
        dtype=complex
    )

    if len(poles) == 0:
        return True

    return np.all(
        np.real(poles) < 0
    )


def impulse_response_first_order(
    pole,
    t
):
    """
    Numerical/analytical impulse response for:

        H(s) = 1 / (s - pole)

    For pole = -2:

        h(t) = e^(-2t)

    For pole = +1:

        h(t) = e^t
    """

    return np.exp(
        pole * t
    )


def step_response_first_order(
    pole,
    t
):
    """
    Step response for:

        H(s) = 1 / (s - pole)

    Y(s) = 1 / [s(s-pole)]

    y(t) = (e^(pole*t) - 1) / pole

    for pole != 0.
    """

    if pole == 0:
        return t

    return (
        np.exp(pole * t) - 1
    ) / pole


def analyze_system(
    numerator,
    denominator
):
    """
    Complete transfer-function analysis.
    """

    zeros, poles = transfer_function_info(
        numerator,
        denominator
    )

    stable = is_stable(
        poles
    )

    return {
        "zeros": zeros,
        "poles": poles,
        "stable": stable
    }