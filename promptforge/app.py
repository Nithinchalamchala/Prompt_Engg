import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

from prompts.strategies import STRATEGIES
from prompts.templates import TASK_CONFIGS
from engine.llm_client import call_llm
from engine.evaluator import evaluate_response

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PromptForge — Prompt Engineering Lab",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS — comprehensive light theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ════════════════════════════════════════════
   1. GLOBAL BACKGROUNDS — kill every dark patch
   ════════════════════════════════════════════ */
.stApp,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stHorizontalBlock"],
[data-testid="stColumn"],
[data-testid="block-container"],
.main, .block-container {
    background-color: #F0F4F8 !important;
    color: #1E293B !important;
}

/* ════════════════════════════════════════════
   2. SIDEBAR
   ════════════════════════════════════════════ */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
}
[data-testid="stSidebar"] *,
[data-testid="stSidebarContent"] * {
    color: #1E293B !important;
}
[data-testid="stSidebar"] hr { border-color: #E2E8F0 !important; }

/* ════════════════════════════════════════════
   3. TABS — the main source of black patches
   ════════════════════════════════════════════ */
.stTabs,
[data-testid="stTabs"],
[data-baseweb="tab-list"],
[data-testid="stTabsContent"],
[data-baseweb="tab-panel"] {
    background-color: #FFFFFF !important;
    color: #1E293B !important;
}
[data-baseweb="tab-list"] {
    border-bottom: 2px solid #E2E8F0 !important;
    background-color: #FFFFFF !important;
    gap: 0 !important;
}
[data-baseweb="tab"] {
    background-color: transparent !important;
    color: #64748B !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    border-bottom: 2px solid transparent !important;
    padding: 0.6rem 1rem !important;
}
[data-baseweb="tab"]:hover {
    color: #2563EB !important;
    background-color: #EFF6FF !important;
}
[data-baseweb="tab"][aria-selected="true"] {
    color: #2563EB !important;
    border-bottom: 2px solid #2563EB !important;
    font-weight: 600 !important;
}
[data-testid="stTabsContent"],
[data-baseweb="tab-panel"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    padding: 1.25rem !important;
}
/* all content inside any tab must be light */
[data-testid="stTabsContent"] *,
[data-baseweb="tab-panel"] * {
    color: #1E293B !important;
    background-color: transparent !important;
}
/* restore explicit background overrides inside tabs */
[data-testid="stTabsContent"] .pf-prompt-box,
[data-baseweb="tab-panel"] .pf-prompt-box {
    background-color: #F8FAFC !important;
    color: #334155 !important;
}
[data-testid="stTabsContent"] .pf-response-box,
[data-baseweb="tab-panel"] .pf-response-box {
    background-color: #FFFFFF !important;
    color: #1E293B !important;
}

/* ════════════════════════════════════════════
   4. METRICS
   ════════════════════════════════════════════ */
[data-testid="stMetric"],
[data-testid="metric-container"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    padding: 0.9rem 1rem !important;
}
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] * {
    color: #64748B !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
    color: #1E3A5F !important;
    font-weight: 700 !important;
    font-size: 1.25rem !important;
}
[data-testid="stMetricDelta"] { color: #059669 !important; }

/* ════════════════════════════════════════════
   5. INPUTS — text area, selectbox, checkbox
   ════════════════════════════════════════════ */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input {
    background-color: #FFFFFF !important;
    color: #1E293B !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 6px !important;
}
[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] input:focus {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 2px rgba(37,99,235,0.15) !important;
}
[data-testid="stTextArea"] label,
[data-testid="stTextInput"] label {
    color: #374151 !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}
/* selectbox */
[data-testid="stSelectbox"] > div > div,
[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    color: #1E293B !important;
}
[data-baseweb="select"] * { color: #1E293B !important; }
/* selectbox dropdown */
[data-baseweb="popover"] *,
[role="listbox"] * {
    background-color: #FFFFFF !important;
    color: #1E293B !important;
}
/* checkbox */
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] span {
    color: #1E293B !important;
    font-size: 0.87rem !important;
}

/* ════════════════════════════════════════════
   6. EXPANDERS
   ════════════════════════════════════════════ */
[data-testid="stExpander"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary * {
    background-color: #FFFFFF !important;
    color: #1E293B !important;
    font-weight: 500 !important;
}
[data-testid="stExpander"] summary:hover {
    background-color: #F8FAFC !important;
}
[data-testid="stExpanderDetails"],
[data-testid="stExpanderDetails"] * {
    background-color: #FFFFFF !important;
    color: #475569 !important;
}

/* ════════════════════════════════════════════
   7. ALERTS (success / error / warning / info)
   ════════════════════════════════════════════ */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    border-width: 1px !important;
}
[data-testid="stAlert"][kind="success"],
div.stSuccess > div {
    background-color: #F0FDF4 !important;
    border-color: #86EFAC !important;
    color: #166534 !important;
}
[data-testid="stAlert"][kind="error"],
div.stError > div {
    background-color: #FFF1F2 !important;
    border-color: #FDA4AF !important;
    color: #9F1239 !important;
}
[data-testid="stAlert"][kind="warning"],
div.stWarning > div {
    background-color: #FFFBEB !important;
    border-color: #FCD34D !important;
    color: #92400E !important;
}
[data-testid="stAlert"][kind="info"],
div.stInfo > div {
    background-color: #EFF6FF !important;
    border-color: #93C5FD !important;
    color: #1E40AF !important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] * { color: inherit !important; }

/* ════════════════════════════════════════════
   8. MARKDOWN & CAPTIONS
   ════════════════════════════════════════════ */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] strong,
[data-testid="stMarkdownContainer"] em {
    color: #1E293B !important;
}
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] * {
    color: #64748B !important;
}
small { color: #64748B !important; }
hr { border-color: #E2E8F0 !important; background: none !important; }

/* ════════════════════════════════════════════
   9. DATAFRAME / TABLE
   ════════════════════════════════════════════ */
[data-testid="stDataFrame"],
[data-testid="stDataFrame"] * {
    background-color: #FFFFFF !important;
    color: #1E293B !important;
}
[data-testid="stDataFrame"] table { border-collapse: collapse !important; }
[data-testid="stDataFrame"] th {
    background-color: #F1F5F9 !important;
    color: #1E3A5F !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    border-bottom: 2px solid #E2E8F0 !important;
}
[data-testid="stDataFrame"] td {
    color: #334155 !important;
    font-size: 0.85rem !important;
    border-bottom: 1px solid #F1F5F9 !important;
}

/* ════════════════════════════════════════════
   10. PROGRESS BAR
   ════════════════════════════════════════════ */
[data-testid="stProgressBar"] > div {
    background-color: #E2E8F0 !important;
    border-radius: 99px !important;
}
[data-testid="stProgressBar"] > div > div {
    background-color: #2563EB !important;
    border-radius: 99px !important;
}
[data-testid="stProgressBar"] + p { color: #64748B !important; font-size: 0.82rem !important; }

/* ════════════════════════════════════════════
   11. BUTTON
   ════════════════════════════════════════════ */
.stButton > button {
    border-radius: 6px !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
}
.stButton > button[kind="primary"] {
    background-color: #2563EB !important;
    color: #FFFFFF !important;
    border: none !important;
    font-weight: 600 !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #1D4ED8 !important;
}
.stButton > button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #1E3A5F !important;
    border: 1px solid #CBD5E1 !important;
}
.stButton > button[kind="secondary"]:hover {
    background-color: #F8FAFC !important;
    border-color: #2563EB !important;
}

/* ════════════════════════════════════════════
   12. CUSTOM COMPONENTS
   ════════════════════════════════════════════ */
.pf-header {
    background: linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%);
    padding: 2rem 2.5rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
}
.pf-header h1 {
    color: #FFFFFF !important;
    font-size: 2rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.5px;
}
.pf-header p {
    color: #BFDBFE !important;
    font-size: 0.95rem;
    margin: 0.4rem 0 0;
}

.pf-section {
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    color: #1E3A5F !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 1.75rem 0 0.75rem;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid #2563EB;
    background: transparent !important;
}

.pf-prompt-box {
    background-color: #F8FAFC !important;
    border: 1px solid #CBD5E1;
    border-left: 3px solid #94A3B8;
    border-radius: 6px;
    padding: 1rem 1.25rem;
    font-family: "JetBrains Mono", "Fira Code", "Courier New", monospace;
    font-size: 0.82rem;
    white-space: pre-wrap;
    color: #334155 !important;
    line-height: 1.6;
}
.pf-response-box {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0;
    border-left: 3px solid #2563EB;
    border-radius: 6px;
    padding: 1rem 1.25rem;
    font-size: 0.9rem;
    color: #1E293B !important;
    line-height: 1.7;
}

.pf-insight {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 1.1rem 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.pf-insight-title {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748B !important;
    margin-bottom: 0.5rem;
}
.pf-insight-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1E3A5F !important;
    line-height: 1.2;
}
.pf-insight-sub {
    font-size: 0.82rem;
    color: #64748B !important;
    margin-top: 0.3rem;
    line-height: 1.6;
}

.pf-concept {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 1rem 1.1rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.pf-concept-title {
    font-weight: 600;
    font-size: 0.88rem;
    color: #1E3A5F !important;
    margin-bottom: 0.3rem;
}
.pf-concept-body {
    font-size: 0.82rem;
    color: #64748B !important;
    line-height: 1.5;
}

.pf-landing {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 2.5rem 3rem;
    max-width: 720px;
    margin: 2rem auto;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.pf-landing h2 { color: #1E3A5F !important; font-size: 1.4rem; margin-top: 0; }
.pf-landing h3 { color: #2563EB !important; font-size: 1rem; margin-top: 1.2rem; }
.pf-landing li { color: #334155 !important; font-size: 0.9rem; margin-bottom: 0.3rem; }
.pf-landing blockquote {
    border-left: 3px solid #2563EB;
    margin: 1rem 0;
    padding: 0.6rem 1rem;
    background-color: #EFF6FF !important;
    border-radius: 0 6px 6px 0;
    color: #1E3A5F !important;
    font-style: italic;
}

/* ════════════════════════════════════════════
   13. CUSTOM HTML TABLE (replaces st.dataframe)
   ════════════════════════════════════════════ */
.pf-table-wrap {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    overflow: hidden;
    margin-top: 0.5rem;
}
.pf-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.84rem;
}
.pf-table thead tr {
    background-color: #F1F5F9;
    border-bottom: 2px solid #E2E8F0;
}
.pf-table thead th {
    padding: 0.65rem 0.9rem;
    text-align: left;
    font-weight: 700;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #1E3A5F;
    white-space: nowrap;
}
.pf-table tbody tr { border-bottom: 1px solid #F1F5F9; }
.pf-table tbody tr:last-child { border-bottom: none; }
.pf-table tbody tr:hover { background-color: #F8FAFC; }
.pf-table tbody td {
    padding: 0.65rem 0.9rem;
    color: #334155;
    vertical-align: middle;
}
.pf-table tbody td:first-child { font-weight: 600; color: #1E3A5F; }
.pf-table .pf-top-badge {
    display: inline-block;
    background-color: #1E3A5F;
    color: #FFFFFF;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 1px 6px;
    border-radius: 3px;
    margin-left: 5px;
    letter-spacing: 0.04em;
    vertical-align: middle;
}

/* ════════════════════════════════════════════
   14. TECHNIQUE CARDS (landing page)
   ════════════════════════════════════════════ */
.pf-tech-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}
.pf-tech-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 1.25rem 1.4rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.pf-tech-card-num {
    font-size: 0.7rem;
    font-weight: 700;
    color: #2563EB;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.3rem;
}
.pf-tech-card-title {
    font-size: 1rem;
    font-weight: 700;
    color: #1E3A5F;
    margin-bottom: 0.5rem;
}
.pf-tech-card-desc {
    font-size: 0.85rem;
    color: #475569;
    line-height: 1.6;
    margin-bottom: 0.75rem;
}
.pf-tech-card-example {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-left: 3px solid #2563EB;
    border-radius: 4px;
    padding: 0.5rem 0.75rem;
    font-family: "Courier New", monospace;
    font-size: 0.78rem;
    color: #334155;
    line-height: 1.5;
}
.pf-tech-card-when {
    font-size: 0.78rem;
    color: #64748B;
    margin-top: 0.5rem;
}
.pf-tech-card-when strong { color: #1E3A5F; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="pf-header">
    <h1>PromptForge</h1>
    <p>Prompt Engineering Evaluation Laboratory &nbsp;|&nbsp; Compare 7 Prompting Strategies on the Same Input</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Configuration")
    st.divider()

    st.markdown("**Task**")
    task_name = st.selectbox("Choose Task", list(TASK_CONFIGS.keys()), label_visibility="collapsed")
    task_config = TASK_CONFIGS[task_name]
    st.caption(f"{task_config['description']}")

    st.divider()
    st.markdown("**Strategies**")
    st.caption("Select which strategies to run and compare.")

    selected_strategies = {}
    for name, cfg in STRATEGIES.items():
        selected = st.checkbox(
            name,
            value=(name in ["Zero-Shot", "Few-Shot", "Chain-of-Thought", "Role Prompting", "Structured Output"]),
            help=cfg["description"],
        )
        selected_strategies[name] = selected


# ─────────────────────────────────────────────
# Input area
# ─────────────────────────────────────────────
col_input, col_run = st.columns([4, 1])

with col_input:
    user_input = st.text_area(
        "Input Text",
        value=task_config["default_input"],
        height=120,
        help="The same text is sent through every selected strategy — only the prompt changes.",
    )

with col_run:
    st.markdown("<br>", unsafe_allow_html=True)
    run_button = st.button("Run Strategies", type="primary", use_container_width=True)

st.divider()

# ─────────────────────────────────────────────
# Chart theme helper
# ─────────────────────────────────────────────
CHART_COLORS = ["#1E3A5F", "#2563EB", "#3B82F6", "#60A5FA", "#93C5FD", "#BFDBFE", "#DBEAFE"]

CHART_LAYOUT = dict(
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#F8FAFC",
    font=dict(family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif", color="#334155", size=11),
    margin=dict(l=10, r=10, t=40, b=10),
    height=300,
)

# ─────────────────────────────────────────────
# Run strategies
# ─────────────────────────────────────────────
if run_button:
    if not os.getenv("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY not found. Add it to promptforge/.env and restart the app.")
        st.stop()

    active_strategies = {k: v for k, v in STRATEGIES.items() if selected_strategies.get(k)}

    if not active_strategies:
        st.warning("Select at least one strategy from the sidebar.")
        st.stop()

    results = {}
    progress_bar = st.progress(0, text="Initialising...")

    for i, (strategy_name, strategy_cfg) in enumerate(active_strategies.items()):
        progress_bar.progress(
            (i + 1) / len(active_strategies),
            text=f"Running: {strategy_name}",
        )
        prompt = strategy_cfg["builder"](task_name, user_input)
        try:
            llm_result = call_llm(prompt)
            eval_result = evaluate_response(
                prompt,
                llm_result["response"],
                llm_result["input_tokens"],
                llm_result["output_tokens"],
            )
            results[strategy_name] = {
                "prompt": prompt,
                "response": llm_result["response"],
                "metrics": eval_result,
                "tokens_in": llm_result["input_tokens"],
                "tokens_out": llm_result["output_tokens"],
                "latency": llm_result["latency_seconds"],
            }
        except Exception as e:
            st.error(f"{strategy_name} failed: {e}")

    progress_bar.empty()

    if not results:
        st.error("No strategies completed successfully.")
        st.stop()

    st.session_state["results"] = results
    st.session_state["task_name"] = task_name

# ─────────────────────────────────────────────
# Display results
# ─────────────────────────────────────────────
if "results" in st.session_state:
    results = st.session_state["results"]
    task_name = st.session_state["task_name"]

    winner = max(results.items(), key=lambda x: x[1]["metrics"]["quality_score"])
    winner_name = winner[0]
    worst_name = min(results.items(), key=lambda x: x[1]["metrics"]["quality_score"])[0]

    st.success(f"Completed — {len(results)} strategies evaluated on task: {task_name}")

    # ── KPI strip ────────────────────────────────
    st.markdown('<p class="pf-section">Summary</p>', unsafe_allow_html=True)

    best_score = winner[1]["metrics"]["quality_score"]
    worst_score = results[worst_name]["metrics"]["quality_score"]
    improvement = best_score - worst_score
    improvement_pct = improvement / max(1, worst_score) * 100
    most_efficient = min(
        results.items(),
        key=lambda x: x[1]["tokens_in"] / max(1, x[1]["metrics"]["quality_score"])
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Best Strategy", winner_name)
    k2.metric("Top Quality Score", f"{best_score:.0f} / 100")
    k3.metric("Improvement vs Baseline", f"+{improvement_pct:.0f}%")
    k4.metric("Most Token-Efficient", most_efficient[0])

    # ── Charts ───────────────────────────────────
    st.markdown('<p class="pf-section">Evaluation Dashboard</p>', unsafe_allow_html=True)

    strategies_list = list(results.keys())
    quality_scores  = [results[s]["metrics"]["quality_score"] for s in strategies_list]
    token_counts    = [results[s]["tokens_in"] for s in strategies_list]
    bar_colors      = [CHART_COLORS[i % len(CHART_COLORS)] for i in range(len(strategies_list))]

    col1, col2, col3 = st.columns(3)

    with col1:
        fig = go.Figure(go.Bar(
            x=strategies_list,
            y=quality_scores,
            marker_color=bar_colors,
            marker_line_color="#E2E8F0",
            marker_line_width=1,
            text=[f"{s:.0f}" for s in quality_scores],
            textposition="outside",
            textfont=dict(size=11, color="#1E3A5F"),
        ))
        fig.update_layout(
            **CHART_LAYOUT,
            title=dict(text="Quality Score (0–100)", font=dict(size=12, color="#1E3A5F")),
            yaxis=dict(range=[0, 115], gridcolor="#E2E8F0", zeroline=False),
            xaxis=dict(tickfont=dict(size=9)),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = go.Figure(go.Scatterpolar(
            r=quality_scores + [quality_scores[0]],
            theta=strategies_list + [strategies_list[0]],
            fill="toself",
            fillcolor="rgba(37,99,235,0.12)",
            line=dict(color="#2563EB", width=2),
            marker=dict(color="#1E3A5F", size=6),
        ))
        fig2.update_layout(
            **CHART_LAYOUT,
            title=dict(text="Strategy Coverage Radar", font=dict(size=12, color="#1E3A5F")),
            polar=dict(
                radialaxis=dict(range=[0, 100], showticklabels=False, gridcolor="#E2E8F0"),
                angularaxis=dict(tickfont=dict(size=9)),
                bgcolor="#F8FAFC",
            ),
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        fig3 = go.Figure(go.Scatter(
            x=token_counts,
            y=quality_scores,
            mode="markers+text",
            marker=dict(color=bar_colors, size=12, line=dict(color="#E2E8F0", width=1)),
            text=strategies_list,
            textposition="top center",
            textfont=dict(size=9, color="#334155"),
        ))
        fig3.update_layout(
            **CHART_LAYOUT,
            title=dict(text="Quality vs. Token Cost", font=dict(size=12, color="#1E3A5F")),
            xaxis=dict(title=dict(text="Input Tokens", font=dict(size=10)), gridcolor="#E2E8F0", zeroline=False),
            yaxis=dict(title=dict(text="Quality Score", font=dict(size=10)), gridcolor="#E2E8F0", zeroline=False),
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ── Comparison table ─────────────────────────
    st.markdown('<p class="pf-section">Comparison Table</p>', unsafe_allow_html=True)

    headers = [
        "Strategy", "Quality Score", "Reasoning Depth", "Specificity",
        "Word Count", "Input Tokens", "Latency (s)", "Structured", "Valid JSON",
    ]
    header_html = "".join(f"<th>{h}</th>" for h in headers)

    rows_html = ""
    for name, data in results.items():
        m = data["metrics"]
        badge = '<span class="pf-top-badge">TOP</span>' if name == winner_name else ""
        row_cells = [
            f"{name}{badge}",
            f"{m['quality_score']:.0f} / 100",
            f"{m['reasoning_depth']*100:.0f}%",
            f"{m['specificity_score']*100:.0f}%",
            str(m["word_count"]),
            str(data["tokens_in"]),
            str(data["latency"]),
            "Yes" if m["has_structure"] else "No",
            "Yes" if m["is_valid_json"] else "No",
        ]
        rows_html += "<tr>" + "".join(f"<td>{c}</td>" for c in row_cells) + "</tr>"

    st.markdown(f"""
    <div class="pf-table-wrap">
        <table class="pf-table">
            <thead><tr>{header_html}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

    # ── Per-strategy response tabs ───────────────
    st.markdown('<p class="pf-section">Strategy Responses</p>', unsafe_allow_html=True)
    st.caption(
        f"Top performer: {winner_name} — Quality Score {winner[1]['metrics']['quality_score']:.0f}/100"
    )

    tab_labels = [s + (" [Top]" if s == winner_name else "") for s in results]
    tabs = st.tabs(tab_labels)

    for tab, (strategy_name, data) in zip(tabs, results.items()):
        with tab:
            m = data["metrics"]
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Quality Score", f"{m['quality_score']:.0f} / 100")
            c2.metric("Reasoning Depth", f"{m['reasoning_depth']*100:.0f}%")
            c3.metric("Specificity", f"{m['specificity_score']*100:.0f}%")
            c4.metric("Input Tokens", data["tokens_in"])
            c5.metric("Latency", f"{data['latency']} s")

            st.markdown('<p style="font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#64748B;margin:1rem 0 0.3rem;">Prompt Sent to Model</p>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="pf-prompt-box">{data["prompt"]}</div>',
                unsafe_allow_html=True,
            )

            st.markdown('<p style="font-size:0.8rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#64748B;margin:1rem 0 0.3rem;">Model Response</p>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="pf-response-box">{data["response"]}</div>',
                unsafe_allow_html=True,
            )
            st.caption(f"About this strategy: {STRATEGIES[strategy_name]['description']}")

    # ── Insights ─────────────────────────────────
    st.markdown('<p class="pf-section">Key Insights</p>', unsafe_allow_html=True)

    ic1, ic2, ic3 = st.columns(3)

    with ic1:
        st.markdown(f"""
        <div class="pf-insight">
            <div class="pf-insight-title">Best Strategy</div>
            <div class="pf-insight-value">{winner_name}</div>
            <div class="pf-insight-sub">
                Quality Score: {best_score:.0f}/100<br>
                Reasoning: {winner[1]['metrics']['reasoning_depth']*100:.0f}%<br>
                Tokens: {winner[1]['tokens_in']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with ic2:
        st.markdown(f"""
        <div class="pf-insight">
            <div class="pf-insight-title">Improvement Over Baseline</div>
            <div class="pf-insight-value">+{improvement_pct:.0f}%</div>
            <div class="pf-insight-sub">
                Baseline ({worst_name}): {worst_score:.0f}/100<br>
                Best ({winner_name}): {best_score:.0f}/100<br>
                Absolute gain: +{improvement:.0f} points
            </div>
        </div>
        """, unsafe_allow_html=True)

    with ic3:
        eff_score = most_efficient[1]['metrics']['quality_score']
        eff_tokens = most_efficient[1]['tokens_in']
        st.markdown(f"""
        <div class="pf-insight">
            <div class="pf-insight-title">Most Token-Efficient</div>
            <div class="pf-insight-value">{most_efficient[0]}</div>
            <div class="pf-insight-sub">
                Quality: {eff_score:.0f}/100<br>
                Input tokens: {eff_tokens}<br>
                Ratio: {eff_score/max(1,eff_tokens)*100:.2f} quality / token
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Concepts glossary ─────────────────────────
    st.markdown('<p class="pf-section">Prompt Engineering Concepts</p>', unsafe_allow_html=True)

    concepts = [
        ("Zero-Shot Prompting",    "Direct instruction with no examples. Tests the model's base knowledge and instruction-following ability."),
        ("Few-Shot Prompting",     "Providing 2–5 labelled examples before the query. Guides output format and quality without additional training."),
        ("Chain-of-Thought",       "Forces step-by-step reasoning before the final answer. Significantly improves accuracy on complex tasks."),
        ("Role Prompting",         "Assigns an expert persona to the model. Activates domain-specific vocabulary, depth, and tone."),
        ("Structured Output",      "Enforces a JSON schema on the response. Enables downstream parsing and consistent cross-strategy comparison."),
        ("Self-Reflection",        "The model critiques its own draft and produces a revised answer. Reduces errors on ambiguous or high-stakes tasks."),
    ]

    for row_start in range(0, len(concepts), 3):
        cols = st.columns(3)
        for col, (title, body) in zip(cols, concepts[row_start:row_start+3]):
            with col:
                st.markdown(f"""
                <div class="pf-concept">
                    <div class="pf-concept-title">{title}</div>
                    <div class="pf-concept-body">{body}</div>
                </div>
                """, unsafe_allow_html=True)

else:
    # ── Landing page — full technique guide ───────

    st.markdown("""
    <div class="pf-landing">
        <h2>Welcome to PromptForge</h2>
        <p style="color:#475569; font-size:0.95rem; line-height:1.7;">
            A controlled laboratory that proves prompt engineering works — with measurable numbers.
            The same input text is sent through 7 distinct prompting strategies on the exact same model.
            The only variable is the prompt design. Select a task, choose your strategies, and click
            <strong>Run Strategies</strong> to see the difference live.
        </p>
        <blockquote>
            The same model. The same input. Measurably different outputs.<br>
            The only variable is prompt engineering.
        </blockquote>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="pf-section">Prompting Techniques — Reference Guide</p>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#64748B; font-size:0.88rem; margin-bottom:1rem;">Learn each technique before running the demo. Every strategy below is applied live when you click Run Strategies.</p>',
        unsafe_allow_html=True,
    )

    techniques = [
        {
            "num": "Technique 01",
            "title": "Zero-Shot Prompting",
            "desc": (
                "Send a direct instruction to the model with no examples. "
                "This is the baseline — it tests what the model already knows and how well it follows a bare instruction. "
                "Most people stop here, which is why their results are inconsistent."
            ),
            "example": "Analyze the sentiment of this text:\n\n[input text]",
            "when": "<strong>Use when:</strong> The task is simple, well-defined, and you need a quick baseline.",
        },
        {
            "num": "Technique 02",
            "title": "Few-Shot Prompting",
            "desc": (
                "Provide 2–5 labeled input-output examples before the actual query. "
                "The model learns the expected format, tone, and depth from those examples — "
                "without any retraining. This is the fastest way to enforce a consistent output structure."
            ),
            "example": 'Input: "Great product!"\nOutput: {"sentiment": "positive"}\n\nInput: [your text]\nOutput:',
            "when": "<strong>Use when:</strong> Output format matters — classification labels, JSON keys, or specific writing style.",
        },
        {
            "num": "Technique 03",
            "title": "Chain-of-Thought (CoT)",
            "desc": (
                "Instruct the model to reason step-by-step before reaching a conclusion. "
                "This forces intermediate reasoning steps into the context window, dramatically improving "
                "accuracy on multi-step tasks. Adding 'Think step by step' can improve accuracy by 40–70%."
            ),
            "example": "Analyze this code for security issues.\nThink step by step:\n1. Identify inputs\n2. Check for injections\n3. Conclude\n\n[code]",
            "when": "<strong>Use when:</strong> The task requires reasoning, analysis, diagnosis, or multi-step logic.",
        },
        {
            "num": "Technique 04",
            "title": "Role Prompting",
            "desc": (
                "Assign the model a specific expert persona before the task. "
                "A model told it is a 'senior security engineer' uses different vocabulary and depth than "
                "one given a bare instruction — it activates domain-specific knowledge already in the model's weights."
            ),
            "example": "You are a senior security engineer with 15 years of experience in application security.\n\nReview this code:\n[code]",
            "when": "<strong>Use when:</strong> You need domain expertise, professional tone, or specialist vocabulary.",
        },
        {
            "num": "Technique 05",
            "title": "Structured Output Prompting",
            "desc": (
                "Provide a JSON schema and instruct the model to respond only in that exact format. "
                "This makes LLM output programmatically parseable, enables downstream processing, "
                "and forces consistent field names and data types across all responses."
            ),
            "example": 'Respond ONLY with valid JSON:\n{\n  "severity": "critical|high|medium|low",\n  "issue": "...",\n  "fix": "..."\n}',
            "when": "<strong>Use when:</strong> Output will be consumed by code, a pipeline, or needs to be compared across runs.",
        },
        {
            "num": "Technique 06",
            "title": "Self-Reflection Prompting",
            "desc": (
                "Ask the model to generate an initial answer, then critically review it, then produce a revised final answer. "
                "This three-phase loop catches assumptions, blind spots, and errors that the first pass misses. "
                "It is especially powerful on ambiguous or high-stakes tasks."
            ),
            "example": "Phase 1 — Initial answer:\n[answer]\n\nPhase 2 — Self-critique:\nWhat is wrong or missing?\n\nPhase 3 — Revised answer:",
            "when": "<strong>Use when:</strong> Accuracy is critical and you can afford 2–3x the tokens.",
        },
        {
            "num": "Technique 07",
            "title": "Meta-Prompting",
            "desc": (
                "Ask the model to first design the ideal prompt for a task, then execute that prompt. "
                "The model reasons about what context, role, format, and constraints would make the prompt best — "
                "then applies that reasoning. Useful when you are unsure how to frame a novel task."
            ),
            "example": "Step 1 — Design the ideal prompt for: [task]\nConsider: role, format, constraints.\n\nStep 2 — Execute that prompt on: [input]",
            "when": "<strong>Use when:</strong> The task is novel or ambiguous and you want the model to self-optimize.",
        },
    ]

    cards_html = '<div class="pf-tech-grid">'
    for t in techniques:
        cards_html += f"""
        <div class="pf-tech-card">
            <div class="pf-tech-card-num">{t['num']}</div>
            <div class="pf-tech-card-title">{t['title']}</div>
            <div class="pf-tech-card-desc">{t['desc']}</div>
            <div class="pf-tech-card-example">{t['example']}</div>
            <div class="pf-tech-card-when">{t['when']}</div>
        </div>"""
    cards_html += "</div>"

    st.markdown(cards_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center; color:#94A3B8; font-size:0.82rem;">Select a task and strategies in the sidebar, then click Run Strategies to see these techniques compete live.</p>',
        unsafe_allow_html=True,
    )
