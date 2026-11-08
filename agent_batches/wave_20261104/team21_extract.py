#!/usr/bin/env python3
"""team21: extract (name, code) pairs from saved listicle HTML files."""
import re, json, html as ihtml, pickle, os

WDIR = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261104")
union = pickle.load(open(os.path.join(WDIR, "team21_union.pkl"), "rb"))

PORN = ["bokep", "pornhub", "xxx", "nude", "sex video", "escort", "call girl",
        "fuck", "dick", "pussy", "boobs", "anal", "porn", "hentai",
        "tante", "video bebas", "video viral", "pemersatu bangsa", "viral twitter"]

def clean(t):
    t = ihtml.unescape(t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def extract_group_pairs(htmlfile, cc, category, max_items=None):
    html = open(htmlfile, encoding="utf-8", errors="ignore").read()
    out = []
    # pattern: name-ish text followed by chat.whatsapp.com/<code> (non-invite, 20-24 chars)
    for m in re.finditer(r"(?P<pre>.{0,120}?)https?://chat\.whatsapp\.com/(?!invite/)(?P<code>[A-Za-z0-9]{20,24})\b", html):
        pre = clean(m.group("pre"))
        code = m.group("code")
        # try to get a name from the tail of pre (after last ':' or '>' or '-')
        name = re.split(r"[:>»\-–—|]\s*", pre)[-1].strip()
        name = re.sub(r"^(https?://\S+|\d+[\.\)]|\*+)\s*", "", name).strip()
        name = name[-80:]
        out.append((name, code))
    # dedupe by code, skip union, skip invite-form
    seen, res = set(), []
    for name, code in out:
        if code in seen or code in union:
            continue
        seen.add(code)
        res.append({"name": name, "code": code, "country": cc, "category": category,
                    "source": os.path.basename(htmlfile)})
        if max_items and len(res) >= max_items:
            break
    return res

if __name__ == "__main__":
    import sys
    tag = sys.argv[1]; cc = sys.argv[2]; cat = sys.argv[3]
    pairs = extract_group_pairs(os.path.join(WDIR, f"team21_{tag}.html"), cc, cat)
    json.dump(pairs, open(os.path.join(WDIR, f"team21_{tag}_candidates.json"), "w"),
              ensure_ascii=False, indent=1)
    print(tag, "candidates:", len(pairs))
