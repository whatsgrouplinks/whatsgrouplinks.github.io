#!/usr/bin/env python3
"""team14 P5 combined run (memory-only, disk-write-block resilient):
1. fetch groupjoin.link Funny p4-35 + Health p2-5, parse RSC payload
2. filter blocked (adult/porn/scam/minors), dedupe vs union + within run
3. verify kept codes via curl STDOUT capture (no disk writes at all):
   LIVE = HTTP 200 + non-empty og:title; transport (timeout/429/5xx/curl-rc) -> retry once after 60s -> pending
4. print VERIFIED_JSON / PENDING_JSON to stdout (also try file writes as a bonus)
"""
import json, re, subprocess, time, concurrent.futures, sys

SCRATCH = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261106/scratch14"
WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261106"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
OG_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
PORN_RE = re.compile(r"porn|pornhub|xxx|nudes?|sex video|escort|call girl|randi|fuck|dick|pussy|boobs|anal|orgasm|cumshot|blowjob", re.I)
SCAM_RE = re.compile(r"receiver and loader|money[- ]?mule|double (your|the) money|counterfeit currency|buy (drugs|cocaine|heroin)|phishing|investment.*(double|2x|guaranteed profit)", re.I)
MINOR_RE = re.compile(r"\b(minor|under ?18|child|teen.*sex|school ?girl.*sex)\b", re.I)

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
        seg = h[m.start():m.start() + 4000]
        dm = re.search(r'"group_desc":"((?:[^"\\]|\\.)*)"', seg)
        lm = re.search(r'"link":"https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{22})"', seg)
        if not lm:
            continue
        cm = re.search(r'"category":\{"id":\d+,"category_name":"([^"]+)","category_slug":"([^"]+)"\}', seg)
        ym = re.search(r'"country":\{"id":\d+,"name":"([^"]+)","iso2":"([A-Z]{2})"', seg)
        tm = re.search(r'"tags":\[([^\]]*)\]', seg)
        out.append({"code": lm.group(1), "name": jstr(m.group(1)),
                    "desc_raw": jstr(dm.group(1)) if dm else "",
                    "tags_raw": tm.group(1) if tm else "",
                    "cat_slug": cm.group(2) if cm else "",
                    "country": ym.group(2) if ym else "International",
                    "tag": tag, "page": page, "total": total})
    return out

def clean_desc(raw, cat, country):
    d = (raw or "").strip()
    d = re.sub(r"^Welcome to my whatsapp group\s*", "", d, flags=re.I)
    d = re.sub(r"Please join my whatsapp group\.?\s*", "", d, flags=re.I)
    d = re.sub(r"\s+", " ", d).strip()
    if len(d) < 8 or d in ("$b7", "$b8") or set(d) <= set("$b78"):
        d = ""
    if d:
        sents = re.split(r"(?<=[.!?])\s+", d)
        d = " ".join(sents[:2])[:220].strip()
        if d and d[-1] not in ".!?":
            d += "."
        return d
    cname = {"funny": "funny jokes, memes and comedy", "health": "health, fitness and wellness tips"}.get(cat, cat)
    ctry = "" if country in ("International", "") else f" from {country}"
    return f"Join this {cat} WhatsApp group{ctry} to enjoy {cname} with active members. Chat, share and have fun with the community every day."

def check_once(code):
    """curl stdout capture; returns (http, og_title_or_'', transport_bool)."""
    try:
        r = subprocess.run(
            ["curl", "-s", "-w", "\n%{http_code}", "--max-time", "30", "-A", UA,
             f"https://chat.whatsapp.com/{code}"],
            capture_output=True, text=True, timeout=40)
    except subprocess.TimeoutExpired:
        return (0, "", True)
    if r.returncode != 0:
        return (0, "", True)
    out = r.stdout
    nl = out.rfind("\n")
    try:
        http = int(out[nl + 1:].strip())
    except ValueError:
        return (0, "", True)
    if http in (429, 500, 502, 503, 504) or http == 0:
        return (http, "", True)
    if http != 200:
        return (http, "", False)
    body = out[:nl]
    if len(body) < 5000:
        return (http, "", True)
    m = OG_RE.search(body)
    title = m.group(1).strip() if m else ""
    return (http, title, False)

