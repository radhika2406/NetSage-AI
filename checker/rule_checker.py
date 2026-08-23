import csv
import os
import re
import ipaddress


# ============================================================
# FILE LOCATION
# ============================================================

CSV_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "cases.csv"
)

RESULT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "checker_results.csv"
)

# ============================================================
# RULE CHECK FUNCTIONS
# ============================================================

def check_gateway(evidence):
    """
    Detect gateway mismatch from evidence.
    Example:
    IP = 192.168.10.10/24
    gateway = 192.168.20.1
    """

    ip_match = re.search(
        r"IP\s*=\s*(\d+\.\d+\.\d+\.\d+)/(\d+)",
        evidence,
        re.IGNORECASE
    )

    gateway_match = re.search(
        r"gateway\s*=\s*(\d+\.\d+\.\d+\.\d+)",
        evidence,
        re.IGNORECASE
    )

    if not ip_match or not gateway_match:
        return None

    ip_address = ip_match.group(1)
    prefix = int(ip_match.group(2))
    gateway = gateway_match.group(1)

    host = ipaddress.ip_interface(
        f"{ip_address}/{prefix}"
    )

    gateway_ip = ipaddress.ip_address(gateway)

    if gateway_ip not in host.network:

        return {
            "rule": "GATEWAY_MISMATCH",
            "status": "FAIL",
            "finding": (
                f"Gateway {gateway} is outside "
                f"host network {host.network}"
            )
        }

    return {
        "rule": "GATEWAY_CHECK",
        "status": "PASS",
        "finding": "Gateway belongs to the correct network"
    }


# ------------------------------------------------------------
# Missing Route
# ------------------------------------------------------------

def check_missing_route(evidence):

    text = evidence.lower()

    if (
        "no route to 192.168.40.0/24" in text
        or "192.168.40.0/24 absent" in text
        or "no route" in text
        or ("route" in text and "absent" in text)
    ):

        return {
            "rule": "MISSING_ROUTE",
            "status": "FAIL",
            "finding": (
                "Route to 192.168.40.0/24 "
                "is missing"
            )
        }

    return None


# ------------------------------------------------------------
# Wrong Next Hop
# ------------------------------------------------------------

def check_next_hop(evidence):

    text = evidence.lower()

    if (
        "wrong next hop" in text
        or "wrong next-hop" in text
        or "10.0.0.9" in text
    ):

        return {
            "rule": "WRONG_NEXT_HOP",
            "status": "FAIL",
            "finding": (
                "Static route uses incorrect "
                "next-hop address"
            )
        }

    return None


# ------------------------------------------------------------
# VLAN
# ------------------------------------------------------------

def check_vlan(evidence):

    text = evidence.lower()

    if "show vlan brief" not in text:
        return None

    # Missing VLAN
    if "vlan 20 absent" in text:

        return {
            "rule": "MISSING_VLAN",
            "status": "FAIL",
            "finding": "Required VLAN 20 is missing"
        }

    # Wrong VLAN assignment
    if (
        "fa0/1 vlan 10" in text
        and "fa0/2 vlan 20" in text
    ):

        return {
            "rule": "WRONG_VLAN",
            "status": "FAIL",
            "finding": (
                "PC2 switch port is assigned "
                "to VLAN 20 instead of VLAN 10"
            )
        }

    # Wireless VLAN
    if "ap port assigned to vlan 20" in text:

        return {
            "rule": "WIRELESS_VLAN",
            "status": "FAIL",
            "finding": (
                "Access point port is assigned "
                "to the wrong VLAN"
            )
        }

    return None


# ------------------------------------------------------------
# Trunk
# ------------------------------------------------------------

def check_trunk(evidence):

    text = evidence.lower()

    if (
        "show interfaces trunk" in text
        and "vlan 30" in text
        and "not in allowed list" in text
    ):

        return {
            "rule": "TRUNK_VLAN",
            "status": "FAIL",
            "finding": (
                "VLAN 30 is not allowed "
                "on the trunk"
            )
        }

    return None


