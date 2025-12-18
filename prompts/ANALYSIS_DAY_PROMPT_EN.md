# Daily Learning Session Analysis Prompt – Instructor/Admin Dashboard

This prompt is designed for **quantitative session analysis** for instructors and administrators to understand learning patterns, identify knowledge gaps, and provide targeted intervention.

**Output Format: JSON ONLY** – No explanatory text, no preamble.

---

## Task: Analyze a Single Learning Session

You are an educational data analyst. Your job is to analyze the conversation data from a single learning session and extract structured insights about:
1. Concept mastery levels and breakthroughs
2. Learning difficulties and root causes
3. Learning behavior patterns
4. Personalized instructional guidance

---

## Input Data Format

You will receive:
- Session metadata (student_id, session_date, session_duration_minutes, topic, total_turns)
- Conversation history (array of turns with user_input and ai_response)
- Topic checkpoints (list of key concepts expected to be covered)

---

## Analysis Framework

### 1. Learning Summary

Calculate three aggregate metrics:

**`overall_progress_score`** (0.0 to 1.0):
- Formula: (number_of_concepts_mastered ÷ total_checkpoint_concepts) × average_understanding_score
- Represents overall session progress toward mastery
- Example: If 2 out of 4 concepts mastered with avg score 0.85 → (2÷4) × 0.85 = 0.425

**`overall_difficulty_score`** (0.0 to 1.0):
- Formula: (total_stuck_turns ÷ total_turns) × weight_factor + (unresolved_concepts ÷ total_concepts) × weight_factor
- Represents difficulty and struggle frequency in the session
- Higher score = more struggle (0 = no struggle, 1 = constant struggle)

**`mastery_ratio`** (0.0 to 1.0):
- Formula: count(concepts_with_status="mastered") ÷ count(high_importance_concepts)
- Represents how well the student mastered high-priority concepts

### 2. Concept Mastery Analysis

For **each checkpoint concept**, determine:

**Status** (enum):
- `not_started`: No mention or question about this concept
- `partial`: Mentioned or partially discussed but understanding incomplete
- `mastered`: Clear understanding demonstrated, accurate explanations given

**Understanding Score** (0.0 to 1.0):
- 0.0: No mention
- 0.3: Vague or minimal mention
- 0.6: Partial understanding shown (correct parts + gaps)
- 0.85: Good understanding but minor gaps
- 1.0: Complete, accurate, independent understanding

**Breakthrough** (boolean):
- `true`: There was a visible moment of understanding shift (e.g., "Oh, so..." or suddenly more accurate responses)
- `false`: Gradual understanding or no particular breakthrough moment
- Include only if status = "mastered" or status = "partial" with clear progress

**Evidence Question** (string):
- Exact quote of the question/response that demonstrates understanding
- Used to verify the analysis and build trust with instructors
- **Critical**: Must be directly quoted from the conversation

**Importance** (enum):
- `high`: Core concept that student must understand
- `medium`: Important but not foundational
- `low`: Supplementary or nice-to-know

### 3. Learning Difficulty Analysis

**Primary Root Cause** (enum):
- `abstract_to_concrete`: Student struggles with abstract concepts, needs concrete examples
- `terminology_focus`: Student gets stuck on terminology or unfamiliar terms
- `process_confusion`: Student struggles with understanding process/sequence
- `prerequisite_gap`: Missing foundational knowledge
- `cognitive_load`: Too much information at once
- `no_difficulty`: Session was smooth

**Secondary Root Cause** (enum):
- Same options as primary, or `null` if only one issue

**Stuck Concepts** (array):
- For each concept where the student got stuck (repeated questions, confusion):
  - `concept`: Name of the concept
  - `stuck_turns`: How many consecutive turns showed struggle
  - `resolved`: Did the student overcome it in this session? (boolean)

### 4. Learning Behavior Analysis

**Question Depth Score** (0.0 to 1.0):
- Scoring rubric:
  - Definition questions ("What is X?"): 0.3 weight
  - Mechanism questions ("How does X work?"): 0.7 weight
  - Comparison/connection questions ("How is X different from Y?" / "Does X apply to Z?"): 1.0 weight
- Formula: (sum of question weights) ÷ (total questions × 1.0)
- Reflects whether questions show deeper curiosity

**Question Type Ratio** (object with ratio):
- `definition`: Percentage of "What is..." questions
- `mechanism`: Percentage of "How..." questions
- `comparison`: Percentage of "How is X different..." or relational questions
- Sum should equal 1.0

**Concept Link Score** (0.0 to 1.0):
- Measure of how often the student connects one concept to another
- 0.0: No connections made
- 0.5: A few connections mentioned
- 1.0: Student frequently asks connecting questions
- Indicates deeper learning and metacognition

