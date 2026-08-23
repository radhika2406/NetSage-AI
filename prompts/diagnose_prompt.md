# Network Troubleshooting Diagnosis Prompt

## Role

Act as a Cisco-style network troubleshooting assistant.

Analyze the network case provided below and identify the most likely
root cause.

Use the symptom, topology information, and supplied command output as
evidence.

Do not assume that the first possible cause is the correct one.

---

## Standard Lab

The cases use the following virtual network.

### Devices

- R1 - Main Router
- R2 - Remote Router
- SW1 - Main Switch
- SW2 - Secondary Switch
- PC1 - 192.168.10.10
- PC2 - 192.168.10.20
- PC3 - 192.168.20.10
- SRV1 - 192.168.30.10
- DNS1 - 192.168.30.20
- Remote Server - 192.168.40.10
- AP1 - Wireless Access Point

### Networks

- VLAN 10: 192.168.10.0/24
- VLAN 20: 192.168.20.0/24
- VLAN 30: 192.168.30.0/24
- R1-R2 link: 10.0.0.0/30
- Remote network: 192.168.40.0/24

### Gateways

- VLAN 10: 192.168.10.1
- VLAN 20: 192.168.20.1
- VLAN 30: 192.168.30.1
- Remote network: 192.168.40.1

---

## Troubleshooting Method

For each case:

1. Read the symptom.
2. Identify the source and destination.
3. Follow the likely network path.
4. Examine the supplied command output.
5. Identify anything that is incorrect or missing.
6. Determine the most likely root cause.
7. Identify the OSI layer involved.
8. Recommend the next command that would confirm the diagnosis.
9. Suggest the appropriate fix.
10. Explain how to verify the fix.

---

## Evidence Rules

The diagnosis must be based on the evidence supplied in the case.

Do not invent command output, IP addresses, routes, VLANs, ACL entries,
or device configurations.

If the supplied evidence is not enough to identify a root cause, say:

"Insufficient evidence"

and provide the command that should be run next.

Do not use the expected answer or reference fields when making the
diagnosis.

---

## Areas to Consider

Depending on the evidence, the problem may involve:

- Physical/interface status
- VLAN configuration
- Trunking
- IP addressing
- Default gateway
- DHCP
- DHCP relay
- DNS
- Static routing
- OSPF
- ACL
- NAT/PAT
- Wireless configuration
- Server gateway configuration

Do not choose a category unless the evidence supports it.

---

# Case

### Case ID

{{case_id}}

### Symptom

{{symptom}}

### Topology

{{topology_note}}

### Show Command Output

{{show_output}}

---

# Required Response

Return the answer using the following format.

## 1. Likely Fault

**Fault:** <most likely root cause>

## 2. OSI Layer

**Layer:** <Layer 1 / Layer 2 / Layer 3 / Layer 4 / Layer 7>

## 3. Networking Concept

**Concept:** <VLAN / Routing / DHCP / DNS / ACL / NAT /
Gateway / OSPF / Wireless / Interface / etc.>

## 4. Severity

**Severity:** <Low / Medium / High>

## 5. Evidence

Identify the important evidence from the supplied command output.

Explain why that evidence points toward the proposed fault.

## 6. Next Command

```text
<next Cisco or endpoint command>