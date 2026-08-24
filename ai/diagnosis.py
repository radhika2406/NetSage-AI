import os
import time
import pandas as pd

from groq import Groq


# ============================================================
# NETSAGE AI - GROQ DIAGNOSIS
# ============================================================

print("=" * 70)
print("NETSAGE AI - GROQ AI DIAGNOSIS")
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

AI_RESULTS_FILE = os.path.join(
    DATA_DIR,
    "ai_results.csv"
)

PROMPT_FILE = os.path.join(
    BASE_DIR,
    "prompts",
    "diagnose_prompt.md"
)


# ============================================================
# CHECK API KEY
# ============================================================

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:

    print()
    print("=" * 70)
    print("ERROR: GROQ_API_KEY WAS NOT FOUND")
    print("=" * 70)
    print()
    print("Set the API key before running this program.")
    print()
    print('Windows CMD:')
    print('set "GROQ_API_KEY=YOUR_GROQ_API_KEY"')
    print()
    print('Windows PowerShell:')
    print('$env:GROQ_API_KEY="YOUR_GROQ_API_KEY"')
    print()

    raise SystemExit(1)


# ============================================================
# CREATE GROQ CLIENT
# ============================================================

client = Groq(
    api_key=API_KEY
)


# ============================================================
# MODEL
# ============================================================

MODEL = "openai/gpt-oss-20b"


# ============================================================
# CHECK REQUIRED FILES
# ============================================================

required_files = {
    "cases.csv": CASES_FILE,
    "checker_results.csv": CHECKER_FILE,
    "diagnose_prompt.md": PROMPT_FILE
}


for name, path in required_files.items():

    if not os.path.exists(path):

        print()
        print(
            f"ERROR: {name} not found."
        )

        print(
            path
        )

        raise SystemExit(1)


# ============================================================
# LOAD CASES
# ============================================================

try:

    cases = pd.read_csv(
        CASES_FILE,
        encoding="utf-8-sig"
    )

except Exception as error:

    print(
        f"ERROR loading cases.csv: {error}"
    )

    raise SystemExit(1)


# ============================================================
# LOAD CHECKER RESULTS
# ============================================================

try:

    checker_results = pd.read_csv(
        CHECKER_FILE,
        encoding="utf-8-sig"
    )

except Exception as error:

    print(
        f"ERROR loading checker_results.csv: {error}"
    )

    raise SystemExit(1)


# ============================================================
# VALIDATE REQUIRED COLUMNS
# ============================================================

required_case_columns = [
    "ID",
    "Symptom",
    "Topology / Devices",
    "Show Output / Evidence"
]

missing_case_columns = [
    column
    for column in required_case_columns
    if column not in cases.columns
]

if missing_case_columns:

    print()
    print(
        "ERROR: cases.csv is missing required columns:"
    )

    print(
        missing_case_columns
    )

    raise SystemExit(1)


if "ID" not in checker_results.columns:

    print()
    print(
        "ERROR: checker_results.csv must contain an ID column."
    )

    raise SystemExit(1)


# ============================================================
# LOAD PROMPT
# ============================================================

