def calculate_score(
    error,
    time_taken,
    hints_used=0,
    operations_used=1
):
    """
    Calculate a mission score.

    Components:
        Accuracy:      0 - 1000
        Speed bonus:   0 - 300
        Hint penalty:  100 per hint
        Operation penalty:
                       25 per extra operation
    """

    # -------------------------------------------------
    # Accuracy
    # -------------------------------------------------

    if error <= 0:
        accuracy_score = 1000
    else:
        accuracy_score = 1000 / (
            1 + (error * 100)
        )

        accuracy_score = min(
            1000,
            max(0, accuracy_score)
        )

    # -------------------------------------------------
    # Speed
    # -------------------------------------------------

    time_taken = max(
        0,
        float(time_taken)
    )

    speed_bonus = max(
        0,
        300 - (time_taken * 5)
    )

    speed_bonus = min(
        300,
        speed_bonus
    )

    # -------------------------------------------------
    # Hint penalty
    # -------------------------------------------------

    hint_penalty = (
        max(0, hints_used) * 100
    )

    # -------------------------------------------------
    # Operation penalty
    # -------------------------------------------------

    extra_operations = max(
        0,
        operations_used - 1
    )

    operation_penalty = (
        extra_operations * 25
    )

    # -------------------------------------------------
    # Final score
    # -------------------------------------------------

    score = (
        accuracy_score
        + speed_bonus
        - hint_penalty
        - operation_penalty
    )

    return max(
        0,
        round(score)
    )