#!/usr/bin/env python3
"""Slow sequential live spot re-check of a stratified sample of the clean file.
curl with browser UA, 1s spacing, one retry on empty og:title. Writes
sample_recheck.json into the wave dir."""
import json, re, subprocess, time, os, random

WAVE = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261108')
clean = json.load(open(os.path.join(WAVE, 'wave_20261108_verified_clean.json')))
random.seed(20261108)
# stratified: every 59th item (~30) + 5 random
sample = clean[::59][:30]
extra = [c for c in random.sample(clean, 10) if c not in sample][:5]
sample = sample + extra
print('sample size:', len(sample))

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0 Safari/537.36')

def check(code):
    url = f'https://chat.whatsapp.com/{code}'
    for attempt in range(2):
        try:
            r = subprocess.run(['curl', '-s', '-L', '--max-time', '25',
                                '-A', UA, url],
                               capture_output=True, text=True, timeout=40)
            html = r.stdout or ''
            m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html)
            title = (m.group(1).strip() if m else '')
            if title and title not in ('WhatsApp Group', 'Join this group on WhatsApp'):
                return True, title
            if attempt == 0:
                time.sleep(5)
        except Exception as e:
            if attempt == 0:
                time.sleep(5)
            else:
                return False, f'transport:{e}'
    return False, 'empty-og-title-after-retry'

results = []
for i, item in enumerate(sample):
    code = item['invite'].rsplit('/', 1)[-1]
    live, title = check(code)
    results.append({'code': code, 'name': item['name'], 'live': live,
                    'og_title': title})
    print(f"{i+1}/{len(sample)} {code} {'LIVE' if live else 'DEAD'} {title[:50]}")
    time.sleep(1)

live_n = sum(1 for r in results if r['live'])
print(f'RESULT: {live_n}/{len(results)} live')
with open(os.path.join(WAVE, 'sample_recheck.json'), 'w') as f:
    json.dump({'sampled': len(results), 'live': live_n, 'results': results},
              f, ensure_ascii=False, indent=1)
