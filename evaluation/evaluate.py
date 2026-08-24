import os
import re
import pandas as pd


# ============================================================
# NETSAGE AI - EVALUATION
# ============================================================

print("=" * 70)
print("NETSAGE AI - EVALUATION REPORT")
print("=" * 70)


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

HUMAN_FILE = os.path.join(
    DATA_DIR,
    "human_reviews.csv"
)

RESPONSIBLE_FILE = os.path.join(
    DATA_DIR,
    "responsible_ai_log.csv"
)


# ============================================================
# REQUIRED FILES
# ============================================================

required_files = {
    "Cases": CASES_FILE,
    "Checker": CHECKER_FILE,
    "AI Results": AI_FILE,
    "Human Reviews": HUMAN_FILE,
    "Responsible AI Log": RESPONSIBLE_FILE
}


missing_files = []

for name, file_path in required_files.items():

    if not os.path.exists(file_path):

        missing_files.append(
            f"{name}: {file_path}"
        )


if missing_files:

    print()
    print("ERROR: Required files are missing.")

    for item in missing_files:

        print(
            f"- {item}"
        )

    print()

    raise SystemExit(1)


# ============================================================
# LOAD CSV SAFELY
# ============================================================

def load_csv(path):

    try:

        return pd.read_csv(
            path,
            encoding="utf-8-sig"
        )

    except Exception as error:

        print()
        print(
            f"ERROR reading: {path}"
        )

        print(
            f"Reason: {error}"
        )

        raise SystemExit(1)


cases = load_csv(
    CASES_FILE
)

checker = load_csv(
    CHECKER_FILE
)

ai = load_csv(
    AI_FILE
)

human = load_csv(
    HUMAN_FILE
)

responsible = load_csv(
    RESPONSIBLE_FILE
)


# ============================================================
# NORMALIZE IDS
# ============================================================

def normalize_ids(df):

    if "ID" not in df.columns:

        return df

    df["ID"] = (
        df["ID"]
        .astype(str)
        .str.strip()
    )

    return df


cases = normalize_ids(cases)
checker = normalize_ids(checker)
ai = normalize_ids(ai)
human = normalize_ids(human)
responsible = normalize_ids(responsible)


# ============================================================
# BASIC VALIDATION
# ============================================================

if "ID" not in cases.columns:

    print(
        "ERROR: cases.csv must contain an ID column."
    )

    raise SystemExit(1)


if "ID" not in checker.columns:

    print(
        "ERROR: checker_results.csv must contain an ID column."
    )

    raise SystemExit(1)


if "ID" not in ai.columns:

    print(
        "ERROR: ai_results.csv must contain an ID column."
    )

    raise SystemExit(1)


# ============================================================
# BASIC COUNTS
# ============================================================

total_cases = (
    cases["ID"]
    .dropna()
    .nunique()
)

checker_cases = (
    checker["ID"]
    .dropna()
    .nunique()
)

ai_cases = (
    ai["ID"]
    .dropna()
    .nunique()
)

human_cases = (
    human["ID"]
    .dropna()
    .nunique()
)

responsible_cases = (
    responsible["ID"]
    .dropna()
    .nunique()
)


# ============================================================
# CASE ID SETS
# ============================================================

case_ids = set(
    cases["ID"]
    .dropna()
    .astype(str)
    .str.strip()
)

checker_ids = set(
    checker["ID"]
    .dropna()
    .astype(str)
    .str.strip()
)

ai_ids = set(
    ai["ID"]
    .dropna()
    .astype(str)
    .str.strip()
)

human_ids = set(
    human["ID"]
    .dropna()
    .astype(str)
    .str.strip()
)

responsible_ids = set(
    responsible["ID"]
    .dropna()
    .astype(str)
    .str.strip()
)


# ============================================================
# COVERAGE
# ============================================================

missing_checker = (
    case_ids - checker_ids
)

missing_ai = (
    case_ids - ai_ids
)

missing_human = (
    case_ids - human_ids
)

missing_responsible = (
    case_ids - responsible_ids
)


checker_completion = (
    checker_cases / total_cases * 100
    if total_cases
    else 0
)

