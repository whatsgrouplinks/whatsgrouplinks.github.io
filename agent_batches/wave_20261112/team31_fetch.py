#!/usr/bin/env python3
"""TEAM31 wave_20261112 — mine team26 leads (Africa/Middle East), skip linktogroups."""
import json, re, time, sys, os
import requests
from html import unescape

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
RAW = os.path.join(WAVE, "team31_raw")
os.makedirs(RAW, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9"}

union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
print("union:", len(union), flush=True)

CODE_RE = re.compile(r"chat\.whatsapp\.com/([A-Za-z0-9]{20,24})")
# also invite codes in hrefs with trailing junk
def extract_codes(html):
    return list(dict.fromkeys(CODE_RE.findall(html)))

def fetch(url, session, tries=3, timeout=60):
    last = None
    for i in range(tries):
        try:
            r = session.get(url, headers=UA, timeout=timeout)
            return r.status_code, r.text
        except Exception as e:
            last = str(e)
            time.sleep(8 if i < tries-1 else 0)
    return None, last

def og_title(html):
    m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html) or \
        re.search(r"<meta\s+property='og:title'\s+content='([^']*)'", html)
    if m: return unescape(m.group(1)).strip()
    m = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', html)
    return unescape(m.group(1)).strip() if m else ""

# ---------- CONTROLS ----------
s = requests.Session()
print("CONTROL live KrDwdK8EIkB6vgauHg5M7N ...", flush=True)
st, html = fetch("https://chat.whatsapp.com/KrDwdK8EIkB6vgauHg5M7N", s, tries=2)
print("  status", st, "og:", repr(og_title(html)) if html else html, flush=True)
print("CONTROL fabricated ZZZZZZZZZZZZZZZZZZZZZZZ ...", flush=True)
st, html = fetch("https://chat.whatsapp.com/ZZZZZZZZZZZZZZZZZZZZZZ", s, tries=2)
print("  status", st, "og:", repr(og_title(html)) if html else html, flush=True)

# ---------- LEADS ----------
leads = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/team26-newdirs-africa-mideast-leads.json"))
targets = [u for u in leads if "linktogroups.com" not in u]
print("targets:", len(targets), "skipped linktogroups:", len(leads)-len(targets), flush=True)

fetched = {}   # url -> {status, codes, note}
all_codes = {} # code -> {source, context}
for url in targets:
    print("FETCH", url, flush=True)
    st, html = fetch(url, s, tries=3)
    if st is None:
        fetched[url] = {"status": "transport-fail", "error": html, "codes": []}
        print("  TRANSPORT FAIL", html, flush=True); continue
    fn = re.sub(r"[^A-Za-z0-9]+", "_", url.replace("https://",""))[:80] + ".html"
    open(os.path.join(RAW, fn), "w", encoding="utf-8").write(html)
    codes = extract_codes(html)
    # phone-number heuristic: count tel: / wa.me numbers vs group codes
    phones = len(re.findall(r"wa\.me/\d{7,}|tel:\+?\d{7,}", html))
    fetched[url] = {"status": st, "codes": codes, "len": len(html), "phones": phones}
    print(f"  status {st} len {len(html)} codes {len(codes)} phone-links {phones}", flush=True)
    for c in codes:
        # grab ~120 chars before the code occurrence for a name hint
        idx = html.find(c)
        ctx = re.sub(r"<[^>]+>", " ", html[max(0, idx-400):idx]).strip()
        ctx = re.sub(r"\s+", " ", unescape(ctx))[-200:]
        all_codes.setdefault(c, {"source": url, "context": ctx})

json.dump(fetched, open(os.path.join(WAVE, "team31_fetch.json"), "w"), indent=1)
json.dump(all_codes, open(os.path.join(WAVE, "team31_extracted.json"), "w"), indent=1)
fresh = {c: v for c, v in all_codes.items() if c not in union}
print("unique codes:", len(all_codes), "fresh:", len(fresh), "in-union:", len(all_codes)-len(fresh), flush=True)
for c, v in fresh.items():
    print(" FRESH", c, "|", v["source"].split("/")[2], "|", v["context"][-120:], flush=True)
