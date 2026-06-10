"""
engine/evaluator.py
-------------------
Heuristic evaluation engine for LLM response quality.

Purpose:
    Quantify the quality of an LLM response WITHOUT using another LLM as a judge
    (which would be circular, slow, and expensive). Instead, we compute a set of
    NLP heuristics that are fast, deterministic, and independently explainable.

The composite Quality Score (0–100) is built from five dimensions:

    Dimension           Weight  What it captures
    ──────────────────  ──────  ──────────────────────────────────────────────
    Content richness     ≤ 30   Word count as a proxy for completeness
    Readability          ≤ 20   Flesch-Kincaid: are the sentences clear?
    Specificity          ≤ 20   Numbers, quoted terms, vocabulary diversity
    Reasoning depth      ≤ 20   Causal connectors (because, therefore, thus…)
    Structure bonus      +  5   Lists, headers, JSON keys present?
    JSON validity bonus  +  5   Response is parseable JSON?

Limitations (acknowledged in the presentation):
    - Metrics are heuristic, not ground-truth human ratings.
    - A verbose but shallow response can score higher than a short but precise one.
    - Semantic correctness is NOT checked — only structural quality.
    - Results are model-version dependent.

These limitations are intentional discussion points in the Q&A.
"""

import re
import json


# ─────────────────────────────────────────────────────────────────────────────
# Low-level text statistics
# ─────────────────────────────────────────────────────────────────────────────

def count_words(text: str) -> int:
    """
    Count whitespace-delimited tokens in text.

    Simple split() is used deliberately — we want a fast approximation of
    content length, not a linguistically precise word count.

    Args:
        text: Any string.

    Returns:
        Integer word count. Empty string returns 0.
    """
    return len(text.split())


def count_sentences(text: str) -> int:
    """
    Count sentences by splitting on terminal punctuation (.  !  ?).

    Returns at least 1 to avoid division-by-zero in readability formulas.

    Args:
        text: Any string.

    Returns:
        Number of non-empty sentence fragments (minimum 1).
    """
    sentences = re.split(r'[.!?]+', text)
    return max(1, len([s for s in sentences if s.strip()]))


def _count_syllables(word: str) -> int:
    """
    Estimate syllable count for a single word using vowel-group heuristics.

    Algorithm:
        1. Strip leading/trailing punctuation and lowercase.
        2. Count vowel groups (consecutive vowels = 1 syllable).
        3. Subtract 1 for silent trailing 'e'.
        4. Return at least 1 (every word has at least one syllable).

    This is a well-known approximation — not linguistically perfect but
    accurate enough for Flesch-Kincaid scoring at corpus scale.

    Args:
        word: A single word token (may include punctuation).

    Returns:
        Estimated syllable count (integer ≥ 1).
    """
    word = word.lower().strip(".,!?;:")

    # Very short words are almost always monosyllabic
    if len(word) <= 3:
        return 1

    vowels = "aeiouy"
    count = 0
    prev_vowel = False

    for char in word:
        is_vowel = char in vowels
        # New vowel group starts only when transitioning from consonant to vowel
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel

    # Silent trailing 'e' does not form its own syllable (e.g. "make" = 1, not 2)
    if word.endswith("e"):
        count = max(1, count - 1)

    return max(1, count)


def flesch_reading_ease(text: str) -> float:
    """
    Compute the Flesch Reading Ease score for a block of text.

    Formula (Flesch, 1948):
        206.835 − 1.015 × (words/sentences) − 84.6 × (syllables/words)

    Score interpretation:
        90–100  : Very easy (5th grade)
        60–70   : Standard (8th–9th grade)
        30–50   : Difficult (college level)
        0–30    : Very difficult (professional/academic)

    Higher score = easier to read. Clamped to [0, 100].

    Args:
        text: Multi-sentence string to evaluate.

    Returns:
        Float in [0.0, 100.0]. Returns 0.0 for empty input.
    """
    words = count_words(text)
    sentences = count_sentences(text)

    # Guard against empty or single-character input
    if words == 0 or sentences == 0:
        return 0.0

    syllables = sum(_count_syllables(w) for w in text.split())
    score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)

    # Clamp to valid range — extreme sentence structures can push outside [0, 100]
    return round(max(0, min(100, score)), 1)


