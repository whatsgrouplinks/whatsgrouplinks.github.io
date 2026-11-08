#!/usr/bin/env python3
"""Team31: extract candidate chat.whatsapp.com codes from source pages, dedupe vs union."""
import json, re, sys
import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')

def load_union():
    u = json.load(open('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/dedupe_union.json'))
    return set(u)

def main():
    union = load_union()
    print(f"union size: {len(union)}", file=sys.stderr)
    sources = json.load(open(sys.argv[1]))  # [{"url":..., "label":..., "country":..., "category":...}]
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    out = []
    for src in sources:
        try:
            r = s.get(src["url"], timeout=50)
            html = r.text
            codes = CODE_RE.findall(html)
            # also grab names from anchor text? keep simple: page title + code
            title = re.search(r'<title>(.*?)</title>', html, re.S | re.I)
            title = (title.group(1).strip()[:120] if title else "") 
            new = []
            for c in codes:
                if len(c) < 20 or len(c) > 24: continue
                if c in union: continue
                new.append(c)
            out.append({"label": src["label"], "url": src["url"], "status": r.status_code,
                        "title": title, "codes_new": sorted(set(new)),
                        "codes_dup": len(set(codes)) - len(set(new))})
            print(f"[{src['label']}] {r.status_code} new={len(set(new))}", file=sys.stderr)
        except Exception as e:
            out.append({"label": src["label"], "url": src["url"], "error": str(e), "codes_new": []})
            print(f"[{src['label']}] ERROR {e}", file=sys.stderr)
    json.dump(out, open('/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/team31_scratch_extract.json','w'), indent=1)
    for o in out:
        print(o["label"], o.get("status", o.get("error")), o.get("codes_new", []))

if __name__ == "__main__":
    main()
