#!/usr/bin/env python3
"""Team 03 extraction for wave 20261109 slice 03.
Fetches listing pages, extracts invite codes + metadata, dedupes vs .existing_codes.json.
Uses curl (not python requests) for all fetches.
"""
import json, re, subprocess, sys, html, time
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

def fetch(url, timeout=30):
    for attempt in range(2):
        try:
            r = subprocess.run(
                ["curl", "-s", "-A", UA, "--max-time", str(timeout), "-L", url],
                capture_output=True, timeout=timeout + 10)
            if r.returncode == 0 and r.stdout:
                return r.stdout.decode("utf-8", errors="replace")
        except Exception as e:
            print("fetch err", url, e, file=sys.stderr)
        time.sleep(1)
    return None

def norm_code(raw):
    if not raw:
        return None
    c = raw.strip()
    c = re.split(r'[?#]', c)[0].rstrip('/')
    return c or None

def extract_code_from_html(h):
    m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_\-]{10,})', h)
    return m.group(1) if m else None

def clean(s):
    if not s:
        return ""
    s = html.unescape(s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def meta(h, prop):
    m = re.search(r'<meta[^>]*(?:property|name)=["\']' + re.escape(prop) + r'["\'][^>]*content=["\']([^"\']*)["\']', h, re.I)
    if m:
        return clean(m.group(1))
    m = re.search(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*(?:property|name)=["\']' + re.escape(prop) + r'["\']', h, re.I)
    return clean(m.group(1)) if m else ""

def process_gi(item):
    url = item["url"]
    slug = url.rstrip('/').split('/')[-1]
    rec = {"listing_url": url, "source": "groupsinvite.link", "slug": slug}
    h = fetch(url)
    if not h:
        rec["error"] = "detail fetch failed"
        return rec, []
    title = re.search(r'<title>(.*?)</title>', h, re.S)
    t = clean(title.group(1)) if title else ""
    t = re.sub(r'\s*WhatsApp Group Invite Link.*$', '', t)
    t = re.sub(r'\s*\|\s*GroupsInvite\s*$', '', t)
    rec["name"] = t
    rec["desc"] = meta(h, "og:description") or meta(h, "description")
    fd = re.search(r'data-full-description="([^"]*)"', h)
    if fd and len(fd.group(1)) > len(rec["desc"]):
        rec["desc"] = clean(fd.group(1))
    rec["tags"] = [clean(x) for x in re.findall(r'class="tag-pill"[^>]*>([^<]+)</a>', h)]
    leads = []
    for s in sorted(set(re.findall(r'https://groupsinvite\.link/group/link/([a-z0-9]+)/', h))):
        u = f"https://groupsinvite.link/group/link/{s}/"
        if u != url:
            leads.append({"url": u, "source": "groupsinvite.link related group (team03 discovery)"})
    rules = fetch(f"https://groupsinvite.link/group/rules/{slug}/")
    if rules:
        rec["code"] = extract_code_from_html(rules)
    if not rec.get("code"):
        rec["error"] = rec.get("error", "") + "; no code on rules page"
    return rec, leads

def process_ong(item):
    url = item["url"]
    code = url.rstrip('/').split('/')[-1]
    rec = {"listing_url": url, "source": "ongrupos.com", "code": norm_code(code)}
    h = fetch(url)
    if not h:
        rec["error"] = "detail fetch failed"
        return rec, []
    rec["name"] = meta(h, "og:title") or clean(re.sub(r'^Grupo WhatsApp - ', '', re.search(r'<title>(.*?)</title>', h, re.S).group(1))) if re.search(r'<title>(.*?)</title>', h, re.S) else ""
    rec["desc"] = meta(h, "description")
    leads = []
    for c in sorted(set(re.findall(r'https://ongrupos\.com/grupo/([A-Za-z0-9]+)', h))):
        u = f"https://ongrupos.com/grupo/{c}"
        if u != url:
            leads.append({"url": u, "source": "ongrupos group detail (team03 discovery)"})
    return rec, leads

def process_gcc(item):
    url = item["url"]
    rec = {"listing_url": url, "source": "groupchatconnect.info"}
    h = fetch(url)
    if not h:
        rec["error"] = "detail fetch failed"
        return rec, []
    m = re.search(r'<h1[^>]*>(.*?)</h1>', h, re.S)
    rec["name"] = clean(re.sub(r'<[^>]+>', '', m.group(1))) if m else (meta(h, "og:title") or "")
    rec["name"] = re.sub(r'\s*على دردشة جماعية.*$', '', rec["name"]).strip()
    rec["desc"] = meta(h, "description") or meta(h, "og:description")
    tok = re.search(r'href="/go/([A-Za-z0-9]+)"', h)
    if tok:
        rec["code"] = tok.group(1)
    else:
        rec["error"] = "no /go/ token found"
    leads = []
    for n in sorted(set(re.findall(r'href="/groupe/(\d+)"', h))):
        u = f"https://groupchatconnect.info/groupe/{n}"
        if u != url:
            leads.append({"url": u, "source": "groupchatconnect.info (team03 discovery)"})
    for n in sorted(set(re.findall(r'href="/channel/(\d+)"', h))):
        u = f"https://groupchatconnect.info/channel/{n}"
        if u != url:
            leads.append({"url": u, "source": "groupchatconnect.info channel (team03 discovery)"})
    return rec, leads

def process_gj(item):
    url = item["url"]
    recs = []
    body = fetch(url)
    if not body:
        return [{"listing_url": url, "source": "groupjoin.link API", "error": "api fetch failed"}], []
    try:
        data = json.loads(body).get("data", [])
    except Exception as e:
        return [{"listing_url": url, "source": "groupjoin.link API", "error": f"json parse: {e}"}], []
    for d in data:
        link = d.get("link") or ""
        m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_\-]{10,})', link)
        recs.append({
            "listing_url": url, "source": "groupjoin.link API",
            "code": m.group(1) if m else None,
            "name": clean(str(d.get("group_title") or "")),
            "desc": clean(str(d.get("group_desc") or "")),
            "country_hint": (d.get("country") or {}).get("iso2") or "",
            "category_hint": (d.get("category") or {}).get("category_name") or "",
            "nsfw": d.get("nsfw"),
            "tags": d.get("tags") or [],
        })
    return recs, []

