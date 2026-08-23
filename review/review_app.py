import streamlit as st
import pandas as pd
import os


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="NetSage AI - Human Review",
    page_icon="🌐",
    layout="wide"
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

CASES_FILE = os.path.join(
    DATA_DIR,
    "cases.csv"
)

CHECKER_FILE = os.path.join(
    DATA_DIR,
    "checker_results.csv"
)

AI_FILE = os.path.join(
    DATA_DIR,
    "ai_results.csv"
)

REVIEWS_FILE = os.path.join(
    DATA_DIR,
    "human_reviews.csv"
)

RESPONSIBLE_LOG_FILE = os.path.join(
    DATA_DIR,
    "responsible_ai_log.csv"
)


# ============================================================
# PAGE TITLE
# ============================================================

st.title("🌐 NetSage AI")

st.subheader(
    "Cisco Network Troubleshooting - Human Review"
)

st.write(
    "Review the AI diagnosis using the supplied "
    "network evidence and rule-checker findings."
)


# ============================================================
# CHECK REQUIRED FILES
# ============================================================

required_files = [
    CASES_FILE,
    CHECKER_FILE,
    AI_FILE
]

for file_path in required_files:

    if not os.path.exists(file_path):

        st.error(
            f"Required file not found:\n{file_path}"
        )

        st.stop()


# ============================================================
# LOAD DATA
# ============================================================

cases = pd.read_csv(
    CASES_FILE,
    encoding="utf-8-sig"
)

checker_results = pd.read_csv(
    CHECKER_FILE,
    encoding="utf-8-sig"
)

ai_results = pd.read_csv(
    AI_FILE,
    encoding="utf-8-sig"
)


# ============================================================
# LOAD HUMAN REVIEWS
# ============================================================

if os.path.exists(REVIEWS_FILE):

    reviews = pd.read_csv(
        REVIEWS_FILE,
        encoding="utf-8-sig"
    )

else:

    reviews = pd.DataFrame(
        columns=[
            "ID",
            "AI_Diagnosis",
            "Reviewer_Decision",
            "Corrected_Fault",
            "Reviewer_Comment"
        ]
    )


# ============================================================
# CALCULATE STATISTICS
# ============================================================

total_cases = len(cases)

reviewed_cases = len(
    reviews[
        reviews["Reviewer_Decision"].notna()
    ]
)

approved_cases = len(
    reviews[
        reviews["Reviewer_Decision"] == "Approved"
    ]
)

corrected_cases = len(
    reviews[
        reviews["Reviewer_Decision"] == "Corrected"
    ]
)

rejected_cases = len(
    reviews[
        reviews["Reviewer_Decision"] == "Rejected"
    ]
)


# ============================================================
# PROJECT STATUS
# ============================================================

st.markdown("## 📊 Project Status")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Cases",
        total_cases
    )

with col2:
    st.metric(
        "Reviewed",
        reviewed_cases
    )

with col3:
    st.metric(
        "Approved",
        approved_cases
    )

with col4:
    st.metric(
        "Corrected",
        corrected_cases
    )

with col5:
    st.metric(
        "Rejected",
        rejected_cases
    )


st.divider()


# ============================================================
# CASE SELECTION
# ============================================================

st.markdown("## 🔎 Select Case")

case_ids = cases["ID"].tolist()

selected_id = st.selectbox(
    "Choose a case:",
    case_ids
)


# ============================================================
# GET SELECTED CASE
# ============================================================

case_row = cases[
    cases["ID"] == selected_id
]

if len(case_row) == 0:

    st.error("Case not found.")

    st.stop()

case = case_row.iloc[0]


# ============================================================
# DISPLAY SYMPTOM
# ============================================================

st.markdown(
    f"## Case {selected_id}"
)

st.markdown("### Symptom")

st.info(
    str(case["Symptom"])
)


# ============================================================
# DISPLAY TOPOLOGY
# ============================================================

st.markdown("### Topology / Devices")

st.code(
    str(case["Topology / Devices"])
)


# ============================================================
# DISPLAY EVIDENCE
# ============================================================

st.markdown("### Show Command Output / Evidence")

st.code(
    str(case["Show Output / Evidence"])
)


# ============================================================
# DISPLAY SEVERITY
# ============================================================

st.markdown("### Severity")

st.warning(
    str(case["Severity"])
)


# ============================================================
# RULE CHECKER
# ============================================================

st.divider()

st.markdown(
    "## 🔍 Deterministic Rule Checker"
)

checker_rows = checker_results[
    checker_results["ID"] == selected_id
]

if len(checker_rows) == 0:

    st.info(
        "No rule checker result found."
    )

else:

    for _, row in checker_rows.iterrows():

        st.markdown(
            f"**Rule:** {row['Rule']}"
        )

        st.markdown(
            f"**Status:** {row['Status']}"
        )

        st.markdown(
            f"**Finding:** {row['Finding']}"
        )

        st.divider()


# ============================================================
# AI DIAGNOSIS
# ============================================================

st.markdown(
    "## 🤖 Gemini AI Diagnosis"
)

ai_rows = ai_results[
    ai_results["ID"] == selected_id
]

if len(ai_rows) == 0:

    st.error(
        "AI diagnosis not found."
    )

    st.stop()

