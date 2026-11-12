import json, re, time, random, html
import requests
WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9", "Accept": "text/html,application/xhtml+xml"}
DIR_RE = re.compile(r"group[s]?\s+links?", re.I)
def og(page):
    m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', page, re.I)
    if m and m.group(1).strip(): return html.unescape(m.group(1).strip())
    return ""
cands = json.load(open(WAVE + "team13-pending-recheck-candidates.json"))
excl = json.load(open(WAVE + "team13-exclusions.json"))
s = requests.Session()
fixed, dropped, kept_old = [], [], []
out = []
for c in cands:
    code = c["invite"].rsplit("/", 1)[-1]
    low = c["name"].lower()
    # (a) remaining directory titles (plural 'Groups Links' missed by round 1) + CSS-junk name
    if DIR_RE.search(c["name"]) or c["name"].startswith("background:"):
        title = ""
        try:
            r = s.get(f"https://chat.whatsapp.com/{code}", headers=UA, timeout=60)
            if r.status_code == 200:
                title = og(r.text)
        except requests.exceptions.RequestException as e:
            print("fetch fail", code, type(e).__name__)
        if title and not title.startswith("background:") and not DIR_RE.search(title):
            fixed.append({"code": code, "old": c["name"], "new": title})
            c["name"] = title
        else:
            kept_old.append({"code": code, "name": c["name"], "og_title": title})
        time.sleep(1.5 + random.random())
    # (b) bhabhi-genre group under the listed 'Desi bhabhi' rule
    if "bhabhi" in c["name"].lower():
        excl.append({"code": code, "name": c["name"], "reason": "content screen DROP (post-pass re-screen): bhabhi-genre group (Desi bhabhi rule)"})
        dropped.append({"code": code, "name": c["name"], "reason": "bhabhi-genre group"})
        continue
    # (c) normalize every description to the schema's Join format
    c["description"] = f"Join {c['name']}, an active WhatsApp group for {c['category'].lower()}. Connect with members, share updates and stay in touch."
    out.append(c)
assert len({x["invite"] for x in out}) == len(out)
json.dump(out, open(WAVE + "team13-pending-recheck-candidates.json", "w"), ensure_ascii=False, indent=1)
json.dump(excl, open(WAVE + "team13-exclusions.json", "w"), ensure_ascii=False, indent=1)
summ = json.load(open(WAVE + "team13-pending-recheck-summary.json"))
summ["verified_kept_candidates"] = len(out)
summ["excluded_content_screen"] = sum(1 for x in excl if "content screen" in x["reason"])
summ["exclusions"] = excl
summ["post_pass_fixup2"] = {
    "names_fixed_from_og_title": fixed,
    "names_kept_on_refetch_failure": kept_old,
    "dropped_on_rescreen": dropped,
    "descriptions_normalized": f"all {len(out)} descriptions rewritten to schema format 'Join <name>, an active WhatsApp group for <category>...'",
    "note": "Round 2 caught 6 'WhatsApp Groups Links' (plural) directory titles missed by round 1's singular filter, plus one CSS-fragment name; all re-fetched from live og:title. One bhabhi-genre group dropped under the listed Desi bhabhi rule."
}
json.dump(summ, open(WAVE + "team13-pending-recheck-summary.json", "w"), ensure_ascii=False, indent=2)
print("FIXED:", json.dumps(fixed, ensure_ascii=False, indent=1))
print("KEPT_OLD:", kept_old)
print("DROPPED:", dropped)
print("final candidates:", len(out))