def main():
    leads = json.load(open(f"{WAVE}/leads_slice_03.json"))
    existing = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
    print(f"slice: {len(leads)} leads; existing codes: {len(existing)}")

    def work(item):
        src = item.get("source", "")
        try:
            if "groupsinvite" in src:
                r, l = process_gi(item); return [r], l
            if "ongrupos" in src:
                r, l = process_ong(item); return [r], l
            if "groupchatconnect" in src:
                r, l = process_gcc(item); return [r], l
            if "team04" in src:
                return process_gj(item)
            return [{"listing_url": item["url"], "source": src, "error": "unknown source type"}], []
        except Exception as e:
            return [{"listing_url": item["url"], "source": src, "error": f"exception: {e}"}], []

    all_recs, all_leads = [], []
    with ThreadPoolExecutor(max_workers=6) as ex:
        for i, (recs, lds) in enumerate(ex.map(work, leads)):
            all_recs.extend(recs)
            all_leads.extend(lds)
            if (i + 1) % 25 == 0:
                print(f"... {i+1}/{len(leads)} done, recs={len(all_recs)}")

    # dedupe codes
    seen = set()
    fresh, dup, nocode = [], 0, 0
    for r in all_recs:
        c = norm_code(r.get("code"))
        r["code"] = c
        if not c:
            nocode += 1
            fresh.append(r)
            continue
        if c in existing or c in seen:
            dup += 1
            r["dup"] = True
            fresh.append(r)
        else:
            seen.add(c)
            fresh.append(r)
    # dedupe leads vs slice urls
    slice_urls = {x["url"] for x in leads}
    new_leads, seen_l = [], set()
    for l in all_leads:
        if l["url"] not in slice_urls and l["url"] not in seen_l:
            seen_l.add(l["url"])
            new_leads.append(l)

    json.dump(fresh, open(f"{WAVE}/team03-raw.json", "w"), ensure_ascii=False, indent=1)
    json.dump(new_leads, open(f"{WAVE}/team03-discovered-leads.json", "w"), ensure_ascii=False, indent=1)
    print(f"records: {len(all_recs)}; dup codes (in existing or repeat): {dup}; no-code records: {nocode}")
    print(f"fresh unique codes: {len(seen)}; new discovered leads: {len(new_leads)}")
    errs = [r for r in all_recs if r.get("error")]
    print(f"records with errors: {len(errs)}")
    for r in errs[:15]:
        print(" ERR:", r.get("listing_url"), "|", r.get("error"))

if __name__ == "__main__":
    main()
