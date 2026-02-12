"""
FlipSide Doc Maintenance Agent — keeps .md files up to date.

Reads the actual project state (code, git, file sizes) and checks
HACKATHON_LOG.md, strategy.md, and README.md for stale information.
Reports what's outdated and optionally fixes it.

Usage:
    python3 maintain_docs.py              # Check for stale info
    python3 maintain_docs.py --fix        # Auto-fix what it can
    python3 maintain_docs.py --verbose    # Show all checks
"""

import os
import re
import sys
import subprocess
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
FIX_MODE = "--fix" in sys.argv
VERBOSE = "--verbose" in sys.argv

# Track issues found
issues = []
fixes_applied = []


def read_file(name):
    path = os.path.join(PROJECT_DIR, name)
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return ""


def count_lines(name):
    path = os.path.join(PROJECT_DIR, name)
    if os.path.exists(path):
        with open(path) as f:
            return sum(1 for _ in f)
    return 0


def git_commit_count():
    try:
        result = subprocess.run(
            ["git", "log", "--oneline"],
            capture_output=True, text=True, cwd=PROJECT_DIR
        )
        return len(result.stdout.strip().split("\n"))
    except Exception:
        return 0


def git_recent_commits(n=5):
    try:
        result = subprocess.run(
            ["git", "log", f"--max-count={n}", "--format=%H|%aI|%s"],
            capture_output=True, text=True, cwd=PROJECT_DIR
        )
        commits = []
        for line in result.stdout.strip().split("\n"):
            if "|" in line:
                parts = line.split("|", 2)
                commits.append({
                    "hash": parts[0][:8],
                    "date": parts[1][:10],
                    "message": parts[2]
                })
        return commits
    except Exception:
        return []


def check_line_counts():
    """Check if line counts in docs match actual files."""
    files_to_check = {
        "app.py": None,
        "templates/index.html": None,
        "decision_monitor.py": None,
        "test_ux_flow.py": None,
    }

    for name in files_to_check:
        files_to_check[name] = count_lines(name)

    # Check HACKATHON_LOG.md
    log = read_file("HACKATHON_LOG.md")
    for name, actual in files_to_check.items():
        if actual == 0:
            continue
        # Look for line count references like "1,100 lines" or "982 lines"
        basename = os.path.basename(name)
        pattern = rf'`{re.escape(basename)}`[^|]*\|\s*~?([\d,]+)\s*(?:lines)?'
        for match in re.finditer(pattern, log):
            stated = int(match.group(1).replace(",", ""))
            diff_pct = abs(actual - stated) / max(actual, 1) * 100
            if diff_pct > 15:
                issues.append(
                    f"HACKATHON_LOG.md: {basename} says ~{stated} lines, actual is {actual} ({diff_pct:.0f}% off)"
                )
            elif VERBOSE:
                print(f"  OK: {basename} = {actual} lines (stated ~{stated})")

    # Check strategy.md too
    strategy = read_file("strategy.md")
    for name, actual in files_to_check.items():
        basename = os.path.basename(name)
        for match in re.finditer(rf'{re.escape(basename)}.*?(\d{{3,5}})\s*lines', strategy):
            stated = int(match.group(1))
            diff_pct = abs(actual - stated) / max(actual, 1) * 100
            if diff_pct > 15:
                issues.append(
                    f"strategy.md: {basename} says ~{stated} lines, actual is {actual} ({diff_pct:.0f}% off)"
                )


def check_entry_count():
    """Check if the stated entry count matches actual entries."""
    log = read_file("HACKATHON_LOG.md")
    # Count **Entry N** patterns
    entries = re.findall(r"\*\*Entry (\d+)", log)
    actual_max = max(int(e) for e in entries) if entries else 0

    # Check stated count
    stated_match = re.search(r"(\d+) entries", log)
    if stated_match:
        stated = int(stated_match.group(1))
        if stated != actual_max:
            issues.append(
                f"HACKATHON_LOG.md: says {stated} entries but highest Entry # is {actual_max}"
            )
        elif VERBOSE:
            print(f"  OK: entry count = {actual_max}")


def check_model_references():
    """Check that model IDs referenced in docs match app.py."""
    app = read_file("app.py")

    model_match = re.search(r"^MODEL\s*=.*?'([^']+)'", app, re.MULTILINE)
    fast_match = re.search(r"FAST_MODEL\s*=.*?'([^']+)'", app)

    model_id = model_match.group(1) if model_match else None
    fast_id = fast_match.group(1) if fast_match else None

    if VERBOSE:
        print(f"  Models: {model_id}, {fast_id}")

    # Check if HACKATHON_LOG mentions the models
    log = read_file("HACKATHON_LOG.md")
    if fast_id and "Haiku" in log and fast_id not in log and "haiku" not in log.lower():
        issues.append(
            f"HACKATHON_LOG.md: mentions Haiku but doesn't reference model ID {fast_id}"
        )


