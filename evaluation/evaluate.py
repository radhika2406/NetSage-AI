import os
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
# CHECK REQUIRED FILES
# ============================================================

required_files = {
    "Cases": CASES_FILE,
    "Checker": CHECKER_FILE,
    "AI Results": AI_FILE,
    "Human Reviews": HUMAN_FILE,
    "Responsible AI Log": RESPONSIBLE_FILE
}


for name, file_path in required_files.items():

    if not os.path.exists(file_path):

        print()
        print(
            f"ERROR: {name} file not found:"
        )

        print(file_path)

        raise SystemExit(1)


# ============================================================
# LOAD DATA
# ============================================================

cases = pd.read_csv(
    CASES_FILE,
    encoding="utf-8-sig"
)

checker = pd.read_csv(
    CHECKER_FILE,
    encoding="utf-8-sig"
)

ai = pd.read_csv(
    AI_FILE,
    encoding="utf-8-sig"
)

human = pd.read_csv(
    HUMAN_FILE,
    encoding="utf-8-sig"
)

responsible = pd.read_csv(
    RESPONSIBLE_FILE,
    encoding="utf-8-sig"
)


# ============================================================
# BASIC COUNTS
# ============================================================

total_cases = len(cases)

checker_cases = (
    checker["ID"]
    .dropna()
    .astype(str)
    .nunique()
)

ai_cases = (
    ai["ID"]
    .dropna()
    .astype(str)
    .nunique()
)

human_cases = (
    human["ID"]
    .dropna()
    .astype(str)
    .nunique()
)

responsible_cases = (
    responsible["ID"]
    .dropna()
    .astype(str)
    .nunique()
)


# ============================================================
# HUMAN REVIEW COUNTS
# ============================================================

approved = len(
    human[
        human["Reviewer_Decision"]
        .astype(str)
        .str.strip()
        == "Approved"
    ]
)

corrected = len(
    human[
        human["Reviewer_Decision"]
        .astype(str)
        .str.strip()
        == "Corrected"
    ]
)

rejected = len(
    human[
        human["Reviewer_Decision"]
        .astype(str)
        .str.strip()
        == "Rejected"
    ]
)


reviewed = approved + corrected + rejected


# ============================================================
# CALCULATE RATES
# ============================================================

if reviewed > 0:

    approval_rate = (
        approved / reviewed
    ) * 100

    correction_rate = (
        corrected / reviewed
    ) * 100

    rejection_rate = (
        rejected / reviewed
    ) * 100

else:

    approval_rate = 0
    correction_rate = 0
    rejection_rate = 0


# ============================================================
# COMPLETION RATES
# ============================================================

if total_cases > 0:

    checker_completion = (
        checker_cases / total_cases
    ) * 100

    ai_completion = (
        ai_cases / total_cases
    ) * 100

    human_completion = (
        human_cases / total_cases
    ) * 100

    responsible_completion = (
        responsible_cases / total_cases
    ) * 100

else:

    checker_completion = 0
    ai_completion = 0
    human_completion = 0
    responsible_completion = 0


# ============================================================
# DISPLAY DATA COMPLETENESS
# ============================================================

print()

print("-" * 70)
print("DATA PIPELINE")
print("-" * 70)

print(
    f"Total cases:              {total_cases}"
)

print(
    f"Checker cases:            {checker_cases}"
)

print(
    f"AI diagnosis cases:       {ai_cases}"
)

print(
    f"Human review cases:        {human_cases}"
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
# HUMAN REVIEW EVALUATION
# ============================================================

print()

print("-" * 70)
print("HUMAN REVIEW RESULTS")
print("-" * 70)

print(
    f"Reviewed:     {reviewed}"
)

print(
    f"Approved:     {approved}"
)

print(
    f"Corrected:    {corrected}"
)

print(
    f"Rejected:     {rejected}"
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
# CASE COVERAGE CHECK
# ============================================================

case_ids = set(
    cases["ID"]
    .astype(str)
    .str.strip()
)

checker_ids = set(
    checker["ID"]
    .astype(str)
    .str.strip()
)

ai_ids = set(
    ai["ID"]
    .astype(str)
    .str.strip()
)

human_ids = set(
    human["ID"]
    .astype(str)
    .str.strip()
)

responsible_ids = set(
    responsible["ID"]
    .astype(str)
    .str.strip()
)


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


# ============================================================
# COVERAGE REPORT
# ============================================================

print()

print("-" * 70)
print("CASE COVERAGE")
print("-" * 70)


if not missing_checker:

    print(
        "Checker:        ALL CASES COVERED"
    )

else:

    print(
        "Checker missing:"
    )

    print(
        sorted(missing_checker)
    )


if not missing_ai:

    print(
        "AI Diagnosis:   ALL CASES COVERED"
    )

else:

    print(
        "AI missing:"
    )

    print(
        sorted(missing_ai)
    )


if not missing_human:

    print(
        "Human Review:   ALL CASES COVERED"
    )

else:

    print(
        "Human review missing:"
    )

    print(
        sorted(missing_human)
    )


if not missing_responsible:

    print(
        "Responsible AI: ALL CASES COVERED"
    )

else:

    print(
        "Responsible AI missing:"
    )

    print(
        sorted(missing_responsible)
    )


# ============================================================
# RESPONSIBLE AI CHECKS
# ============================================================

print()

print("-" * 70)
print("RESPONSIBLE AI CHECKS")
print("-" * 70)


if "Human_Decision" in responsible.columns:

    human_decisions = (
        responsible["Human_Decision"]
        .astype(str)
        .str.strip()
    )

    logged_approved = (
        human_decisions == "Approved"
    ).sum()

    logged_corrected = (
        human_decisions == "Corrected"
    ).sum()

    logged_rejected = (
        human_decisions == "Rejected"
    ).sum()

    print(
        f"Approved decisions logged:  "
        f"{logged_approved}"
    )

    print(
        f"Corrected decisions logged: "
        f"{logged_corrected}"
    )

    print(
        f"Rejected decisions logged:  "
        f"{logged_rejected}"
    )


# ============================================================
# FINAL STATUS
# ============================================================

print()

print("=" * 70)
print("FINAL EVALUATION")
print("=" * 70)

if (
    total_cases == 30
    and checker_cases == 30
    and ai_cases == 30
    and human_cases == 30
    and responsible_cases == 30
):

    print()
    print(
        "STATUS: COMPLETE"
    )

    print()
    print(
        "All 30 cases passed through:"
    )

    print(
        "1. Rule-based checking"
    )

    print(
        "2. AI diagnosis"
    )

    print(
        "3. Human review"
    )

    print(
        "4. Responsible AI logging"
    )

else:

    print()
    print(
        "STATUS: INCOMPLETE"
    )

    print(
        "Some cases are missing from "
        "one or more pipeline stages."
    )


print()
print("=" * 70)
print("Evaluation finished.")
print("=" * 70)