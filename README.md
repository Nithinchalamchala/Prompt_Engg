# PromptForge — Prompt Engineering Evaluation Laboratory

An interactive lab that proves prompt engineering works — with numbers, not just intuition.

> "The same model. The same input. Measurably different outputs.  
> The only variable is prompt engineering."

---

## What Is This?

PromptForge is a controlled laboratory system that applies **7 prompting strategies** to the same input on the same LLM model under identical inference settings, then scores each response using a **custom NLP evaluation engine** — no human raters, no secondary LLM.

Every strategy run answers the question: *how much does prompt design alone change output quality?*

**Answer: 38–76% improvement over zero-shot baseline.**

---

## Live Demo

```
cd promptforge
conda activate base          # or: pip install -r requirements.txt
cp .env.example .env         # then add your OpenAI API key inside
streamlit run app.py
```

Open **http://localhost:8501**

---

## The 7 Strategies

| # | Strategy | Core Idea | Quality Gain |
|---|---|---|---|
| 1 | **Zero-Shot** | Direct instruction, no examples | baseline |
| 2 | **Few-Shot** | 2–3 labelled examples before the task | +38% |
| 3 | **Chain-of-Thought** | "Think step-by-step" | +69% |
| 4 | **Role Prompting** | Assign expert persona | +62% |
| 5 | **Structured Output** | Enforce JSON schema | +55% |
| 6 | **Self-Reflection** | Generate → critique → revise | +76% |
| 7 | **Meta-Prompting** | Model designs its own prompt | +67% |

---

## Project Structure

```
Prompt_Engg/
│
├── promptforge/                  # Main application
│   ├── app.py                    # Streamlit dashboard (entry point)
│   ├── requirements.txt          # Python dependencies
│   ├── .env.example              # API key template
│   │
│   ├── .streamlit/
│   │   └── config.toml           # Light theme configuration
│   │
│   ├── prompts/
│   │   ├── strategies.py         # 7 prompt builder functions
│   │   └── templates.py          # Task configs & default inputs
│   │
│   ├── engine/
│   │   ├── llm_client.py         # OpenAI API abstraction
│   │   └── evaluator.py          # NLP quality scoring engine
│   │
│   └── data/
│       └── examples.py           # Few-shot example sets
│
└── presentation/                 # Presentation materials
    ├── slides.tex                # LaTeX Beamer slides (16 slides)
    ├── speaker_notes.md          # Slide-by-slide delivery guide
    ├── demo_script.md            # Word-for-word live demo script
    ├── qa_prep.md                # 14 faculty Q&A with full answers
    └── resume_description.md     # Resume/portfolio/LinkedIn formats
```

---

## How It Works

```
User Input (Task + Text)
        │
        ▼
Prompt Strategy Engine  ──→  7 different prompts built from same input
        │
        ▼
OpenAI GPT (gpt-4o-mini)  ──→  Same model × 7 API calls
        │
        ▼
Evaluation Engine  ──→  Quality Score (0–100) per response
        │
        ▼
Streamlit Dashboard  ──→  Side-by-side comparison + charts
```

---

## Evaluation Methodology

The quality scoring engine uses **5 deterministic NLP heuristics** — no LLM judge needed:

| Metric | Method | Max Points | What It Captures |
|---|---|---|---|
| Content Richness | word_count / 5, capped | 30 | Completeness |
| Readability | Flesch-Kincaid formula | 20 | Clarity |
| Specificity | Numbers + quotes + vocab diversity | 20 | Concreteness |
| Reasoning Depth | Causal connectors (because, thus…) | 20 | Logical structure |
| Structure Bonus | Lists / headers / JSON keys | 5 | Organisation |
| JSON Validity | Parseable `{}` block present | 5 | Machine readability |
| **Total** | | **100** | |

---

## Setup

### Requirements

- Python 3.10+
- OpenAI API key (free tier works — each full run costs ~$0.01)

### Installation

```bash
git clone https://github.com/Nithinchalamchala/Prompt_Engg.git
cd Prompt_Engg/promptforge

pip install -r requirements.txt

cp .env.example .env
# Edit .env and add:  OPENAI_API_KEY=sk-...

streamlit run app.py
```

### Running with Conda

```bash
conda activate base
cd Prompt_Engg/promptforge
conda run -n base streamlit run app.py
```

---

## Tasks Included

| Task | Best Strategy to Demo | Why |
|---|---|---|
| **Code Review** | Chain-of-Thought + Structured | Zero-shot misses SQL injection; CoT finds it |
| Sentiment Analysis | Structured Output | Shows clean JSON vs prose comparison |
| Text Summarization | Role Prompting | Editor persona produces tightest summaries |
| Question Answering | Chain-of-Thought | Step-by-step reasoning visibly improves structure |
| Essay Grading | Role Prompting | Academic evaluator persona adds rubric depth |

**Best demo task: Code Review.** The input contains a real SQL injection vulnerability. Zero-shot misses it. Chain-of-Thought finds it. Structured output wraps it in parseable JSON with severity levels.

---

## Presentation Materials

All presentation materials are in [`presentation/`](presentation/):

- **[slides.tex](presentation/slides.tex)** — LaTeX Beamer presentation (16 slides).  
  Compile with: `pdflatex slides.tex && pdflatex slides.tex`

- **[speaker_notes.md](presentation/speaker_notes.md)** — Word-for-word delivery guide with timing for each slide.

- **[demo_script.md](presentation/demo_script.md)** — Step-by-step live demo script including what to say while each strategy runs, what to point at, and how to handle failures.

- **[qa_prep.md](presentation/qa_prep.md)** — 14 expected faculty/evaluator questions across 4 categories with complete answers.

- **[resume_description.md](presentation/resume_description.md)** — 5 formats: resume bullets, academic abstract, 2-minute spoken description, LinkedIn summary, portfolio card.

---

## Key Results

Tested on the **Code Review** task (SQL injection detection):

```
Zero-Shot        →  42/100   baseline
Few-Shot         →  58/100   +38%
Chain-of-Thought →  71/100   +69%  ← best quality/cost tradeoff
Role Prompting   →  68/100   +62%
Structured Output→  65/100   +55%
Self-Reflection  →  74/100   +76%  ← highest quality, 2× tokens
Meta-Prompting   →  70/100   +67%
```

---

## Limitations

- Evaluation metrics are heuristic, not ground-truth human ratings
- Semantic correctness is not verified — only structural quality
- Results depend on model version (gpt-4o-mini)
- No RAG (retrieval-augmented generation) support yet

---

## Future Scope

- [ ] RAG integration (ChromaDB + document corpus)
- [ ] Human-in-the-loop evaluation to calibrate quality metrics
- [ ] Automatic prompt optimizer using quality score as fitness function
- [ ] Multi-model comparison (GPT-4, Claude, Gemini)
- [ ] Agentic chaining (auto-select best strategy per task)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| LLM API | OpenAI SDK (`gpt-4o-mini`) |
| UI | Streamlit |
| Charts | Plotly |
| Data | Pandas |
| Config | python-dotenv |
| Evaluation | Custom NLP (stdlib only) |

---

## References

- Wei et al. (2022) — *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*. NeurIPS.
- Shinn et al. (2023) — *Reflexion: Language Agents with Verbal Reinforcement Learning*. NeurIPS.
- Brown et al. (2020) — *Language Models are Few-Shot Learners*. NeurIPS.
- Flesch (1948) — A new readability yardstick. *Journal of Applied Psychology*.

---

## License

MIT License — free to use, modify, and distribute with attribution.
