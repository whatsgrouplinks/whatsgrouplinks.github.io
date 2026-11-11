"""Mine whtspgrouplink listing pages from leads file.
Usage: python3 team24_mine.py [start_index] [count]
Fetches pages sequentially (site is slow), extracts chat.whatsapp.com codes
plus nearby group names, saves raw HTML + candidates checkpoint.
"""
import urllib.request, gzip, json, time, os, re, sys, html

W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
      "Accept": "text/html;q=0.9,*/*;q=0.8", "Accept-Encoding": "gzip, deflate"}

def fetch(url, timeout=90):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        if 'gzip' in r.headers.get('Content-Encoding', ''):
            raw = gzip.decompress(raw)
        return raw.decode('utf-8', errors='replace')

leads = json.load(open(W + "team24-leads-in.json"))
start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
count = int(sys.argv[2]) if len(sys.argv) > 2 else 60
os.makedirs(W + "team24_raw", exist_ok=True)
cand_file = W + "team24_candidates.json"
cands = json.load(open(cand_file)) if os.path.exists(cand_file) else {}
mined_file = W + "team24_mined.json"
mined = json.load(open(mined_file)) if os.path.exists(mined_file) else []

CODE_RE = re.compile(r'chat\.whatsapp\.com/([A-Za-z0-9]{20,24})')

for idx in range(start, min(start + count, len(leads))):
    entry = leads[idx]
    url = entry["url"] if isinstance(entry, dict) else entry
    slug = url.rstrip('/').split('/')[-1] or 'home'
    fn = f"{slug}.html"
    path = W + "team24_raw/" + fn
    if fn in mined:
        print(f"[{idx}] skip {slug} (already mined)", flush=True)
        continue
    try:
        t0 = time.time()
        page = fetch(url)
        open(path, "w").write(page)
        # extract codes with nearby context for names
        found = 0
        for m in CODE_RE.finditer(page):
            code = m.group(1)
            # look backwards up to 600 chars for a group name-ish heading
            ctx = page[max(0, m.start()-800):m.start()]
            # strip tags
            txt = re.sub(r'<[^>]+>', ' ', ctx)
            txt = html.unescape(txt)
            txt = re.sub(r'\s+', ' ', txt).strip()
            name = txt[-120:] if txt else ""
            if code not in cands:
                cands[code] = {"code": code, "page": url, "context": name}
                found += 1
        mined.append(fn)
        json.dump(cands, open(cand_file, "w"), indent=1, ensure_ascii=False)
        json.dump(mined, open(mined_file, "w"), indent=1)
        print(f"[{idx}] {slug}: {len(page)} bytes {time.time()-t0:.1f}s new_codes={found} total_cands={len(cands)}", flush=True)
    except Exception as e:
        print(f"[{idx}] {slug}: FETCH ERR {e}", flush=True)
        json.dump(mined, open(mined_file, "w"), indent=1)
    time.sleep(1.5)
print(f"MINE DONE mined={len(mined)} total_cands={len(cands)}")