ai_completion = (
    ai_cases / total_cases * 100
    if total_cases
    else 0
)

human_completion = (
    human_cases / total_cases * 100
    if total_cases
    else 0
)

responsible_completion = (
    responsible_cases / total_cases * 100
    if total_cases
    else 0
)


# ============================================================
# HUMAN REVIEW COUNTS
# ============================================================

approved = 0
corrected = 0
rejected = 0

if (
    not human.empty
    and
    "Reviewer_Decision" in human.columns
):

    decisions = (
        human["Reviewer_Decision"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    approved = (
        decisions == "Approved"
    ).sum()

    corrected = (
        decisions == "Corrected"
    ).sum()

    rejected = (
        decisions == "Rejected"
    ).sum()


reviewed = (
    approved
    + corrected
    + rejected
)


# ============================================================
# REVIEW RATES
# ============================================================

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
# AI RESPONSE QUALITY CHECKS
# ============================================================

required_sections = [
    "Likely Fault",
    "OSI Layer",
    "Networking Concept",
    "Severity",
    "Evidence",
    "Next Command",
    "Recommended Fix",
    "Verification"
]


def get_diagnosis_text(row):

    if "AI_Diagnosis" not in row.index:

        return ""

    value = row["AI_Diagnosis"]

    if pd.isna(value):

        return ""

    return str(value).strip()


def has_section(text, section):

    patterns = [
        rf"##\s*\d*\.?\s*{re.escape(section)}",
        rf"\*\*{re.escape(section)}:\*\*",
        rf"{re.escape(section)}:"
    ]

    for pattern in patterns:

        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        ):

            return True

    return False


# ============================================================
# ANALYZE AI OUTPUTS
# ============================================================

ai_quality_records = []

if not ai.empty:

    for _, row in ai.iterrows():

        case_id = str(
            row.get(
                "ID",
                ""
            )
        ).strip()

        diagnosis = get_diagnosis_text(
            row
        )

        record = {
            "ID": case_id,
            "Has_Response": bool(diagnosis),
            "Insufficient_Evidence": (
                "insufficient evidence"
                in diagnosis.lower()
            )
        }


        for section in required_sections:

            record[
                "Has_" + section.replace(
                    " ",
                    "_"
                )
            ] = has_section(
                diagnosis,
                section
            )


        ai_quality_records.append(
            record
        )


ai_quality = pd.DataFrame(
    ai_quality_records
)


# ============================================================
# AI QUALITY METRICS
# ============================================================

if not ai_quality.empty:

    response_count = int(
        ai_quality["Has_Response"].sum()
    )

    insufficient_evidence_count = int(
        ai_quality[
            "Insufficient_Evidence"
        ].sum()
    )

else:

    response_count = 0

    insufficient_evidence_count = 0


ai_response_rate = (
    response_count / ai_cases * 100
    if ai_cases
    else 0
)


# ============================================================
# REQUIRED SECTION COMPLETENESS
# ============================================================

section_metrics = {}

for section in required_sections:

    column = (
        "Has_"
        + section.replace(
            " ",
            "_"
        )
    )

    if (
        not ai_quality.empty
        and column in ai_quality.columns
    ):

        count = int(
            ai_quality[column].sum()
        )

    else:

        count = 0


    section_metrics[section] = count


# ============================================================
# RESPONSIBLE AI CHECK
# ============================================================

logged_approved = 0
logged_corrected = 0
logged_rejected = 0

if (
    not responsible.empty
    and
    "Human_Decision"
    in responsible.columns
):

    human_decisions = (
        responsible["Human_Decision"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    logged_approved = (
        human_decisions
        == "Approved"
    ).sum()

    logged_corrected = (
        human_decisions
        == "Corrected"
    ).sum()

    logged_rejected = (
        human_decisions
        == "Rejected"
    ).sum()


logged_review_decisions = (
    logged_approved
    + logged_corrected
    + logged_rejected
)


# ============================================================
# HUMAN / RESPONSIBLE AI CONSISTENCY
# ============================================================

decision_consistency = (
    logged_review_decisions == reviewed
    and reviewed > 0
)


# ============================================================
# PIPELINE STATUS
# ============================================================

pipeline_complete = (
    len(missing_checker) == 0
    and
    len(missing_ai) == 0
    and
    len(missing_human) == 0
    and
    len(missing_responsible) == 0
)


# ============================================================
# DISPLAY DATA PIPELINE
# ============================================================

print()

print("-" * 70)
print("1. DATA PIPELINE")
print("-" * 70)

print(
    f"Total unique cases:       {total_cases}"
)

print(
    f"Rule checker cases:       {checker_cases}"
)

print(
    f"AI diagnosis cases:       {ai_cases}"
)

print(
    f"Human review cases:       {human_cases}"
)

print(
    f"Responsible AI records:   {responsible_cases}"
)

print()

print(
    f"Checker completion:       "
    f"{checker_completion:.2f}%"
)

print(
    f"AI completion:            "
    f"{ai_completion:.2f}%"
)

print(
    f"Human review completion:  "
    f"{human_completion:.2f}%"
)

print(
    f"Responsible AI completion:"
    f" {responsible_completion:.2f}%"
)


# ============================================================
# COVERAGE REPORT
# ============================================================

print()

print("-" * 70)
print("2. CASE COVERAGE")
print("-" * 70)


if not missing_checker:

    print(
        "Checker:        ALL CASES COVERED"
    )

else:

    print(
        f"Checker missing: {sorted(missing_checker)}"
    )


if not missing_ai:

    print(
        "AI Diagnosis:   ALL CASES COVERED"
    )

else:

    print(
        f"AI missing: {sorted(missing_ai)}"
    )


if not missing_human:

    print(
        "Human Review:   ALL CASES COVERED"
    )

else:

    print(
        f"Human missing: {sorted(missing_human)}"
    )


if not missing_responsible:

    print(
        "Responsible AI: ALL CASES COVERED"
    )

else:

    print(
        "Responsible missing:"
    )

    print(
        sorted(missing_responsible)
    )


# ============================================================
# AI RESPONSE QUALITY
# ============================================================

print()

print("-" * 70)
print("3. AI RESPONSE QUALITY")
print("-" * 70)

print(
    f"AI responses available:  "
    f"{response_count}/{ai_cases}"
)

print(
    f"AI response rate:        "
    f"{ai_response_rate:.2f}%"
)

print(
    f"Insufficient evidence:    "
    f"{insufficient_evidence_count}"
)

print()

print(
    "Required section coverage:"
)

for section, count in section_metrics.items():

    percentage = (
        count / ai_cases * 100
        if ai_cases
        else 0
    )

    print(
        f"- {section:<22} "
        f"{count}/{ai_cases} "
        f"({percentage:.2f}%)"
    )


# ============================================================
# HUMAN REVIEW RESULTS
# ============================================================

print()

print("-" * 70)
print("4. HUMAN REVIEW RESULTS")
print("-" * 70)

print(
    f"Reviewed:         {reviewed}"
)

print(
    f"Approved:         {approved}"
)

print(
    f"Corrected:        {corrected}"
)

print(
    f"Rejected:         {rejected}"
)

print()

print(
    f"Approval rate:    "
    f"{approval_rate:.2f}%"
)

print(
    f"Correction rate:  "
    f"{correction_rate:.2f}%"
)

print(
    f"Rejection rate:   "
    f"{rejection_rate:.2f}%"
)


# ============================================================
# RESPONSIBLE AI RESULTS
# ============================================================

print()

print("-" * 70)
print("5. RESPONSIBLE AI CHECK")
print("-" * 70)

print(
    f"Approved logged:   "
    f"{logged_approved}"
)

print(
    f"Corrected logged:  "
    f"{logged_corrected}"
)

print(
    f"Rejected logged:   "
    f"{logged_rejected}"
)

print()

if decision_consistency:

    print(
        "Human review and audit log: CONSISTENT"
    )

elif reviewed == 0:

    print(
        "Human review and audit log: "
        "NO REVIEWS AVAILABLE"
    )

else:

    print(
        "Human review and audit log: "
        "INCONSISTENT"
    )


# ============================================================
# DUPLICATE CHECK
# ============================================================

print()

print("-" * 70)
print("6. DATA INTEGRITY")
print("-" * 70)


def duplicate_count(df):

    if (
        df.empty
        or
        "ID" not in df.columns
    ):

        return 0

    return int(
        df["ID"].duplicated().sum()
    )


cases_duplicates = duplicate_count(
    cases
)

checker_duplicates = duplicate_count(
    checker
)

ai_duplicates = duplicate_count(
    ai
)

human_duplicates = duplicate_count(
    human
)

responsible_duplicates = duplicate_count(
    responsible
)


print(
    f"Cases duplicate IDs:       "
    f"{cases_duplicates}"
)

print(
    f"Checker duplicate IDs:     "
    f"{checker_duplicates}"
)

print(
    f"AI duplicate IDs:          "
    f"{ai_duplicates}"
)

print(
    f"Human review duplicate IDs:"
    f" {human_duplicates}"
)

print(
    f"Responsible duplicate IDs: "
    f"{responsible_duplicates}"
)


# ============================================================
# AI/HUMAN CASE ALIGNMENT
# ============================================================

print()

ai_without_case = (
    ai_ids - case_ids
)

human_without_case = (
    human_ids - case_ids
)

responsible_without_case = (
    responsible_ids - case_ids
)


print(
    f"AI records without case:          "
    f"{len(ai_without_case)}"
)

print(
    f"Human records without case:      "
    f"{len(human_without_case)}"
)

print(
    f"Audit records without case:      "
    f"{len(responsible_without_case)}"
)


# ============================================================
# FINAL STATUS
# ============================================================

print()

print("=" * 70)
print("7. FINAL EVALUATION")
print("=" * 70)


integrity_ok = (
    cases_duplicates == 0
    and
    ai_duplicates == 0
    and
    human_duplicates == 0
    and
    responsible_duplicates == 0
)

alignment_ok = (
    len(ai_without_case) == 0
    and
    len(human_without_case) == 0
    and
    len(responsible_without_case) == 0
)


if pipeline_complete:

    print()
    print(
        "PIPELINE STATUS: COMPLETE"
    )

else:

    print()
    print(
        "PIPELINE STATUS: INCOMPLETE"
    )


if response_count == ai_cases and ai_cases > 0:

    print(
        "AI RESPONSE STATUS: COMPLETE"
    )

else:

    print(
        "AI RESPONSE STATUS: INCOMPLETE"
    )


if integrity_ok:

    print(
        "DATA INTEGRITY: PASS"
    )

else:

    print(
        "DATA INTEGRITY: CHECK REQUIRED"
    )


if alignment_ok:

    print(
        "CASE ALIGNMENT: PASS"
    )

else:

    print(
        "CASE ALIGNMENT: CHECK REQUIRED"
    )


# ============================================================
# IMPORTANT INTERPRETATION
# ============================================================

print()

print("-" * 70)
print("INTERPRETATION")
print("-" * 70)

print(
    "Human approval rate is NOT treated as independent "
    "AI accuracy."
)

print(
    "A human-approved diagnosis indicates that the reviewer "
    "accepted the AI diagnosis."
)

print(
    "A corrected or rejected diagnosis indicates that "
    "human intervention changed or rejected the AI output."
)

print(
    "Independent AI accuracy requires a separate ground-truth "
    "evaluation dataset or trusted reference labels."
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()

print("=" * 70)
print("EVALUATION SUMMARY")
print("=" * 70)

print()

print(
    f"Cases:                 {total_cases}"
)

print(
    f"AI responses:          {ai_cases}"
)

print(
    f"Human reviewed:        {reviewed}"
)

print(
    f"Approved:              {approved}"
)

print(
    f"Corrected:             {corrected}"
)

print(
    f"Rejected:              {rejected}"
)

print(
    f"Approval rate:         {approval_rate:.2f}%"
)

print(
    f"Correction rate:       {correction_rate:.2f}%"
)

print(
    f"Rejection rate:        {rejection_rate:.2f}%"
)

print(
    f"Responsible AI logs:   {responsible_cases}"
)

print()

print("=" * 70)
print("Evaluation finished.")
print("=" * 70)