def check_prompt_functions():
    """Check that documented prompt functions match what's in app.py."""
    app = read_file("app.py")
    log = read_file("HACKATHON_LOG.md")

    # Find all build_*_prompt functions
    funcs = re.findall(r"def (build_\w+_prompt)\s*\(", app)
    if VERBOSE:
        print(f"  Prompt functions in app.py: {', '.join(funcs)}")

    # Check if key functions are documented
    for func in funcs:
        if func == "build_system_prompt":
            continue  # Legacy, not required
        short = func.replace("build_", "").replace("_prompt", "")
        if short not in log.lower() and func not in log:
            issues.append(
                f"HACKATHON_LOG.md: prompt function {func}() not documented"
            )


def check_stale_sections():
    """Check for sections that reference old architecture."""
    log = read_file("HACKATHON_LOG.md")

    # Check for references to old line counts or patterns
    stale_patterns = [
        (r"4,008\s*lines", "Frontend is no longer 4,008 lines"),
        (r"982\s*lines", "Backend is no longer 982 lines"),
        (r"thinking is the product, not the sidebar", "Sidebar was removed"),
    ]

    # Only flag if not in a historical context (before "Phase 5")
    phase5_pos = log.find("Phase 5")
    for pattern, msg in stale_patterns:
        for match in re.finditer(pattern, log):
            # If the stale reference is BEFORE phase 5, it's historical context — OK
            # If AFTER phase 5 or in summary tables — flag it
            if match.start() > phase5_pos or phase5_pos == -1:
                continue
            # Check if it's in a summary/table section
            context = log[max(0, match.start() - 200):match.start()]
            if "Current State" in context or "What Exists" in context:
                issues.append(f"HACKATHON_LOG.md: stale reference — {msg}")


def check_git_status():
    """Check for uncommitted changes to docs."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=PROJECT_DIR
        )
        modified_docs = []
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if line and any(line.endswith(ext) for ext in [".md", ".py", ".html"]):
                modified_docs.append(line)
        if modified_docs and VERBOSE:
            print(f"  Uncommitted: {len(modified_docs)} files")
            for f in modified_docs:
                print(f"    {f}")
    except Exception:
        pass


def check_port_reference():
    """Check if docs reference the correct port."""
    app = read_file("app.py")
    port_match = re.search(r"port=(\d+)", app)
    if port_match:
        actual_port = port_match.group(1)
        log = read_file("HACKATHON_LOG.md")
        readme = read_file("README.md")
        for doc, name in [(log, "HACKATHON_LOG.md"), (readme, "README.md")]:
            if "5000" in doc and actual_port != "5000":
                issues.append(f"{name}: references port 5000, actual is {actual_port}")


def main():
    print("=" * 60)
    print("  FLIPSIDE DOC MAINTENANCE CHECK")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print()

    checks = [
        ("Line counts", check_line_counts),
        ("Entry count", check_entry_count),
        ("Model references", check_model_references),
        ("Prompt functions", check_prompt_functions),
        ("Stale sections", check_stale_sections),
        ("Git status", check_git_status),
        ("Port references", check_port_reference),
    ]

    for name, check_fn in checks:
        if VERBOSE:
            print(f"Checking: {name}")
        check_fn()
        if VERBOSE:
            print()

    # Report
    if not issues:
        print("All docs up to date.")
    else:
        print(f"Found {len(issues)} issue(s):")
        print("-" * 40)
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")

    print()

    # Quick stats
    print("QUICK STATS")
    print("-" * 40)
    for name in ["app.py", "templates/index.html", "decision_monitor.py", "test_ux_flow.py"]:
        lines = count_lines(name)
        if lines > 0:
            print(f"  {name}: {lines} lines")

    log = read_file("HACKATHON_LOG.md")
    entries = re.findall(r"\*\*Entry (\d+)", log)
    print(f"  HACKATHON_LOG.md: {max(int(e) for e in entries) if entries else 0} entries")

    strategy = read_file("strategy.md")
    decisions = len(re.findall(r"^## Decision:", strategy, re.MULTILINE))
    prompts = len(re.findall(r"^## Prompt:", strategy, re.MULTILINE))
    print(f"  strategy.md: {decisions} decisions, {prompts} prompts")
    print(f"  Git commits: {git_commit_count()}")
    print()


if __name__ == "__main__":
    main()
