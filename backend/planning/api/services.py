from datetime import date, datetime

from planning.services import (
    AI_DUPLICATION_MAX_DAYS,
    AI_DUPLICATION_WARNING_THRESHOLD,
    FRENCH_WEEKDAYS,
    format_date_fr,
    generate_duplication_dates,
    join_fr,
)


def make_equipment_key(type_name: str, equipment_id: int) -> str:
    """
    Builds the "type:id" key used to designate an equipment in the AI
    duplication flow: ids alone are only unique within one equipment type.
    """
    return f"{type_name}:{equipment_id}"


def parse_equipment_key(key: str) -> tuple[str, int] | None:
    """Inverse of make_equipment_key. Returns None if `key` is malformed."""
    type_name, separator, raw_id = key.rpartition(":")
    if not separator or not type_name or not raw_id.isdecimal():
        return None
    return type_name, int(raw_id)


def _error(message: str) -> dict:
    return {"status": "error", "message": message, "nb_days_impacted": 0}


def validate_duplication_period(
    weekdays: list, start: str, end: str, today: date
) -> dict:
    """
    Validates the weekdays/start/end part of an AI duplication request and
    computes the effective number of impacted days. Independent of what is
    being duplicated, so it applies to any kind of schedulable equipment.

    Returns {"status": "ok"|"warning"|"error", "message": str, "nb_days_impacted": int}.
    "nb_days_impacted" is 0 on "error" (not computed / not meaningful).
    """
    if not weekdays:
        return _error("Aucun jour de la semaine sélectionné.")
    if len(weekdays) != len(set(weekdays)):
        return _error("Des jours de la semaine sont dupliqués dans la sélection.")
    if any(w < 0 or w > 6 for w in weekdays):
        return _error("Jour de la semaine invalide.")

    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return _error("Date de début invalide.")
    try:
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return _error("Date de fin invalide.")

    # today is not yet over, its plan can still be duplicated onto — but no earlier than that
    if start_date < today:
        return _error("La date de début doit être aujourd'hui ou une date future.")
    if end_date < start_date:
        return _error(
            "La date de fin doit être postérieure ou égale à la date de début."
        )
    if (end_date - start_date).days > AI_DUPLICATION_MAX_DAYS:
        return _error(
            f"La période demandée dépasse le maximum autorisé de {AI_DUPLICATION_MAX_DAYS} jours."
        )

    nb_days_impacted = len(generate_duplication_dates(start_date, weekdays, end_date))
    if nb_days_impacted == 0:
        return _error(
            "Aucun jour de la période ne correspond aux jours de la semaine sélectionnés."
        )

    if nb_days_impacted > AI_DUPLICATION_WARNING_THRESHOLD:
        return {
            "status": "warning",
            "message": f"Cette duplication va modifier {nb_days_impacted} jours, confirmez-vous ?",
            "nb_days_impacted": nb_days_impacted,
        }

    return {"status": "ok", "message": "", "nb_days_impacted": nb_days_impacted}


def validate_ai_equipment_duplication_request(
    equipment_keys: list,
    weekdays: list,
    start: str,
    end: str,
    known_equipment_keys: set[str],
    today: date,
) -> dict:
    """
    Validates the fields extracted by the AI equipment duplication interpreter.
    Same contract as validate_duplication_period, plus the equipment selection checks.
    """
    if not equipment_keys:
        return _error("Aucun équipement sélectionné.")
    if len(equipment_keys) != len(set(equipment_keys)):
        return _error("Des équipements sont dupliqués dans la sélection.")
    if set(equipment_keys) - known_equipment_keys:
        return _error("La sélection contient des équipements non proposés.")

    return validate_duplication_period(weekdays, start, end, today)


def build_ai_equipment_duplication_recap(
    source_date: date,
    equipment_keys: list[str],
    weekdays: list[int],
    start_date: date,
    end_date: date,
    equipment_names_by_key: dict[str, str],
) -> str:
    """
    Builds the French confirmation sentence for an already-validated AI equipment
    duplication request. `equipment_names_by_key` holds every equipment the user could
    have picked (key -> name): it is both the name lookup and what defines "all equipments".

    Always describes EFFECTIVE occurrences (the actual first/last dates the duplication
    will write to), never the raw start/end boundaries, since only some of the days in
    [start, end] may actually match the selected weekdays.
    """
    duplication_dates = generate_duplication_dates(start_date, weekdays, end_date)
    first_occurrence = min(duplication_dates)
    last_occurrence = max(duplication_dates)

    if set(equipment_keys) == set(equipment_names_by_key):
        equipments_fr = "les plannings de tous les équipements"
    elif len(equipment_keys) == 1:
        equipments_fr = f"le planning de {equipment_names_by_key[equipment_keys[0]]}"
    else:
        equipments_fr = "les plannings de " + join_fr(
            [
                equipment_names_by_key[key]
                for key in equipment_keys
                if key in equipment_names_by_key
            ]
        )

    if set(weekdays) == set(range(7)):
        weekdays_fr = "tous les jours"
    else:
        # Every French weekday name takes a plain "s" in the plural (lundi -> lundis)
        weekdays_fr = "tous les " + join_fr(
            [FRENCH_WEEKDAYS[w] + "s" for w in sorted(weekdays)]
        )

    return (
        f"Je récapitule, vous voulez copier {equipments_fr} du {format_date_fr(source_date)} "
        f"sur {weekdays_fr} entre le {format_date_fr(first_occurrence)} "
        f"et le {format_date_fr(last_occurrence)} ?"
    )
