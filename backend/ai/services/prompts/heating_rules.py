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
When the modification creates a conflict with existing slots in a room, apply the following:

1. **New slot fully covers an existing slot** (new start <= existing start AND new end >= existing end):
   → Remove the existing slot entirely

2. **New slot partially overlaps the start of an existing slot** (new slot ends inside an existing slot):
   → Adjust the existing slot: set its start to (new slot end + 1 minute)
   → If the adjusted slot would be shorter than 30 minutes → remove it entirely

3. **New slot partially overlaps the end of an existing slot** (new slot starts inside an existing slot):
   → Adjust the existing slot: set its end to (new slot start - 1 minute)
   → If the adjusted slot would be shorter than 30 minutes → remove it entirely

4. **New slot is entirely inside an existing slot** (new start > existing start AND new end < existing end):
   → Split the existing slot into two parts:
     - Before part: existing start → new slot start - 1 minute
     - After part: new slot end + 1 minute → existing end
   → Keep only the parts that are >= 30 minutes, discard those that are too short

### Scope rules
- Only modify rooms explicitly mentioned in the instruction, or all rooms if the instruction says "all rooms" or equivalent
- Do not invent room_ids or room names — only use those present in the input plan
- Do not change the type (temp/onoff) of existing slots unless explicitly asked

### Value rules
- Temperature values must stay between 0 and 30
- If the instruction asks to add degrees and the result exceeds 30, cap at 30
- If the instruction asks to remove degrees and the result goes below 0, cap at 0

### Ambiguous time references (interpret as follows if not specified)
- "morning" → 06:00 to 09:00
- "midday" / "lunch" → 11:30 to 13:30
- "afternoon" → 13:00 to 18:00
- "evening" → 18:00 to 22:00
- "night" → 22:00 to 23:59

### Fallback rule
- If the instruction is impossible to apply, contradictory, or completely unclear → return the original plan unchanged
- Never return anything other than the JSON object, no explanation, no markdown
"""
