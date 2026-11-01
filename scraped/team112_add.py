#!/usr/bin/env python3
"""Merge team112 chunk JSON files into team112-niche-jobs.json.

Dedupes by invite code within the file and against _existing_invites.pkl
(already-known invites). Usage: python3 team112_add.py chunk.json [...]
"""
import json, os, pickle, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "team112-niche-jobs.json")

CODE_RE = re.compile(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{10,})")

def canon(invite: str):
    m = CODE_RE.search(invite or "")
    return "https://chat.whatsapp.com/" + m.group(1) if m else None

def load_existing():
    p = os.path.join(BASE, "_existing_invites.pkl")
    if os.path.exists(p):
        return set(pickle.load(open(p, "rb")))
    return set()

def load_out():
    if os.path.exists(OUT):
        try:
            return json.load(open(OUT, encoding="utf-8"))
        except Exception:
            return []
    return []

def main():
    existing = load_existing()
    cur = load_out()
    seen = set()
    for g in cur:
        c = canon(g.get("invite", ""))
        if c:
            seen.add(c)
    added = skipped_dup = skipped_known = skipped_bad = 0
    for path in sys.argv[1:]:
        data = json.load(open(path, encoding="utf-8"))
        items = data if isinstance(data, list) else [data]
        for g in items:
            c = canon(g.get("invite", ""))
            name = (g.get("name") or "").strip()
            if not c or not name:
                skipped_bad += 1
                continue
            g["invite"] = c
            if c in seen:
                skipped_dup += 1
                continue
            if c in existing:
                skipped_known += 1
                continue
            g.setdefault("category", "Jobs")
            g.setdefault("description", "")
            g.setdefault("image", "")
            g.setdefault("country", "")
            cur.append(g)
            seen.add(c)
            added += 1
    json.dump(cur, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"added={added} skipped_dup_infile={skipped_dup} "
          f"skipped_already_known={skipped_known} skipped_bad={skipped_bad} "
          f"total_in_file={len(cur)}")

if __name__ == "__main__":
    main()
