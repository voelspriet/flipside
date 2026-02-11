"""
FlipSide Flicker Watcher — Playwright DOM Mutation Monitor

Launches a real browser, triggers a sample analysis, and captures
every DOM mutation on the first visible clause card during streaming.
Takes periodic screenshots to correlate visual state with mutations.

Usage: python3 flicker_watch.py
"""
import json, time, os
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:5000/"
OUTDIR = "/Users/henkvaness/Documents/flipside/flicker_report"
os.makedirs(OUTDIR, exist_ok=True)

# JS to inject: MutationObserver that pushes mutations to window.__mutations
OBSERVER_JS = """
() => {
    window.__mutations = [];
    window.__mutationCount = 0;
    window.__observerAttached = false;

    window.__attachObserver = function() {
        if (window.__observerAttached) return 'already attached';

        // Find the first visible clause card
        var card = document.querySelector('.clause-card:not(.clause-hidden)');
        if (!card) return 'no card found';

        var title = card.getAttribute('data-clause-title') || 'unknown';

        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(m) {
                window.__mutationCount++;
                var target = m.target;
                var targetTag = target.tagName ? target.tagName.toLowerCase() : 'text';
                var targetClass = (target.className && typeof target.className === 'string')
                    ? target.className.split(' ').slice(0, 2).join('.')
                    : '';
                var entry = {
                    time: Date.now(),
                    type: m.type,
                    target: targetTag + (targetClass ? '.' + targetClass : '')
                };

                if (m.type === 'attributes') {
                    entry.attr = m.attributeName;
                    entry.oldVal = (m.oldValue || '').substring(0, 60);
                    entry.newVal = (target.getAttribute(m.attributeName) || '').substring(0, 60);
                    // Skip if no actual change
                    if (entry.oldVal === entry.newVal) return;
                }
                else if (m.type === 'childList') {
                    entry.added = Array.from(m.addedNodes).map(function(n) {
                        var d = n.tagName ? n.tagName.toLowerCase() : 'text';
                        if (n.className) d += '.' + n.className.split(' ')[0];
                        if (!n.tagName) d = 'text("' + (n.textContent || '').substring(0, 40) + '")';
                        return d;
                    });
                    entry.removed = Array.from(m.removedNodes).map(function(n) {
                        var d = n.tagName ? n.tagName.toLowerCase() : 'text';
                        if (n.className) d += '.' + n.className.split(' ')[0];
                        if (!n.tagName) d = 'text("' + (n.textContent || '').substring(0, 40) + '")';
                        return d;
                    });
                }
                else if (m.type === 'characterData') {
                    entry.oldText = (m.oldValue || '').substring(0, 50);
                    entry.newText = (m.target.textContent || '').substring(0, 50);
                }

                window.__mutations.push(entry);
                // Keep max 2000
                if (window.__mutations.length > 2000) window.__mutations.shift();
            });
        });

        observer.observe(card, {
            attributes: true,
            attributeOldValue: true,
            childList: true,
            characterData: true,
            characterDataOldValue: true,
            subtree: true
        });

        window.__observerAttached = true;
        return 'attached to: ' + title.substring(0, 60);
    };

    return 'observer script injected';
}
"""

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=100)
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        print("[1] Loading FlipSide...")
        page.goto(URL)
        page.wait_for_load_state("networkidle")
        page.screenshot(path=f"{OUTDIR}/01_loaded.png")

        print("[2] Clicking 'try sample policy'...")
        page.click("text=try sample policy")

        # Wait for analysis section to appear
        print("[3] Waiting for analysis to start...")
        page.wait_for_selector("#analysis-section:not(.hidden)", timeout=15000)
        page.screenshot(path=f"{OUTDIR}/02_analysis_started.png")
        time.sleep(2)  # Let first cards stream in

        print("[4] Injecting mutation observer...")
        result = page.evaluate(OBSERVER_JS)
        print(f"    Injection: {result}")

        # Try attaching repeatedly until a card appears
        for attempt in range(20):
            attach_result = page.evaluate("window.__attachObserver()")
            print(f"    Attach attempt {attempt+1}: {attach_result}")
            if "attached" in attach_result:
                break
            time.sleep(1)

        page.screenshot(path=f"{OUTDIR}/03_observer_attached.png")

        # Now monitor for 30 seconds, taking screenshots every 3 seconds
        print("[5] Monitoring mutations for 30 seconds...")
        screenshots = []
        for i in range(10):
            time.sleep(3)
            count = page.evaluate("window.__mutationCount")
            mutation_sample = page.evaluate("window.__mutations.slice(-10)")
            ss_path = f"{OUTDIR}/04_monitor_{i:02d}_{count}muts.png"
            page.screenshot(path=ss_path)
            screenshots.append(ss_path)
            print(f"    t={3*(i+1)}s: {count} total mutations, last batch:")
            for m in mutation_sample:
                mtype = m.get("type", "?")
                target = m.get("target", "?")
                if mtype == "attributes":
                    print(f"      [ATTR] {target} :: {m.get('attr')} = \"{m.get('oldVal','')[:30]}\" → \"{m.get('newVal','')[:30]}\"")
                elif mtype == "childList":
                    added = m.get("added", [])
                    removed = m.get("removed", [])
                    if added:
                        print(f"      [ADD]  {target} << {added}")
                    if removed:
                        print(f"      [DEL]  {target} >> {removed}")
                elif mtype == "characterData":
                    print(f"      [TEXT] {target} :: \"{m.get('oldText','')[:30]}\" → \"{m.get('newText','')[:30]}\"")

        # Dump full mutation log
        print("\n[6] Dumping full mutation log...")
        all_mutations = page.evaluate("window.__mutations")
        with open(f"{OUTDIR}/mutations.json", "w") as f:
            json.dump(all_mutations, f, indent=2)
        print(f"    Saved {len(all_mutations)} mutations to mutations.json")

        # Analyze patterns
        print("\n[7] Mutation analysis:")
        attr_changes = {}
        child_changes = {}
        for m in all_mutations:
            if m["type"] == "attributes":
                key = f"{m['target']}.{m.get('attr','?')}"
                attr_changes[key] = attr_changes.get(key, 0) + 1
            elif m["type"] == "childList":
                key = m["target"]
                child_changes[key] = child_changes.get(key, 0) + 1

        if attr_changes:
            print("    Top attribute changes (FLICKER SUSPECTS):")
            for k, v in sorted(attr_changes.items(), key=lambda x: -x[1])[:10]:
                print(f"      {v:4d}x  {k}")

        if child_changes:
            print("    Top child mutations (FLICKER SUSPECTS):")
            for k, v in sorted(child_changes.items(), key=lambda x: -x[1])[:10]:
                print(f"      {v:4d}x  {k}")

        if not attr_changes and not child_changes:
            print("    NO MUTATIONS DETECTED — card is stable!")
            # Check if the card was actually cached
            cache_check = page.evaluate("""
                () => {
                    var card = document.querySelector('.clause-card:not(.clause-hidden)');
                    if (!card) return 'no card';
                    return {
                        title: card.getAttribute('data-clause-title'),
                        classes: card.className,
                        childCount: card.children.length,
                        hasStyle: card.style.cssText
                    };
                }
            """)
            print(f"    Card state: {json.dumps(cache_check, indent=6)}")

        page.screenshot(path=f"{OUTDIR}/05_final.png")

        # Write summary report
        summary = f"""# Flicker Watch Report
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Total mutations: {len(all_mutations)}

## Top attribute changes:
"""
        for k, v in sorted(attr_changes.items(), key=lambda x: -x[1])[:10]:
            summary += f"- {v}x  {k}\n"
        summary += "\n## Top child mutations:\n"
        for k, v in sorted(child_changes.items(), key=lambda x: -x[1])[:10]:
            summary += f"- {v}x  {k}\n"

        with open(f"{OUTDIR}/report.md", "w") as f:
            f.write(summary)

        print(f"\n[8] Full report saved to {OUTDIR}/")
        print("    Press Enter to close browser...")
        input()
        browser.close()

if __name__ == "__main__":
    run()
