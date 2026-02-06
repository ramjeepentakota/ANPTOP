#!/usr/bin/env python3
"""Standalone test script to verify tools count."""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Direct imports to avoid app package issues
import importlib.util

def load_module_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Load tools_config directly
tools_config = load_module_from_file(
    "tools_config",
    os.path.join(os.path.dirname(__file__), "app", "core", "tools_config.py")
)

# Get all the tool dictionaries
DISCOVERY_TOOLS = tools_config.DISCOVERY_TOOLS
SCANNING_TOOLS = tools_config.SCANNING_TOOLS
ENUMERATION_TOOLS = tools_config.ENUMERATION_TOOLS
VULNERABILITY_ASSESSMENT_TOOLS = tools_config.VULNERABILITY_ASSESSMENT_TOOLS
EXPLOITATION_TOOLS = tools_config.EXPLOITATION_TOOLS
POST_EXPLOITATION_TOOLS = tools_config.POST_EXPLOITATION_TOOLS
LATERAL_MOVEMENT_TOOLS = tools_config.LATERAL_MOVEMENT_TOOLS
EVIDENCE_COLLECTION_TOOLS = tools_config.EVIDENCE_COLLECTION_TOOLS
PAYMENT_SYSTEMS_TOOLS = tools_config.PAYMENT_SYSTEMS_TOOLS
BLOCKCHAIN_TOOLS = tools_config.BLOCKCHAIN_TOOLS
API_SECURITY_TOOLS = tools_config.API_SECURITY_TOOLS
SOCIAL_ENGINEERING_TOOLS = tools_config.SOCIAL_ENGINEERING_TOOLS
ALL_SECURITY_TOOLS = tools_config.ALL_SECURITY_TOOLS

print("=" * 60)
print("ANPTOP TOOLS COUNT VERIFICATION - TEST RESULTS")
print("=" * 60)
print()

print(f"{'Category':<35} {'Count':<8} {'Expected':<8} {'Status':<10}")
print("-" * 65)

tests = [
    ("Discovery Tools", len(DISCOVERY_TOOLS), 14),
    ("Scanning Tools", len(SCANNING_TOOLS), 14),
    ("Enumeration Tools", len(ENUMERATION_TOOLS), 35),
    ("Vulnerability Assessment", len(VULNERABILITY_ASSESSMENT_TOOLS), 22),
    ("Exploitation Tools", len(EXPLOITATION_TOOLS), 23),
    ("Post-Exploitation Tools", len(POST_EXPLOITATION_TOOLS), 30),
    ("Lateral Movement Tools", len(LATERAL_MOVEMENT_TOOLS), 22),
    ("Evidence Collection Tools", len(EVIDENCE_COLLECTION_TOOLS), 12),
    ("Payment Systems Tools", len(PAYMENT_SYSTEMS_TOOLS), 10),
    ("Blockchain Tools", len(BLOCKCHAIN_TOOLS), 6),
    ("API Security Tools", len(API_SECURITY_TOOLS), 8),
    ("Social Engineering Tools", len(SOCIAL_ENGINEERING_TOOLS), 3),
]

all_passed = True
for name, actual, expected in tests:
    status = "PASS" if actual == expected else "FAIL"
    if actual != expected:
        all_passed = False
    print(f"{name:<35} {actual:<8} {expected:<8} {status:<10}")

print("-" * 65)

total = sum(t[1] for t in tests)
expected_total = 199
overall_status = "PASS" if total == expected_total else "FAIL"
if total != expected_total:
    all_passed = False

print(f"{'TOTAL TOOLS':<35} {total:<8} {expected_total:<8} {overall_status:<10}")
print()

print("=" * 60)

if all_passed:
    print("SUCCESS: All 199 tools are configured correctly!")
    print()
    print("Tool Categories:")
    for name, actual, expected in tests:
        print(f"  - {name}: {actual}")
    exit_code = 0
else:
    print("FAILURE: Some tools are missing or duplicated!")
    print(f"Expected: {expected_total}, Got: {total}")
    exit_code = 1

print("=" * 60)
sys.exit(exit_code)
