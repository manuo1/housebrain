from datetime import datetime, timedelta


def generate_daily_index_structure():
    """
    Generates the daily index structure with all minutes of the day.
    """
    minutes = {
        (datetime.strptime("00:00", "%H:%M") + timedelta(minutes=i)).strftime(
            "%H:%M"
        ): None
        for i in range(24 * 60)
    }
    # Adding "24:00" for the next day's midnight index
    minutes["24:00"] = None

    return minutes
