#!/usr/bin/env python3
"""
PR Description Validation Script
Checks if a pull request description follows the AGENTS.md guidelines
"""

import sys
import re
from pathlib import Path

REQUIRED_SECTIONS = [
    r"## Summary",
    r"## What Was Done",
    r"## What Needs To Be Done Next", 
    r"## Build Status",
    r"## Issues & Warnings",
    r"## How To Fix Build Failures",
    r"## Testing Status",
    r"## Dependencies & Requirements"
]

BUILD_STATUS_INDICATORS = [
    r"✅ SUCCESS",
    r"❌ FAILED", 
    r"⚠️ WARNINGS"
]

def validate_pr_description(content: str) -> tuple[bool, list[str]]:
    """Validate PR description against AGENTS.md guidelines"""
    errors = []
    
    # Check for required sections
    for section in REQUIRED_SECTIONS:
        if not re.search(section, content, re.MULTILINE):
            errors.append(f"Missing required section: {section}")
    
    # Check for build status indicator
    has_build_status = any(re.search(status, content) for status in BUILD_STATUS_INDICATORS)
    if not has_build_status:
        errors.append("Missing build status indicator (✅ SUCCESS / ❌ FAILED / ⚠️ WARNINGS)")
    
    # Check for build command
    if not re.search(r"```bash", content) and not re.search(r"dotnet build", content):
        errors.append("Missing build command documentation")
    
    # Check for exit code
    if not re.search(r"Exit Code:", content) and not re.search(r"exit code", content, re.IGNORECASE):
        errors.append("Missing exit code documentation") 
    
    # Check for priority indicators
    if not re.search(r"priority:\s*(high|medium|low)", content, re.IGNORECASE):
        errors.append("Missing priority indicators for next steps")
    
    # Check for task checkboxes
    if not re.search(r"- \[[ x]\]", content):
        errors.append("Missing task checkboxes (- [ ] or - [x])")
    
    # Check for specific error format if build failed
    if "❌ FAILED" in content:
        if not re.search(r"/workspace/.*\.cs\(\d+,\d+\)", content):
            errors.append("Build failed but missing specific error format with file paths and line numbers")
    
    return len(errors) == 0, errors

def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_pr.py <pr_description_file>")
        print("Example: python validate_pr.py pr_description.md")
        sys.exit(1)
    
    pr_file = Path(sys.argv[1])
    
    if not pr_file.exists():
        print(f"Error: File {pr_file} does not exist")
        sys.exit(1)
    
    try:
        content = pr_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    is_valid, errors = validate_pr_description(content)
    
    if is_valid:
        print("✅ PR description is valid and follows AGENTS.md guidelines")
        sys.exit(0)
    else:
        print("❌ PR description validation failed:")
        for error in errors:
            print(f"  - {error}")
        print(f"\n📋 Please review AGENTS.md for complete guidelines")
        print(f"✅ Use AGENT_PR_CHECKLIST.md for quick reference")
        sys.exit(1)

if __name__ == "__main__":
    main()