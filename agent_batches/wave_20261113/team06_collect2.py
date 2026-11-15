#!/usr/bin/env python3
"""team06 linkado collector v2: curl-based fetch, 4 workers, 90s timeout."""
import json, re, sys, time, os, subprocess
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261113"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

def fetch(url):
    try:
        p = subprocess.run(["curl", "-s", "-L", "--max-time", "90", "-A", UA, url],
                           capture_output=True, timeout=100)
        if p.returncode == 0 and p.stdout:
            return p.stdout.decode("utf-8", "ignore")
    except Exception:
        pass
    return None

def parse(html, url):
    if not html:
        return None
    codes = re.findall(r"chat\.whatsapp\.com/([A-Za-z0-9_\-]{15,})", html)
    title = ""
    m = re.search(r'<meta property="og:title" content="([^"]*)"', html)
    if m: title = m.group(1).strip()
    if not title:
        m = re.search(r"<title>(.*?)</title>", html, re.S)
        if m: title = re.sub(r"\s+", " ", m.group(1)).strip()
    desc = ""
    m = re.search(r'<meta (?:name|property)="(?:description|og:description)" content="([^"]*)"', html)
    if m: desc = m.group(1).strip()
    return {"url": url, "title": title, "codes": sorted(set(codes)), "desc": desc[:300]}

def main(start, end, workers=4):
    urls = open(os.path.join(WAVE, "team06_urls.txt")).read().splitlines()
    batch = urls[start:end]
    out_path = os.path.join(WAVE, f"team06_pages_{start}_{end}.json")
    results = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for i, res in enumerate(ex.map(lambda u: parse(fetch(u), u), batch)):
            if res is not None:
                results.append(res)
            if (i + 1) % 25 == 0:
                with open(out_path, "w") as f:
                    json.dump(results, f, ensure_ascii=False, indent=1)
                print(f"{i+1}/{len(batch)} fetched, {len(results)} ok, {sum(1 for r in results if r['codes'])} with codes, {time.time()-t0:.0f}s", flush=True)
    with open(out_path, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print(f"DONE {start}-{end}: {len(results)} pages, {sum(1 for r in results if r['codes'])} with codes")

if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 4)