ai_diagnosis = str(
    ai_rows.iloc[0]["AI_Diagnosis"]
)

st.code(
    ai_diagnosis,
    language="text"
)


# ============================================================
# HUMAN REVIEW
# ============================================================

st.divider()

st.markdown(
    "## 👤 Human Review"
)

st.write(
    "Compare the AI diagnosis with the evidence "
    "and rule-checker findings before making a decision."
)


decision = st.radio(
    "Reviewer Decision",
    [
        "Approved",
        "Corrected",
        "Rejected"
    ],
    horizontal=True
)


# ============================================================
# CORRECTION FIELD
# ============================================================

corrected_fault = ""

if decision == "Corrected":

    corrected_fault = st.text_area(
        "Correct Diagnosis",
        placeholder=(
            "Enter the diagnosis that the human "
            "reviewer believes is correct."
        )
    )


# ============================================================
# REVIEW COMMENT
# ============================================================

reviewer_comment = st.text_area(
    "Reviewer Comment",
    placeholder=(
        "Explain why the diagnosis was "
        "approved, corrected, or rejected."
    )
)


# ============================================================
# SAVE REVIEW
# ============================================================

if st.button(
    "💾 Save Human Review",
    type="primary"
):

    # --------------------------------------------------------
    # Validate correction
    # --------------------------------------------------------

    if decision == "Corrected":

        if not corrected_fault.strip():

            st.error(
                "Please enter the corrected diagnosis."
            )

            st.stop()


    # --------------------------------------------------------
    # Create review record
    # --------------------------------------------------------

    new_review = {
        "ID": selected_id,
        "AI_Diagnosis": ai_diagnosis,
        "Reviewer_Decision": decision,
        "Corrected_Fault": corrected_fault,
        "Reviewer_Comment": reviewer_comment
    }


    # --------------------------------------------------------
    # Remove previous review for this case
    # --------------------------------------------------------

    reviews = reviews[
        reviews["ID"] != selected_id
    ]


    # --------------------------------------------------------
    # Add new review
    # --------------------------------------------------------

    reviews = pd.concat(
        [
            reviews,
            pd.DataFrame([new_review])
        ],
        ignore_index=True
    )


    # --------------------------------------------------------
    # Save human_reviews.csv
    # --------------------------------------------------------

    reviews.to_csv(
        REVIEWS_FILE,
        index=False,
        encoding="utf-8-sig"
    )


    # ========================================================
    # RESPONSIBLE AI LOG
    # ========================================================

    if os.path.exists(
        RESPONSIBLE_LOG_FILE
    ):

        log_df = pd.read_csv(
            RESPONSIBLE_LOG_FILE,
            encoding="utf-8-sig"
        )

    else:

        log_df = pd.DataFrame(
            columns=[
                "ID",
                "AI_Diagnosis",
                "Human_Decision",
                "Corrected_Diagnosis",
                "Reason",
                "Action_Taken"
            ]
        )


    # --------------------------------------------------------
    # Remove previous log for this case
    # --------------------------------------------------------

    log_df = log_df[
        log_df["ID"] != selected_id
    ]


    # --------------------------------------------------------
    # Create log entry
    # --------------------------------------------------------

    if decision == "Approved":

        action = (
            "AI diagnosis approved "
            "by human reviewer"
        )

    elif decision == "Corrected":

        action = (
            "AI diagnosis corrected "
            "by human reviewer"
        )

    else:

        action = (
            "AI diagnosis rejected "
            "by human reviewer"
        )


    new_log = {
        "ID": selected_id,
        "AI_Diagnosis": ai_diagnosis,
        "Human_Decision": decision,
        "Corrected_Diagnosis": corrected_fault,
        "Reason": reviewer_comment,
        "Action_Taken": action
    }


    log_df = pd.concat(
        [
            log_df,
            pd.DataFrame([new_log])
        ],
        ignore_index=True
    )


    # --------------------------------------------------------
    # Save responsible_ai_log.csv
    # --------------------------------------------------------

    log_df.to_csv(
        RESPONSIBLE_LOG_FILE,
        index=False,
        encoding="utf-8-sig"
    )


    st.success(
        f"Review for {selected_id} saved successfully."
    )


    st.rerun()


# ============================================================
# SHOW EXISTING REVIEW
# ============================================================

st.divider()

st.markdown(
    "## Existing Human Review"
)

current_review = reviews[
    reviews["ID"] == selected_id
]

if len(current_review) > 0:

    review = current_review.iloc[0]

    st.success(
        f"Decision: {review['Reviewer_Decision']}"
    )

    if str(
        review["Corrected_Fault"]
    ).strip():

        st.write(
            f"**Corrected Diagnosis:** "
            f"{review['Corrected_Fault']}"
        )

    st.write(
        f"**Reviewer Comment:** "
        f"{review['Reviewer_Comment']}"
    )

else:

    st.info(
        "This case has not been reviewed yet."
    )


# ============================================================
# REVIEW SUMMARY
# ============================================================

st.divider()

st.markdown(
    "## 📈 Review Summary"
)

summary = pd.DataFrame(
    {
        "Decision": [
            "Approved",
            "Corrected",
            "Rejected"
        ],
        "Count": [
            approved_cases,
            corrected_cases,
            rejected_cases
        ]
    }
)

st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True
)