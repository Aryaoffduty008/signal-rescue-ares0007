import numpy as np


def manual_convolution(x, h):
    """
    Calculate discrete-time linear convolution manually.

    y[n] = x[n] * h[n]
    """

    output_length = len(x) + len(h) - 1

    y = np.zeros(output_length)

    for n in range(len(x)):
        for k in range(len(h)):
            y[n + k] += x[n] * h[k]

    return y


def verify_convolution(x, h, manual_result):
    """
    Compare manual convolution with NumPy's result.
    """

    numpy_result = np.convolve(x, h)

    return np.allclose(
        manual_result,
        numpy_result
    )
def convolution_error(user_result, correct_result):
    """
    Calculate mean absolute error between
    the player's answer and the correct answer.
    """

    user_result = np.array(user_result)
    correct_result = np.array(correct_result)

    if len(user_result) != len(correct_result):
        return float("inf")

    return np.mean(
        np.abs(user_result - correct_result)
    )