from collections import defaultdict
from datetime import date, datetime, timedelta

from heating.api.constants import DayStatus
from heating.api.selectors import get_room_names_by_ids, get_slots_hashes

AI_DUPLICATION_MAX_DAYS = 365
AI_DUPLICATION_WARNING_THRESHOLD = 30

FRENCH_WEEKDAYS = [
    "lundi",
    "mardi",
    "mercredi",
    "jeudi",
    "vendredi",
    "samedi",
    "dimanche",
]

FRENCH_MONTHS = [
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
]


def group_slots_hashes_by_date(slots_hashes: list) -> dict:
    day_to_hashes = defaultdict(set)
    try:
        for d, h in slots_hashes:
            day_to_hashes[d].add(h)
    except TypeError:
        return {}
    return day_to_hashes


def add_day_status(raw_calendar: list) -> list:
    if not isinstance(raw_calendar, list):
        return []
    try:
        calendar_start_date = raw_calendar[0]["date"]
        calendar_end_date = raw_calendar[-1]["date"]
        qs_start_date = calendar_start_date - timedelta(weeks=1)
    except (IndexError, KeyError, TypeError):
        return []

    slots_hashes = get_slots_hashes(qs_start_date, calendar_end_date)
    if not slots_hashes:
        return raw_calendar
    dates_slots_hashes = group_slots_hashes_by_date(slots_hashes)
    for day in raw_calendar:
        day_date = day.get("date")
        if day_date is None:
            continue
        day_hashes = dates_slots_hashes.get(day_date)

        # day without a heating plan
        if day_hashes is None:
            day["status"] = DayStatus.EMPTY
            continue

        # day having the same heating plans as the same day of the previous week
        day_of_previous_week = day_date - timedelta(weeks=1)
        day_of_previous_week_hashes = dates_slots_hashes.get(day_of_previous_week)
        if day_hashes == day_of_previous_week_hashes:
            day["status"] = DayStatus.NORMAL
            continue

        # day not having the same heating plans as the same day of the previous week
        else:
            day["status"] = DayStatus.DIFFERENT

    return raw_calendar


def generate_duplication_dates(
    start_date: date, weekdays: list[int], end_date: date
) -> list[date]:
    weekdays = sorted(set(weekdays))
    dates = []

    for weekday in weekdays:
        # Calculate the number of days until the next requested weekday
        days_ahead = (weekday - start_date.weekday()) % 7

        # If it's 0, it means start_date is already on this weekday
        if days_ahead == 0:
            next_date = start_date
        else:
            next_date = start_date + timedelta(days=days_ahead)

        # Add all occurrences of this day until end_date
        while next_date <= end_date:
            dates.append(next_date)
            next_date += timedelta(days=7)

    dates.sort()
    return dates


