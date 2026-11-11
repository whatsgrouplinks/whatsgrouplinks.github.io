#!/usr/bin/env python3
"""TEAM 06 — Stage 3: enrich the 183 verified entries with full names (from <h1>)
and real descriptions (from og:description tail) by re-fetching their listing pages.
Re-screens full name + description; drops any that fail screening.
"""
import json, re, os, time, html, threading
from concurrent.futures import ThreadPoolExecutor
import requests, sys
sys.path.insert(0, "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111")
from team06_stage2 import is_scam_or_porn, classify  # reuse screening + classify

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S | re.I)
OGD_RE = re.compile(r'og:description\\",\\"content\\":\\"((?:[^\\"\\\\]|\\\\.)*)', re.I)

def enrich(url, session):
    try:
        r = session.get(url, timeout=25)
        if r.status_code != 200:
            return None
        h = r.text
        name, desc = None, None
        m = H1_RE.search(h)
        if m:
            t = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
            t = re.sub(r"^grupo de whatsapp\s+", "", t, flags=re.I)
            t = re.sub(r"\s*[-–—|]\s*[^-–—|]{2,40}$", "", t).strip()
            if t:
                name = t[:120]
        m = OGD_RE.search(h)
        if m:
            d = html.unescape(m.group(1)).strip()
            # strip "Grupo de WhatsApp <name>, na categoria <cat>. " prefix
            d2 = re.sub(r"^grupo de whatsapp .{3,150}?,\s*na categoria [^.]{2,40}\.\s*", "", d, flags=re.I)
            if d2 and d2 != d:
                desc = d2[:300]
            elif d and not d.lower().startswith("grupo de whatsapp"):
                desc = d[:300]
        return {"name": name, "desc": desc}
    except Exception:
        return None

def main():
    verified = json.load(open(os.path.join(WAVE, "team06-leads-slice6.json")))
    cands = json.load(open(os.path.join(WAVE, "team06-stage1-candidates.json")))
    code2src = {}
    for c in cands:
        code2src.setdefault(c["code"], c["source"])
    session = requests.Session()
    session.headers.update(UA)
    results = {}

    def work(entry):
        code = entry["invite"].rsplit("/", 1)[-1]
        src = code2src.get(code)
        if not src:
            return
        en = enrich(src, session)
        time.sleep(0.5)
        results[code] = en

    with ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(work, verified))
    json.dump(results, open(os.path.join(WAVE, "team06-stage3-enrich.json"), "w"), ensure_ascii=False)

    out, dropped = [], []
    for e in verified:
        code = e["invite"].rsplit("/", 1)[-1]
        en = results.get(code) or {}
        name = en.get("name") or e["name"]
        desc = en.get("desc") or e["description"]
        reason = is_scam_or_porn(name + " " + desc)
        if reason:
            dropped.append({"code": code, "reason": reason})
            continue
        e2 = dict(e)
        e2["name"] = name
        e2["description"] = desc
        out.append(e2)
    json.dump(out, open(os.path.join(WAVE, "team06-leads-slice6.json"), "w"), ensure_ascii=False)
    summ = json.load(open(os.path.join(WAVE, "team06-leads-slice6-summary.json")))
    summ["exclusions"] = summ.get("exclusions", []) + dropped
    summ["verified"] = len(out)
    summ["notes"] += (f" Stage3 enrichment: re-fetched {len(verified)} listing pages; "
                      f"full names recovered from <h1>, real descriptions from og:description; "
                      f"{len(dropped)} dropped on re-screen; "
                      f"{sum(1 for e in out if not e['description'].startswith('Grupo de WhatsApp'))} entries now carry a real description.")
    json.dump(summ, open(os.path.join(WAVE, "team06-leads-slice6-summary.json"), "w"), ensure_ascii=False, indent=2)
    print(f"ENRICHED verified={len(out)} dropped={len(dropped)} real-desc={sum(1 for e in out if not e['description'].startswith('Grupo de WhatsApp'))}")

if __name__ == "__main__":
    main()
