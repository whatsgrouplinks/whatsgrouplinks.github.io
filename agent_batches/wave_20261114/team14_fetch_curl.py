#!/usr/bin/env python3
"""team14 v3: fetch whatshub.es grupo pages 801-1600 via curl subprocess.
curl proved robust in manual tests while requests+proxy failed ~50% wave-wide.
Same checkpoint format as v2 (team14-fetch-checkpoint.json)."""
import json, re, time, html, os, subprocess

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

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

def fetch_page(gid):
    for attempt in range(3):
        try:
            p = subprocess.run(
                ["curl", "-sS", "-A", UA, "--max-time", "60",
                 f"https://www.whatshub.es/grupo/{gid}"],
                capture_output=True, text=True, timeout=70)
            if p.returncode == 0 and len(p.stdout) > 1000:
                return p.stdout
            print(f"[{gid}] curl rc={p.returncode} len={len(p.stdout)} attempt {attempt+1} err={p.stderr[:100]}", flush=True)
        except Exception as e:
            print(f"[{gid}] curl exc attempt {attempt+1}: {str(e)[:100]}", flush=True)
        time.sleep(15 * (attempt + 1))
    return None

def save():
    json.dump({"done": sorted(done), "raw": raw, "fails": fails},
              open(ckpt_path, "w"), ensure_ascii=False)

PAUSE = 2.5
consecutive_fail = 0
todo = [g for g in ids if g not in done]
print(f"todo: {len(todo)} pages", flush=True)
for gid in todo:
    fails = [f for f in fails if f.get("id") != gid]
    html_text = fetch_page(gid)
    if html_text is None:
        fails.append({"id": gid, "error": "curl fetch failed after 3 attempts"})
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
        save()
    if consecutive_fail >= 5:
        print("STOPPING: 5 consecutive failures - banking checkpoint", flush=True)
        break
    time.sleep(PAUSE)

save()
print(f"FINISH done={len(done)} raw={len(raw)} fails={len(fails)}", flush=True)