def validate_ai_duplication_request(
    room_ids: list,
    weekdays: list,
    start: str,
    end: str,
    known_room_ids: set[int],
    today: date,
) -> dict:
    """
    Validates the fields extracted by the AI duplication interpreter and computes the
    effective number of impacted days.

    Returns {"status": "ok"|"warning"|"error", "message": str, "nb_days_impacted": int}.
    "nb_days_impacted" is 0 on "error" (not computed / not meaningful).
    """
    if not room_ids:
        return {"status": "error", "message": "Aucune pièce sélectionnée.", "nb_days_impacted": 0}
    if len(room_ids) != len(set(room_ids)):
        return {"status": "error", "message": "Des pièces sont dupliquées dans la sélection.", "nb_days_impacted": 0}
    if set(room_ids) - known_room_ids:
        return {"status": "error", "message": "La sélection contient des pièces non proposées.", "nb_days_impacted": 0}

    if not weekdays:
        return {"status": "error", "message": "Aucun jour de la semaine sélectionné.", "nb_days_impacted": 0}
    if len(weekdays) != len(set(weekdays)):
        return {"status": "error", "message": "Des jours de la semaine sont dupliqués dans la sélection.", "nb_days_impacted": 0}
    if any(w < 0 or w > 6 for w in weekdays):
        return {"status": "error", "message": "Jour de la semaine invalide.", "nb_days_impacted": 0}

    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return {"status": "error", "message": "Date de début invalide.", "nb_days_impacted": 0}
    try:
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return {"status": "error", "message": "Date de fin invalide.", "nb_days_impacted": 0}

    # today is not yet over, its plan can still be duplicated onto — but no earlier than that
    if start_date < today:
        return {"status": "error", "message": "La date de début doit être aujourd'hui ou une date future.", "nb_days_impacted": 0}
    if end_date < start_date:
        return {"status": "error", "message": "La date de fin doit être postérieure ou égale à la date de début.", "nb_days_impacted": 0}
    if (end_date - start_date).days > AI_DUPLICATION_MAX_DAYS:
        return {
            "status": "error",
            "message": f"La période demandée dépasse le maximum autorisé de {AI_DUPLICATION_MAX_DAYS} jours.",
            "nb_days_impacted": 0,
        }

    nb_days_impacted = len(generate_duplication_dates(start_date, weekdays, end_date))
    if nb_days_impacted == 0:
        return {
            "status": "error",
            "message": "Aucun jour de la période ne correspond aux jours de la semaine sélectionnés.",
            "nb_days_impacted": 0,
        }

    if nb_days_impacted > AI_DUPLICATION_WARNING_THRESHOLD:
        return {
            "status": "warning",
            "message": f"Cette duplication va modifier {nb_days_impacted} jours, confirmez-vous ?",
            "nb_days_impacted": nb_days_impacted,
        }

    return {"status": "ok", "message": "", "nb_days_impacted": nb_days_impacted}


def format_date_fr(day: date) -> str:
    """Formats a date as "lundi 18 août 2026" (French, spelled out weekday and month)."""
    return f"{FRENCH_WEEKDAYS[day.weekday()]} {day.day} {FRENCH_MONTHS[day.month - 1]} {day.year}"


def _join_fr(items: list[str]) -> str:
    """Joins items with commas and "et" before the last one, from 2 items up ("a et b", "a, b et c")."""
    if len(items) <= 1:
        return items[0] if items else ""
    return ", ".join(items[:-1]) + " et " + items[-1]


def build_ai_duplication_recap(
    source_date: date,
    room_ids: list[int],
    weekdays: list[int],
    start_date: date,
    end_date: date,
    all_room_ids: set[int],
) -> str:
    """
    Builds the French confirmation sentence for an already-validated AI duplication request.
    Always describes EFFECTIVE occurrences (the actual first/last dates the duplication will
    write to), never the raw start/end boundaries, since only some of the days in [start, end]
    may actually match the selected weekdays.
    """
    duplication_dates = generate_duplication_dates(start_date, weekdays, end_date)
    first_occurrence = min(duplication_dates)
    last_occurrence = max(duplication_dates)

    room_names = get_room_names_by_ids(set(room_ids))
    if set(room_ids) == all_room_ids:
        rooms_fr = "les plannings de toutes les pièces"
    elif len(room_ids) == 1:
        rooms_fr = f"le planning de {room_names[room_ids[0]]}"
    else:
        rooms_fr = "les plannings de " + _join_fr(
            [room_names[room_id] for room_id in room_ids if room_id in room_names]
        )

    if set(weekdays) == set(range(7)):
        weekdays_fr = "tous les jours"
    else:
        weekdays_fr = "tous les " + _join_fr(
            [FRENCH_WEEKDAYS[w] for w in sorted(weekdays)]
        )

    return (
        f"Je récapitule, vous voulez copier {rooms_fr} du {format_date_fr(source_date)} "
        f"sur {weekdays_fr} entre le {format_date_fr(first_occurrence)} "
        f"et le {format_date_fr(last_occurrence)} ?"
    )
