"""Team24 wave 20261112 miner: fetch whtspgrouplink listing pages, extract codes+names.
Usage: python3 team24_mine12.py [start_index] [count]
Checkpoints after every page: team24_mined12.json (mined slugs),
team24_candidates12.json ({code: {code, page, name}}).
Extraction: <li>Name - <a href=chat.whatsapp.com/CODE>, table <tr><td>Name</td>
<td><a href=...CODE>, /invite/ format, ANY fallback. Glued-code guard: a 23/24-char
capture followed by 'tps://' is trimmed to 22 chars (malformed duplicated https://).
"""
import urllib.request, gzip, json, time, os, re, sys, html

W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
PREV = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
      "Accept": "text/html;q=0.9,*/*;q=0.8", "Accept-Encoding": "gzip, deflate"}

def fetch(url, timeout=90):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        if 'gzip' in r.headers.get('Content-Encoding', ''):
            raw = gzip.decompress(raw)
        return raw.decode('utf-8', errors='replace')

LI_RE = re.compile(
    r'<li[^>]*>(.*?)<a\s[^>]*href="https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})"',
    re.DOTALL | re.IGNORECASE)
TR_RE = re.compile(
    r'<tr[^>]*>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>.*?<a\s[^>]*href="https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})"',
    re.DOTALL | re.IGNORECASE)
ANY_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')

def clean_name(raw):
    name = re.sub(r'<[^>]+>', ' ', raw)
    name = html.unescape(name)
    name = re.sub(r'\s+', ' ', name).strip(' \u2013-\u2014|\u2022\u00b7')
    name = name.strip()
    # strip trailing "Join Group" / "Join" artefacts
    name = re.sub(r'\s*[-–—]\s*Join\s*$', '', name, flags=re.I)
    return name[:140]

def extract(page, url, cands):
    seen_here = set()
    added_named = 0
    for m in list(LI_RE.finditer(page)) + list(TR_RE.finditer(page)):
        raw_name, code = m.group(1), m.group(2)
        if len(code) > 22 and page[m.end(2):m.end(2)+6].startswith("tps://"):
            code = code[:22]
        if code in seen_here:
            continue
        seen_here.add(code)
        name = clean_name(raw_name)
        if code not in cands or not cands[code].get("name"):
            cands[code] = {"code": code, "page": url, "name": name}
            added_named += 1
    for m in ANY_RE.finditer(page):
        code = m.group(1)
        if len(code) > 22 and page[m.end(1):m.end(1)+6].startswith("tps://"):
            code = code[:22]
        if code not in cands:
            cands[code] = {"code": code, "page": url, "name": ""}
    return len(cands)

def main():
    leads = json.load(open(PREV + "team24-whtspgrouplink-leads.json"))
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    count = int(sys.argv[2]) if len(sys.argv) > 2 else len(leads) - start
    os.makedirs(W + "team24_raw", exist_ok=True)
    cand_file = W + "team24_candidates12.json"
    mined_file = W + "team24_mined12.json"
    cands = json.load(open(cand_file)) if os.path.exists(cand_file) else {}
    mined = json.load(open(mined_file)) if os.path.exists(mined_file) else []
    mined_set = set(mined)
    for idx in range(start, min(start + count, len(leads))):
        url = leads[idx]
        slug = url.rstrip('/').split('/')[-1] or 'home'
        fn = f"{slug}.html"
        path = W + "team24_raw/" + fn
        if fn in mined_set:
            print(f"[{idx}] skip {slug} (already mined)", flush=True)
            continue
        try:
            t0 = time.time()
            page = fetch(url)
            open(path, "w").write(page)
            before = len(cands)
            extract(page, url, cands)
            mined.append(fn); mined_set.add(fn)
            json.dump(cands, open(cand_file, "w"), indent=1, ensure_ascii=False)
            json.dump(mined, open(mined_file, "w"), indent=1)
            print(f"[{idx}] {slug}: {len(page)} bytes {time.time()-t0:.1f}s new={len(cands)-before} total={len(cands)}", flush=True)
        except Exception as e:
            print(f"[{idx}] {slug}: FETCH ERR {type(e).__name__}: {e}", flush=True)
            json.dump(mined, open(mined_file, "w"), indent=1)
        time.sleep(1.5)
    print(f"MINE DONE mined={len(mined)} total_cands={len(cands)}")

if __name__ == "__main__":
    main()
