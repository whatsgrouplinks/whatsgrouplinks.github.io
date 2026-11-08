#!/usr/bin/env python3
"""team14 P5 groupjoin.link harvest: Funny pages 4-35, Health pages 2-5.
Parses the Next.js RSC payload embedded in each tag page (full group JSON).
Writes raw candidates to scratch14/raw.json.
"""
import json, re, subprocess, time

SCRATCH = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261106/scratch14"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def fetch(url):
    for attempt in range(3):
        r = subprocess.run(["curl", "-sL", "--max-time", "60", "-A", UA, url],
                           capture_output=True, text=True)
        if r.returncode == 0 and len(r.stdout) > 5000:
            return r.stdout
        print(f"  fetch fail {url} attempt {attempt+1} rc={r.returncode} len={len(r.stdout)}", flush=True)
        time.sleep(5)
    return ""

def jstr(s):
    try:
        return json.loads('"' + s + '"')
    except Exception:
        return s

def parse_page(html_text, tag, page):
    h = html_text.replace('\\"', '"').replace("\\u0026", "&")
    out = []
    total_m = re.search(r'"currentCount":(\d+)', h)
    total = int(total_m.group(1)) if total_m else None
    for m in re.finditer(r'"group_title":"((?:[^"\\]|\\.)*)"', h):
        start = m.start()
        seg = h[start:start + 4000]
        title = jstr(m.group(1))
        dm = re.search(r'"group_desc":"((?:[^"\\]|\\.)*)"', seg)
        desc = jstr(dm.group(1)) if dm else ""
        lm = re.search(r'"link":"https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{22})"', seg)
        if not lm:
            continue
        code = lm.group(1)
        cm = re.search(r'"category":\{"id":\d+,"category_name":"([^"]+)","category_slug":"([^"]+)"\}', seg)
        cat_name = cm.group(1) if cm else ""
        cat_slug = cm.group(2) if cm else ""
        ym = re.search(r'"country":\{"id":\d+,"name":"([^"]+)","iso2":"([A-Z]{2})"', seg)
        iso2 = ym.group(2) if ym else "International"
        tm = re.search(r'"tags":\[([^\]]*)\]', seg)
        tags = tm.group(1) if tm else ""
        out.append({"code": code, "name": title, "desc_raw": desc, "tags_raw": tags,
                    "cat_name": cat_name, "cat_slug": cat_slug, "country": iso2,
                    "tag": tag, "page": page, "total": total})
    return out

def main():
    jobs = [("funny", p) for p in range(4, 36)] + [("health", p) for p in range(2, 6)]
    allc = []
    totals = {}
    for tag, page in jobs:
        url = f"https://www.groupjoin.link/tag/{tag}?page={page}"
        html_text = fetch(url)
        if not html_text:
            print(f"FAIL {tag} p{page}", flush=True)
            continue
        cands = parse_page(html_text, tag, page)
        if cands and cands[0]["total"]:
            totals[tag] = cands[0]["total"]
        print(f"{tag} p{page}: {len(cands)} groups", flush=True)
        allc.extend(cands)
        # best-effort incremental snapshot: ONE attempt, never blocks the run
        try:
            with open(f"{SCRATCH}/raw.jsonl", "wb", buffering=0) as f:
                f.write(("\n".join(json.dumps(c, ensure_ascii=False) for c in allc) + "\n").encode("utf-8"))
        except PermissionError:
            print(f"  snapshot EPERM (kept in memory)", flush=True)
        time.sleep(1.0)
    print("TOTAL raw:", len(allc), "totals:", totals, flush=True)
    payload = json.dumps({"candidates": allc, "totals": totals}, ensure_ascii=False, indent=1).encode("utf-8")
    for i in range(60):
        try:
            with open(f"{SCRATCH}/raw.json", "wb", buffering=0) as f:
                f.write(payload)
            print("raw.json written", flush=True)
            break
        except PermissionError:
            print(f"raw.json write EPERM, retry {i}", flush=True)
            time.sleep(5)
    else:
        print("raw.json WRITE FAILED after retries", flush=True)

if __name__ == "__main__":
    main()
