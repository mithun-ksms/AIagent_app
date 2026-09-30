# 🌍 European City Intelligence System
### A Multi-Agent AI System for Real-Time European City Research and Comparison

**Author:** Mithun Surriya KS
**Date:** September 2026
**Live App:** [Add your Streamlit URL here]
**GitHub:** github.com/mithun-ksms
**Tools:** Python · Streamlit · Serper API · Gemini API · Plotly

---

## What It Does

You type any two European cities. Four AI agents work in sequence to research each city in real time and produce a structured, data-backed comparison report — covering cost of living, job market, and quality of life — with a visual dashboard showing key numbers side by side.

The whole process takes under 60 seconds per city, pulling live data from across the web rather than relying on a static dataset.

---

## Why I Built This

I'm applying to Erasmus Mundus joint Master's programmes in AI and Data Science, which involve studying across multiple European countries. The question of where to live, how much it costs, and what the job market looks like after graduating is genuinely relevant to me — and I couldn't find a single tool that answered it clearly and honestly for any city I chose.

Most cost-of-living resources are either out of date, buried in forums, or require manually reading through multiple sites. This project automates that research process and synthesises it into one readable report, directly addressing a problem I was personally trying to solve.

---

## How It Works — The Multi-Agent Architecture

Rather than asking a single AI model to "tell me about Amsterdam," this system uses four specialised agents that each do one job and pass their findings to the next:

```
User types: "Amsterdam" + "Barcelona"
                    ↓
Agent 1 — Cost of Living Collector
Searches the web for current rent, food, and transport costs
Returns: raw text snippets from cost-of-living sites
                    ↓
Agent 2 — Job Market Researcher
Searches for available jobs, average salaries, and tech/data roles
Returns: raw text snippets from job market sources
                    ↓
Agent 3 — Quality of Life Analyst
Searches for safety scores, healthcare, student life, public transport
Returns: raw text snippets from quality-of-life sources
                    ↓
Agent 4 — Synthesiser
Reads all three agents' findings
Sends to Gemini with a structured prompt
Returns: a clean, honest, formatted city report
                    ↓
Number Extractor
Asks Gemini to pull key numbers from both reports as JSON
Powers the comparison dashboard and bar chart
```

Each agent receives the previous agent's output — so by the time Agent 4 runs, it has a full picture of all three research areas to synthesise from. This is a **pipeline agent architecture**: fixed steps in sequence, each with a defined role.

---

## Technical Implementation

**Search layer — Serper API**
Agents 1, 2, and 3 use the Serper API to query Google programmatically, returning organic search results as structured JSON. Each agent uses a targeted search query designed to surface the most relevant data for its specific research area.

**Synthesis layer — Gemini API (REST)**
Agent 4 and the number extractor call the Gemini API directly via HTTP POST — no SDK, avoiding package conflicts on deployment. The prompt instructs Gemini to use a fixed output format, making the response reliably parseable.

**Number extraction — JSON parsing**
The number extractor prompts Gemini to return only a JSON object containing monthly costs and salary ranges for both cities. Python's `json.loads()` converts this into a dictionary used to populate the metric cards and Plotly chart.

**Frontend — Streamlit**
`st.status()` provides live progress updates as each agent runs. `st.columns()` renders the two-city comparison side by side. `st.metric()` displays the headline numbers with delta comparisons. `plotly.graph_objects` draws the grouped bar chart.

**Retry logic**
All Gemini calls include a retry loop (up to 5 attempts, 10-second intervals) to handle temporary server load spikes gracefully.

---

## Stack

| Component | Technology |
|---|---|
| Language | Python |
| Frontend | Streamlit |
| Web search | Serper API |
| AI synthesis | Gemini 3.1 Flash Lite (REST) |
| Charts | Plotly |
| Deployment | Streamlit Cloud |

---

## What the App Shows

**Comparison Dashboard**
- Monthly cost of living (€) for each city
- Minimum and maximum salary ranges for data/tech roles
- Grouped bar chart comparing both cities visually

**Full Reports — side by side**
Each city report is structured into four sections:
- 💰 Cost of Living — specific monthly figures
- 💼 Job Market — salary ranges and role availability
- 🌟 Quality of Life — safety, healthcare, student life
- ✅ Verdict — honest summary of who the city suits

**Download**
Both reports are downloadable as plain text files.

---

## Limitations

- **Data freshness:** search snippets reflect whatever is currently indexed — older pages may still surface. Results are indicative, not definitive.
- **Number accuracy:** salary and cost figures are extracted from snippets and synthesised by Gemini. Treat them as ballpark estimates, not precise data.
- **Coverage:** works best for major European cities with a strong English-language web presence. Smaller cities may return thinner results.
- **Gemini rate limits:** the free tier occasionally returns 503 errors under high demand — the retry logic handles most cases but very busy periods may require a second attempt.

---

## Connection to Broader Research

This project is part of an ongoing series applying data science and AI to real-world urban and social questions:

- [London Urban Inequality Analyser](https://londoninequalitydashboard-r8w46bkkvvt6xmeyxbu7ku.streamlit.app) — Random Forest + SHAP explainability on London deprivation data
- [Berlin Deprivation Analysis](https://berlin-deprivation-analysis-xdgfhmbpccbe5cc8mcvsx3.streamlit.app) — Cross-city comparison with London, R² = 0.97
- [AI Tourism Assistant — London](https://github.com/mithun-ksms/london-tourism-chatbot) — Gemini-powered chatbot with live API integration

The City Intelligence System extends this work by moving from static datasets to live, agent-driven research — and from single-city analysis to real-time cross-city comparison.

---

## Files in This Repository

- `app.py` — full Streamlit application
- `requirements.txt` — dependencies
- `README.md` — this document
