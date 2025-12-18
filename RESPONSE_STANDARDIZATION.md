# Response Structure Standardization Plan

## Current State Analysis

### 1. _chat_init (Initial Session Start)
**Current Response Fields:**
- `brief_reaction` (from LLM)
- `next_question` (from LLM)
- `checkpoints` (from LLM)

**User-facing message location:** `next_question`

**State updates:**
```python
state["brief_reaction"] = response_data.get("brief_reaction", "")
state["next_question"] = response_data.get("next_question", "")
state["checkpoints"] = response_data.get("checkpoints", [])
```

### 2. _detect_stuck (User Response Analysis)
**Current Response Fields:**
- `is_stuck` (from LLM)
- `ai_response` (from LLM)

**User-facing message location:** `ai_response`

**State updates:**
```python
state["is_stuck"] = response_data.get("is_stuck", False)
hint_msg = response_data.get("ai_response", "생각해볼까요?")
state["ai_response"] = f"{hint_msg}\n(남은 기회: {remaining}회)"
```

### 3. _chat_eval (Progress Evaluation)
**Current Response Fields:**
- `overall_progress` (from LLM)
- `checkpoints_evaluation` (from LLM)
- `misconceptions` (from LLM)
- `learning_summary` (from LLM)

**State updates:**
```python
state["evaluation"] = evaluation_result  # Entire evaluation dict stored
```

### 4. _chat_advanced (Adaptive Questioning/Reporting)
**Current Response Fields:**
- `response_type` (from LLM)
- `question` (from LLM, for questions)
- `report` (from LLM, for reports)

**User-facing message location:** `question` field OR embedded in report

**State updates - Issue:** Different handling for questions vs reports:
```python
if response_type == "progress_report":
  state["advanced_response"] = advanced_result  # Report stored
  state["next_action"] = "end_session"
else:
  state["ai_response"] = advanced_result.get("question", response_text)  # Question stored
  state["advanced_response"] = advanced_result
  state["next_action"] = "continue"
```

## Key Inconsistencies Identified

| Function | Message Source | Field Name | Issue |
|----------|---|---|---|
| _chat_init | LLM response | `next_question` | User message not in `ai_response` |
| _detect_stuck | LLM response | `ai_response` | User message properly placed |
| _chat_advanced (Q) | LLM response | `question` | User message not in standard location |
| _chat_advanced (Report) | LLM response | `report.narrative` | No `ai_response` field at all |

## Proposed Standardization

### Unified Response Structure

All LLM responses should follow a common pattern:

```json
{
  "response_type": "question|report|evaluation|...",
  "user_facing_message": "The text to display to the user",
  "metadata": {
    "question_type": "foundational|deepening|integrative",
    "progress_level": 0-100,
    "checkpoints_status": {...}
  },
  "internal_data": {
    "evaluation": {...},
    "report_data": {...}
  }
}
```

### State TypedDict Updates

Add unified field to ChatState:
```python
class ChatState(TypedDict):
  # ... existing fields ...
  user_facing_message: str  # Standardized user message from LLM
  response_metadata: dict   # response_type, question_type, etc.
```

### Function Changes Required

1. **_chat_init**:
   - Extract `next_question` → map to `user_facing_message`
   - Keep `brief_reaction` and `checkpoints` in state

2. **_detect_stuck**:
   - Extract `ai_response` → map to `user_facing_message`
   - Add attempt count formatting in code (not in prompt)

3. **_chat_eval**:
   - Store full evaluation in state (no change)
   - Extract key metrics

4. **_chat_advanced**:
   - Questions: Extract `question` → map to `user_facing_message`
   - Reports: Extract report content → prepare for report.py processing

### Prompt File Updates Required

All prompts should output:
```json
{
  "response_type": "...",
  "user_facing_message": "...",
  "other_fields": {}
}
```

Files affected:
- SYSTEM_PROMPT_INIT_EN.md → Use `user_facing_message` for question
- SYSTEM_PROMPT_STUCK_EN.md → Use `user_facing_message` for response
- SYSTEM_PROMPT_ADVANCED_EN.md → Use `user_facing_message` for question/report
- (And Korean versions of all)

## Implementation Order

1. ✅ Create unified response structure definition
2. ⬜ Update SYSTEM_PROMPT_INIT_EN.md for `user_facing_message`
3. ⬜ Update SYSTEM_PROMPT_STUCK_EN.md for `user_facing_message`
4. ⬜ Update SYSTEM_PROMPT_ADVANCED_EN.md for `user_facing_message`
5. ⬜ Update all Korean prompt files
6. ⬜ Modify _chat_init to extract and map fields
7. ⬜ Modify _detect_stuck to extract and map fields
8. ⬜ Modify _chat_advanced to extract and map fields
9. ⬜ Add `user_facing_message` to ChatState TypedDict
10. ⬜ Update chat_qna initial state with new field
11. ⬜ Create report.py to consume standardized structure
