# Report Writing Guidelines – Capturing the Real Learning Journey

This report is not a simple summary. **It is a record that reveals how the learner thinks and grows.**

## 1. Learning Journey Narrative (3–4 sentences)

**What to capture:**
The learner’s initial level of understanding shown in the first response
Moments of struggle → breakthrough → decisive understanding
Changes in the learner’s language, expressions, or metaphors

**Writing principles:**

Use concrete dialogue references such as: “At first, the learner thought X, but…”

Avoid abstract evaluations (e.g., “They understood well”)

Use observable evidence (e.g., “By describing the filter as ‘sliding,’ the learner accurately grasped the mechanism”)

**Example:**

“At first, the learner vaguely described CNNs as ‘models that analyze images.’ However, in turn 5, they independently created the metaphor ‘filters move like sliding windows,’ which shows they grasped the essence of convolution. In turn 12, they briefly struggled to explain pooling, but broke through by connecting ‘computational reduction’ with ‘preserving important features.’”

## 2. Key Achievements – Evolution of Thinking (3–5 items)

**For each checkpoint:**

✓ [Checkpoint Name] (Achieved at Turn N)

Initial Misconception: What the learner misunderstood at first (if any)

Turning Point: The question or hint that triggered the “aha” moment

Final Expression: The learner’s explanation in their own words (direct quote)

Significance: Why this understanding matters

**Example:**

✓ Convolution Understanding (Achieved at Turn 6)
- Initial Misconception: Passive framing such as “filters find features”
- Turning Point: When asked “How does the filter move?”, the learner replied “by sliding…”
- Final Expression: “The filter slides over the image, matches patterns at each position, and stacks the results into a feature map”
- Significance: Demonstrates fundamental understanding of the mechanism rather than rote memorization

## 3. Learning Pattern Analysis
### Strengths (Evidence-based)

Support each strength with **actual dialogue** examples:

Ability to connect concepts (e.g., “understood A by linking it to B”)
Spontaneous curiosity or questioning (e.g., “Then what happens to C?”)
Recovery after being stuck (e.g., “Got stuck at X, but resolved it independently after hint Y”)

## Challenges (Root Cause Analysis)

For each difficulty:

**What** was difficult (concept, terminology, abstraction, etc.)
**Why** it was difficult (lack of prerequisite knowledge, cognitive leap, confusing terms, etc.)
**How** it was resolved, or what remains unresolved

**Example:**

“The learner experienced two points of difficulty during the convolution stage. The issue appeared to be difficulty translating abstract terms like ‘feature extraction’ into concrete operations. Once specific examples such as ‘edges or lines’ were introduced, understanding was immediate—suggesting a learning style that requires time to move from abstract to concrete.”

## 4. Incomplete Areas (Honest Assessment)

**Remaining concepts:**

Checkpoints not yet covered
Concepts only partially understood
Ideas that the learner “recognizes but cannot yet explain”

**Why they matter:**

How each gap affects overall understanding
Whether immediate remediation is required or can be deferred

## 5. Next Steps (Concrete & Actionable)
**Immediate Practice (within 1–3 days)**
1. [Hands-on task using today’s concepts]
- Specific assignment (e.g., “Implement a simple CNN on MNIST”)
- Estimated time
- Success criteria

**Deeper Learning (within 1–2 weeks)**
2. [Theoretical expansion]
- Recommended resources (specific links or chapters)
- Why this resource is recommended
- Expected learning outcome

**Connected Learning (if applicable)**
3. [Related concepts]
- How they connect to today’s learning
- Prerequisite knowledge check

**Review Points**
4. [Key items to revisit]
- Concepts that caused confusion today
- Simple self-test questions

## 6. Closing Message (Personalized & Motivational)

**Include:**

- Re-emphasis of specific learner strengths
- The most impressive moment in this session
- Encouragement without exaggeration
- A natural bridge to the next goal

**Example:**

“Over approximately 40 minutes and 18 turns, the learner progressed to explaining CNN mechanisms in their own words. The moment in turn 6, where they independently created the ‘sliding window’ metaphor, was particularly impressive—this kind of spontaneous analogy is a strong indicator of deep understanding. The next step is to translate today’s concepts into code and experience how they become concrete.”

**Mandatory Writing Rules**

**✅ Do**

1. Use direct quotes from the learner
2. Capture specific moments (e.g., “When the learner said X at turn N…”)
3. Be honest about gaps in understanding
4. Personalize by identifying unique learning patterns
5. Make next steps measurable and actionable

**❌ Don’t**

1. Generic praise (“Good job”, “Excellent”)
2. Abstract evaluations (“Understood the concept”)
3. Unsupported claims
4. Vague advice (“Study more”)
5. Overstated encouragement (“Mastered perfectly”)

**Length & Tone**

- Length: 2–3 A4 pages
- Tone: Respectful, treating the learner as an equal partner
- Style: Natural English, minimal formality
- Structure: Clear sections with visual separation

**Output Requirement (JSON)**

After writing the human-readable report, structure it into the following JSON format:
```json
{
  "session_info": {
    "session_id": "...",
    "topic": "...",
    "total_turns": 18,
    "final_progress": 0.67,
    "completion_reason": "...",
    "duration_minutes": 42
  },
  
  "learning_journey": {
    "narrative": "3-4문장의 학습 여정 서술...",
    "key_moments": [
      {
        "turn_number": 5,
        "moment_type": "breakthrough",
        "description": "..."
      }
    ]
  },
  
  "key_achievements": [
    {
      "checkpoint_name": "...",
      "achieved_at_turn": 6,
      "initial_misconception": "... 또는 null",
      "turning_point": {
        "turn_number": 5,
        "trigger": "...",
        "learner_quote": "실제 대화에서 인용"
      },
      "final_understanding": "학습자의 언어로...",
      "significance": "이 이해가 왜 중요한지..."
    }
  ],
  
  "learning_patterns": {
    "strengths": [
      {
        "strength": "...",
        "evidence": [
          {"turn_number": 5, "example": "..."}
        ]
      }
    ],
    "challenges": [
      {
        "challenge": "...",
        "stuck_count": 2,
        "root_cause": "abstract_to_concrete",
        "resolution": "..."
      }
    ]
  },
  
  "incomplete_areas": [
    {
      "area": "...",
      "coverage_level": "not_started",
      "importance": "important",
      "reason": "..."
    }
  ],
  
  "next_steps": {
    "immediate_practice": [...],
    "deeper_learning": [...],
    "connected_learning": [...],
    "review_points": [...]
  },
  
  "closing_message": {
    "acknowledgment": "...",
    "most_impressive_moment": "...",
    "encouragement": "...",
    "bridge_to_next": "..."
  }
}
```

**Important:**
1. Fill in all fields
2. Quote the learner’s actual expressions
3. Use real turn numbers
4. initial_misconception may be null; no other fields may be
5. Enum values must be exact

Do not output JSON alone.
First write the report for humans, then provide the structured JSON.

Begin the answer directly with the **report content**, without meta explanations.