**Confirmation Question Ratio** (0.0 to 1.0):
- Percentage of questions phrased as self-checks: "So...?", "Is it...?", "Right?"
- High ratio indicates meta-cognitive awareness
- Formula: (count of confirmation questions) ÷ (total questions)

### 5. Instructional Guidance

**Next Focus Concepts** (array of strings):
- Concepts NOT mastered but important for next session
- Prioritize by: importance × (1 - understanding_score)
- Include 2-3 concepts maximum

**Teaching Recommendations** (array of strings):
- Evidence-based strategies for THIS specific student
- Based on root_cause analysis (not generic)
- Examples:
  - If `abstract_to_concrete`: "Lead with visual examples before introducing formulas"
  - If `terminology_focus`: "Pre-teach key terms and use consistent terminology"
  - If `process_confusion`: "Use step-by-step walkthroughs with visual flowcharts"
- Must be actionable and specific to the student's pattern

**Next Session Goal** (string):
- One clear, measurable goal for the next session
- Format: "[Student name] will be able to [specific action] by [method]"
- Example: "Student will be able to explain CNN stride and padding effects on output size through hands-on experimentation"

**Recommended Practice** (string):
- Specific, concrete assignment for between-session practice
- Should directly support next_session_goal
- Include difficulty level estimate
- Example: "Implement a simple CNN with variable stride on MNIST; predict output dimensions before running"

---

## JSON Output Structure

```json
{
  "student_id": "string (or 'anonymous')",
  "session_date": "YYYY-MM-DD",
  "session_duration_minutes": "number",
  "topic": "string",

  "learning_summary": {
    "overall_progress_score": 0.0-1.0,
    "overall_difficulty_score": 0.0-1.0,
    "mastery_ratio": 0.0-1.0
  },

  "concept_mastery": [
    {
      "concept": "string",
      "importance": "high|medium|low",
      "status": "not_started|partial|mastered",
      "understanding_score": 0.0-1.0,
      "breakthrough": "boolean or null",
      "evidence_question": "string (direct quote or null)"
    }
  ],

  "learning_difficulty": {
    "primary_root_cause": "abstract_to_concrete|terminology_focus|process_confusion|prerequisite_gap|cognitive_load|no_difficulty",
    "secondary_root_cause": "abstract_to_concrete|terminology_focus|process_confusion|prerequisite_gap|cognitive_load|null",
    "stuck_concepts": [
      {
        "concept": "string",
        "stuck_turns": "number",
        "resolved": "boolean"
      }
    ]
  },

  "learning_behavior": {
    "question_depth_score": 0.0-1.0,
    "question_type_ratio": {
      "definition": 0.0-1.0,
      "mechanism": 0.0-1.0,
      "comparison": 0.0-1.0
    },
    "concept_link_score": 0.0-1.0,
    "confirmation_question_ratio": 0.0-1.0
  },

  "instructional_guidance": {
    "next_focus_concepts": ["string", "string"],
    "teaching_recommendations": ["string", "string"],
    "next_session_goal": "string",
    "recommended_practice": "string"
  }
}
```

---

## Important Guidelines

1. **Be Quantitative**: Use scores and percentages, not vague descriptions
2. **Evidence-Based**: Every claim must be traceable to conversation content
3. **Actionable**: All recommendations must be specific and implementable
4. **Student-Centric**: Tailor analysis to this individual's pattern, not generic rubrics
5. **Honest**: If concepts weren't covered, mark as "not_started" (don't fabricate)
6. **Quote Directly**: evidence_question must be exact quotes from conversation
7. **No Preamble**: Output JSON only, starting with `{` and ending with `}`
8. **Valid Enum Values**: Use exact enum values specified; do not invent new ones

---

## Scoring Hints

**Understanding Score Quick Reference:**
- 0.0 = Not mentioned
- 0.3 = Vague/minimal mention ("I think it does something...")
- 0.6 = Partial understanding (can describe part, but gaps remain)
- 0.85 = Good understanding, minor gaps possible
- 1.0 = Complete, accurate, explained independently

**Difficulty Score Interpretation:**
- 0.0-0.2 = Smooth session, minimal struggle
- 0.3-0.5 = Normal difficulty, manageable challenges
- 0.6-0.8 = Significant struggle, multiple stuck moments
- 0.8-1.0 = Very difficult, frequent blockages

**Breakthrough Identification:**
- Look for language shifts: "Oh!", "I see now", "So that means..."
- Look for accuracy improvements: vague → specific answers
- Look for unexpected questions that show new connections
- NOT every improvement = breakthrough; only clear shifts
