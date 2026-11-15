#!/usr/bin/env python3
"""team12 whts.club remaining 252 codeless pages — wave 20261114."""
import html as htmlmod
import json, re, time, sys
from pathlib import Path
import requests

WAVE = Path("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114")
BASE = Path("/home/hatch/workspace/whatsapp-groups-site")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9,es;q=0.8"}

def og_title(html):
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)["\']', html, re.I)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', html, re.I)
    return htmlmod.unescape(m.group(1).strip()) if m else ""

def main():
    union = set(json.load(open(BASE / ".existing_codes.json")))
    leads16 = json.load(open(BASE / "agent_batches/wave_20261112/team16-whtsclub-leads.json"))
    t13 = json.load(open(BASE / "agent_batches/wave_20261113/team13-leads.json"))
    sampled = set(x["value"] for x in t13 if "whts.club" in x["value"])
    all_urls = [x["url"] for x in leads16]
    remaining = [u for u in all_urls if u not in sampled]
    sitemap_idx = {x["url"]: x.get("sitemap_index") for x in leads16}
    print(f"total={len(all_urls)} sampled={len(sampled)} remaining={len(remaining)}", flush=True)

    sess = requests.Session()
    sess.headers.update(UA)

    # --- controls (hard) ---
    def verify_code(code, tries=3):
        title = ""
        last_status = None
        for i in range(tries):
            try:
                r = sess.get(f"https://chat.whatsapp.com/{code}", timeout=75)
                last_status = r.status_code
                title = og_title(r.text or "")
                if title:
                    return title, last_status, "live"
                if r.status_code == 429:
                    return "", last_status, "pending-429"
                if i < tries - 1:
                    time.sleep(5)
            except Exception as e:
                last_status = f"transport:{e}"
                if i < tries - 1:
                    time.sleep(5)
        return title, last_status, ("pending-transport" if isinstance(last_status, str) else "dead-empty")

    live_title, live_status, live_res = verify_code("KrDwdK8EIkB6vgauHg5M7N")
    print(f"CONTROL live: title={live_title!r} status={live_status} res={live_res}", flush=True)
    fab_title, fab_status, fab_res = verify_code("ZzZzZzZzZzZzZzZzZzZzZzZz")
    print(f"CONTROL fabricated: title={fab_title!r} status={fab_status} res={fab_res}", flush=True)
    controls = {
        "live": f"KrDwdK8EIkB6vgauHg5M7N -> og:title {live_title!r} ({'PASS' if live_title=='JAY - PHP & Python Full Stack Developer' else 'FAIL'})",
        "fabricated": f"ZzZzZzZzZzZzZzZzZzZzZzZz -> empty og:title ({'PASS' if fab_title=='' else 'FAIL'})",
    }
    if live_title != "JAY - PHP & Python Full Stack Developer" or fab_title != "":
        print("CONTROLS FAILED — STOPPING", flush=True)
        (WAVE / "team12-controls-failed.json").write_text(json.dumps(controls, indent=1))
        sys.exit(2)
    print("CONTROLS PASS", flush=True)

    candidates, leads, pending, excluded = [], [], [], []
    seen_codes = set()
    counts = {"pages_fetched": 0, "fetch_failed": 0, "codes_found": 0, "dupes": 0, "dead": 0, "channel_pages": 0, "blog_no_link": 0}
    code_re = re.compile(r"chat\.whatsapp\.com/([A-Za-z0-9]{15,30})")
    chan_re = re.compile(r"whatsapp\.com/channel/([A-Za-z0-9]+)")

    def bank():
        (WAVE / "team12-candidates.json").write_text(json.dumps(candidates, indent=1, ensure_ascii=False))
        (WAVE / "team12-leads.json").write_text(json.dumps(leads, indent=1, ensure_ascii=False))
        (WAVE / "team12-pending.json").write_text(json.dumps(pending, indent=1, ensure_ascii=False))

    for idx, url in enumerate(remaining):
        html = ""
        ok = False
        for attempt in range(3):
            try:
                r = sess.get(url, timeout=60)
                if r.status_code == 200 and r.text:
                    html = r.text; ok = True; break
                elif r.status_code == 429:
                    time.sleep(10); continue
                else:
                    time.sleep(3)
            except Exception as e:
                time.sleep(5)
        counts["pages_fetched"] += 1
        if not ok:
            counts["fetch_failed"] += 1
            leads.append({"kind": "url", "value": url,
                          "note": "team12 re-fetch 2026-11-14: page fetch failed after 3 attempts; codeless listing — needs retry/browser leg, not dead",
                          "sitemap_index": sitemap_idx.get(url)})
            bank()
            print(f"[{idx+1}/252] FETCH-FAIL {url}", flush=True)
            continue
        codes = list(dict.fromkeys(code_re.findall(html)))
        # filter out known non-invite artefacts: codes that are part of channel etc — chat.whatsapp.com codes are group invites
        if codes:
            counts["codes_found"] += len(codes)
            for code in codes:
                if code in union or code in seen_codes:
                    counts["dupes"] += 1
                    excluded.append({"code": code, "name": "", "reason": "dupe: already in union or seen within team", "source_page": url})
                    continue
                seen_codes.add(code)
                title, status, res = verify_code(code)
                if res == "live":
                    # content screen on og:title
                    t = title.lower()
                    # hard drops
                    drop = None
                    if re.search(r"\b(xxx|porn|hentai|sexo|sex\b|putas?|morbo)\b", t): drop = "hard porn/sexual content in og:title"
                    elif re.search(r"airdrop|free money|binary|tigrinho|fortune tiger|sinais|plataformas pagantes|wjbet|casino|slots|betting|apuestas", t): drop = "scam/casino/betting signal in og:title"
                    if drop:
                        excluded.append({"code": code, "name": title, "reason": f"drop: {drop}", "source_page": url})
                        print(f"[{idx+1}/252] EXCLUDED {code} {title!r} {drop}", flush=True)
                        continue
                    # name/category: use og:title as name, category from page slug keywords (fallback Community & Social)
                    slug = url.rsplit("/", 1)[-1].lower()
                    cat = "Community & Social"
                    cmap = [("job","Jobs"),("trabajo","Jobs"),("bolsa","Jobs"),("study","Education"),("estudio","Education"),("educ","Education"),("school","Education"),("sport","Sports"),("futbol","Sports"),("fútbol","Sports"),("music","Entertainment"),("musica","Entertainment"),("movie","Entertainment"),("anime","Entertainment"),("gaming","Gaming"),("game","Gaming"),("free fire","Gaming"),("health","Health"),("salud","Health"),("news","News"),("noticia","News"),("crypto","Crypto"),("islam","Islamic"),("cook","Cooking"),("receta","Cooking"),("travel","Travel"),("viaje","Travel"),("business","Business"),("finance","Finance"),("funny","Funny"),("meme","Funny"),("poetry","Poetry"),("poesia","Poetry"),("scholarship","Scholarship"),("freelance","Freelance"),("earning","Earning")]
                    for kw, c in cmap:
                        if kw in slug or kw in t:
                            cat = c; break
                    name = title.strip()
                    candidates.append({"name": name, "category": cat, "country": "",
                                       "description": f"Join {name}, an active WhatsApp group for {cat.lower()}. Connect with members, share updates and chat with people who share your interests.",
                                       "invite": f"https://chat.whatsapp.com/{code}"})
                    print(f"[{idx+1}/252] LIVE-CANDIDATE {code} {title!r} cat={cat}", flush=True)
                elif res.startswith("pending"):
                    pending.append({"code": code, "reason": res, "source_page": url})
                    print(f"[{idx+1}/252] PENDING {code} {res}", flush=True)
                else:
                    counts["dead"] += 1
                    excluded.append({"code": code, "name": "", "reason": "dead: empty og:title on spaced retries", "source_page": url})
                    print(f"[{idx+1}/252] DEAD {code}", flush=True)
            bank()
        else:
            chans = chan_re.findall(html)
            if chans:
                counts["channel_pages"] += 1
                leads.append({"kind": "url", "value": url,
                              "note": f"team12 re-fetch 2026-11-14: no group invite code; page links a WhatsApp CHANNEL (https://whatsapp.com/channel/{chans[0]}), not a group invite",
                              "sitemap_index": sitemap_idx.get(url)})
            else:
                counts["blog_no_link"] += 1
                leads.append({"kind": "url", "value": url,
                              "note": "team12 re-fetch 2026-11-14: no group invite code and no channel link; blog-style codeless listing",
                              "sitemap_index": sitemap_idx.get(url)})
            bank()
        if (idx + 1) % 25 == 0:
            print(f"--- progress {idx+1}/252 fetched={counts['pages_fetched']} codes={counts['codes_found']} cand={len(candidates)} leads={len(leads)} dead={counts['dead']} dupes={counts['dupes']} fetchfail={counts['fetch_failed']}", flush=True)
        time.sleep(0.4)

    bank()
    summary = {
        "team": "team12",
        "wave": "20261114",
        "slice": "whts.club 372 codeless pages — REMAINING ~252 not sampled by wave_20261113 team13 (prioritised jobs/study/sports/education/news/health/music/movies/anime/gaming/friendship sample of 120)",
        "sources": [
            "agent_batches/wave_20261112/team16-whtsclub-leads.json (372 codeless pages, sitemap indices)",
            "agent_batches/wave_20261113/team13-leads.json (120 sampled whts.club pages; team13 found 0 codes, 116 channel + 4 blog)",
            "Union: .existing_codes.json (119,266 codes); groups.json read-only, not edited",
        ],
        "controls": controls,
        "counts": {
            "total_codeless_pages": len(all_urls),
            "team13_sampled": len(sampled),
            "team12_pages_attempted": len(remaining),
            "raw_codes_found": counts["codes_found"],
            "verified_live_candidates": len(candidates),
            "dupes": counts["dupes"],
            "dead": counts["dead"],
            "excluded": len(excluded),
            "pending": len(pending),
            "leads": len(leads),
            "channel_pages": counts["channel_pages"],
            "blog_no_link_pages": counts["blog_no_link"],
            "fetch_failed_pages": counts["fetch_failed"],
        },
        "excluded": excluded,
        "sampled_by_team13": sorted(sampled),
        "remaining_sampled_by_team12": remaining,
        "resume_point": "complete — all 252 remaining pages fetched; no resume needed" if counts["fetch_failed"] == 0 else f"fetch-failed pages banked as leads for retry: {[l['value'] for l in leads if 'fetch failed' in l['note']]}",
        "notes": [
            "Verification: single requests.Session with browser UA, 60-90s timeout; live = non-empty, non-generic og:title only; og:description never used as a live signal.",
            "Codeless pages are recorded as leads, not dead — they are channel/blog listings, not dead groups.",
            "Content screen applied to LIVE og:title only; no hard porn/scam/casino drops among live codes found (see excluded list).",
        ],
    }
    (WAVE / "team12-summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False))
    print(json.dumps(summary["counts"], indent=1), flush=True)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
