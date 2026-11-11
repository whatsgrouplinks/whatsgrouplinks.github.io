#!/usr/bin/env python3
"""TEAM 01 — rename pass over BANKED verified records whose name is junk
(HTML fragments, pure-symbol strings, 'Entrar no Grupo', dates).
Fetches og:title via head-read; replaces the name (and regenerates the
description) when the current name is junk and og:title is usable.
Run AFTER verification passes finish; edits team01-leads-slice1.json in place
(and the stream file if present).
"""
import json, re, sys, os
sys.path.insert(0, "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111")
from team01_verify_stream import head_check

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"

def is_junk_name(n):
    if not n or not n.strip():
        return True
    s = n.strip()
    if "<" in s or ">" in s:
        return True
    if "class=" in s or "wp-block" in s or "is-style" in s or "href=" in s:
        return True
    if s in {"Now", "NOW", "Link", "Links", "Group", "CHAT LINK", "Entrar no Grupo",
             "Join", "Join Group", "Join Now"}:
        return True
    if re.match(r"^[A-Z][a-z]{2} \d{1,2}, \d{4}$", s):
        return True
    if len(s) <= 2:
        return True
    if not re.search(r"[A-Za-z0-9]", s):
        return True  # pure symbols/emoji, no alphanumeric
    return False

def main():
    for path in [os.path.join(WAVE, "team01-leads-slice1.json"),
                 os.path.join(WAVE, "team01-stream-verified.json")]:
        try:
            recs = json.load(open(path))
        except Exception:
            continue
        fixed = 0
        for rec in recs:
            if not is_junk_name(rec.get("name", "")):
                continue
            code = rec["invite"].split("/")[-1]
            http, og, err = head_check(code)
            if http == 200 and og and not is_junk_name(og):
                rec["name"] = og[:120]
                cat = rec.get("category", "Community & Social")
                rec["description"] = (f"Join {og[:120]}, an active WhatsApp group for {cat.lower()}. "
                                      "Connect with members, share updates and stay in touch.")
                fixed += 1
                print(f"  renamed {code}: -> {og[:60]}", flush=True)
            else:
                print(f"  could not rename {code} (og={og!r} err={err})", flush=True)
        if fixed:
            tmp = path + ".tmp"
            json.dump(recs, open(tmp, "w"), ensure_ascii=False)
            os.replace(tmp, path)
        print(f"{os.path.basename(path)}: renamed {fixed}", flush=True)

if __name__ == "__main__":
    main()
