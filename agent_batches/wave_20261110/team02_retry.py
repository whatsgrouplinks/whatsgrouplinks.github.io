#!/usr/bin/env python3
"""Team 02 wave 20261110: gentle retry of transport-failed listings only.
2 workers, 60s timeout. Moves successes into team02-extracted.json and
removes them from team02-fetch-problems.json transport_fail."""
import json, re, subprocess, html, os
from concurrent.futures import ThreadPoolExecutor

WAVE10 = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
CKPT = f"{WAVE10}/team02-extracted.json"
PROB = f"{WAVE10}/team02-fetch-problems.json"
LEADS = f"{WAVE10}/team02-new-leads-raw.json"

def fetch(url):
    try:
        r = subprocess.run(["curl","-s","-L","--max-time","60","-A",UA,url],
                           capture_output=True, timeout=70)
        return r.stdout.decode("utf-8", errors="ignore"), r.returncode
    except Exception:
        return "", -1

def norm_code(raw):
    return raw.split("?")[0].split("#")[0].rstrip("/")

existing = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
groups = json.load(open("/home/hatch/workspace/whatsapp-groups-site/groups.json"))
gcode_re = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)')
for e in groups:
    m = gcode_re.search(e.get("invite",""))
    if m:
        existing.add(m.group(1))

extracted = json.load(open(CKPT))
done = {r["listing_url"]: r for r in extracted}
problems = json.load(open(PROB))
leads_raw = json.load(open(LEADS))
new_leads = {l["url"]: l["source"] for l in leads_raw}

COUNTRY_MAP = {"india":"IN","pakistan":"PK","bangladesh":"BD","nepal":"NP","sri-lanka":"LK",
 "united-states":"US","usa":"US","united-kingdom":"UK","uk":"GB","canada":"CA","australia":"AU",
 "uae":"AE","saudi-arabia":"SA","nigeria":"NG","kenya":"KE","ghana":"GH","south-africa":"ZA",
 "indonesia":"ID","malaysia":"MY","philippines":"PH","germany":"DE","france":"FR"}

todo = [p["url"] for p in problems["transport_fail"]]
print(f"retry todo={len(todo)}", flush=True)

def save():
    json.dump(list(done.values()), open(CKPT,"w"), ensure_ascii=False, indent=1)
    json.dump(problems, open(PROB,"w"), ensure_ascii=False, indent=1)
    json.dump([{"url": u, "source": s} for u, s in sorted(new_leads.items())],
              open(LEADS,"w"), ensure_ascii=False, indent=1)

def process(url):
    src = "groupsinvite.link related group"
    listing_id = url.rstrip("/").split("/")[-1]
    body, rc = fetch(url)
    if not body or len(body) < 500:
        return ("still-fail-listing", url, rc)
    title_m = re.search(r'<meta property="og:title" content="([^"]*)"', body)
    title = html.unescape(title_m.group(1)).strip() if title_m else ""
    if not title:
        tm = re.search(r'<title>([^<]*)</title>', body)
        title = html.unescape(tm.group(1)).replace(" WhatsApp Group Invite Link | GroupsInvite","").strip() if tm else ""
    desc_m = re.search(r'data-full-description="([^"]*)"', body)
    desc = html.unescape(desc_m.group(1)).strip() if desc_m else ""
    country = "IN"
    cm = re.search(r'href="https://groupsinvite\.link/group/country/([^"/]+)/"', body)
    if cm:
        country = COUNTRY_MAP.get(cm.group(1).lower(), "IN")
    for rid in set(re.findall(r'https://groupsinvite\.link/group/link/([a-z0-9]+)/', body)):
        rurl = f"https://groupsinvite.link/group/link/{rid}/"
        if rurl != url:
            new_leads.setdefault(rurl, "groupsinvite.link related group (found on listing page)")
    rules_url = f"https://groupsinvite.link/group/rules/{listing_id}/"
    rbody, rrc = fetch(rules_url)
    codes = re.findall(r'chat\.whatsapp\.com/invite/([A-Za-z0-9_\-]+)', rbody)
    codes += re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9_\-]{15,})', rbody)
    codes = [norm_code(c) for c in codes if norm_code(c).lower() != "invite"]
    if not codes:
        if not rbody or len(rbody) < 500:
            return ("still-fail-rules", url, rrc)
        return ("no-code", url, title)
    code = codes[0]
    status = "new"
    if code in existing: status = "dup-existing"
    elif any(v.get("code")==code for v in done.values()): status = "dup-in-slice"
    rec = {"listing_url": url, "rules_url": rules_url, "code": code,
           "title": title, "description": desc, "country": country,
           "status": status, "source": src}
    return ("ok", url, rec)

n = 0
still_fail = []
with ThreadPoolExecutor(max_workers=2) as ex:
    for status, url, info in ex.map(process, todo):
        n += 1
        if status == "ok":
            done[url] = info
            problems["transport_fail"] = [p for p in problems["transport_fail"] if p["url"] != url]
            print(f"[{n}/{len(todo)}] recovered {info['status']} {info['code']} :: {info['title']}", flush=True)
        elif status == "no-code":
            problems["transport_fail"] = [p for p in problems["transport_fail"] if p["url"] != url]
            problems["dead"].append({"url": url, "source": "groupsinvite.link related group",
                                     "title": info, "note": "no invite code on rules page (JS-gated?)"})
            print(f"[{n}/{len(todo)}] no-code {url}", flush=True)
        else:
            still_fail.append(url)
            for p in problems["transport_fail"]:
                if p["url"] == url:
                    p["note"] = f"retry {status} rc={info}"
            print(f"[{n}/{len(todo)}] {status} {url}", flush=True)
        if n % 5 == 0:
            save()
save()
print(f"RETRY DONE recovered={sum(1 for u in todo if u in done)} still_fail={len(still_fail)} "
      f"transport_left={len(problems['transport_fail'])} dead={len(problems['dead'])}")
