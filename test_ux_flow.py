"""
FlipSide UX Flow Tester — simulates a user session via HTTP.

Hits /sample, then streams /analyze/<id>, parsing SSE events
in real-time to detect UX issues:
- How long before first flip card appears
- Whether quick_done fires and sets flipCardsBuilt
- Whether deep analysis data arrives after quick_done
- Whether the verdict button WOULD work (data available for polling)
- Total timing per phase

Usage:
    python3 test_ux_flow.py              # Full flow with timing
    python3 test_ux_flow.py --verbose    # Show all SSE events
"""

import requests
import json
import re
import sys
import time

BASE = "http://127.0.0.1:5001"
VERBOSE = "--verbose" in sys.argv
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "FlipSide-UX-Tester/1.0"})

def log(msg, indent=0):
    prefix = "  " * indent
    print(f"{prefix}{msg}")

def test_sample_flow():
    log("=" * 60)
    log("  FLIPSIDE UX FLOW TEST")
    log("=" * 60)
    log("")

    # Step 1: Hit /sample
    log("[1] POST /sample ...")
    t0 = time.time()
    resp = SESSION.post(f"{BASE}/sample", json={"role": "tenant", "depth": "standard"})
    if resp.status_code != 200:
        log(f"  FAIL: status {resp.status_code}")
        return
    data = resp.json()
    doc_id = data["doc_id"]
    log(f"  OK: doc_id={doc_id[:12]}... ({time.time()-t0:.2f}s)")
    log(f"  filename: {data.get('filename', '?')}")
    log(f"  text_length: {data.get('text_length', '?')}")
    log("")

    # Step 2: Stream /analyze/<id>
    log(f"[2] GET /analyze/{doc_id[:12]}... (SSE stream)")
    log("")

    t_start = time.time()
    t_first_card = None
    t_quick_done = None
    t_deep_data_start = None
    t_done = None

    response_content = ""
    quick_done_length = 0
    parsed_clause_count = 0
    phases_seen = []
    event_count = 0
    clause_titles = []
    thinking_chars = 0
    deep_analysis_chars = 0

    with SESSION.get(f"{BASE}/analyze/{doc_id}", stream=True) as r:
        for line in r.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data: "):
                continue

            event_count += 1
            try:
                msg = json.loads(line[6:])
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type", "")
            elapsed = time.time() - t_start

            if VERBOSE:
                content_preview = str(msg.get("content", ""))[:80]
                log(f"  [{elapsed:6.1f}s] {msg_type}: {content_preview}")

            if msg_type == "phase":
                phases_seen.append(msg.get("content", ""))
                log(f"  [{elapsed:5.1f}s] PHASE: {msg.get('content', '')}")

            elif msg_type == "thinking_start":
                log(f"  [{elapsed:5.1f}s] thinking_start")

            elif msg_type == "thinking":
                thinking_chars += len(msg.get("content", ""))

            elif msg_type == "thinking_done":
                log(f"  [{elapsed:5.1f}s] thinking_done ({thinking_chars} chars of reasoning)")

            elif msg_type == "text_start":
                log(f"  [{elapsed:5.1f}s] text_start")

            elif msg_type == "text":
                chunk = msg.get("content", "")
                response_content += chunk

                # Simulate incremental clause detection
                if quick_done_length == 0:  # During quick scan
                    segments = response_content.split("\n---\n")
                    # Also try flexible split
                    if len(segments) <= 1:
                        segments = re.split(r'\n+---\n+', response_content)

                    for i in range(parsed_clause_count, len(segments) - 1):
                        seg = segments[i]
                        if re.search(r'^### ', seg, re.MULTILINE) and re.search(r'(GREEN|YELLOW|RED)', seg, re.IGNORECASE):
                            title_match = re.search(r'^### \s*(.+?)(?:\s+\(|$)', seg, re.MULTILINE)
                            title = title_match.group(1).strip() if title_match else f"Clause {i}"
                            clause_titles.append(title)
                            if t_first_card is None:
                                t_first_card = time.time() - t_start
                                log(f"  [{elapsed:5.1f}s] FIRST CARD: \"{title}\"")
                            else:
                                log(f"  [{elapsed:5.1f}s]   card #{len(clause_titles)}: \"{title}\"")
                    parsed_clause_count = max(parsed_clause_count, len(segments) - 1)

            elif msg_type == "text_done":
                log(f"  [{elapsed:5.1f}s] text_done (total: {len(response_content)} chars)")

            elif msg_type == "quick_done":
                t_quick_done = time.time() - t_start
                quick_done_length = len(response_content)

                # Final sweep — parse last segment
                segments = re.split(r'\n+---\n+', response_content)
                for i in range(parsed_clause_count, len(segments)):
                    seg = segments[i]
                    if re.search(r'^### ', seg, re.MULTILINE) and re.search(r'(GREEN|YELLOW|RED)', seg, re.IGNORECASE):
                        title_match = re.search(r'^### \s*(.+?)(?:\s+\(|$)', seg, re.MULTILINE)
                        title = title_match.group(1).strip() if title_match else f"Clause {i}"
                        clause_titles.append(title)
                        log(f"  [{elapsed:5.1f}s]   card #{len(clause_titles)}: \"{title}\" (final sweep)")
                parsed_clause_count = len(segments)

                qdData = {}
                try:
                    qdData = json.loads(msg.get("content", "{}"))
                except:
                    pass
                qdSec = qdData.get("seconds", 0)
                log(f"  [{elapsed:5.1f}s] QUICK_DONE: {len(clause_titles)} cards in {qdSec:.1f}s (content: {quick_done_length} chars)")
                thinking_chars = 0  # Reset for deep phase

            elif msg_type == "done":
                t_done = time.time() - t_start
                deep_analysis_chars = len(response_content) - quick_done_length

                doneData = {}
                try:
                    doneData = json.loads(msg.get("content", "{}"))
                except:
                    pass
                log(f"  [{elapsed:5.1f}s] DONE (deep analysis: {deep_analysis_chars} chars)")
                break

            elif msg_type == "error":
                log(f"  [{elapsed:5.1f}s] ERROR: {msg.get('content', '')}")
                break

    # Summary
    log("")
    log("=" * 60)
    log("  RESULTS")
    log("=" * 60)
    log("")
    log(f"  Total SSE events:     {event_count}")
    log(f"  Phases seen:          {', '.join(phases_seen)}")
    log(f"  Cards parsed:         {len(clause_titles)}")
    log("")

    log("  TIMING")
    log("  " + "-" * 40)
    if t_first_card is not None:
        log(f"  First card appeared:  {t_first_card:.1f}s")
    else:
        log(f"  First card appeared:  NEVER (BUG!)")

    if t_quick_done is not None:
        log(f"  Quick scan done:      {t_quick_done:.1f}s")
    else:
        log(f"  Quick scan done:      NEVER")

    if t_done is not None:
        log(f"  Total (incl. deep):   {t_done:.1f}s")
    log("")

    # Verdict button simulation
    log("  VERDICT BUTTON SIMULATION")
    log("  " + "-" * 40)
    if quick_done_length > 0 and len(response_content) > quick_done_length + 100:
        log(f"  Deep data available:  YES ({deep_analysis_chars} chars)")
        log(f"  Verdict would work:   YES")
    else:
        log(f"  Deep data available:  NO")
        log(f"  Verdict would work:   NO (BUG — polling would hang)")
    log("")

    # Card list
    if clause_titles:
        log("  CLAUSES FOUND")
        log("  " + "-" * 40)
        for i, title in enumerate(clause_titles, 1):
            log(f"  {i:2d}. {title}")
    log("")

    # Deep analysis preview
    if deep_analysis_chars > 0:
        deep_text = response_content[quick_done_length:]
        log("  DEEP ANALYSIS PREVIEW (first 300 chars)")
        log("  " + "-" * 40)
        log(f"  {deep_text[:300]}")
    log("")

    log("=" * 60)
    log("  End of test")
    log("=" * 60)


if __name__ == "__main__":
    test_sample_flow()
