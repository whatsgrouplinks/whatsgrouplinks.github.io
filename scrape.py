#!/usr/bin/env python3
"""Scrape groupizo.com group listings: name, category, description, image, real WhatsApp invite link."""
import re, json, html, time, sys
import urllib.request, urllib.error

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def fetch(url, timeout=20):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return None

def get_group_urls():
    urls = []
    for i in range(1, 12):
        xml = fetch(f"https://groupizo.com/sitemaps/sitemap-groups-{i}.xml")
        if xml:
            urls += re.findall(r'<loc>(https://groupizo\.com/[^<]+)</loc>', xml)
    return urls

def parse_group_page(content, url):
    d = {'url': url, 'name': '', 'category': '', 'description': '', 'image': '', 'invite': '', 'country': ''}
    # name from h1
    m = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
    if m:
        d['name'] = html.unescape(re.sub(r'<[^>]+>', '', m.group(1)).strip())
    # meta description: "Join X, a WhatsApp group listed under Y on Groupizo. ..."
    m = re.search(r'<meta name="description" content="([^"]+)"', content)
    if m:
        desc = html.unescape(m.group(1))
        d['description'] = desc
        cm = re.search(r'listed under (\w[\w &]*) on', desc)
        if cm:
            d['category'] = cm.group(1).strip()
    # group image: pps.whatsapp.net image with group name alt (not logo)
    imgs = re.findall(r'<img[^>]+src="(https://pps\.whatsapp\.net/[^"]+)"[^>]*alt="([^"]*)"', content)
    if not imgs:
        imgs = re.findall(r'<img[^>]+alt="([^"]*)"[^>]+src="(https://pps\.whatsapp\.net/[^"]+)"', content)
        imgs = [(s, a) for a, s in imgs]
    for src, alt in imgs:
        if 'logo' not in alt.lower() and len(alt) > 3:
            d['image'] = src.split('?')[0] + '?w=200'  # keep simple
            d['image'] = src
            break
    # verify URL from join button
    m = re.search(r"window\.location\.href='(/verify/[^']+)'", content)
    if m:
        d['verify'] = 'https://groupizo.com' + m.group(1)
    # country flag
    m = re.search(r'flagcdn\.com/w40/([a-z]{2})\.png', content)
    if m:
        d['country'] = m.group(1).upper()
    return d

def get_invite(verify_url):
    content = fetch(verify_url)
    if not content:
        return ''
    m = re.search(r'https://chat\.whatsapp\.com/[A-Za-z0-9]+', content)
    return m.group(0) if m else ''

def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else '/home/hatch/workspace/whatsapp-groups-site/groups.json'
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    start_from = int(sys.argv[3]) if len(sys.argv) > 3 else 0

    urls = get_group_urls()
    print(f"Found {len(urls)} group URLs", flush=True)
    if limit:
        urls = urls[start_from:start_from+limit]
    else:
        urls = urls[start_from:]

    # resume support
    existing = []
    try:
        with open(out_path) as f:
            existing = json.load(f)
        done_urls = {g['url'] for g in existing}
        urls = [u for u in urls if u not in done_urls]
        print(f"Resuming: {len(existing)} done, {len(urls)} remaining", flush=True)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    results = existing
    for i, url in enumerate(urls):
        page = fetch(url)
        if not page:
            continue
        g = parse_group_page(page, url)
        if not g['name'] or not g.get('verify'):
            continue
        # skip groups with inactive links (no verify invite)
        g['invite'] = get_invite(g['verify'])
        if not g['invite']:
            continue
        g.pop('verify', None)
        results.append(g)
        if (i + 1) % 25 == 0:
            with open(out_path, 'w') as f:
                json.dump(results, f, ensure_ascii=False)
            print(f"  {i+1}/{len(urls)} scraped, {len(results)} valid", flush=True)
        time.sleep(0.3)  # be polite

    with open(out_path, 'w') as f:
        json.dump(results, f, ensure_ascii=False)
    print(f"DONE: {len(results)} groups with valid invite links", flush=True)

if __name__ == '__main__':
    main()
