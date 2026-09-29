
import requests
import streamlit as st
import time
import json
import plotly.graph_objects as go

# -------------------------
# PAGE SETUP
# -------------------------

st.set_page_config(
    page_title="European City Intelligence",
    page_icon="🌍",
    layout="wide"
)

SERPER_KEY = st.secrets["SERPER_KEY"]
GEMINI_KEY = st.secrets["GEMINI_KEY"]

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-3.1-flash-lite:generateContent"
)

# -------------------------
# AGENT 1: COST OF LIVING
# -------------------------

def agent_1_cost_of_living(city):
    response = requests.post(
        "https://google.serper.dev/search",
        json={
            "q": f"cost of living {city} 2026 monthly rent food transport",
            "num": 5
        },
        headers={
            "X-API-KEY": SERPER_KEY,
            "Content-Type": "application/json"
        },
        timeout=30
    )
    response.raise_for_status()
    results = response.json()

    cost_info = ""

    for result in results.get("organic", []):
        cost_info += (
            result.get("title", "")
            + ": "
            + result.get("snippet", "")
            + "\n"
        )

    return cost_info


# -------------------------
# AGENT 2: JOB MARKET
# -------------------------

def agent_2_job_market(city, cost_data):
    response = requests.post(
        "https://google.serper.dev/search",
        json={
            "q": f"{city} job market 2026 average salary data analyst tech jobs",
            "num": 5
        },
        headers={
            "X-API-KEY": SERPER_KEY,
            "Content-Type": "application/json"
        },
        timeout=30
    )
    response.raise_for_status()
    results = response.json()

    job_info = ""

    for result in results.get("organic", []):
        job_info += (
            result.get("title", "")
            + ": "
            + result.get("snippet", "")
            + "\n"
        )

    return job_info


# -------------------------
# AGENT 3: QUALITY OF LIFE
# -------------------------

def agent_3_quality_of_life(city, cost_data, job_data):
    response = requests.post(
        "https://google.serper.dev/search",
        json={
            "q": f"{city} quality of life 2026 safety healthcare student life transport",
            "num": 5
        },
        headers={
            "X-API-KEY": SERPER_KEY,
            "Content-Type": "application/json"
        },
        timeout=30
    )
    response.raise_for_status()
    results = response.json()

    quality_info = ""

    for result in results.get("organic", []):
        quality_info += (
            result.get("title", "")
            + ": "
            + result.get("snippet", "")
            + "\n"
        )

    return quality_info


# -------------------------
# AGENT 4: REPORT SYNTHESIS
# -------------------------

def agent_4_synthesise(city, cost_data, job_data, quality_data):

    prompt = f"""
You are an honest city research advisor for {city}.

Write a clear and informative report using this format:

💰 COST OF LIVING
2-3 sentences with specific numbers in euros.
Mention rent, food and transport where available.

💼 JOB MARKET
2-3 sentences on jobs, employment opportunities
and salaries.

🌟 QUALITY OF LIFE
2-3 sentences on safety, healthcare,
student life and transport.

✅ VERDICT
One balanced paragraph explaining who
this city may be suitable for and its challenges.

Use only the supplied research data.
Do not invent figures or present uncertain
information as confirmed facts.
Mention when reliable figures are unavailable.

RESEARCH DATA:

COST:
{cost_data}

JOBS:
{job_data}

QUALITY:
{quality_data}
"""

    url = f"{GEMINI_URL}?key={GEMINI_KEY}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    for attempt in range(5):
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()

            if data.get("candidates"):
                return data["candidates"][0]["content"]["parts"][0]["text"]

        except requests.RequestException:
            if attempt == 4:
                break

        time.sleep(10)

    return "Could not generate report. Please try again."


# -------------------------
# NUMBER EXTRACTOR
# -------------------------

def extract_numbers(city1, report1, city2, report2):

    prompt = f"""
Read these two city reports and extract key numbers.

Return ONLY a valid JSON object with this format:

{{
    "monthly_cost": {{"city1": 0, "city2": 0}},
    "min_salary": {{"city1": 0, "city2": 0}},
    "max_salary": {{"city1": 0, "city2": 0}}
}}

Use actual numbers in euros.
If a number is not mentioned, use 0.
Do not guess or invent values.
Use monthly figures for monthly costs and
consistent salary periods for salary comparisons.

City 1 ({city1}):
{report1}

City 2 ({city2}):
{report2}
"""

    url = f"{GEMINI_URL}?key={GEMINI_KEY}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    for attempt in range(5):
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()

            if data.get("candidates"):
                raw = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(raw)

        except (requests.RequestException, KeyError, IndexError, ValueError):
            if attempt == 4:
                break

        time.sleep(10)

    return None


# -------------------------
# PIPELINE FUNCTION
# -------------------------

def run_pipeline(city, status_container):

    with status_container:
        st.write(f"🔍 Agent 1: Collecting cost of living for {city}...")
        cost_data = agent_1_cost_of_living(city)
        st.write("✅ Agent 1 done!")

        st.write(f"💼 Agent 2: Researching job market for {city}...")
        job_data = agent_2_job_market(city, cost_data)
        st.write("✅ Agent 2 done!")

        st.write(f"🌟 Agent 3: Analysing quality of life for {city}...")
        quality_data = agent_3_quality_of_life(
            city, cost_data, job_data
        )
        st.write("✅ Agent 3 done!")

        st.write(f"✍️ Agent 4: Writing report for {city}...")
        report = agent_4_synthesise(
            city, cost_data, job_data, quality_data
        )
        st.write("✅ Report complete!")

    return report


