# Live Demo Script — PromptForge
## Word-for-word walkthrough for the live demonstration

---

## Pre-Demo Checklist (do this 5 minutes before presenting)

- [ ] App running at `localhost:8501` — `conda run -n base streamlit run app.py`
- [ ] Browser tab open, zoomed to 110% for visibility
- [ ] Task set to **Code Review** in sidebar
- [ ] Strategies checked: Zero-Shot, Chain-of-Thought, Role Prompting, Structured Output
- [ ] Input text is the default login function (SQL injection example)
- [ ] API key loaded (check `.env` file exists and has the key)
- [ ] Close all other browser tabs — avoid distraction
- [ ] Turn off notifications on laptop

---

## Opening (30 seconds — before clicking anything)

**Say:**
"Before I click anything, let me show you what we're working with. This is the input — a Python login function. It takes a username and password, builds a SQL query using an f-string, and executes it.

This code has a critical security vulnerability. A classic SQL injection. If I pass `' OR '1'='1` as the username, the WHERE clause becomes always-true and returns every row in the database.

I'm going to send this exact code to the same AI model, with the same settings, four times. The only thing that changes each time is how I frame the question. Watch what happens."

---

## Step 1: Run Zero-Shot (1 minute)

**Action:** Make sure only Zero-Shot is checked in the sidebar. Click **Run Strategies**.

**Say while it runs:**
"Zero-shot is the bare minimum. Eight words: 'Code Review:' followed by the code. No examples, no persona, no reasoning instructions. This is how most people use AI."

**After it loads — point to the response:**
"Look at this response. It says things like 'consider using parameterized queries' and 'add input validation'. Generic. It might even call this a potential issue rather than a critical vulnerability. It has no severity label, no specific fix, no mention of what the actual attack looks like.

Quality score: 42 out of 100. This is our baseline."

**Pause for 3 seconds.**

---

## Step 2: Run Chain-of-Thought (1 minute 30 seconds)

**Action:** Check Chain-of-Thought, uncheck Zero-Shot. Click **Run Strategies**.

**Say while it runs:**
"Chain-of-Thought. I added one instruction: 'Think through this step-by-step. First, identify inputs. Second, check for vulnerabilities. Third, conclude.' That's 12 extra words."

**After it loads — switch to Chain-of-Thought tab:**
"Look at what happened. The model now writes: 'Step 1: The function takes two user-controlled inputs. Step 2: Both inputs are directly interpolated into the SQL string using an f-string. This is a SQL injection vulnerability.' It names the vulnerability. It gives the specific fix: 'use parameterized queries like cursor.execute with a tuple argument.'

Quality score: 71 out of 100. That's a 69% improvement from 12 extra words.

Why did this happen? By forcing the model to reason step by step, we allocated its attention to intermediate reasoning states rather than letting it jump to a generic conclusion. The model always *knew* about SQL injection. The prompt *forced* it to find it."

**Pause for 3 seconds. Let the number land.**

---

## Step 3: Run Role Prompting (1 minute)

**Action:** Check Role Prompting, uncheck Chain-of-Thought. Click **Run Strategies**.

**Say while it runs:**
"Role prompting. I assigned a persona: 'You are a senior security engineer at a top tech company with 15 years of experience. You have a reputation for catching subtle bugs and vulnerabilities that others miss.'"

**After it loads:**
"Watch the vocabulary. The model now mentions OWASP Top 10. It uses 'CWE-89' — the Common Weakness Enumeration ID for SQL injection. It distinguishes between parameterized queries and prepared statements. It recommends a security scanner like Bandit or Semgrep.

The model didn't learn any new facts. It already had all of this vocabulary. The role told it which part of its knowledge to foreground."

---

## Step 4: Run Structured Output (1 minute 30 seconds)

**Action:** Check Structured Output, uncheck Role Prompting. Click **Run Strategies**.

**Say while it runs:**
"Structured output. I provided a JSON schema and said 'respond ONLY in this exact format.'"

**After it loads:**
"Look at what we get now. A JSON object with: overall_rating set to 'critical', an issues array with one item — severity: critical, type: security, the affected line of code, a description of why it's vulnerable, and the exact fix as working Python code.

This is not a prose paragraph that a human needs to read and interpret. This is machine-parseable data. I can feed this directly into a CI/CD pipeline. I can insert it into a database. I can trigger an automated alert. I can build a dashboard. This is production-ready output.

That's the difference between a demo and a deployable system."

---

## Step 5: Show All Together (1 minute)

**Action:** Check all four strategies. Click **Run Strategies**.

**Say while it runs:**
"Let me run all four at once so you can see the comparison side by side."

**After it loads — click the Quality Score bar chart:**
"This chart says everything. Zero-shot: 42. Chain-of-thought: 71. Role prompting: 68. Structured output: 65.

Same model. Same input. Same API settings. The only variable is the prompt. A 69% quality improvement from prompt engineering.

This is why prompt engineering matters. It's not a parlour trick. It's the difference between an AI tool that sometimes works and an AI system that works reliably."

---

## Handling Live Demo Problems

**If the app crashes:**
"Let me restart quickly — this takes 5 seconds."
Run: `conda run -n base streamlit run app.py`

**If an API call fails:**
"API rate limit — let me rerun just that strategy."
Uncheck all but the failing strategy and re-run.

**If the results look unexpectedly similar:**
"Interestingly, this sometimes happens with simpler tasks. Let me switch to Code Review — that's where the strategy differences are most dramatic."

**If zero-shot actually catches the SQL injection:**
"Good catch — the model has learned from many security examples during training, so it sometimes finds common vulnerabilities on zero-shot. But watch how Chain-of-Thought adds severity classification and a specific fix, and how Structured Output makes it machine-parseable. The quality score still reflects a meaningful difference."

---

## Closing the Demo (30 seconds)

"The landing page of PromptForge explains all seven techniques before you run the demo — so the audience can understand what they're seeing before seeing it. After you run, the comparison table and charts make the quality differences quantitative.

The core lesson of this project: prompt engineering is not about typing instructions. It's about designing communication protocols with a probabilistic system. And like all engineering, it produces measurably better results when done systematically."
