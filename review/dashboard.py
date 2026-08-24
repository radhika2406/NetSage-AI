import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# NETSAGE AI - PROFESSIONAL DASHBOARD
# ============================================================

st.set_page_config(
    page_title="NetSage AI",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(BASE_DIR, "data")

CASES_FILE = os.path.join(DATA_DIR, "cases.csv")
CHECKER_FILE = os.path.join(DATA_DIR, "checker_results.csv")
AI_FILE = os.path.join(DATA_DIR, "ai_results.csv")
HUMAN_FILE = os.path.join(DATA_DIR, "human_reviews.csv")
RESPONSIBLE_FILE = os.path.join(
    DATA_DIR,
    "responsible_ai_log.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

def load_csv(path):

    if not os.path.exists(path):
        return pd.DataFrame()

    try:
        return pd.read_csv(
            path,
            encoding="utf-8-sig"
        )
    except Exception:
        return pd.DataFrame()


cases = load_csv(CASES_FILE)
checker = load_csv(CHECKER_FILE)
ai = load_csv(AI_FILE)
human = load_csv(HUMAN_FILE)
responsible = load_csv(RESPONSIBLE_FILE)


if cases.empty:
    st.error("Unable to load cases.csv.")
    st.stop()


# ============================================================
# COLOR PALETTE
# ============================================================

NAVY = "#16324F"
TEAL = "#167D8D"
LIGHT_TEAL = "#DCEFF2"
GREEN = "#2E7D62"
AMBER = "#C98A18"
RED = "#B84A4A"
SLATE = "#536273"
LIGHT_BG = "#F5F7FA"
BORDER = "#D9E0E7"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    f"""
    <style>

    html, body, [class*="css"] {{
        font-family: "Segoe UI", Arial, sans-serif;
    }}

    .main-title {{
        font-size: 30px;
        font-weight: 700;
        color: {NAVY};
        margin-bottom: 2px;
    }}

    .subtitle {{
        font-size: 14px;
        color: {SLATE};
        margin-bottom: 18px;
    }}

    .section-title {{
        font-size: 19px;
        font-weight: 650;
        color: {NAVY};
        margin-top: 8px;
        margin-bottom: 8px;
    }}

    .metric-card {{
        background: white;
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 15px 16px;
        min-height: 105px;
    }}

    .metric-label {{
        font-size: 12px;
        color: {SLATE};
        margin-bottom: 6px;
    }}

    .metric-value {{
        font-size: 25px;
        font-weight: 700;
        color: {NAVY};
    }}

    .metric-note {{
        font-size: 11px;
        color: {SLATE};
        margin-top: 5px;
    }}

    .status-box {{
        border-radius: 8px;
        padding: 10px 14px;
        background: {LIGHT_TEAL};
        border: 1px solid #B8DDE2;
        color: {NAVY};
        font-size: 13px;
    }}

    .footer {{
        text-align: center;
        color: {SLATE};
        font-size: 12px;
        padding: 15px;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# COUNTS
# ============================================================

total_cases = len(cases)

checker_cases = (
    checker["ID"].nunique()
    if not checker.empty and "ID" in checker.columns
    else 0
)

ai_cases = (
    ai["ID"].nunique()
    if not ai.empty and "ID" in ai.columns
    else 0
)

human_cases = (
    human["ID"].nunique()
    if not human.empty and "ID" in human.columns
    else 0
)

responsible_cases = (
    responsible["ID"].nunique()
    if not responsible.empty and "ID" in responsible.columns
    else 0
)


# ============================================================
# HUMAN REVIEW
# ============================================================

approved = 0
corrected = 0
rejected = 0

if (
    not human.empty
    and "Reviewer_Decision" in human.columns
):

    decisions = (
        human["Reviewer_Decision"]
        .astype(str)
        .str.strip()
    )

    approved = (decisions == "Approved").sum()
    corrected = (decisions == "Corrected").sum()
    rejected = (decisions == "Rejected").sum()


reviewed = approved + corrected + rejected

approval_rate = (
    approved / reviewed * 100
    if reviewed
    else 0
)

correction_rate = (
    corrected / reviewed * 100
    if reviewed
    else 0
)

rejection_rate = (
    rejected / reviewed * 100
    if reviewed
    else 0
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🌐 NetSage AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Evidence-based network troubleshooting with AI assistance '
    'and human oversight'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    "### 🌐 NetSage AI"
)

st.sidebar.caption(
    "Network Diagnosis Platform"
)

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Case Analysis",
        "Evaluation",
        "Responsible AI"
    ]
)

st.sidebar.divider()

st.sidebar.markdown(
    "**Pipeline**"
)

st.sidebar.caption(
    "Evidence → Rules → AI → Human → Audit"
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    st.markdown(
        '<div class="section-title">'
        'System Overview'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Monitor case processing, diagnostic coverage, "
        "and human validation results."
    )

    st.write("")


    # ========================================================
    # KPI CARDS
    # ========================================================

    cols = st.columns(5)

    metrics = [
        ("Total Cases", total_cases, "Test dataset"),
        ("Rule Checked", checker_cases, "Deterministic"),
        ("AI Diagnosed", ai_cases, "AI analysis"),
        ("Human Reviewed", human_cases, "Human oversight"),
        ("Approved", approved, "Human accepted")
    ]

    for col, metric in zip(cols, metrics):

        with col:

            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">
                        {metric[0]}
                    </div>
                    <div class="metric-value">
                        {metric[1]}
                    </div>
                    <div class="metric-note">
                        {metric[2]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


    st.write("")
    st.divider()


    # ========================================================
    # PIPELINE
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        'Diagnostic Pipeline'
        '</div>',
        unsafe_allow_html=True
    )

    pipeline = pd.DataFrame(
        {
            "Stage": [
                "Cases",
                "Rule Checker",
                "AI Diagnosis",
                "Human Review",
                "Responsible AI"
            ],
            "Cases": [
                total_cases,
                checker_cases,
                ai_cases,
                human_cases,
                responsible_cases
            ]
        }
    )

    fig_pipeline = px.bar(
        pipeline,
        x="Cases",
        y="Stage",
        orientation="h",
        text="Cases",
        color_discrete_sequence=[TEAL]
    )

    fig_pipeline.update_traces(
        textposition="outside",
        marker_line_width=0
    )

    fig_pipeline.update_layout(
        height=280,
        margin=dict(
            l=10,
            r=20,
            t=20,
            b=20
        ),
        xaxis=dict(
            title="Number of cases",
            dtick=5,
            gridcolor="#E8EDF2"
        ),
        yaxis=dict(
            title=""
        ),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig_pipeline,
        use_container_width=True,
        config={"displayModeBar": False}
    )


    # ========================================================
    # TWO CHARTS
    # ========================================================

    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # REVIEW DONUT
    # --------------------------------------------------------

    with col1:

        st.markdown(
            '<div class="section-title">'
            'Human Review Outcomes'
            '</div>',
            unsafe_allow_html=True
        )

        review_df = pd.DataFrame(
            {
                "Decision": [
                    "Approved",
                    "Corrected",
                    "Rejected"
                ],
                "Cases": [
                    approved,
                    corrected,
                    rejected
                ]
            }
        )

        if reviewed:

            fig_review = px.pie(
                review_df,
                names="Decision",
                values="Cases",
                hole=0.62,
                color="Decision",
                color_discrete_map={
                    "Approved": GREEN,
                    "Corrected": AMBER,
                    "Rejected": RED
                }
            )

            fig_review.update_traces(
                textinfo="label+percent",
                textfont_size=12,
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Cases: %{value}<br>"
                    "Share: %{percent}"
                    "<extra></extra>"
                )
            )

            fig_review.update_layout(
                height=330,
                margin=dict(
                    l=10,
                    r=10,
                    t=15,
                    b=10
                ),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    y=-0.08
                ),
                paper_bgcolor="white"
            )

            st.plotly_chart(
                fig_review,
                use_container_width=True,
                config={"displayModeBar": False}
            )


    # --------------------------------------------------------
    # SEVERITY
    # --------------------------------------------------------

    with col2:

        st.markdown(
            '<div class="section-title">'
            'Severity Distribution'
            '</div>',
            unsafe_allow_html=True
        )

        if "Severity" in cases.columns:

            severity_df = (
                cases["Severity"]
                .astype(str)
                .str.strip()
                .value_counts()
                .reset_index()
            )

            severity_df.columns = [
                "Severity",
                "Cases"
            ]

            fig_severity = px.bar(
                severity_df,
                x="Cases",
                y="Severity",
                orientation="h",
                text="Cases",
                color="Severity",
                color_discrete_map={
                    "High": RED,
                    "Medium": AMBER,
                    "Low": GREEN
                }
            )

            fig_severity.update_traces(
                textposition="outside"
            )

            fig_severity.update_layout(
                height=330,
                margin=dict(
                    l=10,
                    r=20,
                    t=15,
                    b=10
                ),
                xaxis=dict(
                    title="Cases",
                    gridcolor="#E8EDF2"
                ),
                yaxis=dict(
                    title=""
                ),
                showlegend=False,
                plot_bgcolor="white",
                paper_bgcolor="white"
            )

            st.plotly_chart(
                fig_severity,
                use_container_width=True,
                config={"displayModeBar": False}
            )


    st.divider()


    # ========================================================
    # NETWORK CONCEPTS
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        'Network Problem Categories'
        '</div>',
        unsafe_allow_html=True
    )

    if "Concept" in cases.columns:

        concept_df = (
            cases["Concept"]
            .astype(str)
            .str.strip()
            .value_counts()
            .reset_index()
        )

        concept_df.columns = [
            "Concept",
            "Cases"
        ]

        fig_concept = px.bar(
            concept_df,
            x="Cases",
            y="Concept",
            orientation="h",
            text="Cases",
            color_discrete_sequence=[NAVY]
        )

        fig_concept.update_traces(
            textposition="outside"
        )

        fig_concept.update_layout(
            height=420,
            margin=dict(
                l=10,
                r=30,
                t=15,
                b=20
            ),
            xaxis=dict(
                title="Number of cases",
                gridcolor="#E8EDF2"
            ),
            yaxis=dict(
                title=""
            ),
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig_concept,
            use_container_width=True,
            config={"displayModeBar": False}
        )


    st.divider()


    # ========================================================
    # CASE TABLE
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        'Case Dataset'
        '</div>',
        unsafe_allow_html=True
    )

    display_columns = [
        "ID",
        "Symptom",
        "Expected Fault",
        "OSI",
        "Concept",
        "Severity"
    ]

    display_columns = [
        col
        for col in display_columns
        if col in cases.columns
    ]

    if display_columns:

        st.dataframe(
            cases[display_columns],
            use_container_width=True,
            hide_index=True,
            height=420
        )


# ============================================================
# CASE ANALYSIS
# ============================================================

elif page == "Case Analysis":

    st.markdown(
        '<div class="section-title">'
        'Network Case Analysis'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Inspect the complete evidence → rules → AI → "
        "human validation chain for an individual case."
    )


    case_ids = (
        cases["ID"]
        .astype(str)
        .tolist()
    )

    selected_id = st.selectbox(
        "Select Case",
        case_ids
    )


    case_rows = cases[
        cases["ID"].astype(str)
        == selected_id
    ]


    case = case_rows.iloc[0]


    # ========================================================
    # CASE METRICS
    # ========================================================

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Severity",
            str(case.get("Severity", "N/A"))
        )

    with c2:

        st.metric(
            "OSI Layer",
            str(case.get("OSI", "N/A"))
        )

    with c3:

        st.metric(
            "Concept",
            str(case.get("Concept", "N/A"))
        )


    st.divider()


    st.markdown("**Symptom**")

    st.info(
        str(case["Symptom"])
    )


    c1, c2 = st.columns(2)

    with c1:

        st.markdown("**Topology / Devices**")

        st.code(
            str(
                case["Topology / Devices"]
            )
        )

    with c2:

        st.markdown("**Expected Fault**")

        st.warning(
            str(
                case.get(
                    "Expected Fault",
                    "N/A"
                )
            )
        )


    st.markdown("**Command Output / Evidence**")

    st.code(
        str(
            case[
                "Show Output / Evidence"
            ]
        )
    )


    st.divider()


    # ========================================================
    # RULE CHECKER
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🔍 Deterministic Rule Checker'
        '</div>',
        unsafe_allow_html=True
    )

    checker_rows = checker[
        checker["ID"].astype(str)
        == selected_id
    ]

    if not checker_rows.empty:

        for _, row in checker_rows.iterrows():

            st.write(
                f"**Rule:** "
                f"{row.get('Rule', '')}"
            )

            status = str(
                row.get("Status", "")
            )

            if status.upper() == "FAIL":

                st.error(
                    f"Rule status: {status}"
                )

            else:

                st.success(
                    f"Rule status: {status}"
                )

            st.write(
                f"**Finding:** "
                f"{row.get('Finding', '')}"
            )


    st.divider()


    # ========================================================
    # AI
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '🤖 AI Diagnosis'
        '</div>',
        unsafe_allow_html=True
    )

    ai_rows = ai[
        ai["ID"].astype(str)
        == selected_id
    ]

    if not ai_rows.empty:

        st.markdown(
            str(
                ai_rows.iloc[0][
                    "AI_Diagnosis"
                ]
            )
        )


    st.divider()


    # ========================================================
    # HUMAN
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        '👤 Human Validation'
        '</div>',
        unsafe_allow_html=True
    )

    human_rows = human[
        human["ID"].astype(str)
        == selected_id
    ]

    if not human_rows.empty:

        review = human_rows.iloc[0]

        decision = str(
            review.get(
                "Reviewer_Decision",
                ""
            )
        )

        if decision == "Approved":

            st.success(
                "✓ AI diagnosis approved"
            )

        elif decision == "Corrected":

            st.warning(
                "⚠ AI diagnosis corrected"
            )

        elif decision == "Rejected":

            st.error(
                "✕ AI diagnosis rejected"
            )

        else:

            st.info(
                f"Review status: {decision}"
            )

        st.dataframe(
            review.to_frame(
                name="Value"
            ),
            use_container_width=True
        )


# ============================================================
# EVALUATION
# ============================================================

elif page == "Evaluation":

    st.markdown(
        '<div class="section-title">'
        'Evaluation & Performance'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Evaluation of the complete 30-case "
        "NetSage AI pipeline."
    )


    # ========================================================
    # METRICS
    # ========================================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Rule Coverage",
            f"{checker_cases}/{total_cases}"
        )

    with c2:

        st.metric(
            "AI Coverage",
            f"{ai_cases}/{total_cases}"
        )

    with c3:

        st.metric(
            "Human Review",
            f"{human_cases}/{total_cases}"
        )

    with c4:

        st.metric(
            "Approval Rate",
            f"{approval_rate:.0f}%"
        )


    st.divider()


    # ========================================================
    # COVERAGE CHART
    # ========================================================

    evaluation_df = pd.DataFrame(
        {
            "Stage": [
                "Rule Checker",
                "AI Diagnosis",
                "Human Review",
                "Responsible AI"
            ],
            "Cases": [
                checker_cases,
                ai_cases,
                human_cases,
                responsible_cases
            ]
        }
    )


    fig_eval = px.bar(
        evaluation_df,
        x="Stage",
        y="Cases",
        text="Cases",
        color_discrete_sequence=[TEAL]
    )

    fig_eval.update_traces(
        textposition="outside"
    )

    fig_eval.update_layout(
        height=350,
        margin=dict(
            l=10,
            r=20,
            t=20,
            b=20
        ),
        yaxis=dict(
            title="Cases",
            range=[0, max(total_cases + 5, 35)],
            gridcolor="#E8EDF2"
        ),
        xaxis=dict(
            title=""
        ),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig_eval,
        use_container_width=True,
        config={"displayModeBar": False}
    )


    # ========================================================
    # REVIEW DISTRIBUTION
    # ========================================================

    col1, col2 = st.columns([1, 1])


    with col1:

        review_df = pd.DataFrame(
            {
                "Decision": [
                    "Approved",
                    "Corrected",
                    "Rejected"
                ],
                "Cases": [
                    approved,
                    corrected,
                    rejected
                ]
            }
        )

        fig = px.pie(
            review_df,
            names="Decision",
            values="Cases",
            hole=0.62,
            color="Decision",
            color_discrete_map={
                "Approved": GREEN,
                "Corrected": AMBER,
                "Rejected": RED
            }
        )

        fig.update_traces(
            textinfo="label+percent"
        )

        fig.update_layout(
            title="Human Validation",
            height=350
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )


    with col2:

        summary = pd.DataFrame(
            {
                "Metric": [
                    "Total Cases",
                    "Rule Checker",
                    "AI Diagnosis",
                    "Human Review",
                    "Responsible AI",
                    "Approved",
                    "Corrected",
                    "Rejected"
                ],
                "Result": [
                    total_cases,
                    f"{checker_cases}/{total_cases}",
                    f"{ai_cases}/{total_cases}",
                    f"{human_cases}/{total_cases}",
                    f"{responsible_cases}/{total_cases}",
                    approved,
                    corrected,
                    rejected
                ]
            }
        )

        st.markdown("**Evaluation Summary**")

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True
        )


    st.info(
        "The 100% approval result represents human review "
        "outcomes across the 30 test cases. It should not "
        "be presented as independently verified AI accuracy "
        "without a separate ground-truth dataset."
    )


# ============================================================
# RESPONSIBLE AI
# ============================================================

elif page == "Responsible AI":

    st.markdown(
        '<div class="section-title">'
        'Responsible AI & Human Oversight'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        "NetSage AI combines deterministic validation, "
        "AI reasoning, human review, and audit logging."
    )


    st.divider()


    # ========================================================
    # PIPELINE TABLE
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        'Human-in-the-Loop Architecture'
        '</div>',
        unsafe_allow_html=True
    )

    architecture = pd.DataFrame(
        {
            "Stage": [
                "Network Evidence",
                "Rule Checker",
                "AI Diagnosis",
                "Human Review",
                "Final Decision",
                "Audit Log"
            ],
            "Purpose": [
                "Collect symptoms and command output",
                "Identify deterministic faults",
                "Reason about root cause",
                "Validate AI diagnosis",
                "Approve, correct or reject",
                "Maintain traceable history"
            ]
        }
    )

    st.dataframe(
        architecture,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # OVERSIGHT DONUT
    # ========================================================

    review_df = pd.DataFrame(
        {
            "Decision": [
                "Approved",
                "Corrected",
                "Rejected"
            ],
            "Cases": [
                approved,
                corrected,
                rejected
            ]
        }
    )


    if reviewed:

        fig = px.pie(
            review_df,
            names="Decision",
            values="Cases",
            hole=0.65,
            color="Decision",
            color_discrete_map={
                "Approved": GREEN,
                "Corrected": AMBER,
                "Rejected": RED
            }
        )

        fig.update_traces(
            textinfo="label+percent"
        )

        fig.update_layout(
            title="Human Oversight Outcomes",
            height=400
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )


    # ========================================================
    # PRINCIPLES
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        'Responsible AI Principles'
        '</div>',
        unsafe_allow_html=True
    )

    principles = [
        "Evidence-based reasoning",
        "Deterministic rule validation",
        "Human-in-the-loop approval",
        "Traceable AI decisions",
        "Audit logging",
        "No blind acceptance of AI output",
        "Insufficient evidence triggers further investigation"
    ]

    for principle in principles:

        st.markdown(
            f"✓ {principle}"
        )


    st.divider()


    # ========================================================
    # AUDIT LOG
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        'Audit Log'
        '</div>',
        unsafe_allow_html=True
    )

    if responsible.empty:

        st.info(
            "No responsible AI records available."
        )

    else:

        st.dataframe(
            responsible,
            use_container_width=True,
            hide_index=True,
            height=400
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    '<div class="footer">'
    'NetSage AI • Network Troubleshooting • '
    'AI Assistance • Human Oversight'
    '</div>',
    unsafe_allow_html=True
)