# ─────────────────────────────────────────────────────────────────────────────
# Content quality signals
# ─────────────────────────────────────────────────────────────────────────────

def has_structure(text: str) -> bool:
    """
    Detect whether a response contains explicit structural formatting.

    Structural markers indicate the model organised its thoughts rather than
    producing a wall of prose. This is a strong signal of prompt engineering
    effectiveness — zero-shot rarely produces structure; CoT and structured
    output prompts almost always do.

    Patterns checked:
        \\d+\\.      — numbered list items  (1. 2. 3.)
        [-•*]        — bullet points
        \\*\\*…\\*\\* — bold markdown
        ##|###       — markdown headers
        "key":       — JSON object keys
        Step \\d     — explicit step labels
        Phase \\d    — phase labels (self-reflection output)

    Args:
        text: Model response string.

    Returns:
        True if any structural pattern is found, False otherwise.
    """
    structure_markers = [
        r'\d+\.',        # numbered lists:  1. 2. 3.
        r'[-•*]',        # bullet points
        r'\*\*.*\*\*',   # markdown bold
        r'##|###',       # markdown headers
        r'"[^"]+":',     # JSON keys  "key":
        r'Step \d',      # step-by-step markers
        r'Phase \d',     # phase labels from self-reflection
    ]
    return any(re.search(pattern, text) for pattern in structure_markers)


def is_valid_json(text: str) -> bool:
    """
    Check whether the response contains a parseable JSON object.

    Uses regex to locate the outermost {...} block first (handles responses
    that include preamble text before the JSON), then attempts json.loads().

    This metric specifically rewards the Structured Output strategy, where the
    prompt explicitly demands JSON. If zero-shot accidentally produces JSON it
    also scores the bonus, but that is intentional — we reward the output property,
    not just the strategy.

    Args:
        text: Model response string.

    Returns:
        True if a valid JSON object is found anywhere in the text, False otherwise.
    """
    cleaned = text.strip()

    # Find the first { ... } block, allowing newlines inside (re.DOTALL)
    json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if json_match:
        try:
            json.loads(json_match.group())
            return True
        except (json.JSONDecodeError, ValueError):
            pass

    return False


def specificity_score(text: str) -> float:
    """
    Estimate how specific and concrete the response is (0.0 to 1.0).

    Vague responses use generalities; specific responses reference exact numbers,
    quote terms from the input, and use varied vocabulary. This heuristic captures
    that without semantic understanding.

    Components:
        - Number frequency: each numeric token contributes 0.05 (capped)
        - Quoted term frequency: each quoted phrase contributes 0.10 (capped)
        - Vocabulary diversity: unique_words / total_words (type-token ratio)

    Args:
        text: Model response string.

    Returns:
        Float in [0.0, 1.0]. Higher = more specific.
    """
    # Count standalone numeric tokens (integers and decimals)
    has_numbers = len(re.findall(r'\b\d+\.?\d*\b', text))

    # Count quoted phrases of at least 3 characters — likely domain terms or citations
    has_quotes = len(re.findall(r'"[^"]{3,}"', text))

    # Type-token ratio: high diversity = varied vocabulary = more specific
    word_variety = len(set(text.lower().split())) / max(1, count_words(text))

    score = min(1.0, (has_numbers * 0.05 + has_quotes * 0.1 + word_variety * 0.5))
    return round(score, 2)


