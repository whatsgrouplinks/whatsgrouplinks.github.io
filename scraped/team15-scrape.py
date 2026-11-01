#!/usr/bin/env python3
"""TEAM 15: Islamic WhatsApp groups mega-scraper v2 — name-from-context extraction."""
import json, os, re, time, html as ihtml
import urllib.request

SITE_DIR = os.path.expanduser('~/workspace/whatsapp-groups-site')
SCRAPED = os.path.join(SITE_DIR, 'scraped')
OUT = os.path.join(SCRAPED, 'team15-islamic.json')

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'

PAGES = [
    'https://77links.com/islamic-whatsapp-group-links/',
    'https://77links.com/arabic-whatsapp-group-links/',
    'https://groupda.com/spiritual/best-islamic-whatsapp-group-link-2022/',
    'https://whatgroups.com/online-quran-students-whatsapp-group-links/',
    'https://freewagroup.com/naat-whatsapp-group-links/',
    'https://whatzgrouplink.com/tag/pakistani-islamic-whatsapp-group/',
    'http://grouplink.com.in/malayalam-islamic-whatsapp-group-links/',
    'https://freewagroup.com/islamic-whatsapp-group-links/',
    'https://www.whatsappgrouplinkspk.com/islamic-whatsapp-group-links-pakistan/',
]

SKIP_TEXTS = {'join', 'join group', 'click here', 'join now', 'link', 'join link', 'join here',
              'join group link', 'view all group links', 'whatsapp group links'}

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode('utf-8', errors='ignore')

def strip_tags(s):
    s = re.sub(r'<script.*?</script>', ' ', s, flags=re.I | re.S)
    s = re.sub(r'<style.*?</style>', ' ', s, flags=re.I | re.S)
    s = re.sub(r'<[^>]+>', '\n', s)
    s = re.sub(r'<[^>]*$', '', s)  # drop unterminated trailing tag fragment
    s = ihtml.unescape(s)
    s = re.sub(r'[ \t]+', ' ', s)
    return s

def extract_name_from_context(pre_text):
    """Take the last meaningful non-skip line as group name."""
    lines = [l.strip() for l in pre_text.split('\n') if l.strip()]
    # drop trailing generic lines
    while lines and lines[-1].lower() in SKIP_TEXTS:
        lines.pop()
    if not lines:
        return ''
    name = lines[-1]
    # also handle "Name | description" style — take before |
    if '|' in name and len(name.split('|')[0].strip()) > 2:
        name = name.split('|')[0].strip()
    name = re.sub(r'\s+', ' ', name).strip()
    return name[:120]

def extract(html_text):
    results = []
    # find every invite link occurrence
    for m in re.finditer(r'https?://chat\.whatsapp\.com/([A-Za-z0-9_-]+)', html_text):
        url = m.group(0).split('?')[0]
        code = m.group(1)
        # look back up to 1200 chars for the name context
        pre = html_text[max(0, m.start()-1200):m.start()]
        text = strip_tags(pre)
        name = extract_name_from_context(text)
        if not name or name.lower() in SKIP_TEXTS or len(name) < 3:
            continue
        results.append((name, url, code))
    return results

def main():
    existing = set()
    gj = os.path.join(SITE_DIR, 'groups.json')
    if os.path.exists(gj):
        for g in json.load(open(gj)):
            code = (g.get('invite','') or '').strip().split('/')[-1].split('?')[0]
            if code: existing.add(code)
    for fn in os.listdir(SCRAPED):
        if fn.endswith('.json') and fn != 'team15-islamic.json':
            try:
                for g in json.load(open(os.path.join(SCRAPED, fn))):
                    code = (g.get('invite','') or '').strip().split('/')[-1].split('?')[0]
                    if code: existing.add(code)
            except Exception:
                pass
    print(f"Existing codes to skip: {len(existing)}")

    all_groups, seen = [], set()
    for url in PAGES:
        try:
            print(f"Fetching: {url}")
            h = fetch(url)
            pairs = extract(h)
            added = 0
            for name, link, code in pairs:
                if code in existing or code in seen:
                    continue
                seen.add(code)
                all_groups.append({
                    'name': name,
                    'category': 'Islamic',
                    'description': f"Join {name}, an Islamic WhatsApp group for Quran, naat, bayan and religious discussions.",
                    'image': '',
                    'invite': link,
                    'country': '',
                })
                added += 1
            print(f"  raw pairs: {len(pairs)}, new unique: {added}")
        except Exception as e:
            print(f"  ERROR: {e}")
        time.sleep(0.5)

    with open(OUT, 'w') as f:
        json.dump(all_groups, f, indent=2, ensure_ascii=False)
    print(f"\nTOTAL new Islamic groups: {len(all_groups)} -> {OUT}")

if __name__ == '__main__':
    main()
