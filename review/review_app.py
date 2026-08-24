import os
import pandas as pd
import streamlit as st


# ============================================================
# NETSAGE AI - HUMAN REVIEW APPLICATION
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
# PAGE HEADER
# ============================================================

st.title("🌐 NetSage AI")

st.subheader(
    "Cisco Network Troubleshooting — Human Review"
)

st.write(
    "Review the AI diagnosis against the supplied "
    "network evidence and deterministic rule-checker findings."
)


# ============================================================
# REQUIRED FILE CHECK
# ============================================================

required_files = {
    "cases.csv": CASES_FILE,
    "checker_results.csv": CHECKER_FILE,
    "ai_results.csv": AI_FILE
}


for name, path in required_files.items():

    if not os.path.exists(path):

        st.error(
            f"Required file not found: {name}"
        )

        st.code(path)

        st.stop()


# ============================================================
# LOAD DATA
# ============================================================

def load_csv(path):

    try:

        return pd.read_csv(
            path,
            encoding="utf-8-sig"
        )

    except Exception as error:

        st.error(
            f"Unable to read {path}: {error}"
        )

        st.stop()


cases = load_csv(
    CASES_FILE
)

checker_results = load_csv(
    CHECKER_FILE
)

ai_results = load_csv(
    AI_FILE
)


# ============================================================
# VALIDATE REQUIRED COLUMNS
# ============================================================

required_case_columns = [
    "ID",
    "Symptom",
    "Topology / Devices",
    "Show Output / Evidence"
]

for column in required_case_columns:

    if column not in cases.columns:

        st.error(
            f"cases.csv is missing column: {column}"
        )

        st.stop()


if "ID" not in checker_results.columns:

    st.error(
        "checker_results.csv is missing the ID column."
    )

    st.stop()


if "ID" not in ai_results.columns:

    st.error(
        "ai_results.csv is missing the ID column."
    )

    st.stop()


if "AI_Diagnosis" not in ai_results.columns:

    st.error(
        "ai_results.csv is missing the AI_Diagnosis column."
    )

    st.stop()


# ============================================================
# NORMALIZE IDS
# ============================================================

cases["ID"] = (
    cases["ID"]
    .astype(str)
    .str.strip()
)

checker_results["ID"] = (
    checker_results["ID"]
    .astype(str)
    .str.strip()
)

ai_results["ID"] = (
    ai_results["ID"]
    .astype(str)
    .str.strip()
)


# ============================================================
# LOAD HUMAN REVIEWS
# ============================================================

