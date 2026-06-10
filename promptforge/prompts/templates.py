"""
prompts/templates.py
--------------------
Task configuration registry for PromptForge.

Each entry in TASK_CONFIGS defines one lab task that can be selected from the
sidebar. The task name is passed to every prompt builder function as the `task`
argument, so all 7 strategies automatically operate on the same task description.

Schema per entry:
    description         : One-line human-readable goal shown in the sidebar.
    default_input       : Pre-loaded example text shown in the input text area.
                          Chosen to be interesting and to expose meaningful
                          differences between prompting strategies.
    expected_output_type: Describes the ideal response format — used in the
                          landing page and slide explanations.

Design notes:
    - "Code Review" is the best demo task: zero-shot misses the SQL injection,
      CoT catches it step-by-step, structured output wraps it in parseable JSON.
    - "Sentiment Analysis" shows the clearest structured output difference.
    - "Essay Grading" shows role prompting impact most dramatically.
"""

TASK_CONFIGS = {

    # ── Sentiment Analysis ────────────────────────────────────────────────────
    # The default input is a realistic negative customer complaint with mixed
    # signals (angry tone + specific details) to make the classification
    # non-trivial and expose differences in nuance across strategies.
    "Sentiment Analysis": {
        "description": "Analyze the sentiment of a given text",
        "default_input": (
            "The new software update completely broke my workflow. I've lost hours trying "
            "to fix issues that didn't exist before. The support team keeps sending "
            "copy-paste responses."
        ),
        "expected_output_type": "structured JSON with sentiment, confidence, key phrases",
    },

    # ── Text Summarization ────────────────────────────────────────────────────
    # Multi-sentence technical paragraph about LLMs — chosen because the ideal
    # summary requires understanding which facts are load-bearing vs. decorative.
    # CoT and role prompting visibly improve the signal-to-noise ratio here.
    "Text Summarization": {
        "description": "Summarize a given passage concisely",
        "default_input": (
            "Large language models (LLMs) are neural networks trained on massive text datasets "
            "to understand and generate human language. They work by predicting the next token "
            "in a sequence, learning patterns, grammar, facts, and even reasoning abilities. "
            "Models like GPT-4 and Claude use transformer architectures with billions of "
            "parameters. They can perform tasks like translation, coding, analysis, and creative "
            "writing without task-specific training — a capability called zero-shot generalization. "
            "However, they also hallucinate facts, carry biases from training data, and struggle "
            "with very recent events."
        ),
        "expected_output_type": "2-3 sentence summary",
    },

    # ── Code Review ───────────────────────────────────────────────────────────
    # BEST DEMO TASK. The login function contains a classic SQL injection
    # vulnerability (f-string interpolation directly into a query). Zero-shot
    # typically misses or underweights it. CoT finds it through reasoning.
    # Role prompting adds security vocabulary. Structured output gives severity.
    "Code Review": {
        "description": "Review code for bugs, security issues, and improvements",
        "default_input": (
            "def login(username, password):\n"
            "    query = f\"SELECT * FROM users WHERE username='{username}' AND password='{password}'\"\n"
            "    result = db.execute(query)\n"
            "    if result:\n"
            "        session['user'] = username\n"
            "        return True\n"
            "    return False"
        ),
        "expected_output_type": "structured review with severity levels",
    },

    # ── Question Answering ────────────────────────────────────────────────────
    # An open-ended ML concepts question that requires comparing three paradigms.
    # CoT produces a clearly structured comparison; zero-shot tends to be shallow.
    "Question Answering": {
        "description": "Answer a factual or analytical question",
        "default_input": (
            "What are the main differences between supervised, unsupervised, and reinforcement "
            "learning? When would you use each approach?"
        ),
        "expected_output_type": "clear, structured answer",
    },

    # ── Essay Grading ─────────────────────────────────────────────────────────
    # Intentionally weak essay (vague claims, no evidence, short). Role prompting
    # with an 'academic evaluator' persona produces the most detailed rubric-style
    # feedback compared to zero-shot, making the strategy difference very visible.
    "Essay Grading": {
        "description": "Grade a student essay with detailed feedback",
        "default_input": (
            "Artificial intelligence will change everything. It can do many things humans do "
            "but faster. Some people worry about jobs but AI will also create new ones. "
            "Overall AI is good for society because it helps doctors and scientists. "
            "We should embrace it carefully."
        ),
        "expected_output_type": "grade, rubric scores, detailed feedback",
    },
}
