#!/usr/bin/env python3
"""TEAM18 igrupos detail-page miner: harvest title/desc/country/tag for gids.
Invite codes are NOT in static HTML (verified on gid 527264) -> leads, not candidates.
Checkpoints to team18-igrupos-mined.jsonl after every gid."""
import requests, re, json, time, sys, html as htmllib

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
S = requests.Session()

def clean(s):
    s = htmllib.unescape(s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def parse(gid, page):
    if "404 - Page Not Found" in page or "<title>404" in page:
        return {"gid": gid, "status": 404}
    t = re.search(r"<title>(.*?)</title>", page, re.S)
    title = clean(t.group(1)) if t else ""
    # description: the group text block after votes; grab visible body text lines
    h = re.sub(r"<(style|script)[^>]*>.*?</\1>", "", page, flags=re.S)
    txt = re.sub(r"<[^>]+>", "\n", h)
    lines = [clean(l) for l in txt.split("\n") if clean(l)]
    desc = ""
    for i, l in enumerate(lines):
        if l == title and i + 3 < len(lines):
            # description usually a few lines after title/votes block
            pass
    # heuristic: longest line that is not boilerplate
    cands = [l for l in lines if 40 < len(l) < 500 and not l.startswith(("Igrupos", "Te recomendamos", "Grupo solo", "Comparte", "GESTION", "Iniciar", "Registrarse", "Recibe"))]
    desc = cands[0] if cands else ""
    country = ""
    m = re.search(r"images/banderas64/([A-Z]{2})\.png", page)
    if m:
        country = m.group(1)
    tags = sorted(set(re.findall(r"tag/whatsapp/([a-z0-9\-]+)", page)))
    # votes
    votes = re.findall(r">(\d+)<", page)
    return {"gid": gid, "status": 200, "title": title, "description": desc,
            "country": country, "tags": tags, "url": f"https://www.igrupos.com/grupo/{gid}"}

def main():
    gids = list(range(526723, 526886)) + list(range(527087, 527265))
    done = set()
    out_path = f"{WAVE}/team18-igrupos-mined.jsonl"
    try:
        with open(out_path) as f:
            for line in f:
                try:
                    done.add(json.loads(line)["gid"])
                except Exception:
                    pass
    except FileNotFoundError:
        pass
    todo = [g for g in gids if g not in done]
    print(f"total {len(gids)} done {len(done)} todo {len(todo)}", flush=True)
    n200 = n404 = nerr = 0
    with open(out_path, "a") as f:
        for gid in todo:
            try:
                r = S.get(f"https://www.igrupos.com/grupo/{gid}", headers=UA, timeout=90)
                rec = parse(gid, r.text)
                if rec["status"] == 200:
                    n200 += 1
                else:
                    n404 += 1
            except Exception as e:
                rec = {"gid": gid, "status": "ERR", "error": str(e)[:120]}
                nerr += 1
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            if (n200 + n404 + nerr) % 25 == 0:
                print(f"progress {n200+n404+nerr}/{len(todo)} live={n200} 404={n404} err={nerr}", flush=True)
            time.sleep(0.15)
    print(f"DONE live={n200} 404={n404} err={nerr}", flush=True)

if __name__ == "__main__":
    main()
