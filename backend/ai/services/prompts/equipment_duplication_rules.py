def get_rules() -> str:
    """
    Business rules for interpreting an equipment plan duplication instruction.
    Injected into the system prompt.

    Scope: this prompt ONLY extracts fields from the instruction. It does not validate dates,
    does not compute effective occurrences, and does not build any recap message — all of that
    is done deterministically in Python after this call, using the fields returned here.

    Equipments are referred to by a "type:id" key (e.g. "water_heater:1") rather than a bare id,
    because ids are only unique within one equipment type.
    """
    return """
### What you are given
- today: the real current date, the only reference point for resolving relative dates
- equipments: the list of equipments available to duplicate onto (key + name only)

### Fields to extract
- equipment_keys: which equipments to duplicate onto, using the exact "key" values of the given list
- weekdays: which weekdays to repeat on (0=lundi .. 6=dimanche)
- start: first date to apply the duplication to
- end: last date to apply the duplication to (inclusive)

### Defaults (apply silently, do not ask for these)
- If no equipment is mentioned (e.g. "copie ce jour", "copie cette journée"): use ALL keys from
  the given equipments list
- Equipments can be matched by partial match / substring in their name (case-insensitive)
- Never invent a key: only use keys present in the given equipments list
- If no weekday is mentioned: it means every day of the week → weekdays = [0, 1, 2, 3, 4, 5, 6]
- If no start date is mentioned: start = today + 1 day

### Never default this — always ask for clarification if missing
- end: there is no safe default. If the instruction does not give an end date (explicit date, or a
  clearly resolvable reference like "jusqu'à la fin de la semaine", "jusqu'au 30 août"), return
  status "clarify" and ask specifically for the end date. Never invent one.

### Date resolution
- All dates you output must be absolute "YYYY-MM-DD" values, computed from today
- Relative references ("demain", "la semaine prochaine", "jusqu'à la fin de semaine", "vendredi
  prochain", "fin du mois prochain", etc.) are always relative to today

### Only one instruction at a time
- You must return a single set of fields (one equipment_keys, one weekdays, one start, one end)
- If the instruction actually describes several distinct groups that can't be expressed as a single
  set (e.g. "chauffe-eau A tous les mercredis jusqu'à fin août, et chauffe-eau B tous les vendredis
  jusqu'à fin septembre"), do NOT try to merge or pick one — return status "invalid" (see below)

### When the instruction is understood but incomplete
- status: "clarify"
- message: a short, specific question in French about exactly what's missing (usually the end date)

### When the instruction cannot be understood, or describes several distinct requests at once
- status: "invalid"
- message (French, generic, always the same wording): "Je n'ai pas compris votre demande. Elle doit préciser les équipements, les jours de la semaine et les dates de début et de fin. Si votre demande contient plusieurs instructions différentes, merci de les faire une par une."

### When the instruction is complete
- status: "ready"
- message: ""
- equipment_keys, weekdays, start, end: the extracted fields
"""
