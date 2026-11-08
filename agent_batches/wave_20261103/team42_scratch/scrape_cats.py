#!/usr/bin/env python3
"""TEAM 42 - harvest whatsappkanali.com /kategori pages (server-rendered RSC records)."""
import re, json, subprocess, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'

def fetch(url, out):
    r = subprocess.run(['curl','-sL','--max-time','120','-A',UA,'--compressed',url,'-o',out],
                       capture_output=True, text=True)
    return os.path.exists(out) and os.path.getsize(out) > 5000

def parse_records(h):
    out = []
    chunks = h.split('{\\"title\\":\\"')
    for ch in chunks[1:]:
        m = re.match(r'((?:[^\\]|\\.)*?)\\"[,}]', ch)
        if not m: continue
        try:
            title = m.group(1).encode('latin1').decode('unicode_escape')
        except Exception:
            title = m.group(1)
        m2 = re.search(r'categorySlug\\":\\"([^\\"]+)\\"', ch)
        m3 = re.search(r'inviteUrl\\":\\"(https://[^\\"]+)\\"', ch)
        if not (m2 and m3): continue
        url = m3.group(1).replace('\\u0026','&')
        cm = re.match(r'https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', url)
        if not cm: continue  # channels skipped
        out.append({'title': title, 'catslug': m2.group(1), 'code': cm.group(1)})
    return out

def main():
    slugs = [s.strip() for s in open(os.path.join(BASE, sys.argv[1])) if s.strip()]
    worker = sys.argv[2]
    allrecs = {}
    for slug in slugs:
        out = os.path.join(BASE, 'cat_%s_p1.html' % slug)
        ok = fetch('https://whatsappkanali.com/kategori/'+slug, out)
        print('W%s fetch %s ok=%s' % (worker, slug, ok), flush=True)
        if not ok: continue
        h = open(out, encoding='utf-8', errors='ignore').read()
        recs = parse_records(h)
        maxp = 1
        for ph in set(re.findall(r'href="(/kategori/'+re.escape(slug)+r'\?page=(\d+))"', h)):
            maxp = max(maxp, int(ph[1]))
        for p in range(2, maxp+1):
            outp = os.path.join(BASE, 'cat_%s_p%d.html' % (slug, p))
            if fetch('https://whatsappkanali.com/kategori/%s?page=%d' % (slug, p), outp):
                recs.extend(parse_records(open(outp, encoding='utf-8', errors='ignore').read()))
        print('W%s %s: %d recs, %d pages' % (worker, slug, len(recs), maxp), flush=True)
        for r in recs:
            allrecs.setdefault(r['code'], r)
    json.dump(allrecs, open(os.path.join(BASE, 'catrecs_%s.json' % worker), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('W%s TOTAL UNIQUE: %d' % (worker, len(allrecs)), flush=True)

if __name__ == '__main__':
    main()