if os.path.exists(REVIEWS_FILE):

    reviews = load_csv(
        REVIEWS_FILE
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
# NORMALIZE HUMAN REVIEW DATA
# ============================================================

if "ID" not in reviews.columns:

    reviews["ID"] = ""

if "Reviewer_Decision" not in reviews.columns:

    reviews["Reviewer_Decision"] = ""

if "AI_Diagnosis" not in reviews.columns:

    reviews["AI_Diagnosis"] = ""

if "Corrected_Fault" not in reviews.columns:

    reviews["Corrected_Fault"] = ""

if "Reviewer_Comment" not in reviews.columns:

    reviews["Reviewer_Comment"] = ""


reviews["ID"] = (
    reviews["ID"]
    .astype(str)
    .str.strip()
)


# ============================================================
# STATISTICS
# ============================================================

total_cases = (
    cases["ID"]
    .nunique()
)

reviewed_cases = 0
approved_cases = 0
corrected_cases = 0
rejected_cases = 0


if not reviews.empty:

    decisions = (
        reviews["Reviewer_Decision"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    reviewed_cases = (
        decisions.isin(
            [
                "Approved",
                "Corrected",
                "Rejected"
            ]
        ).sum()
    )

    approved_cases = (
        decisions == "Approved"
    ).sum()

    corrected_cases = (
        decisions == "Corrected"
    ).sum()

    rejected_cases = (
        decisions == "Rejected"
    ).sum()


# ============================================================
# PROJECT STATUS
# ============================================================

st.markdown(
    "## 📊 Human Review Status"
)

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

st.markdown(
    "## 🔎 Select Network Case"
)

case_ids = (
    cases["ID"]
    .tolist()
)

selected_id = st.selectbox(
    "Choose a case:",
    case_ids
)


# ============================================================
# SELECT CASE
# ============================================================

case_rows = cases[
    cases["ID"] == selected_id
]


if case_rows.empty:

    st.error(
        "Selected case could not be found."
    )

    st.stop()


case = case_rows.iloc[0]


# ============================================================
# CASE HEADER
# ============================================================

st.markdown(
    f"## Case {selected_id}"
)


# ============================================================
# CASE METADATA
# ============================================================

meta1, meta2, meta3 = st.columns(3)


with meta1:

    st.markdown(
        "**Severity**"
    )

    st.info(
        str(
            case.get(
                "Severity",
                "Not provided"
            )
        )
    )


with meta2:

    st.markdown(
        "**OSI Layer**"
    )

    st.info(
        str(
            case.get(
                "OSI",
                "Not provided"
            )
        )
    )


with meta3:

    st.markdown(
        "**Concept**"
    )

    st.info(
        str(
            case.get(
                "Concept",
                "Not provided"
            )
        )
    )


# ============================================================
# SYMPTOM
# ============================================================

st.markdown(
    "### 1. Network Symptom"
)

st.info(
    str(
        case["Symptom"]
    )
)


# ============================================================
# TOPOLOGY
# ============================================================

st.markdown(
    "### 2. Topology / Devices"
)

st.code(
    str(
        case["Topology / Devices"]
    ),
    language="text"
)


# ============================================================
# COMMAND OUTPUT
# ============================================================

st.markdown(
    "### 3. Supplied Command Output / Evidence"
)

st.code(
    str(
        case["Show Output / Evidence"]
    ),
    language="text"
)


# ============================================================
# EXPECTED FAULT
# ============================================================
# IMPORTANT:
# This is shown only for dataset/reference inspection.
# It must NOT be used as evidence when reviewing the AI.
# ============================================================

with st.expander(
    "Dataset Reference Information"
):

    if "Expected Fault" in case.index:

        st.caption(
            "Reference label from the dataset. "
            "Do not use this as supplied evidence when "
            "evaluating the AI diagnosis."
        )

        st.write(
            str(
                case["Expected Fault"]
            )
        )

    else:

        st.info(
            "No reference fault is available."
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


if checker_rows.empty:

    st.warning(
        "No deterministic rule-checker result "
        "was found for this case."
    )

else:

    for _, row in checker_rows.iterrows():

        rule = str(
            row.get(
                "Rule",
                ""
            )
        )

        status = str(
            row.get(
                "Status",
                ""
            )
        ).strip()

        finding = str(
            row.get(
                "Finding",
                ""
            )
        )

        st.markdown(
            f"**Rule:** {rule}"
        )

        if status.upper() == "FAIL":

            st.error(
                f"Status: {status}"
            )

        elif status.upper() == "PASS":

            st.success(
                f"Status: {status}"
            )

        else:

            st.warning(
                f"Status: {status}"
            )

        st.markdown(
            f"**Finding:** {finding}"
        )

        st.divider()


# ============================================================
# AI DIAGNOSIS
# ============================================================

st.markdown(
    "## 🤖 Groq AI Diagnosis"
)

ai_rows = ai_results[
    ai_results["ID"] == selected_id
]


if ai_rows.empty:

    st.error(
        "AI diagnosis not found for this case."
    )

    st.stop()


ai_diagnosis = str(
    ai_rows.iloc[0]["AI_Diagnosis"]
).strip()


if not ai_diagnosis:

    st.error(
        "AI diagnosis is empty."
    )

    st.stop()


# ------------------------------------------------------------
# Insufficient evidence indicator
# ------------------------------------------------------------

if (
    "insufficient evidence"
    in ai_diagnosis.lower()
):

    st.warning(
        "⚠ The AI marked this case as "
        "'Insufficient evidence'."
    )


st.markdown(
    ai_diagnosis
)


# ============================================================
# REVIEW GUIDANCE
# ============================================================

st.divider()

st.markdown(
    "## 🧭 Human Review Guidance"
)

st.write(
    """
Before making a decision:

1. Check whether the diagnosis is supported by the supplied evidence.
2. Check whether the proposed OSI layer and networking concept are reasonable.
3. Check whether the cited evidence actually appears in the case.
4. Check whether the next command would genuinely help confirm the diagnosis.
5. Do not approve a diagnosis merely because it sounds plausible.
6. If evidence is insufficient, the AI should explicitly acknowledge that.
"""
)


# ============================================================
# HUMAN REVIEW FORM
# ============================================================

st.markdown(
    "## 👤 Human Decision"
)


# ------------------------------------------------------------
# Existing review
# ------------------------------------------------------------

existing_review = reviews[
    reviews["ID"] == selected_id
]


existing_decision = ""

if not existing_review.empty:

    existing_decision = str(
        existing_review.iloc[0][
            "Reviewer_Decision"
        ]
    ).strip()


# ------------------------------------------------------------
# Decision
# ------------------------------------------------------------

decision_options = [
    "Approved",
    "Corrected",
    "Rejected"
]


decision = st.radio(
    "Reviewer Decision",
    decision_options,
    index=(
        decision_options.index(
            existing_decision
        )
        if existing_decision
        in decision_options
        else 0
    ),
    horizontal=True
)


# ============================================================
# CORRECTED DIAGNOSIS
# ============================================================

corrected_fault = ""


if decision == "Corrected":

    previous_correction = ""

    if not existing_review.empty:

        previous_correction = str(
            existing_review.iloc[0].get(
                "Corrected_Fault",
                ""
            )
        )

    corrected_fault = st.text_area(
        "Correct Diagnosis",
        value=previous_correction,
        placeholder=(
            "Enter the diagnosis that the reviewer "
            "believes is correct."
        )
    )


# ============================================================
# REVIEW COMMENT
# ============================================================

previous_comment = ""

if not existing_review.empty:

    previous_comment = str(
        existing_review.iloc[0].get(
            "Reviewer_Comment",
            ""
        )
    )


reviewer_comment = st.text_area(
    "Reviewer Comment",
    value=previous_comment,
    placeholder=(
        "Explain why the AI diagnosis was "
        "approved, corrected, or rejected."
    )
)


# ============================================================
# SAVE REVIEW
# ============================================================

if st.button(
    "💾 Save Human Review",
    type="primary",
    use_container_width=True
):

    # --------------------------------------------------------
    # VALIDATE CORRECTION
    # --------------------------------------------------------

    if decision == "Corrected":

        if not corrected_fault.strip():

            st.error(
                "Please enter the corrected diagnosis."
            )

            st.stop()


    # --------------------------------------------------------
    # VALIDATE REVIEW COMMENT
    # --------------------------------------------------------

    if not reviewer_comment.strip():

        st.error(
            "Please provide a reviewer comment explaining "
            "the decision."
        )

        st.stop()


    # ========================================================
    # CREATE HUMAN REVIEW
    # ========================================================

    new_review = {
        "ID": selected_id,
        "AI_Diagnosis": ai_diagnosis,
        "Reviewer_Decision": decision,
        "Corrected_Fault": corrected_fault.strip(),
        "Reviewer_Comment": reviewer_comment.strip()
    }


    # --------------------------------------------------------
    # Remove previous review for this case
    # --------------------------------------------------------

    reviews = reviews[
        reviews["ID"] != selected_id
    ]


    # --------------------------------------------------------
    # Add current review
    # --------------------------------------------------------

    reviews = pd.concat(
        [
            reviews,
            pd.DataFrame(
                [new_review]
            )
        ],
        ignore_index=True
    )


    # ========================================================
    # SAVE HUMAN REVIEW
    # ========================================================

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

        log_df = load_csv(
            RESPONSIBLE_LOG_FILE
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
    # Normalize log
    # --------------------------------------------------------

    if "ID" not in log_df.columns:

        log_df["ID"] = ""

    log_df["ID"] = (
        log_df["ID"]
        .astype(str)
        .str.strip()
    )


    # --------------------------------------------------------
    # Remove previous log
    # --------------------------------------------------------

    log_df = log_df[
        log_df["ID"] != selected_id
    ]


    # ========================================================
    # ACTION DESCRIPTION
    # ========================================================

    if decision == "Approved":

        action = (
            "AI diagnosis approved "
            "by human reviewer."
        )

    elif decision == "Corrected":

        action = (
            "AI diagnosis corrected "
            "by human reviewer."
        )

    else:

        action = (
            "AI diagnosis rejected "
            "by human reviewer."
        )


    # ========================================================
    # CREATE AUDIT LOG ENTRY
    # ========================================================

    new_log = {
        "ID": selected_id,
        "AI_Diagnosis": ai_diagnosis,
        "Human_Decision": decision,
        "Corrected_Diagnosis": corrected_fault.strip(),
        "Reason": reviewer_comment.strip(),
        "Action_Taken": action
    }


    log_df = pd.concat(
        [
            log_df,
            pd.DataFrame(
                [new_log]
            )
        ],
        ignore_index=True
    )


    # ========================================================
    # SAVE AUDIT LOG
    # ========================================================

    log_df.to_csv(
        RESPONSIBLE_LOG_FILE,
        index=False,
        encoding="utf-8-sig"
    )


    # ========================================================
    # SUCCESS
    # ========================================================

    st.success(
        f"Review for {selected_id} saved successfully."
    )

    st.rerun()


# ============================================================
# EXISTING REVIEW
# ============================================================

st.divider()

st.markdown(
    "## 📋 Existing Human Review"
)


current_review = reviews[
    reviews["ID"] == selected_id
]


if not current_review.empty:

    review = current_review.iloc[0]

    review_decision = str(
        review.get(
            "Reviewer_Decision",
            ""
        )
    )


    if review_decision == "Approved":

        st.success(
            "✓ AI diagnosis approved"
        )

    elif review_decision == "Corrected":

        st.warning(
            "⚠ AI diagnosis corrected"
        )

    elif review_decision == "Rejected":

        st.error(
            "✕ AI diagnosis rejected"
        )

    else:

        st.info(
            f"Decision: {review_decision}"
        )


    if str(
        review.get(
            "Corrected_Fault",
            ""
        )
    ).strip():

        st.markdown(
            "**Corrected Diagnosis:**"
        )

        st.info(
            str(
                review["Corrected_Fault"]
            )
        )


    st.markdown(
        "**Reviewer Comment:**"
    )

    st.write(
        str(
            review.get(
                "Reviewer_Comment",
                ""
            )
        )
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


# ============================================================
# REVIEW INTERPRETATION
# ============================================================

if reviewed_cases > 0:

    approval_rate = (
        approved_cases
        / reviewed_cases
        * 100
    )

    correction_rate = (
        corrected_cases
        / reviewed_cases
        * 100
    )

    rejection_rate = (
        rejected_cases
        / reviewed_cases
        * 100
    )


    st.markdown(
        "### Review Rates"
    )

    r1, r2, r3 = st.columns(3)


    with r1:

        st.metric(
            "Approval Rate",
            f"{approval_rate:.1f}%"
        )


    with r2:

        st.metric(
            "Correction Rate",
            f"{correction_rate:.1f}%"
        )


    with r3:

        st.metric(
            "Rejection Rate",
            f"{rejection_rate:.1f}%"
        )


    st.caption(
        "These rates describe human review outcomes. "
        "They are not independent measurements of AI accuracy."
    )