try:

    with open(
        PROMPT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        prompt_template = file.read()

except Exception as error:

    print(
        f"ERROR loading diagnosis prompt: {error}"
    )

    raise SystemExit(1)


print()
print(
    f"Cases loaded: {len(cases)}"
)

print(
    f"Checker results loaded: {len(checker_results)}"
)

print(
    "Prompt loaded successfully."
)


# ============================================================
# LOAD EXISTING AI RESULTS
# ============================================================

if os.path.exists(AI_RESULTS_FILE):

    try:

        ai_results = pd.read_csv(
            AI_RESULTS_FILE,
            encoding="utf-8-sig"
        )

    except Exception:

        print()
        print(
            "WARNING: Existing ai_results.csv "
            "could not be read."
        )

        print(
            "A new result file will be created."
        )

        ai_results = pd.DataFrame(
            columns=[
                "ID",
                "AI_Diagnosis"
            ]
        )

else:

    ai_results = pd.DataFrame(
        columns=[
            "ID",
            "AI_Diagnosis"
        ]
    )


# ============================================================
# ENSURE REQUIRED AI COLUMNS
# ============================================================

if "ID" not in ai_results.columns:

    ai_results["ID"] = pd.Series(
        dtype="object"
    )


if "AI_Diagnosis" not in ai_results.columns:

    ai_results["AI_Diagnosis"] = pd.Series(
        dtype="object"
    )


# ============================================================
# NORMALIZE EXISTING IDs
# ============================================================

if len(ai_results) > 0:

    ai_results["ID"] = (
        ai_results["ID"]
        .astype(str)
        .str.strip()
    )


# ============================================================
# REMOVE DUPLICATE EXISTING RESULTS
# ============================================================

if len(ai_results) > 0:

    ai_results = (
        ai_results
        .drop_duplicates(
            subset=["ID"],
            keep="last"
        )
        .reset_index(drop=True)
    )


# ============================================================
# FIND EXISTING CASES
# ============================================================

existing_ids = set(
    ai_results["ID"]
    .dropna()
    .astype(str)
    .str.strip()
)


print()
print(
    f"Existing AI results: {len(existing_ids)}"
)


if existing_ids:

    print(
        "Already completed:"
    )

    print(
        sorted(existing_ids)
    )


# ============================================================
# HELPER FUNCTION
# ============================================================

def safe_text(value):
    """
    Convert CSV values into safe text for the prompt.
    """

    if pd.isna(value):

        return "Not provided."

    return str(value).strip()


# ============================================================
# PROCESS CASES
# ============================================================

for index, case in cases.iterrows():

    case_id = safe_text(
        case["ID"]
    )


    # --------------------------------------------------------
    # SKIP EMPTY CASE ID
    # --------------------------------------------------------

    if not case_id:

        print()
        print(
            f"[SKIP] Row {index + 1} has no case ID."
        )

        continue


    # --------------------------------------------------------
    # SKIP CASES ALREADY COMPLETED
    # --------------------------------------------------------

    if case_id in existing_ids:

        print()
        print(
            f"[SKIP] {case_id} already exists."
        )

        continue


    print()
    print("=" * 70)

    print(
        f"[{index + 1}/{len(cases)}] "
        f"Diagnosing {case_id}"
    )

    print("=" * 70)


    # ========================================================
    # GET RULE CHECKER FINDINGS
    # ========================================================

    checker_rows = checker_results[
        checker_results["ID"]
        .astype(str)
        .str.strip()
        == case_id
    ]


    if not checker_rows.empty:

        checker_parts = []

        for _, row in checker_rows.iterrows():

            rule = safe_text(
                row.get(
                    "Rule",
                    ""
                )
            )

            status = safe_text(
                row.get(
                    "Status",
                    ""
                )
            )

            finding = safe_text(
                row.get(
                    "Finding",
                    ""
                )
            )

            checker_parts.append(
                f"Rule: {rule}\n"
                f"Status: {status}\n"
                f"Finding: {finding}"
            )


        checker_text = "\n\n".join(
            checker_parts
        )

    else:

        checker_text = (
            "No deterministic rule checker "
            "finding was available for this case."
        )


    # ========================================================
    # BUILD PROMPT
    # ========================================================

    prompt = prompt_template


    # --------------------------------------------------------
    # INSERT CASE INFORMATION
    # --------------------------------------------------------

    prompt = prompt.replace(
        "{{case_id}}",
        case_id
    )

    prompt = prompt.replace(
        "{{symptom}}",
        safe_text(
            case["Symptom"]
        )
    )

    prompt = prompt.replace(
        "{{topology_note}}",
        safe_text(
            case["Topology / Devices"]
        )
    )

    prompt = prompt.replace(
        "{{show_output}}",
        safe_text(
            case["Show Output / Evidence"]
        )
    )


    # ========================================================
    # ADD CHECKER FINDINGS AS SUPPORTING EVIDENCE
    # ========================================================

    prompt += """

---

# DETERMINISTIC RULE CHECKER FINDINGS

The following findings were produced by the deterministic
rule-checking stage.

Treat these findings as additional evidence.

Do not automatically accept them as the final diagnosis.
Evaluate them against the actual symptom, topology, and
supplied command output.

"""

    prompt += checker_text


    # ========================================================
    # FINAL AI INSTRUCTION
    # ========================================================

    prompt += """

---

# FINAL INSTRUCTION

Now diagnose this case.

Use only the information supplied above.

Do not use any expected answer or hidden reference answer.

Do not invent network information.

If the evidence is insufficient to identify a root cause,
write exactly:

Insufficient evidence

in the Likely Fault field and explain what additional
evidence is required.

Return the diagnosis using the required response structure
defined in the prompt.
"""


    # ========================================================
    # CALL GROQ
    # ========================================================

    try:

        response = client.chat.completions.create(

            model=MODEL,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are NetSage AI, a Cisco-style "
                        "network troubleshooting assistant. "
                        "Your diagnosis must be evidence-based. "
                        "Never invent network information. "
                        "Do not use expected answers or "
                        "hidden reference fields."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.2,

            max_tokens=1800
        )


        # ====================================================
        # EXTRACT RESPONSE
        # ====================================================

        diagnosis = ""


        try:

            diagnosis = (
                response
                .choices[0]
                .message
                .content
            )

        except Exception:

            diagnosis = ""


        if diagnosis is None:

            diagnosis = ""


        diagnosis = str(
            diagnosis
        ).strip()


        # ====================================================
        # VALIDATE RESPONSE
        # ====================================================

        if not diagnosis:

            print()
            print(
                f"FAILED: {case_id}"
            )

            print(
                "Groq returned an empty diagnosis."
            )

            continue


        # ====================================================
        # SAVE RESULT
        # ====================================================

        new_result = pd.DataFrame(
            [
                {
                    "ID": case_id,
                    "AI_Diagnosis": diagnosis
                }
            ]
        )


        ai_results = pd.concat(
            [
                ai_results,
                new_result
            ],
            ignore_index=True
        )


        # ----------------------------------------------------
        # Remove accidental duplicates
        # ----------------------------------------------------

        ai_results = (
            ai_results
            .drop_duplicates(
                subset=["ID"],
                keep="last"
            )
            .reset_index(drop=True)
        )


        # ====================================================
        # SAVE AFTER EVERY CASE
        # ====================================================

        ai_results.to_csv(
            AI_RESULTS_FILE,
            index=False,
            encoding="utf-8-sig"
        )


        existing_ids.add(
            case_id
        )


        print()
        print(
            f"SUCCESS: {case_id}"
        )

        print(
            "AI diagnosis saved."
        )

        print(
            f"Results file: {AI_RESULTS_FILE}"
        )


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as error:

        error_message = str(
            error
        )


        print()
        print(
            f"FAILED: {case_id}"
        )

        print(
            f"Reason: {error_message}"
        )


        # ----------------------------------------------------
        # API RATE LIMIT / QUOTA
        # ----------------------------------------------------

        if (
            "429" in error_message
            or
            "rate" in error_message.lower()
            or
            "limit" in error_message.lower()
            or
            "quota" in error_message.lower()
        ):

            print()
            print("=" * 70)
            print("GROQ API LIMIT DETECTED")
            print("=" * 70)

            print()
            print(
                "Stopping safely."
            )

            print(
                "Already completed cases are saved."
            )

            print()

            break


        # ----------------------------------------------------
        # MODEL ERROR
        # ----------------------------------------------------

        if (
            "model" in error_message.lower()
            and
            (
                "not found" in error_message.lower()
                or
                "does not exist" in error_message.lower()
                or
                "invalid" in error_message.lower()
            )
        ):

            print()
            print(
                "The selected Groq model may be unavailable."
            )

            print(
                f"Current model: {MODEL}"
            )

            print()

            break


        # ----------------------------------------------------
        # OTHER ERROR
        # ----------------------------------------------------

        print(
            "Skipping this case and continuing."
        )

        time.sleep(2)


    # ========================================================
    # SMALL DELAY
    # ========================================================

    time.sleep(1)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 70)
print("NETSAGE AI - GROQ DIAGNOSIS COMPLETE")
print("=" * 70)

print()

print(
    f"Total cases: {len(cases)}"
)

print(
    f"AI results available: {len(ai_results)}"
)

remaining_cases = max(
    0,
    len(cases) - len(ai_results)
)

print(
    f"Remaining cases: {remaining_cases}"
)

print()

print(
    "Results file:"
)

print(
    AI_RESULTS_FILE
)

print()

if remaining_cases == 0:

    print(
        "STATUS: ALL CASES PROCESSED"
    )

else:

    print(
        "STATUS: SOME CASES REMAIN"
    )

print()

print("=" * 70)