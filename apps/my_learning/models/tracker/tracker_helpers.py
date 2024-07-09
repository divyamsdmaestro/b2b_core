def get_actual_progress(old_progress, new_progress):
    """Returns the actual progress based on custom logic."""

    if old_progress < new_progress <= 100:
        progress = new_progress
    elif new_progress > old_progress and new_progress > 100:
        progress = 100
    else:
        progress = old_progress
    return progress
