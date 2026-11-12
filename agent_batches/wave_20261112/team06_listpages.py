#!/usr/bin/env python3
"""TEAM06 wave_20261112: sample retry of team07 slice7 failed listing pages."""
import json, re, time, random, collections
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
PREV = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/"
BUILD = "/home/hatch/workspace/whatsapp-groups-site/"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
CODE_RX = re.compile(r"chat\.whatsapp\.com/([A-Za-z0-9]{10,30})")

def main():
    leads = json.load(open(PREV + "team07-leads-slice7-leads.json"))
    existing = set(json.load(open(BUILD + ".existing_codes.json")))
    # stratified sample: 12 per top host, cap 80
    by_host = collections.defaultdict(list)
    for u in leads:
        host = u.split("/")[2] if "://" in u else "?"
        by_host[host].append(u)
    sample = []
    for host, urls in sorted(by_host.items(), key=lambda kv: -len(kv[1])):
        sample.extend(urls[:12])
    sample = sample[:80]
    random.seed(20261112)
    random.shuffle(sample)
    print(f"sample={len(sample)} of {len(leads)} failed pages", flush=True)

    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    still_failed, resolved, codes_found = [], [], set()
    for i, url in enumerate(sample):
        try:
            r = s.get(url, timeout=30, allow_redirects=True)
            if r.status_code == 200 and len(r.text) > 500:
                codes = set(CODE_RX.findall(r.text or ""))
                fresh = {c for c in codes if c not in existing}
                codes_found |= fresh
                resolved.append({"url": url, "status": 200, "codes_on_page": len(codes), "fresh_codes": len(fresh)})
            else:
                still_failed.append(url)
        except Exception as e:
            still_failed.append(url)
        time.sleep(random.uniform(1.5, 3.0))
        if (i + 1) % 20 == 0:
            print(f"[{i+1}/{len(sample)}] resolved={len(resolved)} failed={len(still_failed)} fresh_codes={len(codes_found)}", flush=True)
    json.dump(still_failed, open(WAVE + "team06-leads-slice7-pending-leads.json", "w"), ensure_ascii=False, indent=1)
    json.dump({"sampled": len(sample), "resolved": resolved, "still_failed_count": len(still_failed),
               "fresh_codes_found": sorted(codes_found)},
              open(WAVE + "team06-leads-slice7-pending-leads-report.json", "w"), ensure_ascii=False, indent=1)
    print(f"DONE sampled={len(sample)} resolved={len(resolved)} still_failed={len(still_failed)} fresh_codes={len(codes_found)}", flush=True)

if __name__ == "__main__":
    main()
