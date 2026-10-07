import matplotlib.pyplot as plt


def show_signal(t, signal, title="ARES-7 Signal"):
    """
    Display a signal waveform.
    """

    plt.figure(figsize=(10, 5))

    plt.plot(t, signal)

    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")

    plt.grid(True)

    plt.tight_layout()

    plt.show()