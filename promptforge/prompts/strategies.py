"""
prompts/strategies.py
---------------------
The core of PromptForge — seven prompt engineering strategy builders.

Each builder function takes identical arguments (task name + user input) and
returns a complete prompt string. The STRATEGIES registry maps strategy names
to their builder functions and descriptions, allowing app.py to iterate over
all strategies uniformly.

Key design principle — controlled experiment:
    Every builder receives the SAME task and SAME user_input. The only variable
    is the prompt structure around that input. This is why output differences are
    attributable solely to prompt engineering, not to different inputs or models.

Strategy progression (intended demo order):
    1. Zero-Shot    — bare baseline, no scaffolding
    2. Few-Shot     — add examples, no reasoning guidance
    3. Chain-of-Thought — add reasoning steps, no persona
    4. Role Prompting   — add expert persona, no format enforcement
    5. Structured Output — enforce JSON schema, no reasoning steps
    6. Self-Reflection   — three-phase critique-and-revise loop
    7. Meta-Prompting    — model designs its own prompt then executes it

Adding a new strategy:
    1. Write a build_<name>_prompt(task, user_input) -> str function below.
    2. Add an entry to the STRATEGIES dict with "builder" and "description".
    3. The strategy will automatically appear in the sidebar and run with all others.
"""

from data.examples import (
    FEW_SHOT_SENTIMENT_EXAMPLES,
    FEW_SHOT_SUMMARY_EXAMPLES,
    FEW_SHOT_CODE_REVIEW_EXAMPLES,
)


# ─────────────────────────────────────────────────────────────────────────────
# Strategy 1: Zero-Shot
# ─────────────────────────────────────────────────────────────────────────────

def build_zero_shot_prompt(task: str, user_input: str) -> str:
    """
    Build a zero-shot prompt: task label followed immediately by the input.

    This is the simplest possible prompt — just tell the model what to do and
    hand it the input. No examples, no persona, no format instructions.

    Used as the baseline in the evaluation. All other strategies should score
    higher than this on the quality metrics.

    Args:
        task      : Task name string (e.g. "Code Review").
        user_input: The text the user pasted into the input area.

    Returns:
        A minimal prompt string: "{task}:\n\n{user_input}"
    """
    return f"{task}:\n\n{user_input}"


# ─────────────────────────────────────────────────────────────────────────────
# Strategy 2: Few-Shot
# ─────────────────────────────────────────────────────────────────────────────

def build_few_shot_prompt(task: str, user_input: str) -> str:
    """
    Build a few-shot prompt by injecting 2–3 labelled examples before the input.

    The examples are selected from data/examples.py based on a keyword match
    against the task name. If no match is found, falls back to zero-shot (the
    task doesn't have curated examples yet).

    Why few-shot works:
        The model has seen millions of "Input: … Output: …" patterns during
        pre-training. Providing concrete examples activates this pattern-matching
        ability and anchors the output to the demonstrated format, tone, and depth
        — without any gradient updates (in-context learning).

    Args:
        task      : Task name string used for example set selection.
        user_input: The text the user wants analysed.

    Returns:
        Prompt string with examples prepended, ending with "Output:" to prime
        the model to continue in the demonstrated format.
    """
    # Select the right example set based on keyword presence in the task name
    if "sentiment" in task.lower():
        examples = FEW_SHOT_SENTIMENT_EXAMPLES
    elif "summar" in task.lower():
        examples = FEW_SHOT_SUMMARY_EXAMPLES
    elif "code" in task.lower() or "review" in task.lower():
        examples = FEW_SHOT_CODE_REVIEW_EXAMPLES
    else:
        # No examples available for this task — fall back to zero-shot
        return build_zero_shot_prompt(task, user_input)

    # Format each example as an Input/Output pair separated by blank lines
    shots = ""
    for ex in examples:
        shots += f"Input: {ex['input']}\nOutput: {ex['output']}\n\n"

    return f"""{task}

Here are examples of high-quality responses:

{shots}Now apply the same approach to this input:
Input: {user_input}
Output:"""


