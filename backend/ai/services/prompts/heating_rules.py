def get_rules() -> str:
    """
    Business rules for heating plan modification.
    Injected into the system prompt.
    Tweak this file to improve LLM output quality without touching the prompt structure.
    """
    return """
### Slot format rules
- "start" and "end" must be in HH:MM format (00:00 to 23:59)
- "start" must be strictly before "end"
- Minimum slot duration is 30 minutes
- All slots in a given room must have the same type: either all "temp" or all "onoff"
- If type is "temp": value must be a number between 0 and 30 (integer or float, e.g. 19, 20.5)
- If type is "onoff": value must be exactly the string "on" or "off"
- A room can have an empty slots array [] if no heating is scheduled for that day

### Overlap resolution rules
When the new slot conflicts with existing slots, you MUST resolve the conflict before returning.
Never return overlapping slots — the result must always be a valid non-overlapping list.

**Case 1 — New slot fully covers an existing slot:**
Existing: 10:00-12:00. New: 09:00-13:00.
→ Remove the existing slot. Result: [09:00-13:00]

**Case 2 — New slot partially overlaps the END of an existing slot:**
Existing: 08:00-16:00 at 21°. New: 12:00-18:00 at 19°.
→ Trim the existing slot: set its end to 11:59. Result: [08:00-11:59 at 21°, 12:00-18:00 at 19°]
→ If the trimmed slot would be shorter than 30 minutes → remove it entirely.

**Case 3 — New slot partially overlaps the START of an existing slot:**
Existing: 14:00-20:00 at 21°. New: 12:00-15:00 at 19°.
→ Trim the existing slot: set its start to 15:01. Result: [12:00-15:00 at 19°, 15:01-20:00 at 21°]
→ If the trimmed slot would be shorter than 30 minutes → remove it entirely.

**Case 4 — New slot is entirely INSIDE an existing slot:**
Existing: 08:00-20:00 at 21°. New: 12:00-14:00 at 19°.
→ Split the existing slot into two parts:
  - Before: 08:00-11:59 at 21°
  - After:  14:01-20:00 at 21°
→ Keep only parts that are >= 30 minutes, discard shorter ones.
Result: [08:00-11:59 at 21°, 12:00-14:00 at 19°, 14:01-20:00 at 21°]

### Scope rules
- Only modify rooms explicitly mentioned in the instruction, or all rooms if the instruction says "all rooms", "toutes les pièces" or equivalent
- Rooms can also be selected by a partial match / substring in their name, e.g. "toutes les pièces qui contiennent 'chambre' dans leur nom" must match every room whose name contains that substring (case-insensitive), not just an exact name
- Do not invent room_ids or room names — only use those present in the input plan
- Do not change the type (temp/onoff) of existing slots unless explicitly asked

### Value rules
- Temperature values must stay between 0 and 30
- If the instruction asks to add degrees and the result exceeds 30, cap at 30
- If the instruction asks to remove degrees and the result goes below 0, cap at 0

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
- If the instruction is impossible to apply, contradictory, refers to a room that does not exist,
  or is completely unclear: set "success" to false and explain why in "reason",
  using the same language as the user's instruction
- In all cases (success or failure), always return the full rooms array with the current state of the plan
- Never return anything other than the JSON object
"""
