import csv
import os
import re
import ipaddress


# ============================================================
# NETSAGE AI - CISCO NETWORK RULE CHECKER
# ============================================================

print("=" * 70)
print("NETSAGE AI - CISCO NETWORK RULE CHECKER")
print("=" * 70)


# ============================================================
# FILE PATHS
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

CSV_FILE = os.path.join(
    DATA_DIR,
    "cases.csv"
)

RESULT_FILE = os.path.join(
    DATA_DIR,
    "checker_results.csv"
)


# ============================================================
# RULE: DEFAULT GATEWAY
# ============================================================

def check_gateway(evidence):

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

    try:

        host = ipaddress.ip_interface(
            f"{ip_address}/{prefix}"
        )

        gateway_ip = ipaddress.ip_address(
            gateway
        )

    except ValueError:

        return {
            "rule": "INVALID_IP_CONFIGURATION",
            "status": "FAIL",
            "finding": (
                "Invalid IP address or prefix "
                "detected in supplied evidence"
            )
        }

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
        "finding": (
            "Gateway belongs to the host network"
        )
    }


# ============================================================
# RULE: MISSING ROUTE
# ============================================================

def check_missing_route(evidence):

    text = evidence.lower()

    patterns = [
        "no route to 192.168.40.0/24",
        "192.168.40.0/24 absent",
        "no route",
        "route absent"
    ]

    if any(
        pattern in text
        for pattern in patterns
    ):

        return {
            "rule": "MISSING_ROUTE",
            "status": "FAIL",
            "finding": (
                "Evidence indicates that a required "
                "route is missing"
            )
        }

    return None


# ============================================================
# RULE: WRONG NEXT HOP
# ============================================================

def check_next_hop(evidence):

    text = evidence.lower()

    if (
        "wrong next hop" in text
        or "wrong next-hop" in text
    ):

        return {
            "rule": "WRONG_NEXT_HOP",
            "status": "FAIL",
            "finding": (
                "Evidence indicates that the "
                "configured next-hop is incorrect"
            )
        }

    return None


# ============================================================
# RULE: VLAN
# ============================================================

def check_vlan(evidence):

    text = evidence.lower()

    if "show vlan brief" not in text:

        return None

    if "vlan 20 absent" in text:

        return {
            "rule": "MISSING_VLAN",
            "status": "FAIL",
            "finding": (
                "Required VLAN 20 is missing"
            )
        }

    if (
        "fa0/1 vlan 10" in text
        and "fa0/2 vlan 20" in text
    ):

        return {
            "rule": "WRONG_VLAN",
            "status": "FAIL",
            "finding": (
                "Evidence indicates that the "
                "PC2 switch port is assigned "
                "to the wrong VLAN"
            )
        }

    if (
        "ap port assigned to vlan 20"
        in text
    ):

        return {
            "rule": "WIRELESS_VLAN",
            "status": "FAIL",
            "finding": (
                "Access point port is assigned "
                "to the wrong VLAN"
            )
        }

    return None


# ============================================================
# RULE: TRUNK
# ============================================================

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


# ============================================================
# RULE: DHCP
# ============================================================

def check_dhcp(evidence):

    text = evidence.lower()

    if (
        "no pool for 192.168.10.0/24"
        in text
        or
        "no pool exists for 192.168.10.0/24"
        in text
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


# ============================================================
# RULE: DNS
# ============================================================

def check_dns(evidence):

    text = evidence.lower()

    if (
        "dns request timed out"
        in text
        or (
            "nslookup" in text
            and "timeout" in text
        )
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
                "IP connectivity appears to work "
                "while DNS resolution fails"
            )
        }

    return None


# ============================================================
# RULE: ACL
# ============================================================

def check_acl(evidence):

    text = evidence.lower()

    if (
        "deny from 192.168.10.0/24"
        in text
        and
        "192.168.30.0/24"
        in text
    ):

        return {
            "rule": "ACL_BLOCK",
            "status": "FAIL",
            "finding": (
                "ACL denies traffic from "
                "192.168.10.0/24 to "
                "192.168.30.0/24"
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

    if (
        "tcp port 80" in text
        and "denies" in text
    ):

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


# ============================================================
# RULE: NAT
# ============================================================

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
        or
        "nat acl does not match" in text
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
        and
        "not 192.168.20.0/24"
        in text
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
                "for the server is missing"
            )
        }

    return None


# ============================================================
# RULE: INTERFACE
# ============================================================

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


# ============================================================
# RULE: DUPLICATE IP
# ============================================================

def check_duplicate_ip(evidence):

    text = evidence.lower()

    if (
        "same ip associated with different mac"
        in text
        or
        "same ip associated with different macs"
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
# RUN ALL RULES
# ============================================================

def check_case(case):

    evidence = str(
        case.get(
            "Show Output / Evidence",
            ""
        )
    )

    findings = []

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

    for rule in rules:

        try:

            result = rule(
                evidence
            )

        except Exception as error:

            result = {
                "rule": (
                    f"{rule.__name__.upper()}_ERROR"
                ),
                "status": "ERROR",
                "finding": (
                    f"Rule could not be evaluated: "
                    f"{error}"
                )
            }

        if result:

            findings.append(
                result
            )

    return findings


# ============================================================
# LOAD CASES
# ============================================================

def load_cases():

    with open(
        CSV_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(
            file
        )

        return list(reader)


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(results):

    with open(
        RESULT_FILE,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        writer = csv.writer(
            file
        )

        writer.writerow(
            [
                "ID",
                "Rule",
                "Status",
                "Finding"
            ]
        )

        for result in results:

            writer.writerow(
                [
                    result["ID"],
                    result["rule"],
                    result["status"],
                    result["finding"]
                ]
            )


# ============================================================
# MAIN
# ============================================================

def main():

    if not os.path.exists(
        CSV_FILE
    ):

        print(
            f"ERROR: cases.csv not found:"
        )

        print(
            CSV_FILE
        )

        raise SystemExit(1)


    cases = load_cases()


    print()
    print(
        f"Total cases loaded: "
        f"{len(cases)}"
    )

    print()


    all_results = []


    for index, case in enumerate(
        cases,
        start=1
    ):

        case_id = str(
            case.get(
                "ID",
                ""
            )
        ).strip()


        print(
            f"[{index}/{len(cases)}] "
            f"Checking {case_id}"
        )


        findings = check_case(
            case
        )


        if findings:

            for finding in findings:

                print(
                    f"  [{finding['status']}] "
                    f"{finding['rule']}"
                )

                print(
                    f"  {finding['finding']}"
                )

                all_results.append(
                    {
                        "ID": case_id,
                        "rule": finding["rule"],
                        "status": finding["status"],
                        "finding": finding["finding"]
                    }
                )

        else:

            print(
                "  [INFO] No deterministic "
                "rule matched."
            )

            all_results.append(
                {
                    "ID": case_id,
                    "rule": "NONE",
                    "status": "INFO",
                    "finding": (
                        "No deterministic rule "
                        "matched the supplied evidence"
                    )
                }
            )

        print()


    # ========================================================
    # SAVE
    # ========================================================

    save_results(
        all_results
    )


    print("=" * 70)
    print("CHECK COMPLETE")
    print("=" * 70)

    print(
        f"Cases processed: "
        f"{len(cases)}"
    )

    print(
        f"Checker records: "
        f"{len(all_results)}"
    )

    print(
        f"Results saved to:"
    )

    print(
        RESULT_FILE
    )

    print("=" * 70)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()