# ─────────────────────────────────────────────────────────────────────────────
# Strategy 3: Chain-of-Thought (CoT)
# ─────────────────────────────────────────────────────────────────────────────

def build_chain_of_thought_prompt(task: str, user_input: str) -> str:
    """
    Build a Chain-of-Thought prompt that forces step-by-step reasoning.

    Based on Wei et al. (2022) "Chain-of-Thought Prompting Elicits Reasoning
    in Large Language Models". The key insight: by forcing intermediate reasoning
    steps into the context window, the model allocates attention heads to
    intermediate states rather than jumping directly to a conclusion.

    The four-step scaffold is generic enough to work across all task types:
        1. Identify key elements  → grounds the model in the input
        2. Consider multiple angles → prevents premature conclusion
        3. Reason through implications → produces the middle steps
        4. Justified conclusion → ensures the final answer is backed by step 3

    Args:
        task      : Task name string.
        user_input: Text to analyse.

    Returns:
        Prompt string ending with "Step-by-step reasoning:" to trigger
        the model's reasoning trace before the final answer.
    """
    return f"""{task}

Input: {user_input}

Think through this step-by-step:
1. First, identify the key elements and context
2. Consider multiple interpretations or angles
3. Reason through the implications
4. Arrive at a well-justified conclusion

Step-by-step reasoning:"""


# ─────────────────────────────────────────────────────────────────────────────
# Strategy 4: Role Prompting
# ─────────────────────────────────────────────────────────────────────────────

def build_role_prompt(task: str, user_input: str) -> str:
    """
    Build a role prompt by assigning a task-specific expert persona.

    Why role prompting works:
        LLMs are trained on text written by experts in many fields. Assigning a
        specific professional persona activates domain-specific vocabulary, depth
        of analysis, and communication style already latent in the model's weights.
        The model doesn't gain new knowledge — it selects which parts of its
        knowledge to foreground.

    Role selection:
        The role_map matches keywords in the task name to a persona description.
        Each persona is designed to activate the most useful domain expertise:
        - "sentiment" → NLP researcher (knows affective computing vocabulary)
        - "summar"    → Technical editor (knows compression without distortion)
        - "code"      → Security engineer (knows OWASP, CVEs, secure patterns)
        - "question"  → CS professor (knows how to structure explanations)
        - "essay"     → Academic evaluator (knows rubric-based assessment)

    Args:
        task      : Task name string used for role selection.
        user_input: Text to analyse.

    Returns:
        Prompt string beginning with the persona description, then the task and input.
    """
    role_map = {
        # For sentiment: NLP + affective computing expertise
        "sentiment": (
            "You are a senior NLP researcher with 10 years of experience in computational "
            "linguistics and affective computing. You specialize in nuanced sentiment analysis "
            "for enterprise applications."
        ),
        # For summarization: precision and concision expertise
        "summar": (
            "You are an expert technical writer and editor at a leading academic journal. "
            "Your summaries are known for being precise, informative, and jargon-free."
        ),
        # For code review: security-first mindset with years of vulnerability hunting
        "code": (
            "You are a senior security engineer and code reviewer at a top tech company with "
            "15 years of experience. You have a reputation for catching subtle bugs and security "
            "vulnerabilities that others miss."
        ),
        # For Q&A: pedagogical depth and clarity
        "question": (
            "You are a world-class professor and educator with deep expertise across computer "
            "science, mathematics, and applied AI. You explain complex concepts with clarity "
            "and pedagogical precision."
        ),
        # For essay grading: rubric-based academic assessment
        "essay": (
            "You are a rigorous academic evaluator at a top university. You assess essays based "
            "on clarity of argument, use of evidence, critical thinking, and writing quality."
        ),
    }

    # Select the role whose keyword matches the task; fall back to generic expert
    role = next(
        (v for k, v in role_map.items() if k in task.lower()),
        "You are a world-class expert in your domain with exceptional analytical and communication skills.",
    )

    return f"""{role}

Your task: {task}

Input to analyze:
{user_input}

Provide your expert analysis:"""


