"""
FlipSide Decision Monitor — Hackathon Strategy Tracker

Reads strategy.md, hackaton.md, HACKATHON_LOG.md, and git history to produce
a jury-readable decision timeline. Shows what was tried, what failed, what
worked, and how Claude 4.6 was used at each step.

Usage:
    python3 decision_monitor.py              # Generate full report
    python3 decision_monitor.py --watch      # Watch for changes and regenerate
    python3 decision_monitor.py --json       # Output as JSON (for integration)
"""

import os
import re
import json
import sys
import time
import subprocess
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(PROJECT_DIR, "decision_report")

WATCHED_FILES = [
    "strategy.md",
    "hackaton.md",
    "HACKATHON_LOG.md",
    "hackathon_log_update.md",
    "templates/index.html",
    "app.py",
]


def git_log(max_count=50):
    """Extract recent git commits with timestamps and messages."""
    try:
        result = subprocess.run(
            ["git", "log", f"--max-count={max_count}", "--format=%H|%aI|%s"],
            capture_output=True, text=True, cwd=PROJECT_DIR
        )
        commits = []
        for line in result.stdout.strip().split("\n"):
            if "|" in line:
                parts = line.split("|", 2)
                commits.append({
                    "hash": parts[0][:8],
                    "date": parts[1],
                    "message": parts[2]
                })
        return commits
    except Exception:
        return []


