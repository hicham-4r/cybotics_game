# ============================================================
# LEVEL SCORE
# ============================================================

def calculate_level_score(
    completion_time,
    target_time,
    completion_bonus,
    time_multiplier
):
    """
    Calculate the score earned for completing one level.

    The player always receives the level completion bonus.

    Completing the level faster than the target time gives
    an additional time bonus.

    A slow completion never produces negative time points.
    """

    safe_completion_time = max(
        0.0,
        float(completion_time)
    )

    safe_target_time = max(
        0.0,
        float(target_time)
    )

    safe_completion_bonus = max(
        0,
        int(completion_bonus)
    )

    safe_time_multiplier = max(
        0.0,
        float(time_multiplier)
    )


    time_saved = max(
        0.0,
        safe_target_time
        - safe_completion_time
    )


    time_bonus = int(
        round(
            time_saved
            * safe_time_multiplier
        )
    )


    level_score = (
        safe_completion_bonus
        + time_bonus
    )


    return {
        "completion_bonus": safe_completion_bonus,
        "time_bonus": time_bonus,
        "level_score": level_score,
        "time_saved": time_saved,
    }


# ============================================================
# DEATH PENALTY
# ============================================================

def calculate_death_penalty(
    current_score,
    penalty_percent
):
    """
    Calculate a percentage-based death penalty.

    The result can never exceed the player's current score,
    therefore score can never become negative.
    """

    safe_score = max(
        0,
        int(current_score)
    )

    safe_percent = max(
        0.0,
        float(penalty_percent)
    )


    penalty = int(
        round(
            safe_score
            * safe_percent
        )
    )


    penalty = min(
        penalty,
        safe_score
    )


    return penalty


# ============================================================
# COMPLETE-RUN BONUSES
# ============================================================

def calculate_run_completion_bonuses(
    death_count,
    full_completion_bonus,
    perfect_run_bonus
):
    """
    Calculate bonuses that are awarded only after completing
    the entire current run.

    A perfect run means completing the run without dying.

    Manual level restarts do not currently prevent a perfect
    run because the project specification defines the perfect
    condition specifically around deaths.
    """

    safe_deaths = max(
        0,
        int(death_count)
    )

    completion_bonus = max(
        0,
        int(full_completion_bonus)
    )

    available_perfect_bonus = max(
        0,
        int(perfect_run_bonus)
    )


    if safe_deaths == 0:

        perfect_bonus = (
            available_perfect_bonus
        )

    else:

        perfect_bonus = 0


    total_bonus = (
        completion_bonus
        + perfect_bonus
    )


    return {
        "full_completion_bonus": completion_bonus,
        "perfect_run_bonus": perfect_bonus,
        "total_bonus": total_bonus,
        "perfect_run": safe_deaths == 0,
    }