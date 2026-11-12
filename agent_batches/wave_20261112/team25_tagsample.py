#!/usr/bin/env python3
"""TEAM25: sample ~30 of 766 wglfinder /tag/ archive pages.
Check: do they carry group cards with chat.whatsapp.com invite codes,
or only post excerpts linking to already-mined posts?
"""
import json, re, time, requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
LEADS = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/team20-wglfinder-leads.json"
UNION = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})

CODE_RE = re.compile(r"chat\.whatsapp\.com/([A-Za-z0-9]{20,24})")
POSTLINK_RE = re.compile(r'href="(https://wglfinder\.com/[^"]*-whatsapp-group-link[^"]*)"')

def main():
    tags = json.load(open(LEADS))
    union = set(json.load(open(UNION)))
    # deterministic spread: every 25th + a few from head/tail -> 31 pages
    idx = list(range(0, len(tags), 25))[:30]
    idx.append(len(tags) - 1)
    sample = [tags[i] for i in sorted(set(idx))]
    print(f"sampling {len(sample)} tag pages")
    out = []
    for n, url in enumerate(sample, 1):
        rec = {"url": url}
        try:
            r = S.get(url, timeout=45)
            html = r.text or ""
            rec["http"] = r.status_code
            rec["bytes"] = len(html)
            codes = sorted(set(CODE_RE.findall(html)))
            rec["codes_found"] = codes
            rec["fresh_codes"] = [c for c in codes if c not in union]
            posts = sorted(set(POSTLINK_RE.findall(html)))
            rec["post_links"] = posts[:20]
            rec["n_post_links"] = len(posts)
            # group-card markers
            rec["has_join_button"] = ("Join Group" in html or "join-group" in html.lower()
                                      or "whatsapp-group-link" in html and "Join" in html)
            rec["snippet_markers"] = {
                "read_more": html.lower().count("read more"),
                "excerpt_class": html.lower().count("excerpt"),
                "entry_title": html.lower().count("entry-title"),
            }
        except Exception as e:
            rec["http"] = 0
            rec["error"] = f"{type(e).__name__}: {str(e)[:150]}"
            rec["codes_found"] = []
            rec["fresh_codes"] = []
            rec["post_links"] = []
            rec["n_post_links"] = 0
        out.append(rec)
        print(f"[{n}/{len(sample)}] {url.split('/tag/')[1][:60]} http={rec.get('http')} "
              f"codes={len(rec['codes_found'])} fresh={len(rec['fresh_codes'])} posts={rec['n_post_links']}", flush=True)
        with open(WAVE + "team25-tagsample.json", "w") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        time.sleep(3)
    tot_codes = sum(len(r["codes_found"]) for r in out)
    tot_fresh = sum(len(r["fresh_codes"]) for r in out)
    print(f"TOTAL pages={len(out)} codes_found={tot_codes} fresh={tot_fresh}")

if __name__ == "__main__":
    main()
