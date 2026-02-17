#!/usr/bin/env python3
"""Pre-cache all 14 sample SSE streams for offline demos.
Run while Flask server is active: python warmup.py"""

import requests
import json
import sys
import time

BASE = 'http://127.0.0.1:5001'
SAMPLES = [
    'lease', 'insurance', 'tos', 'employment', 'loan', 'gym',
    'medical', 'hoa', 'coupon', 'wedding', 'sweepstakes', 'pet',
    'timeshare', 'hackathon'
]

def main():
    # Check which samples need caching
    status = requests.get(f'{BASE}/cache-status', timeout=5).json()
    cached = set(status['cached'])
    force = '--force' in sys.argv

    to_run = SAMPLES if force else [s for s in SAMPLES if s not in cached]

    if not to_run:
        print(f'All {len(cached)} samples already cached! Use --force to re-cache.')
        return

    print(f'Caching {len(to_run)} samples ({len(cached)} already cached)...\n')

    for i, sample_type in enumerate(to_run):
        t0 = time.time()
        print(f'[{i+1}/{len(to_run)}] {sample_type}...', end=' ', flush=True)

        try:
            # Create sample document
            resp = requests.post(f'{BASE}/sample',
                                 json={'type': sample_type}, timeout=10)
            doc_id = resp.json()['doc_id']

            # Consume the SSE stream (triggers recording in the server)
            event_count = 0
            has_error = False
            with requests.get(f'{BASE}/analyze/{doc_id}',
                              stream=True, timeout=600) as sse:
                for line in sse.iter_lines(decode_unicode=True):
                    if line and line.startswith('data: '):
                        event_count += 1
                        try:
                            payload = json.loads(line[6:])
                            if payload.get('type') == 'error':
                                print(f'\n  ERROR: {payload.get("content", "")}')
                                has_error = True
                        except:
                            pass

            elapsed = round(time.time() - t0, 1)
            status_icon = '!' if has_error else 'OK'
            print(f'{status_icon} ({event_count} events, {elapsed}s)')

        except Exception as e:
            elapsed = round(time.time() - t0, 1)
            print(f'FAILED ({e}) [{elapsed}s]')

    # Final status
    status = requests.get(f'{BASE}/cache-status', timeout=5).json()
    print(f'\nDone! {len(status["cached"])}/{status["total_samples"]} samples cached '
          f'({status["total_events"]} total events)')
    if status['missing']:
        print(f'Missing: {", ".join(status["missing"])}')

if __name__ == '__main__':
    main()