def git_diff_stat():
    """Show what's changed since last commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--stat"],
            capture_output=True, text=True, cwd=PROJECT_DIR
        )
        return result.stdout.strip()
    except Exception:
        return ""


def read_file(name):
    """Read a project file, return contents or empty string."""
    path = os.path.join(PROJECT_DIR, name)
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    return ""


def extract_strategies(content):
    """Extract decision sections from strategy.md."""
    decisions = []
    sections = re.split(r"^## ", content, flags=re.MULTILINE)
    for section in sections[1:]:  # skip header
        lines = section.strip().split("\n")
        title = lines[0].strip()
        date_match = re.search(r"\*\*Date\*\*:\s*(.+)", section)
        date = date_match.group(1).strip() if date_match else "unknown"

        # Extract key insight
        insight_match = re.search(r"\*\*Key insight\*\*:\s*(.+)", section)
        insight = insight_match.group(1).strip() if insight_match else ""

        # Count attempts/steps
        attempts = len(re.findall(r"^\d+\.", section, re.MULTILINE))

        decisions.append({
            "title": title,
            "date": date,
            "insight": insight,
            "attempts": attempts,
            "full_text": section[:500]
        })
    return decisions


def extract_hackathon_progress(content):
    """Extract prompt execution status from hackaton.md."""
    done = len(re.findall(r"\|\s*done\s*\|", content, re.IGNORECASE))
    skipped = len(re.findall(r"\|\s*skipped\s*\|", content, re.IGNORECASE))
    total = done + skipped
    # Count by category
    categories = {}
    for match in re.finditer(r"\|\s*(done|skipped)\s*\|\s*(\w+)", content, re.IGNORECASE):
        cat = match.group(2)
        categories[cat] = categories.get(cat, 0) + 1
    return {
        "total": total,
        "done": done,
        "skipped": skipped,
        "categories": categories
    }


def count_frontend_features(content):
    """Count interactive features in index.html by markers."""
    markers = {
        "event_listeners": len(re.findall(r"addEventListener", content)),
        "css_animations": len(re.findall(r"@keyframes", content)),
        "state_variables": len(re.findall(r"var\s+\w+\s*=\s*(?:true|false|0|1|\[\]|\{\}|new Set|new Map|null)", content)),
        "dom_functions": len(re.findall(r"function\s+\w+\s*\(", content)),
        "total_lines": content.count("\n") + 1,
    }
    return markers


def detect_model_architecture(backend_content):
    """Detect model configuration from app.py."""
    arch = {"models": [], "parallel": False, "fast_model": None, "deep_model": None}

    # Match os.environ.get('...', 'default') — capture the default value (last quoted string)
    fast_match = re.search(r"FAST_MODEL\s*=.*?,\s*['\"]([^'\"]+)['\"]", backend_content)
    if fast_match:
        arch["fast_model"] = fast_match.group(1)
        arch["models"].append(fast_match.group(1))

    model_match = re.search(r"^MODEL\s*=.*?,\s*['\"]([^'\"]+)['\"]", backend_content, re.MULTILINE)
    if model_match:
        arch["deep_model"] = model_match.group(1)
        arch["models"].append(model_match.group(1))

    arch["parallel"] = bool(re.search(r"threading\.Thread", backend_content))
    return arch


def extract_failure_patterns(log_content):
    """Extract documented AI failures from HACKATHON_LOG.md."""
    failures = []
    for match in re.finditer(
        r"\*\*Entry \d+ — FAILURE: (.+?)\*\*\n(.+?)(?=\n\*\*Entry|\n---|\Z)",
        log_content, re.DOTALL
    ):
        failures.append({
            "pattern": match.group(1).strip(),
            "description": match.group(2).strip()[:200]
        })
    return failures


def build_report(output_json=False):
    """Build the full decision monitoring report."""
    report = {
        "generated": datetime.now().isoformat(),
        "project": "FlipSide — the other side of small print",
    }

    # Git activity
    commits = git_log()
    report["git"] = {
        "total_commits": len(commits),
        "recent": commits[:10],
        "uncommitted_changes": git_diff_stat()
    }

    # Strategy decisions
    strategy = read_file("strategy.md")
    report["strategies"] = extract_strategies(strategy)

    # Hackathon prompt progress
    hackathon = read_file("hackaton.md")
    report["prompt_progress"] = extract_hackathon_progress(hackathon)

    # Frontend complexity
    frontend = read_file("templates/index.html")
    report["frontend"] = count_frontend_features(frontend)

    # Model architecture
    backend = read_file("app.py")
    report["architecture"] = detect_model_architecture(backend)

    # Documented failures (from both log files)
    log = read_file("HACKATHON_LOG.md")
    log_update = read_file("hackathon_log_update.md")
    failures = extract_failure_patterns(log)
    failures.extend(extract_failure_patterns(log_update))
    report["failures"] = failures

    # Decision count and categories
    strategy_count = len(report["strategies"])
    failure_count = len(report["failures"])

    if output_json:
        return json.dumps(report, indent=2)

    # Build human-readable report
    lines = []
    lines.append("=" * 60)
    lines.append("  FLIPSIDE DECISION MONITOR")
    lines.append("  Generated: " + report["generated"][:19])
    lines.append("=" * 60)
    lines.append("")

    # Overview
    lines.append("OVERVIEW")
    lines.append("-" * 40)
    p = report["prompt_progress"]
    lines.append(f"  Prompts executed:  {p['done']}/{p['total']} ({p['skipped']} skipped)")
    lines.append(f"  Strategy decisions: {strategy_count}")
    lines.append(f"  Documented failures: {failure_count}")
    lines.append(f"  Git commits:        {report['git']['total_commits']}")
    f = report["frontend"]
    lines.append(f"  Frontend lines:     {f['total_lines']}")
    lines.append(f"  Event listeners:    {f['event_listeners']}")
    lines.append(f"  CSS animations:     {f['css_animations']}")
    lines.append(f"  JS functions:       {f['dom_functions']}")
    lines.append("")

    # Model architecture
    arch = report.get("architecture", {})
    if arch.get("fast_model") or arch.get("deep_model"):
        lines.append("MODEL ARCHITECTURE")
        lines.append("-" * 40)
        if arch.get("fast_model"):
            lines.append(f"  Fast model (cards): {arch['fast_model']}")
        if arch.get("deep_model"):
            lines.append(f"  Deep model (Opus):  {arch['deep_model']}")
        lines.append(f"  Parallel threads:   {'Yes' if arch.get('parallel') else 'No'}")
        lines.append("")

    # Strategy decisions
    lines.append("STRATEGY DECISIONS")
    lines.append("-" * 40)
    for i, s in enumerate(report["strategies"], 1):
        lines.append(f"  {i}. {s['title']}")
        lines.append(f"     Date: {s['date']}")
        if s["attempts"]:
            lines.append(f"     Attempts: {s['attempts']}")
        if s["insight"]:
            lines.append(f"     Insight: {s['insight'][:100]}")
        lines.append("")

    # AI failures
    if report["failures"]:
        lines.append("DOCUMENTED AI FAILURES")
        lines.append("-" * 40)
        for i, f in enumerate(report["failures"], 1):
            lines.append(f"  {i}. {f['pattern']}")
            lines.append(f"     {f['description'][:120]}")
            lines.append("")

    # Recent git activity
    lines.append("RECENT GIT ACTIVITY")
    lines.append("-" * 40)
    for c in report["git"]["recent"]:
        date_short = c["date"][:10] if c["date"] else "?"
        lines.append(f"  [{c['hash']}] {date_short}  {c['message'][:60]}")
    lines.append("")

    if report["git"]["uncommitted_changes"]:
        lines.append("UNCOMMITTED CHANGES")
        lines.append("-" * 40)
        lines.append(report["git"]["uncommitted_changes"])
        lines.append("")

    # Prompt categories
    if report["prompt_progress"]["categories"]:
        lines.append("PROMPT CATEGORIES")
        lines.append("-" * 40)
        for cat, count in sorted(
            report["prompt_progress"]["categories"].items(),
            key=lambda x: -x[1]
        ):
            lines.append(f"  {count:3d}  {cat}")
        lines.append("")

    lines.append("=" * 60)
    lines.append("  End of report")
    lines.append("=" * 60)

    return "\n".join(lines)


def watch_mode():
    """Watch for file changes and regenerate report."""
    print("Decision Monitor — watching for changes (Ctrl+C to stop)")
    print(f"Watching: {', '.join(WATCHED_FILES)}")
    print()

    os.makedirs(REPORT_DIR, exist_ok=True)

    last_mtimes = {}
    for f in WATCHED_FILES:
        path = os.path.join(PROJECT_DIR, f)
        if os.path.exists(path):
            last_mtimes[f] = os.path.getmtime(path)

    # Generate initial report
    report = build_report()
    report_path = os.path.join(REPORT_DIR, "decision_report.txt")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"Initial report: {report_path}")
    print(report)

    while True:
        time.sleep(5)
        changed = False
        for f in WATCHED_FILES:
            path = os.path.join(PROJECT_DIR, f)
            if os.path.exists(path):
                mtime = os.path.getmtime(path)
                if f not in last_mtimes or mtime != last_mtimes[f]:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Changed: {f}")
                    last_mtimes[f] = mtime
                    changed = True

        if changed:
            report = build_report()
            with open(report_path, "w") as f:
                f.write(report)
            json_report = build_report(output_json=True)
            json_path = os.path.join(REPORT_DIR, "decision_report.json")
            with open(json_path, "w") as f:
                f.write(json_report)
            print(f"Report updated: {report_path}")
            print(report)


if __name__ == "__main__":
    if "--watch" in sys.argv:
        watch_mode()
    elif "--json" in sys.argv:
        print(build_report(output_json=True))
    else:
        print(build_report())