# ------------------------------------------------------------
# DHCP
# ------------------------------------------------------------

def check_dhcp(evidence):

    text = evidence.lower()

    if (
        "no pool for 192.168.10.0/24" in text
        or "no pool exists for 192.168.10.0/24" in text
    ):

        return {
            "rule": "DHCP_POOL",
            "status": "FAIL",
            "finding": (
                "DHCP pool for "
                "192.168.10.0/24 is missing"
            )
        }

    if "no ip helper-address" in text:

        return {
            "rule": "DHCP_RELAY",
            "status": "FAIL",
            "finding": (
                "DHCP relay/helper address "
                "is missing"
            )
        }

    if "all addresses leased" in text:

        return {
            "rule": "DHCP_POOL_EXHAUSTED",
            "status": "FAIL",
            "finding": (
                "DHCP pool has no available "
                "addresses"
            )
        }

    if "no lease for wireless subnet" in text:

        return {
            "rule": "WIRELESS_DHCP",
            "status": "FAIL",
            "finding": (
                "No DHCP lease exists "
                "for the wireless subnet"
            )
        }

    return None


# ------------------------------------------------------------
# DNS
# ------------------------------------------------------------

def check_dns(evidence):

    text = evidence.lower()

    if (
        "dns request timed out" in text
        or "nslookup" in text and "timeout" in text
    ):

        return {
            "rule": "DNS_FAILURE",
            "status": "FAIL",
            "finding": (
                "DNS request is timing out"
            )
        }

    if (
        "ping 192.168.30.10" in text
        and "nslookup" in text
        and "timeout" in text
    ):

        return {
            "rule": "DNS_SERVER",
            "status": "FAIL",
            "finding": (
                "IP connectivity works but "
                "DNS resolution fails"
            )
        }

    return None


# ------------------------------------------------------------
# ACL
# ------------------------------------------------------------

def check_acl(evidence):

    text = evidence.lower()

    if (
        "deny from 192.168.10.0/24" in text
        and "192.168.30.0/24" in text
    ):

        return {
            "rule": "ACL_BLOCK",
            "status": "FAIL",
            "finding": (
                "ACL denies traffic from "
                "VLAN 10 to VLAN 30"
            )
        }

    if (
        "icmp denied" in text
        and "tcp/80 permitted" in text
    ):

        return {
            "rule": "ACL_ICMP",
            "status": "FAIL",
            "finding": (
                "ACL blocks ICMP traffic"
            )
        }

    if "tcp port 80" in text and "denies" in text:

        return {
            "rule": "ACL_HTTP",
            "status": "FAIL",
            "finding": (
                "ACL blocks HTTP traffic "
                "on TCP port 80"
            )
        }

    if (
        "acl applied outbound instead of inbound"
        in text
    ):

        return {
            "rule": "ACL_DIRECTION",
            "status": "FAIL",
            "finding": (
                "ACL is applied in the "
                "wrong direction"
            )
        }

    if "no guest-to-lan deny rule" in text:

        return {
            "rule": "GUEST_ISOLATION",
            "status": "FAIL",
            "finding": (
                "Guest-to-LAN isolation ACL "
                "is missing"
            )
        }

    return None


# ------------------------------------------------------------
# NAT
# ------------------------------------------------------------

