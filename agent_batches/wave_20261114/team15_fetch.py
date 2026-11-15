#!/usr/bin/env python3
"""team15 wave_20261114: fetch whatshub.es grupo pages (sitemap positions 1601-2781),
extract chat.whatsapp.com codes from page/related-card descriptions, dedupe vs union,
verify live via chat.whatsapp.com og:title, screen content, write candidates.
Checkpoints to progress jsonl so partial work banks."""
import json, re, sys, time, random, html, os
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
PREV = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261113"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

ids = json.load(open(os.path.join(WAVE, "whatshub-ids.json")))
slice_ids = ids[1600:2781]  # positions 1601-2781
print(f"slice size: {len(slice_ids)} first={slice_ids[0]} last={slice_ids[-1]}", flush=True)

union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
prev_cands = set()
try:
    for c in json.load(open(os.path.join(PREV, "team15-candidates.json"))):
        prev_cands.add(c["invite"].rsplit("/", 1)[-1])
except Exception as e:
    print("prev candidates load fail:", e, flush=True)
print(f"union={len(union)} prev_team15={len(prev_cands)}", flush=True)

PROG = os.path.join(WAVE, "team15-progress.jsonl")
done = set()
if os.path.exists(PROG):
    for line in open(PROG):
        try:
            done.add(json.loads(line)["page_id"])
        except Exception:
            pass
print(f"already done: {len(done)}", flush=True)

BAD_TITLE = re.compile(r"(?i)\b(porn|xxx|sexo explicito|putas|onlyfans|escort|tigrinho|fortune tiger|sinais|plataformas pagantes|wjbet|casino|slots|apostas|airdrop|free money|dinheiro grátis|ganhar dinheiro|renda extra|binary|opções binárias|binarias)\b")

def unesc(s):
    return html.unescape(s).strip()

def parse_page(page_id, h):
    """Return list of (code, name, category_hint, tags). Codes from main desc + related cards."""
    out = []
    # main group name from title
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    main_name = unesc(re.sub(r"\s*\|\s*Grupo de WhatsApp.*$", "", m.group(1))) if m else ""
    # category from /c/ links
    cats = re.findall(r'href="/c/([^"]+)"', h)
    # main description block: any chat.whatsapp.com code in whole page, attributed to main group
    # related cards: each <a class="detalle-recomendacion" ...>...</a>
    cards = re.findall(r'<a class="detalle-recomendacion" href="/grupo/\d+"[^>]*>(.*?)</a>', h, re.S)
    for card in cards:
        nm = re.search(r'detalle-recomendacion-nombre[^>]*>(.*?)</span>', card, re.S)
        name = unesc(nm.group(1)) if nm else ""
        for code in set(re.findall(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})", card)):
            out.append((code, name, cats))
    # codes elsewhere on page (main description) -> main group name
    seen = {c for c, _, _ in out}
    for code in set(re.findall(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})", h)):
        if code not in seen:
            out.append((code, main_name, cats))
    return out

def verify(session, code):
    """Return (status, og_title): status in live/dead/pending."""
    url = f"https://chat.whatsapp.com/{code}"
    for attempt in range(3):
        try:
            r = session.get(url, timeout=60)
            if r.status_code == 429:
                return "pending", f"HTTP 429 attempt {attempt+1}"
            t = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]*)"', r.text)
            if not t:
                t = re.search(r'<meta[^>]*content="([^"]*)"[^>]*property="og:title"', r.text)
            title = html.unescape(t.group(1)).strip() if t else ""
            if title:
                return "live", title
            if attempt < 2:
                time.sleep(15)
        except requests.RequestException as e:
            if attempt < 2:
                time.sleep(15)
            else:
                return "pending", f"transport: {type(e).__name__}"
    return "dead", "empty og:title after 3 attempts"

def main():
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
                      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"})
    # controls
    st, title = verify(s, "KrDwdK8EIkB6vgauHg5M7N")
    print(f"CONTROL live: {st} title={title!r}", flush=True)
    if st != "live" or title != "JAY - PHP & Python Full Stack Developer":
        print("CONTROL LIVE FAILED - STOP", flush=True); return
    st2, title2 = verify(s, "ZzZzZzZzZzZzZzZzZzZzZzZz")
    print(f"CONTROL fabricated: {st2} title={title2!r}", flush=True)
    if st2 != "dead":
        print("CONTROL FABRICATED FAILED - STOP", flush=True); return

    raw = {}   # code -> (name, cats, page_id)
    fetch_fail = []
    consecutive_fail = 0
    for idx, pid in enumerate(slice_ids):
        if pid in done:
            continue
        try:
            r = s.get(f"https://www.whatshub.es/grupo/{pid}", timeout=30)
            if r.status_code != 200:
                fetch_fail.append({"page_id": pid, "reason": f"HTTP {r.status_code}"})
                consecutive_fail += 1
            else:
                consecutive_fail = 0
                for code, name, cats in parse_page(pid, r.text):
                    if code not in raw:
                        raw[code] = (name, cats, pid)
                        with open(os.path.join(WAVE, "team15-raw.jsonl"), "a") as rf:
                            rf.write(json.dumps({"code": code, "name": name, "cats": cats, "page_id": pid}) + "\n")
        except requests.RequestException as e:
            fetch_fail.append({"page_id": pid, "reason": f"{type(e).__name__}: {e}"})
            consecutive_fail += 1
        with open(PROG, "a") as f:
            f.write(json.dumps({"page_id": pid, "raw_codes": len(raw),
                                "fetch_fail": len(fetch_fail)}) + "\n")
        if consecutive_fail >= 5:
            print(f"THROTTLED: {consecutive_fail} consecutive fetch failures at idx {idx} pid {pid} - STOP", flush=True)
            break
        if (idx + 1) % 25 == 0:
            print(f"progress: {idx+1}/{len(slice_ids)} pages, raw codes so far {len(raw)}, fetch fails {len(fetch_fail)}", flush=True)
        time.sleep(4 + random.random() * 2)
    json.dump({"raw": {c: list(v) for c, v in raw.items()}, "fetch_fail": fetch_fail,
               "fetched_pages": len(done) + len(slice_ids) - len(fetch_fail) if False else None},
              open(os.path.join(WAVE, "team15-raw.json"), "w"))
    print(f"DONE fetch: raw codes {len(raw)} fetch fails {len(fetch_fail)}", flush=True)
    # verification + dedupe + screening happens in a second script using team15-raw.json

if __name__ == "__main__":
    main()
