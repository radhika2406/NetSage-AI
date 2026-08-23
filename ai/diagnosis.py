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
    print("Run this first:")
    print()
    print('set "GROQ_API_KEY=YOUR_GROQ_API_KEY"')
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
# CHECK FILES
# ============================================================

if not os.path.exists(CASES_FILE):

    print("ERROR: cases.csv not found.")
    raise SystemExit(1)


if not os.path.exists(CHECKER_FILE):

    print("ERROR: checker_results.csv not found.")
    raise SystemExit(1)


if not os.path.exists(PROMPT_FILE):

    print("ERROR: diagnose_prompt.md not found.")
    raise SystemExit(1)


# ============================================================
# LOAD CASES
# ============================================================

cases = pd.read_csv(
    CASES_FILE,
    encoding="utf-8-sig"
)


# ============================================================
# LOAD CHECKER RESULTS
# ============================================================

checker_results = pd.read_csv(
    CHECKER_FILE,
    encoding="utf-8-sig"
)


# ============================================================
# LOAD PROMPT
# ============================================================

with open(
    PROMPT_FILE,
    "r",
    encoding="utf-8"
) as file:

    prompt_template = file.read()


print()
print(
    f"Cases loaded: {len(cases)}"
)

print(
    f"Checker results loaded: "
    f"{len(checker_results)}"
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

        print(
            "Existing ai_results.csv could not be read."
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
# FIND EXISTING CASES
# ============================================================

if (
    "ID" in ai_results.columns
    and len(ai_results) > 0
):

    existing_ids = set(
        ai_results["ID"]
        .dropna()
        .astype(str)
        .str.strip()
    )

else:

    existing_ids = set()


print()
print(
    f"Existing AI results: "
    f"{len(existing_ids)}"
)

if existing_ids:

    print(
        "Already completed:"
    )

    print(
        sorted(existing_ids)
    )


# ============================================================
# PROCESS CASES
# ============================================================

for index, case in cases.iterrows():

    case_id = str(
        case["ID"]
    ).strip()


    # --------------------------------------------------------
    # SKIP CASES ALREADY COMPLETED
    # --------------------------------------------------------

    if case_id in existing_ids:

        print()
        print(
            f"[SKIP] {case_id} "
            f"already exists."
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


    if len(checker_rows) > 0:

        checker_parts = []

        for _, row in checker_rows.iterrows():

            checker_parts.append(
                f"Rule: {row.get('Rule', '')}\n"
                f"Status: {row.get('Status', '')}\n"
                f"Finding: {row.get('Finding', '')}"
            )

        checker_text = "\n\n".join(
            checker_parts
        )

    else:

        checker_text = (
            "No deterministic rule checker "
            "finding was available."
        )


    # ========================================================
    # BUILD PROMPT
    # ========================================================

    prompt = prompt_template

    prompt = prompt.replace(
        "{{case_id}}",
        case_id
    )

    prompt = prompt.replace(
        "{{symptom}}",
        str(case["Symptom"])
    )

    prompt = prompt.replace(
        "{{topology_note}}",
        str(case["Topology / Devices"])
    )

    prompt = prompt.replace(
        "{{show_output}}",
        str(case["Show Output / Evidence"])
    )


    # --------------------------------------------------------
    # ADD RULE CHECKER INFORMATION
    # --------------------------------------------------------

    prompt += """

============================================================
DETERMINISTIC RULE CHECKER FINDINGS
============================================================

"""

    prompt += checker_text


    # --------------------------------------------------------
    # FINAL TASK
    # --------------------------------------------------------

    prompt += """

============================================================
FINAL TASK
============================================================

Analyze the case using the supplied evidence.

Use:

1. Symptom
2. Topology / Devices
3. Show Command Output / Evidence
4. Deterministic Rule Checker Findings

Do NOT invent:

- IP addresses
- VLANs
- routes
- ACL entries
- interfaces
- command output
- configurations

Do NOT blindly accept the rule checker.

If the evidence is insufficient, say:

Insufficient evidence

Return exactly these sections:

Root Cause:
<most likely root cause>

Confidence:
<0-100%>

OSI Layer:
<Layer 1 / Layer 2 / Layer 3 / Layer 4 / Layer 7>

Concept:
<VLAN / Routing / DHCP / DNS / ACL / NAT /
Gateway / OSPF / Wireless / Interface / etc.>

Evidence:
- <important evidence>

Next Command:
<Cisco or endpoint command>

Why This Command:
<why the command will confirm the diagnosis>

Fix Steps:
1. <step 1>
2. <step 2>

Verification:
<how to verify the fix>

Human Review:
Pending
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
                        "Reason from evidence and do not "
                        "invent network information."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.2,

            max_tokens=1500
        )


        # ----------------------------------------------------
        # GET RESPONSE
        # ----------------------------------------------------

        diagnosis = (
            response
            .choices[0]
            .message
            .content
        )


        if not diagnosis:

            diagnosis = (
                "No diagnosis returned by Groq."
            )


        diagnosis = diagnosis.strip()


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
        # SAVE AFTER EVERY CASE
        # ----------------------------------------------------

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
            f"Saved result to:"
        )

        print(
            AI_RESULTS_FILE
        )


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as error:

        error_message = str(error)


        print()
        print(
            f"FAILED: {case_id}"
        )

        print(
            f"Reason: {error_message}"
        )


        # ----------------------------------------------------
        # API LIMIT
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
            "not found" in error_message.lower()
        ):

            print()
            print(
                "The selected Groq model is unavailable."
            )

            print(
                f"Current model: {MODEL}"
            )

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
    f"Total cases: "
    f"{len(cases)}"
)

print(
    f"AI results available: "
    f"{len(ai_results)}"
)

print(
    f"Remaining cases: "
    f"{len(cases) - len(ai_results)}"
)

print()

print(
    "Results file:"
)

print(
    AI_RESULTS_FILE
)

print()

print("=" * 70)