# ─────────────────────────────────────────────────────────────────────────────
# Strategy 5: Structured Output
# ─────────────────────────────────────────────────────────────────────────────

def build_structured_output_prompt(task: str, user_input: str) -> str:
    """
    Build a prompt that enforces a specific JSON schema on the response.

    Why structured output matters in production:
        Prose responses require NLP parsing to extract actionable data.
        JSON responses are directly parseable by any downstream system —
        CI/CD pipelines, databases, dashboards, or APIs — with zero additional
        processing. This is why almost all production AI integrations use
        structured output prompting.

    Schema selection:
        Each task type has a purpose-built schema that captures the most
        useful fields for that domain. The schemas are embedded directly in
        the prompt (not via OpenAI's function calling / JSON mode) to keep
        the technique pure and visible to the audience.

    Args:
        task      : Task name string used for schema selection.
        user_input: Text to analyse.

    Returns:
        Prompt string that ends with "JSON response:" to prime JSON output,
        with the exact schema the model should conform to.
    """
    schema_map = {
        # Sentiment: confidence + intensity + evidence phrases
        "sentiment": """{
  "sentiment": "positive|negative|neutral",
  "confidence": 0.0-1.0,
  "intensity": "mild|moderate|strong",
  "key_phrases": ["phrase1", "phrase2"],
  "reasoning": "brief explanation"
}""",
        # Summarization: summary + key points + compression ratio
        "summar": """{
  "summary": "2-3 sentence summary",
  "key_points": ["point1", "point2", "point3"],
  "word_count_reduction": "X%",
  "topics": ["topic1", "topic2"]
}""",
        # Code review: severity-graded issue list — production CI/CD ready
        "code": """{
  "overall_rating": "critical|poor|acceptable|good|excellent",
  "issues": [
    {
      "severity": "critical|high|medium|low",
      "type": "security|logic|performance|style",
      "line": "affected code",
      "problem": "description",
      "fix": "suggested fix"
    }
  ],
  "summary": "overall assessment"
}""",
        # Essay: numeric rubric scores summing to 100
        "essay": """{
  "grade": "A/B/C/D/F",
  "score": 0-100,
  "rubric": {
    "argument_clarity": 0-25,
    "evidence_use": 0-25,
    "critical_thinking": 0-25,
    "writing_quality": 0-25
  },
  "strengths": ["strength1"],
  "improvements": ["improvement1"],
  "feedback": "detailed paragraph"
}""",
    }

    # Fall back to a generic schema for tasks without a specific one
    schema = next(
        (v for k, v in schema_map.items() if k in task.lower()),
        '{\n  "result": "your analysis",\n  "confidence": 0.0-1.0,\n  "reasoning": "explanation"\n}',
    )

    return f"""{task}

Input: {user_input}

Respond ONLY with valid JSON matching this exact schema:
{schema}

JSON response:"""


# ─────────────────────────────────────────────────────────────────────────────
# Strategy 6: Self-Reflection
# ─────────────────────────────────────────────────────────────────────────────

