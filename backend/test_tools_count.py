#!/usr/bin/env python3
"""Test script to verify tools count."""

import sys
sys.path.insert(0, '.')

from app.core.tools_config import (
    DISCOVERY_TOOLS, SCANNING_TOOLS, ENUMERATION_TOOLS,
    VULNERABILITY_ASSESSMENT_TOOLS, EXPLOITATION_TOOLS,
    POST_EXPLOITATION_TOOLS, LATERAL_MOVEMENT_TOOLS,
    EVIDENCE_COLLECTION_TOOLS, PAYMENT_SYSTEMS_TOOLS,
    BLOCKCHAIN_TOOLS, API_SECURITY_TOOLS, SOCIAL_ENGINEERING_TOOLS,
    ALL_SECURITY_TOOLS
)

print("=== ANPTOP TOOLS COUNT VERIFICATION ===\n")

print(f"{'Category':<30} {'Count':<10} {'Status':<15}")
print("-" * 55)

tests = [
    ("Discovery", len(DISCOVERY_TOOLS), 14),
    ("Scanning", len(SCANNING_TOOLS), 14),
    ("Enumeration", len(ENUMERATION_TOOLS), 35),
    ("Vulnerability Assessment", len(VULNERABILITY_ASSESSMENT_TOOLS), 22),
    ("Exploitation", len(EXPLOITATION_TOOLS), 23),
    ("Post-Exploitation", len(POST_EXPLOITATION_TOOLS), 30),
    ("Lateral Movement", len(LATERAL_MOVEMENT_TOOLS), 22),
    ("Evidence Collection", len(EVIDENCE_COLLECTION_TOOLS), 12),
    ("Payment Systems", len(PAYMENT_SYSTEMS_TOOLS), 10),
    ("Blockchain", len(BLOCKCHAIN_TOOLS), 6),
    ("API Security", len(API_SECURITY_TOOLS), 1),
    ("Social Engineering", len(SOCIAL_ENGINEERING_TOOLS), 3),
]

all_passed = True
for name, actual, expected in tests:
    status = "PASS" if actual == expected else "FAIL"
    if actual != expected:
        all_passed = False
    print(f"{name:<30} {actual:<10} {status:<15}")

print("-" * 55)

total = sum(t[1] for t in tests)
expected_total = 196
overall_status = "PASS" if total == expected_total else "FAIL"
if total != expected_total:
    all_passed = False

print(f"{'TOTAL':<30} {total:<10} {overall_status:<15}")
print()

if all_passed:
    print("SUCCESS: All 196 tools are configured correctly!")
else:
    print("FAILURE: Some tools are missing or duplicated!")
    print(f"Expected: {expected_total}, Got: {total}")

sys.exit(0 if all_passed else 1)
