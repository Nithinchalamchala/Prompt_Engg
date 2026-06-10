"""
data/examples.py
----------------
Curated few-shot examples used by the Few-Shot prompting strategy.

Each list contains 2–3 high-quality input/output pairs for a specific task type.
The few-shot strategy builder (prompts/strategies.py) selects the appropriate list
based on a keyword match against the task name, then injects these pairs into the
prompt before the actual user input.

Why this matters:
    Without examples, the model must infer the desired output format from the
    instruction alone (zero-shot). With examples, the model anchors its response
    to the demonstrated format, tone, and depth — this is 'in-context learning'.

Adding new task types:
    1. Create a new list following the {"input": ..., "output": ...} schema.
    2. Export it at the bottom of this file.
    3. Register the keyword match in build_few_shot_prompt() in strategies.py.
"""


# ─────────────────────────────────────────────────────────────────────────────
# Sentiment Analysis Examples
# Expected output: JSON with sentiment label, confidence, key phrases, intensity.
# These examples cover the three polarity classes (negative, neutral, positive)
# so the model sees all possible output values before it classifies.
# ─────────────────────────────────────────────────────────────────────────────
FEW_SHOT_SENTIMENT_EXAMPLES = [
    {
        "input": "The product arrived damaged and customer service was useless.",
        # Strong negative — both physical problem and service failure present
        "output": '{"sentiment": "negative", "confidence": 0.95, "key_phrases": ["arrived damaged", "useless"], "intensity": "strong"}'
    },
    {
        "input": "Delivery was okay, product works fine but nothing special.",
        # Neutral — mixed mild positives and negatives cancel out
        "output": '{"sentiment": "neutral", "confidence": 0.78, "key_phrases": ["okay", "works fine", "nothing special"], "intensity": "mild"}'
    },
    {
        "input": "Absolutely exceeded my expectations! Best purchase this year.",
        # Strong positive — superlatives and exclamation indicate high intensity
        "output": '{"sentiment": "positive", "confidence": 0.98, "key_phrases": ["exceeded expectations", "best purchase"], "intensity": "strong"}'
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Text Summarization Examples
# Expected output: A single concise sentence that preserves the core claim.
# Two examples show the model that we want compression without distortion —
# the summary should not introduce facts not in the original.
# ─────────────────────────────────────────────────────────────────────────────
FEW_SHOT_SUMMARY_EXAMPLES = [
    {
        "input": (
            "Artificial intelligence is transforming healthcare by enabling faster diagnosis, "
            "personalized treatment plans, and drug discovery. Machine learning models can analyze "
            "medical images with accuracy comparable to specialists."
        ),
        # Covers all three use cases from the input in one sentence
        "output": (
            "AI is revolutionizing healthcare through faster diagnosis, personalized treatments, "
            "and drug discovery, with ML models matching specialist accuracy in image analysis."
        )
    },
    {
        "input": (
            "Climate change poses significant risks to global food security. Rising temperatures, "
            "extreme weather events, and shifting precipitation patterns are already affecting crop "
            "yields in many regions."
        ),
        # Preserves the causal chain (climate change → mechanisms → crop yields)
        "output": (
            "Climate change threatens global food security by reducing crop yields through "
            "rising temperatures, extreme weather, and altered rainfall patterns."
        )
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Code Review Examples
# Expected output: A severity label followed by a specific, actionable fix.
# Both examples are real-world security vulnerabilities (SQL injection,
# plaintext passwords) so the model understands we want security-first analysis.
# ─────────────────────────────────────────────────────────────────────────────
FEW_SHOT_CODE_REVIEW_EXAMPLES = [
    {
        "input": (
            "def get_user(id):\n"
            '    query = f"SELECT * FROM users WHERE id = {id}"\n'
            "    return db.execute(query)"
        ),
        # Demonstrates the expected format: SEVERITY: issue. Fix: specific code change.
        "output": (
            "CRITICAL: SQL Injection vulnerability. User-controlled input `id` is directly "
            "interpolated into the query string. Fix: use parameterized queries — "
            "`db.execute('SELECT * FROM users WHERE id = ?', (id,))`"
        )
    },
    {
        "input": (
            "password = input('Enter password: ')\n"
            "if password == stored_password:"
        ),
        # Shows that non-SQL issues (auth, crypto) follow the same output format
        "output": (
            "SECURITY: Plaintext password comparison. Passwords should be hashed. "
            "Fix: use `bcrypt.checkpw(password.encode(), stored_hash)` instead of direct comparison."
        )
    },
]
