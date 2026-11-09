#!/usr/bin/env python3
"""Team 13 step 2: group pages -> redirect -> chat code. One similar-groups expansion round."""
import json, os, re, subprocess, time
from concurrent.futures import ThreadPoolExecutor

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
RAW = os.path.join(WAVE, "team13_raw")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

step1 = json.load(open(os.path.join(WAVE, "team13_step1.json")))
groups = step1["groups"]  # gid -> info
existing = set(json.load(open(os.path.expanduser("~/workspace/whatsapp-groups-site/.existing_codes.json"))))

def fetch_group(gid):
    fn = os.path.join(RAW, f"group-{gid}.html")
    if os.path.exists(fn) and os.path.getsize(fn) > 500:
        html = open(fn, encoding="utf-8", errors="ignore").read()
    else:
        r = subprocess.run(["curl", "-sL", "--max-time", "30", "-A", UA,
                            "-o", fn, "-w", "%{http_code}",
                            f"https://grupbul.com/group/{gid}"],
                           capture_output=True, text=True, timeout=45)
        try:
            html = open(fn, encoding="utf-8", errors="ignore").read()
        except Exception:
            html = ""
    time.sleep(0.4)
    return gid, html

def parse_group(gid, html):
    info = {"gid": gid, "bytes": len(html)}
    m = re.search(r"<title>(.*?)\s*\[WhatsApp Group\]", html)
    info["name"] = m.group(1).strip() if m else ""
    # redirect link
    m = re.search(r'href="/redirect/(\d+)/(\d+)"', html)
    info["redirect"] = f"/redirect/{m.group(1)}/{m.group(2)}" if m else ""
    # own category
    m = re.search(r"/en/category/whatsapp/\d+/([^\"']+)", html)
    info["own_cat_slug"] = m.group(1) if m else ""
    # description: text between the h1 and Similar section
    m = re.search(r'<h1 class="text-center my-3">.*?</h1>(.*?)<h3 class="mb-0">Similar', html, re.S)
    if m:
        t = re.sub(r"<[^>]+>", " ", m.group(1))
        info["desc"] = re.sub(r"\s+", " ", t).strip()[:600]
    else:
        info["desc"] = ""
    # similar group ids
    sims = sorted(set(re.findall(r"/group/(\d+)", html)) - {gid})
    info["similar_ids"] = sims
    return info

def resolve_redirect(gid, redir):
    """HEAD the redirect URL (no follow) and read refresh: header for chat code."""
    if not redir:
        return ""
    url = "https://grupbul.com" + redir
    try:
        r = subprocess.run(["curl", "-s", "--max-time", "20", "-A", UA, "-D", "-", "-o", "/dev/null", url],
                           capture_output=True, text=True, timeout=30)
        m = re.search(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{10,})", r.stdout)
        if m:
            return m.group(1).split("?")[0].split("#")[0].rstrip("/")
        # fallback: follow once, check effective url
        r2 = subprocess.run(["curl", "-sL", "--max-time", "20", "-A", UA, "-o", "/dev/null",
                             "-w", "%{url_effective}", url],
                            capture_output=True, text=True, timeout=30)
        m2 = re.search(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{10,})", r2.stdout)
        return m2.group(1) if m2 else ""
    except Exception:
        return ""

# round 1: listed groups
gids = sorted(groups.keys())
print(f"round1: {len(gids)} group pages", flush=True)
parsed = {}
with ThreadPoolExecutor(max_workers=3) as ex:
    for gid, html in ex.map(fetch_group, gids):
        parsed[gid] = parse_group(gid, html)
        print(gid, parsed[gid]["name"][:50], "| redir:", parsed[gid]["redirect"],
              "| sims:", len(parsed[gid]["similar_ids"]), flush=True)

# expansion: similar ids not already known, cap 60, prefer ones whose own category is in our slice
extra = []
for gid, p in parsed.items():
    for s in p["similar_ids"]:
        if s not in groups and s not in extra:
            extra.append(s)
extra = extra[:60]
print(f"expansion: {len(extra)} similar group ids", flush=True)
if extra:
    with ThreadPoolExecutor(max_workers=3) as ex:
        for gid, html in ex.map(fetch_group, extra):
            parsed[gid] = parse_group(gid, html)
            groups.setdefault(gid, {"gid": gid, "cat": "Unknown-similar", "from": "similar-carousel", "list_name": "", "list_desc": ""})
            print("EXP", gid, parsed[gid]["name"][:50], "| redir:", parsed[gid]["redirect"], flush=True)

# resolve redirects sequentially-ish (3 workers, site is slow)
def resolve_one(gid):
    code = resolve_redirect(gid, parsed[gid].get("redirect", ""))
    time.sleep(0.3)
    return gid, code

codes = {}
with ThreadPoolExecutor(max_workers=3) as ex:
    for gid, code in ex.map(resolve_one, sorted(parsed.keys())):
        codes[gid] = code
        print("CODE", gid, code, flush=True)

out = {"groups": groups, "parsed": parsed, "codes": codes}
json.dump(out, open(os.path.join(WAVE, "team13_step2.json"), "w"), indent=1)
fresh = {g: c for g, c in codes.items() if c and c not in existing}
print("resolved:", sum(1 for c in codes.values() if c), "/", len(codes))
print("fresh (not in existing):", len(fresh))
print("dup vs existing:", sum(1 for c in codes.values() if c and c in existing))