def build_self_reflection_prompt(task: str, user_input: str) -> str:
    """
    Build a three-phase self-reflection prompt: generate → critique → revise.

    Based on the 'Reflexion' paradigm (Shinn et al., 2023). The model is forced
    to act as both author and critic of its own output, catching errors that
    single-pass generation misses.

    Phase structure:
        Phase 1 — Initial Response:
            Standard generation. The model answers without constraints.
        Phase 2 — Critical Self-Review:
            The model is asked to identify its own assumptions, gaps, and errors.
            Three guiding questions focus the critique:
            - What assumptions did you make?
            - What could be wrong or incomplete?
            - What important angles did you miss?
        Phase 3 — Refined Final Answer:
            Using the self-critique as a guide, the model revises its answer.
            The revised answer should be more accurate than Phase 1.

    Why it works:
        The model's knowledge of "what a good answer looks like" is often better
        than its first-pass generation. The self-review phase lets that evaluative
        knowledge feed back into the generation process.

    Args:
        task      : Task name string.
        user_input: Text to analyse.

    Returns:
        Prompt string with three explicit phase labels. The model fills in all
        three phases sequentially, producing a visible reasoning trail.
    """
    return f"""{task}

Input: {user_input}

PHASE 1 — Initial Response:
Provide your initial analysis or answer.

PHASE 2 — Critical Self-Review:
Now critically examine your Phase 1 response:
- What assumptions did you make?
- What could be wrong or incomplete?
- What important angles did you miss?

PHASE 3 — Refined Final Answer:
Based on your self-critique, provide an improved, more accurate final response.

Begin:"""


# ─────────────────────────────────────────────────────────────────────────────
# Strategy 7: Meta-Prompting
# ─────────────────────────────────────────────────────────────────────────────

def build_meta_prompt(task: str, user_input: str) -> str:
    """
    Build a meta-prompt: ask the model to design its own ideal prompt, then use it.

    This is the most sophisticated strategy. Rather than the human engineer
    deciding how to frame the task, the model reasons about what role, context,
    format, and constraints would produce the best prompt — then executes it.

    Two-step structure:
        Step 1 — Prompt design:
            The model considers the task and decides: what persona is most useful?
            What context does it need? What output format works best? What
            constraints should be in place?
        Step 2 — Prompt execution:
            The model executes the prompt it just designed on the actual input.

    When to use:
        Novel or ambiguous tasks where the engineer isn't sure how to frame the
        prompt. The model often designs better prompts than humans for tasks it
        has seen many variants of during training.

    Args:
        task      : Task name string.
        user_input: Text to analyse.

    Returns:
        Prompt string with two explicit step labels. The model produces both
        its self-designed prompt and the resulting output.
    """
    return f"""You are a Prompt Engineering expert. Your job is to:
1. First analyze what an ideal prompt for this task would look like
2. Then use that ideal prompt to produce the best possible output

Task to accomplish: {task}
Input: {user_input}

Step 1 — Design the ideal prompt for this task:
[Think about: what role, what context, what format, what constraints would make this prompt best]

Step 2 — Execute that ideal prompt:
[Apply the prompt you designed and produce the final output]"""


# ─────────────────────────────────────────────────────────────────────────────
# Strategy registry
# ─────────────────────────────────────────────────────────────────────────────

# STRATEGIES is the single source of truth for all strategy metadata.
# app.py iterates over this dict to build the sidebar checkboxes, run loop,
# and tab labels. Adding an entry here is all that is needed to register
# a new strategy in the full application.
STRATEGIES = {
    "Zero-Shot": {
        "builder": build_zero_shot_prompt,
        "description": "Direct instruction with no examples. Tests base model capability.",
    },
    "Few-Shot": {
        "builder": build_few_shot_prompt,
        "description": "Provide 2-3 examples before the actual input. Guides format and quality.",
    },
    "Chain-of-Thought": {
        "builder": build_chain_of_thought_prompt,
        "description": "Force step-by-step reasoning before reaching a conclusion.",
    },
    "Role Prompting": {
        "builder": build_role_prompt,
        "description": "Assign a specific expert persona to prime domain knowledge.",
    },
    "Structured Output": {
        "builder": build_structured_output_prompt,
        "description": "Enforce JSON schema output for consistency and parseability.",
    },
    "Self-Reflection": {
        "builder": build_self_reflection_prompt,
        "description": "Model critiques its own first draft and produces an improved answer.",
    },
    "Meta-Prompting": {
        "builder": build_meta_prompt,
        "description": "Ask the model to design its own ideal prompt, then execute it.",
    },
}
