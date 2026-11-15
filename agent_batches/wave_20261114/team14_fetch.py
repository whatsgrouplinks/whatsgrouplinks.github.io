#!/usr/bin/env python3
"""team14: fetch whatshub.es grupo pages 801-1600, mine invite codes from related-group cards.
v2: fresh Session per request (proxy keep-alive reuse was failing every other request),
retry with spaced backoff, 5s pause between pages."""
import json, re, time, html, os
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
      "Connection": "close"}

ids = json.load(open(f"{WAVE}/team14-slice-ids.json"))
ckpt_path = f"{WAVE}/team14-fetch-checkpoint.json"
done = set()
raw = {}
fails = []
if os.path.exists(ckpt_path):
    ck = json.load(open(ckpt_path))
    done = set(ck.get("done", []))
    raw = ck.get("raw", {})
    fails = ck.get("fails", [])
    print(f"resumed: {len(done)} done, {len(raw)} raw codes, {len(fails)} fails", flush=True)

CARD_RE = re.compile(r'<a class="detalle-recomendacion" href="/grupo/(\d+)"[^>]*>(.*?)</a>', re.S)
NAME_RE = re.compile(r'detalle-recomendacion-nombre"[^>]*>(.*?)</span>', re.S)
CODE_RE = re.compile(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})')
TAG_RE = re.compile(r'<span class="tag[^"]*"[^>]*>([^<]+)</span>')

PAUSE = 5.0

def fetch_page(gid):
    for attempt in range(3):
        s = requests.Session()
        s.headers.update(UA)
        try:
            r = s.get(f"https://www.whatshub.es/grupo/{gid}", timeout=60)
            if r.status_code == 200:
                return r.text
            print(f"[{gid}] HTTP {r.status_code} attempt {attempt+1}", flush=True)
            if r.status_code in (429, 503):
                time.sleep(30)
        except Exception as e:
            print(f"[{gid}] {type(e).__name__} attempt {attempt+1}: {str(e)[:100]}", flush=True)
        finally:
            s.close()
        time.sleep(10 * (attempt + 1))
    return None

consecutive_fail = 0
for gid in ids:
    if gid in done:
        continue
    # drop stale fail entries for this id (will re-attempt)
    fails = [f for f in fails if f.get("id") != gid]
    html_text = fetch_page(gid)
    if html_text is None:
        fails.append({"id": gid, "error": "fetch failed after 3 attempts"})
        consecutive_fail += 1
        print(f"[{gid}] FAILED (consecutive {consecutive_fail})", flush=True)
    else:
        consecutive_fail = 0
        for rel_id, body in CARD_RE.findall(html_text):
            m = CODE_RE.search(body)
            if not m:
                continue
            code = m.group(1)
            nm = NAME_RE.search(body)
            name = html.unescape(nm.group(1).strip()) if nm else ""
            tags = [html.unescape(t).strip() for t in TAG_RE.findall(body)]
            if code not in raw:
                raw[code] = {"name": name, "tags": tags, "src_grupo": gid, "rel_grupo": int(rel_id)}
        done.add(gid)
        if len(done) % 25 == 0:
            print(f"[{gid}] done={len(done)} raw={len(raw)} fails={len(fails)}", flush=True)
    if len(done) % 10 == 0:
        json.dump({"done": sorted(done), "raw": raw, "fails": fails},
                  open(ckpt_path, "w"), ensure_ascii=False)
    if consecutive_fail >= 5:
        print("STOPPING: 5 consecutive failures - banking checkpoint", flush=True)
        break
    time.sleep(PAUSE)

json.dump({"done": sorted(done), "raw": raw, "fails": fails},
          open(ckpt_path, "w"), ensure_ascii=False)
print(f"FINISH done={len(done)} raw={len(raw)} fails={len(fails)}", flush=True)