def check_nat(evidence):

    text = evidence.lower()

    if (
        "empty" in text
        and "no nat configuration" in text
    ):

        return {
            "rule": "NAT_MISSING",
            "status": "FAIL",
            "finding": (
                "NAT/PAT configuration is missing"
            )
        }

    if (
        "nat acl doesn't match" in text
        or "nat acl does not match" in text
    ):

        return {
            "rule": "NAT_ACL",
            "status": "FAIL",
            "finding": (
                "NAT ACL does not match "
                "the internal network"
            )
        }

    if (
        "nat acl permits vlan 10"
        in text
        and "not 192.168.20.0/24" in text
    ):

        return {
            "rule": "NAT_INCOMPLETE",
            "status": "FAIL",
            "finding": (
                "NAT ACL does not include "
                "VLAN 20"
            )
        }

    if "no static translation" in text:

        return {
            "rule": "STATIC_NAT",
            "status": "FAIL",
            "finding": (
                "Static NAT translation "
                "for SRV1 is missing"
            )
        }

    return None


# ------------------------------------------------------------
# Interface
# ------------------------------------------------------------

def check_interface(evidence):

    text = evidence.lower()

    if "administratively down" in text:

        return {
            "rule": "INTERFACE_SHUTDOWN",
            "status": "FAIL",
            "finding": (
                "Interface is administratively down"
            )
        }

    if "up/down" in text:

        return {
            "rule": "INTERFACE_LINK",
            "status": "FAIL",
            "finding": (
                "Interface is up but line "
                "protocol is down"
            )
        }

    return None


# ------------------------------------------------------------
# Duplicate IP
# ------------------------------------------------------------

def check_duplicate_ip(evidence):

    text = evidence.lower()

    if (
        "same ip associated with different mac"
        in text
        or "same ip associated with different macs"
        in text
    ):

        return {
            "rule": "DUPLICATE_IP",
            "status": "FAIL",
            "finding": (
                "Same IP address is associated "
                "with multiple MAC addresses"
            )
        }

    return None


# ============================================================
# CHECK ONE CASE
# ============================================================

def check_case(case):

    evidence = case["Show Output / Evidence"]

    findings = []

    # Run every rule
    rules = [
        check_gateway,
        check_missing_route,
        check_next_hop,
        check_vlan,
        check_trunk,
        check_dhcp,
        check_dns,
        check_acl,
        check_nat,
        check_interface,
        check_duplicate_ip
    ]

    # Gateway needs special arguments
    gateway_result = check_gateway(evidence)

    if gateway_result:
        findings.append(gateway_result)

    # Other rules use evidence only
    for rule in rules[1:]:

        result = rule(evidence)

        if result:
            findings.append(result)

    return findings


# ============================================================
# LOAD CSV
# ============================================================

def load_cases():

    with open(
        CSV_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        return list(reader)

def save_results(results):

    with open(
        RESULT_FILE,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "ID",
            "Rule",
            "Status",
            "Finding"
        ])

        for result in results:

            writer.writerow([
                result["ID"],
                result["rule"],
                result["status"],
                result["finding"]
            ])

# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("=" * 70)
    print("NETSAGE AI - CISCO NETWORK RULE CHECKER")
    print("=" * 70)

    cases = load_cases()

    print(f"Total cases loaded: {len(cases)}")
    print()

    all_results = []

    for case in cases:

        case_id = case["ID"]
        expected = case["Expected Fault"]

        print(f"CASE {case_id}")
        print("-" * 70)

        print(f"Expected Fault: {expected}")

        findings = check_case(case)

        if findings:

            for finding in findings:

                print(
                    f"[{finding['status']}] "
                    f"{finding['rule']}"
                )

                print(
                    f"Finding: "
                    f"{finding['finding']}"
                )

                all_results.append({
                    "ID": case_id,
                    "rule": finding["rule"],
                    "status": finding["status"],
                    "finding": finding["finding"]
                })

        else:

            print(
                "[INFO] No deterministic rule "
                "matched this case."
            )

            all_results.append({
                "ID": case_id,
                "rule": "NONE",
                "status": "INFO",
                "finding": "No rule matched"
            })

        print()

    # Save all results
    save_results(all_results)

    print("=" * 70)
    print("CHECK COMPLETE")
    print(f"Results saved to: {RESULT_FILE}")
    print("=" * 70)

# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()