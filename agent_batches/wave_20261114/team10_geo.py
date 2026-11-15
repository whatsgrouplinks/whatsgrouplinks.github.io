#!/usr/bin/env python3
"""TEAM10: retry ?unirse=1 on the 50 geo-gated igrupos gids team12 banked as leads.
Straight retry, no header spoofing: if the country gate still withholds the
invite, the gid stays a lead for a matching-country browser leg."""
import requests, re, json, time, sys, html as htmllib
sys.path.insert(0, '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114')
from team10_lib import UA

W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
S = requests.Session()

def clean(s):
    return re.sub(r"\s+", " ", htmllib.unescape(s or "")).strip()

def classify(gid, page, status):
    rec = {"gid": gid, "http": status}
    if status != 200:
        rec["class"] = "http_" + str(status)
        return rec
    if "404 - Page Not Found" in page or "<title>404" in page:
        rec["class"] = "deleted_404"
        return rec
    codes = sorted(set(re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{10,30})', page)))
    # exclude share URLs: web.whatsapp.com/send is not chat.whatsapp.com, fine
    if codes:
        rec["class"] = "wa_code"
        rec["codes"] = codes
        return rec
    # real telegram join link (not t.me/share)
    tg = sorted(set(re.findall(r'https?://t\.me/(?!share\b)([A-Za-z0-9_]+)', page)))
    m_country = re.search(r'Grupo solo para gente de\s*<img[^>]*banderas64/([A-Z]{2})', page)
    m_detect = re.search(r'Pa[^<]*s detectado\s*<img[^>]*banderas64/([A-Z]{2})', page)
    rec["need_country"] = m_country.group(1) if m_country else ""
    rec["detected_country"] = m_detect.group(1) if m_detect else ""
    if tg:
        rec["class"] = "telegram_only"
        rec["tg"] = tg
        return rec
    if rec["need_country"] and rec["detected_country"] and rec["need_country"] != rec["detected_country"]:
        rec["class"] = "geo_gated"
        return rec
    # no invite visible, no country mismatch found
    title = re.search(r"<title>(.*?)</title>", page, re.S)
    rec["title"] = clean(title.group(1)) if title else ""
    rec["class"] = "no_invite_visible"
    return rec

def main():
    geo = json.load(open(f"{W}/team10-geo-slice.json"))
    gids = [g["gid"] for g in geo]
    done = set()
    out_path = f"{W}/team10-geo-results.jsonl"
    try:
        with open(out_path) as f:
            for line in f:
                try: done.add(json.loads(line)["gid"])
                except Exception: pass
    except FileNotFoundError:
        pass
    todo = [g for g in gids if g not in done]
    print(f"total {len(gids)} done {len(done)} todo {len(todo)}", flush=True)
    with open(out_path, "a") as f:
        for gid in todo:
            t0 = time.time()
            try:
                r = S.get(f"https://www.igrupos.com/grupo/{gid}?unirse=1", headers=UA, timeout=60)
                rec = classify(gid, r.text, r.status_code)
            except Exception as e:
                rec = {"gid": gid, "class": "transport_error", "error": f"{type(e).__name__}: {str(e)[:120]}"}
            rec["secs"] = round(time.time() - t0, 1)
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            print(gid, rec["class"], rec.get("codes", rec.get("need_country", "")), f"{rec['secs']}s", flush=True)
            time.sleep(0.5)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