def main():
    jobs = [("funny", p) for p in range(4, 36)] + [("health", p) for p in range(2, 6)]
    allc, totals = [], {}
    for tag, page in jobs:
        html_text = fetch(f"https://www.groupjoin.link/tag/{tag}?page={page}")
        if not html_text:
            print(f"FAIL {tag} p{page}", flush=True)
            continue
        cands = parse_page(html_text, tag, page)
        if cands and cands[0]["total"]:
            totals[tag] = cands[0]["total"]
        print(f"{tag} p{page}: {len(cands)} groups", flush=True)
        allc.extend(cands)
        time.sleep(1.0)
    print(f"HARVEST_DONE raw={len(allc)} totals={totals}", flush=True)
    union = set(json.load(open(f"{WAVE}/dedupe_union.json")))
    seen, kept, dropped = set(), [], {"union": 0, "dup": 0, "adult": 0, "porn": 0, "scam": 0, "minor": 0, "badname": 0}
    for c in allc:
        code = c["code"]
        if code in union:
            dropped["union"] += 1; continue
        if code in seen:
            dropped["dup"] += 1; continue
        seen.add(code)
        if c["cat_slug"] == "adult":
            dropped["adult"] += 1; continue
        blob = f"{c['name']} {c['desc_raw']} {c['tags_raw']}"
        if PORN_RE.search(blob):
            dropped["porn"] += 1; continue
        if SCAM_RE.search(blob):
            dropped["scam"] += 1; continue
        if MINOR_RE.search(blob):
            dropped["minor"] += 1; continue
        name = re.sub(r"\s+", " ", c["name"].strip())[:120]
        if not name or len(name) < 2:
            dropped["badname"] += 1; continue
        kept.append({"code": code, "name": name, "category": c["tag"],
                     "country": c["country"] if c["country"] else "International",
                     "description": clean_desc(c["desc_raw"], c["tag"], c["country"]),
                     "invite": f"https://chat.whatsapp.com/{code}", "image": ""})
    print(f"BUILD_DONE kept={len(kept)} dropped={dropped}", flush=True)
    live, pending, dead = [], [], []
    transport = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(check_once, it["code"]): it for it in kept}
        done = 0
        for fut in concurrent.futures.as_completed(futs):
            it = futs[fut]
            try:
                http, title, tr = fut.result()
            except Exception:
                http, title, tr = 0, "", True
            done += 1
            if done % 25 == 0:
                print(f"  verify {done}/{len(kept)} live={len(live)} transport={len(transport)} dead={len(dead)}", flush=True)
            if tr:
                transport.append(it)
            elif http == 200 and title:
                live.append(it)
            else:
                dead.append(it["code"])
    print(f"VERIFY_PASS1 live={len(live)} transport={len(transport)} dead={len(dead)}", flush=True)
    if transport:
        print("waiting 60s before transport retry...", flush=True)
        time.sleep(60)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            futs = {ex.submit(check_once, it["code"]): it for it in transport}
            for fut in concurrent.futures.as_completed(futs):
                it = futs[fut]
                try:
                    http, title, tr = fut.result()
                except Exception:
                    http, title, tr = 0, "", True
                if tr:
                    pending.append({"code": it["code"], "name": it["name"], "category": it["category"],
                                    "country": it["country"], "invite": it["invite"]})
                elif http == 200 and title:
                    live.append(it)
                else:
                    dead.append(it["code"])
    print(f"VERIFY_FINAL live={len(live)} pending={len(pending)} dead={len(dead)}", flush=True)
    print("VERIFIED_JSON " + json.dumps(live, ensure_ascii=False), flush=True)
    print("PENDING_JSON " + json.dumps(pending, ensure_ascii=False), flush=True)
    # bonus: try file writes
    for obj, path in [(live, f"{SCRATCH}/harvest_live.json"), (pending, f"{SCRATCH}/harvest_pend.json")]:
        for i in range(10):
            try:
                open(path, "wb", buffering=0).write(json.dumps(obj, ensure_ascii=False, indent=1).encode())
                print(f"wrote {path}", flush=True)
                break
            except PermissionError:
                time.sleep(3)

if __name__ == "__main__":
    main()
