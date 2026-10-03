def get_rules() -> str:
    """
    Business rules for equipment plan modification.
    Injected into the system prompt.
    Tweak this file to improve LLM output quality without touching the prompt structure.

    Kept separate from heating_rules.py on purpose: equipments are on/off only
    (no temperature) and are identified by a (type, id) pair rather than a room_id,
    so sharing one rules text would force the LLM to ignore half of it.
    """
    return """
### Slot format rules
- "start" and "end" must be in HH:MM format (00:00 to 23:59)
- "start" must be strictly before "end"
- Minimum slot duration is 30 minutes
- Every slot must have "type": "onoff" and "value" exactly equal to the string "on" or "off"
- An equipment can have an empty slots array [] if nothing is scheduled for that day

### Overlap resolution rules
When the new slot conflicts with existing slots, you MUST resolve the conflict before returning.
Never return overlapping slots — the result must always be a valid non-overlapping list.

**Case 1 — New slot fully covers an existing slot:**
Existing: 10:00-12:00. New: 09:00-13:00.
→ Remove the existing slot. Result: [09:00-13:00]

**Case 2 — New slot partially overlaps the END of an existing slot:**
Existing: 08:00-16:00. New: 12:00-18:00.
→ Trim the existing slot: set its end to 11:59. Result: [08:00-11:59, 12:00-18:00]
→ If the trimmed slot would be shorter than 30 minutes → remove it entirely.

**Case 3 — New slot partially overlaps the START of an existing slot:**
Existing: 14:00-20:00. New: 12:00-15:00.
→ Trim the existing slot: set its start to 15:01. Result: [12:00-15:00, 15:01-20:00]
→ If the trimmed slot would be shorter than 30 minutes → remove it entirely.

**Case 4 — New slot is entirely INSIDE an existing slot:**
Existing: 08:00-20:00. New: 12:00-14:00.
→ Split the existing slot into two parts:
  - Before: 08:00-11:59
  - After:  14:01-20:00
→ Keep only parts that are >= 30 minutes, discard shorter ones.
Result: [08:00-11:59, 12:00-14:00, 14:01-20:00]

### Scope rules
- Each entry of the plan is an equipment identified by its "type" and "id" (e.g. a water heater)
- Only modify equipments explicitly mentioned in the instruction, or all equipments if the instruction says "all equipments", "tous les équipements" or equivalent
- Equipments can also be selected by a partial match / substring in their name (case-insensitive), e.g. "chauffe-eau" must match an equipment named "Chauffe-eau cuisine"
- If the instruction targets a kind of equipment (e.g. "les chauffe-eau"), match it against both the "name" and the "type" of each equipment
- Do not invent equipments — only use the "type", "id" and "name" present in the input plan, and never change them
- Never add or remove an equipment from the plan, only change its slots

### "Off" instructions always mean an empty zone
"Éteindre"/"turn off"/"couper" for a given time range means REMOVING the "on" range,
i.e. making that range empty (no slot covering it) — apply the overlap resolution rules
above as a pure deletion, never insert a new slot for that range.
Never write "value": "off" for a new slot — an empty (uncovered) range IS the off state.
Example: existing slot 06:00-22:00 "on". Instruction: "éteins entre 12:00 et 14:00".
→ Result: [06:00-11:59 "on", 14:01-22:00 "on"] (the 12:00-14:00 gap is simply empty, no slot there)

"Allumer"/"turn on" for a range with no existing slot means adding a new slot
covering that range with "value": "on".

### Ambiguous time references (interpret as follows if not specified)
- "morning" / "matin" → 06:00 to 09:00
- "midday" / "midi" / "lunch" / "déjeuner" → 11:30 to 13:30
- "afternoon" / "après-midi" → 13:00 to 18:00
- "evening" / "soir" → 18:00 to 22:00
- "night" / "nuit" → 22:00 to 23:59

### Duration-based instructions
- If the instruction gives a duration instead of an explicit end time (e.g. "pendant 3 heures", "for 2 hours"), use the current time given at the top of the user prompt as the start, and compute the end by adding the duration
- If adding the duration would cross midnight (end time numerically before start time), cap the end at 23:59 instead — never return an end time that is numerically before the start time
- Round the resulting start/end to the nearest 5 minutes if needed to keep a clean HH:MM value

### Success and failure reporting
- If the modification was applied successfully: set "success" to true and "reason" to ""
- If the instruction is impossible to apply, contradictory, refers to an equipment that does not exist,
  or is completely unclear: set "success" to false and explain why in "reason",
  using the same language as the user's instruction
- In all cases (success or failure), always return the full equipments array with the current state of the plan
- Never return anything other than the JSON object
"""
