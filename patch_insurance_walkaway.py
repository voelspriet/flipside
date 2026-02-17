"""
Patch the insurance cache entry with a fresh, complete walkaway analysis.
The existing cache has walkaway_thinking/text but no walkaway_done (timed out).
This script:
  1. Creates the insurance sample doc to get its text loaded
  2. Calls /deepdive/{doc_id}/walkaway
  3. Remaps generic events -> walkaway_* prefixed events
  4. Splices them into the cache replacing the incomplete walkaway
"""

import requests
import json
import sys
import time

BASE = 'http://127.0.0.1:8093'
CACHE_PATH = 'data/sample_cache.json'

print('Creating insurance sample doc...')
resp = requests.post(f'{BASE}/sample', json={'type': 'insurance'}, timeout=10)
doc_id = resp.json()['doc_id']
print(f'  doc_id: {doc_id}')

# Give prescan a moment (but it'll skip prescan since insurance is cached)
time.sleep(1)

print('Fetching walkaway via deepdive...')
t0 = time.time()
new_walkaway_events = []

with requests.get(f'{BASE}/deepdive/{doc_id}/walkaway',
                  stream=True, timeout=600) as sse:
    for line in sse.iter_lines(decode_unicode=True):
        if not line or not line.startswith('data: '):
            continue
        try:
            payload = json.loads(line[6:])
        except Exception:
            continue
        etype = payload.get('type', '')
        content = payload.get('content', '')

        if etype == 'thinking':
            new_type = 'walkaway_thinking'
        elif etype == 'text':
            new_type = 'walkaway_text'
        elif etype == 'done':
            new_type = 'walkaway_done'
        elif etype == 'error':
            print(f'  ERROR from deepdive: {content}')
            sys.exit(1)
        else:
            continue  # skip 'phase' etc.

        chunk = f'data: {json.dumps({"type": new_type, "content": content})}\n\n'
        new_walkaway_events.append(chunk)
        sys.stdout.write('.')
        sys.stdout.flush()

elapsed = round(time.time() - t0, 1)
print(f'\n  Got {len(new_walkaway_events)} walkaway events in {elapsed}s')

# Patch the cache
print('Patching cache...')
with open(CACHE_PATH) as f:
    cache = json.load(f)

events = cache['insurance']

# Strip incomplete walkaway events and the error event
stripped = []
for e in events:
    try:
        p = json.loads(e.split('data: ', 1)[1])
        t = p.get('type', '')
    except Exception:
        t = ''
    if t in ('walkaway_thinking', 'walkaway_text', 'walkaway_done', 'error'):
        continue
    stripped.append(e)

# Find position just before the final 'done' event and insert walkaway there
done_idx = next((i for i, e in enumerate(stripped)
                 if '"type": "done"' in e or '"type":"done"' in e), len(stripped))

patched = stripped[:done_idx] + new_walkaway_events + stripped[done_idx:]
cache['insurance'] = patched

with open(CACHE_PATH, 'w') as f:
    json.dump(cache, f)

print(f'  Patched: {len(events)} -> {len(patched)} events')
print('Done! Reload the server to pick up the new cache.')
