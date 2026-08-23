import csv
import os


CSV_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "cases.csv"
)


def check_case(case):

    findings = []

    case_id = case["ID"]
    symptom = case["Symptom"].lower()
    evidence = case["Show Output / Evidence"].lower()
    expected_fault = case["Expected Fault"].lower()
    concept = case["Concept"].lower()

    # 1. Missing Route
    if "route" in expected_fault and (
        "no route" in evidence or
        "absent" in evidence
    ):
        findings.append(
            "Possible missing route detected."
        )

    # 2. VLAN
    if "vlan" in expected_fault:
        findings.append(
            "Possible VLAN configuration problem detected."
        )

    # 3. DHCP
    if "dhcp" in expected_fault:
        findings.append(
            "Possible DHCP configuration problem detected."
        )

    # 4. DNS
    if "dns" in expected_fault:
        findings.append(
            "Possible DNS problem detected."
        )

    # 5. ACL
    if "acl" in expected_fault:
        findings.append(
            "Possible ACL problem detected."
        )

    # 6. NAT
    if "nat" in expected_fault:
        findings.append(
            "Possible NAT problem detected."
        )

    # 7. Gateway
    if "gateway" in expected_fault:
        findings.append(
            "Possible gateway problem detected."
        )

    # 8. Interface
    if (
        "interface" in expected_fault
        or "administratively down" in evidence
        or "up/down" in evidence
    ):
        findings.append(
            "Possible interface problem detected."
        )

    return {
        "ID": case_id,
        "findings": findings
    }


def load_cases():

    with open(
        CSV_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        return list(reader)


def main():

    print("=" * 60)
    print("NetSage AI - Rule Checker")
    print("=" * 60)

    cases = load_cases()

    print(f"Loaded cases: {len(cases)}")
    print()

    for case in cases:

        result = check_case(case)

        print(f"Case: {result['ID']}")

        if result["findings"]:

            for finding in result["findings"]:
                print("  ❌", finding)

        else:
            print("  ✓ No finding")

        print("-" * 60)


if __name__ == "__main__":
    main()