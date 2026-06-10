# Resume & Project Description — PromptForge

---

## One-Line Summary (for resume bullet or LinkedIn)

Built an interactive prompt engineering evaluation system that demonstrates 40–76% quality improvements across 7 prompting strategies (Zero-Shot, Few-Shot, Chain-of-Thought, Role, Structured Output, Self-Reflection, Meta-Prompting) using a custom NLP evaluation engine.

---

## Resume Project Entry (3–5 bullets)

**PromptForge — Prompt Engineering Evaluation Laboratory** | Python, Streamlit, OpenAI API
*Tools: OpenAI GPT API · Streamlit · Plotly · Pandas · Python NLP*

- Designed and built an interactive web application comparing 7 prompt engineering strategies (Zero-Shot, Few-Shot, Chain-of-Thought, Role Prompting, Structured Output, Self-Reflection, Meta-Prompting) on the same LLM model and input, demonstrating measurable quality improvements of 38–76% over baseline.
- Engineered a custom heuristic evaluation engine measuring LLM response quality across 5 dimensions (content richness, readability via Flesch-Kincaid, specificity, reasoning depth, structure) — achieving quality scoring without human annotation or secondary LLM evaluation.
- Implemented a controlled experimental design where all strategies use identical model (GPT-4o-mini), temperature, max_tokens, and input — isolating prompt design as the sole independent variable.
- Built an interactive Streamlit dashboard with real-time side-by-side strategy comparison, Plotly visualizations (bar chart, radar chart, quality-vs-token scatter), and a custom HTML comparison table with severity badges.

---

## Project Description — Academic Submission Format

**Project Title:** PromptForge: An Interactive Laboratory for Measuring Prompt Engineering Impact on LLM Output Quality

**Abstract:**
PromptForge is a controlled laboratory system designed to demonstrate and quantify the effect of prompt engineering on Large Language Model output quality. The system applies seven distinct prompting strategies — Zero-Shot, Few-Shot, Chain-of-Thought, Role Prompting, Structured Output, Self-Reflection, and Meta-Prompting — to identical inputs on the same model under identical inference settings. Response quality is evaluated using a custom heuristic engine measuring five dimensions: content richness (word count), readability (Flesch-Kincaid), specificity (numeric density, vocabulary diversity), reasoning depth (causal connector frequency), and structural organisation. A composite Quality Score (0–100) drives an interactive Streamlit dashboard featuring real-time side-by-side comparison, three chart types, and a full prompt-and-response viewer per strategy. Experimental results show quality improvements of 38–76% over zero-shot baseline, with Chain-of-Thought providing the best quality-to-token-cost tradeoff (+69% at minimal overhead) and Self-Reflection achieving the highest absolute score (+76% at 2× token cost).

**Technologies:** Python 3.11, OpenAI SDK (gpt-4o-mini), Streamlit 1.35, Plotly, python-dotenv, custom NLP evaluation pipeline.

**Key Contributions:**
- Controlled experimental design isolating prompt design as the independent variable
- Heuristic quality evaluation engine requiring no human annotation or secondary LLM
- Modular strategy registry enabling rapid addition of new prompting techniques
- Production-ready dashboard with responsive light theme and machine-parseable HTML table

---

## Interview / Viva Description (spoken, 2 minutes)

"PromptForge is a project I built to solve a specific problem: there's no standard way to demonstrate or measure the impact of different prompt engineering strategies on LLM output. Most people know that 'better prompts give better results' but can't quantify it or show it live.

The system works like a controlled experiment. I take one piece of text, send it through seven different prompting strategies to the exact same model with the same settings, and measure the quality of each response. The only variable is the prompt design.

The hardest engineering challenge was the evaluation engine — how do you measure LLM output quality without using another LLM, which would be circular? I built a custom NLP scorer using five heuristics: word count for completeness, Flesch-Kincaid for readability, numeric density and vocabulary diversity for specificity, causal connector frequency for reasoning depth, and JSON parseability for structured output. Combined, they give a 0–100 quality score.

The results are striking. Zero-shot baseline scores around 42. Chain-of-Thought — which adds 'think step by step' — scores 71. That's a 69% improvement from 12 extra words. Self-reflection, which has the model critique and revise its own answer, scores 74 but costs twice the tokens.

The dashboard shows all of this in real time: side-by-side prompts and responses, quality metric charts, and a comparison table. It's designed to be used as a live demonstration during the presentation.

The project demonstrates seven key prompt engineering techniques, a custom evaluation methodology, and the full engineering cycle of design → build → measure → visualize."

---

## LinkedIn / Portfolio Summary

**PromptForge — Prompt Engineering Evaluation Laboratory**

An interactive lab that proves prompt engineering works — with numbers, not just intuition.

The same input. The same AI model. Seven different prompt designs. Measurably different outputs.

Built with Python, Streamlit, and the OpenAI API, PromptForge runs seven prompting strategies (Zero-Shot, Few-Shot, Chain-of-Thought, Role Prompting, Structured Output, Self-Reflection, Meta-Prompting) on identical inputs and evaluates each response using a custom NLP quality scoring engine — no human raters, no secondary LLM.

Key results: 38–76% quality improvement over baseline. Chain-of-Thought shows +69% from 12 extra words.

Technologies: Python · Streamlit · OpenAI SDK · Plotly · Custom NLP evaluation

---

## Project Card (one-paragraph format for portfolio websites)

PromptForge is a prompt engineering evaluation laboratory built to quantify the impact of seven prompting strategies — Zero-Shot, Few-Shot, Chain-of-Thought, Role Prompting, Structured Output, Self-Reflection, and Meta-Prompting — on LLM response quality. The system applies each strategy to the same input on the same model under identical inference conditions, then scores each response across five quality dimensions using a custom NLP evaluation engine. An interactive Streamlit dashboard presents results in real time with side-by-side prompt/response viewers, three Plotly charts, and a full comparison table. Results show 38–76% quality improvement over zero-shot baseline, with Chain-of-Thought delivering the best quality-to-cost tradeoff. Built with Python, OpenAI's gpt-4o-mini, Streamlit, and Plotly.
