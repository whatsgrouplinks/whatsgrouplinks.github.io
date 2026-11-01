#!/usr/bin/env python3
"""Append WhatsApp group entries to team111-social.json with dedupe by invite code."""
import json, sys, os, re

PATH = "/home/hatch/workspace/whatsapp-groups-site/scraped/team111-social.json"
BANNED = ["porn", "xxx", "sex", "sexy", "nude", "escort", "call girl", "desi girl",
          "hot girl", "bhabhi", "aunty video", "mms", "leaked video", "18+",
          "dating", "playboy", "massage girl", "adult"]

items = []
if os.path.exists(PATH):
    try:
        items = json.load(open(PATH))
    except Exception:
        items = []

def code_of(invite):
    m = re.search(r"chat\.whatsapp\.com/([A-Za-z0-9\-_]+)", invite)
    return m.group(1) if m else ""

seen = {code_of(i.get("invite", "")) for i in items}
added, dup, skip = 0, 0, 0
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    obj = json.loads(line)
    code = code_of(obj.get("invite", ""))
    text = (obj.get("name", "") + " " + obj.get("description", "")).lower()
    if len(code) < 10 or "..." in obj.get("invite", ""):
        skip += 1
        continue
    if any(b in text for b in BANNED):
        skip += 1
        continue
    if code in seen:
        dup += 1
        continue
    seen.add(code)
    obj["invite"] = f"https://chat.whatsapp.com/{code}"
    obj.setdefault("image", "")
    obj.setdefault("country", "")
    items.append(obj)
    added += 1

json.dump(items, open(PATH, "w"), ensure_ascii=False, indent=1)
print(f"added={added} dup={dup} skip={skip} total={len(items)}")