def reasoning_depth_score(text: str) -> float:
    """
    Score how deeply the response reasons through its answer (0.0 to 1.0).

    Causal and logical connectors (because, therefore, thus, consequently…)
    indicate that the model is explaining its reasoning rather than just stating
    conclusions. This directly measures the impact of Chain-of-Thought prompting.

    The score is computed as: min(1.0, hits / 8), so 8 or more reasoning words
    in the response yields the maximum score.

    Args:
        text: Model response string.

    Returns:
        Float in [0.0, 1.0]. Higher = deeper explicit reasoning.
    """
    # Expanded list of reasoning connectors used in academic and analytical writing
    reasoning_words = [
        "because", "therefore", "however", "although", "since", "thus",
        "consequently", "furthermore", "specifically", "in contrast", "notably",
        "this means", "which suggests", "as a result", "step", "first", "second",
        "finally", "critically", "importantly",
    ]

    text_lower = text.lower()

    # Count how many distinct reasoning words appear at least once
    hits = sum(1 for w in reasoning_words if w in text_lower)

    # Normalise: 8 hits = full score. Prevents penalising short-but-deep responses.
    return round(min(1.0, hits / 8), 2)


# ─────────────────────────────────────────────────────────────────────────────
# Master evaluation function
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_response(
    prompt: str,
    response: str,
    input_tokens: int,
    output_tokens: int,
) -> dict:
    """
    Run all quality metrics on a single LLM response and return a results dict.

    This is the only function called from app.py. It aggregates all sub-metrics
    and computes the composite Quality Score that drives the dashboard charts.

    Composite Quality Score breakdown (max 100):
        ≤ 30  Content richness  : word_count / 5, capped at 30
              (150+ word response = full content points)
        ≤ 20  Readability       : flesch_reading_ease / 100 × 20
        ≤ 20  Specificity       : specificity_score × 20
        ≤ 20  Reasoning depth   : reasoning_depth_score × 20
        +  5  Structure bonus   : if has_structure
        +  5  JSON validity     : if is_valid_json

    Args:
        prompt       : The prompt sent to the model (used only for word count).
        response     : The raw text response from the model.
        input_tokens : Tokens consumed by the prompt (from API usage metadata).
        output_tokens: Tokens in the response (from API usage metadata).

    Returns:
        dict with keys:
            word_count        (int)   — Response word count
            sentence_count    (int)   — Approximate sentence count
            reading_ease      (float) — Flesch Reading Ease score [0, 100]
            has_structure     (bool)  — Structural formatting detected
            is_valid_json     (bool)  — Response contains parseable JSON
            specificity_score (float) — Specificity signal [0.0, 1.0]
            reasoning_depth   (float) — Reasoning depth signal [0.0, 1.0]
            token_efficiency  (float) — Words produced per input token
            quality_score     (float) — Composite quality score [0.0, 100.0]
            prompt_word_count (int)   — Word count of the input prompt
    """
    # Compute all sub-metrics
    word_count      = count_words(response)
    sentence_count  = count_sentences(response)
    reading_ease    = flesch_reading_ease(response)
    structured      = has_structure(response)
    json_valid      = is_valid_json(response)
    specificity     = specificity_score(response)
    reasoning_depth = reasoning_depth_score(response)

    # Output words per input token — measures how much useful content
    # the model produces relative to how much it was given to read
    token_efficiency = round(word_count / max(1, input_tokens), 3)

    # ── Composite quality score ──────────────────────────────────────────────
    quality = (
        min(30, word_count / 5)       +   # Content richness — capped so verbosity alone can't win
        (reading_ease / 100) * 20     +   # Readability contribution
        (specificity * 20)            +   # Specificity contribution
        (reasoning_depth * 20)        +   # Reasoning depth contribution
        (5 if structured else 0)      +   # Bonus: response is organised
        (5 if json_valid else 0)          # Bonus: response is machine-parseable
    )

    return {
        "word_count":        word_count,
        "sentence_count":    sentence_count,
        "reading_ease":      reading_ease,
        "has_structure":     structured,
        "is_valid_json":     json_valid,
        "specificity_score": specificity,
        "reasoning_depth":   reasoning_depth,
        "token_efficiency":  token_efficiency,
        "quality_score":     round(min(100, quality), 1),  # Hard cap at 100
        "prompt_word_count": count_words(prompt),
    }