# -------------------------
# DISPLAY REPORT
# -------------------------

def display_report(report):

    sections = report.split("\n\n")

    for section in sections:
        section = section.strip()

        if not section:
            continue

        if "✅" in section:
            st.success(section)
        else:
            with st.container(border=True):
                st.markdown(section)


# -------------------------
# HEADER
# -------------------------

st.title("🌍 European City Intelligence System")

st.markdown(
    "**4 AI Agents research any two European cities and compare them**"
)

st.markdown("---")


# -------------------------
# SEARCH BOXES
# -------------------------

col1, col2 = st.columns(2)

with col1:
    city1 = st.text_input(
        "🏙️ First city",
        placeholder="e.g. Amsterdam"
    )

with col2:
    city2 = st.text_input(
        "🏙️ Second city",
        placeholder="e.g. Barcelona"
    )

search_button = st.button(
    "🚀 Compare Cities",
    use_container_width=True,
    type="primary"
)

st.markdown("---")


# -------------------------
# MAIN LOGIC
# -------------------------

if search_button:

    if not city1.strip() or not city2.strip():
        st.error("Please enter both city names.")

    elif city1.strip().lower() == city2.strip().lower():
        st.error("Please enter two different cities.")

    else:

        try:
            # CITY 1 PIPELINE

            with st.status(
                f"🤖 Researching {city1}...",
                expanded=True
            ) as status1:

                report1 = run_pipeline(city1, status1)

                status1.update(
                    label=f"✅ {city1} done!",
                    state="complete"
                )

            # CITY 2 PIPELINE

            with st.status(
                f"🤖 Researching {city2}...",
                expanded=True
            ) as status2:

                report2 = run_pipeline(city2, status2)

                status2.update(
                    label=f"✅ {city2} done!",
                    state="complete"
                )

            st.markdown("---")

            # -------------------------
            # COMPARISON DASHBOARD
            # -------------------------

            st.subheader("📊 Comparison Dashboard")

            numbers = extract_numbers(
                city1, report1,
                city2, report2
            )

            if numbers:

                monthly1 = numbers["monthly_cost"]["city1"]
                monthly2 = numbers["monthly_cost"]["city2"]

                min1 = numbers["min_salary"]["city1"]
                min2 = numbers["min_salary"]["city2"]

                max1 = numbers["max_salary"]["city1"]
                max2 = numbers["max_salary"]["city2"]

                # METRIC CARDS

                m1, m2, m3 = st.columns(3)

                with m1:
                    st.metric(
                        "💰 Monthly Cost",
                        f"€{monthly1:,}" if monthly1 else "N/A",
                        delta=(
                            f"vs €{monthly2:,} in {city2}"
                            if monthly1 and monthly2 else None
                        ),
                        delta_color="inverse"
                    )

                with m2:
                    st.metric(
                        "💼 Min Salary",
                        f"€{min1:,}" if min1 else "N/A",
                        delta=(
                            f"vs €{min2:,} in {city2}"
                            if min1 and min2 else None
                        )
                    )

                with m3:
                    st.metric(
                        "📈 Max Salary",
                        f"€{max1:,}" if max1 else "N/A",
                        delta=(
                            f"vs €{max2:,} in {city2}"
                            if max1 and max2 else None
                        )
                    )

                # BAR CHART

                categories = [
                    "Monthly Cost",
                    "Min Salary",
                    "Max Salary"
                ]

                city1_values = [
                    monthly1, min1, max1
                ]

                city2_values = [
                    monthly2, min2, max2
                ]

                fig = go.Figure()

                fig.add_trace(
                    go.Bar(
                        name=city1,
                        x=categories,
                        y=city1_values,
                        marker_color="#1A4A8A"
                    )
                )

                fig.add_trace(
                    go.Bar(
                        name=city2,
                        x=categories,
                        y=city2_values,
                        marker_color="#E63946"
                    )
                )

                fig.update_layout(
                    barmode="group",
                    title=f"{city1} vs {city2} — Key Numbers (€)",
                    yaxis_title="Amount (€)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                st.caption(
                    "Figures are extracted from AI-generated reports. "
                    "Check the original research before relying on them."
                )

            else:
                st.warning(
                    "Could not extract comparison numbers. "
                    "The city reports are still available below."
                )

            st.markdown("---")

            # -------------------------
            # FULL REPORTS
            # -------------------------

            st.subheader("📋 Full Reports")

            rep1, rep2 = st.columns(2)

            with rep1:
                st.markdown(f"### 🏙️ {city1}")

                display_report(report1)

                st.download_button(
                    label=f"⬇️ Download {city1} Report",
                    data=report1,
                    file_name=f"{city1.lower()}_report.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="dl1"
                )

            with rep2:
                st.markdown(f"### 🏙️ {city2}")

                display_report(report2)

                st.download_button(
                    label=f"⬇️ Download {city2} Report",
                    data=report2,
                    file_name=f"{city2.lower()}_report.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="dl2"
                )

        except requests.RequestException as e:
            st.error(f"API request failed: {e}")

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
