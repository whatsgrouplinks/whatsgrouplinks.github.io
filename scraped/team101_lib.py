"""Team 101 dedup/save helper. Usage: python3 team101_lib.py --append file-with-links.json OR import functions."""
import json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))  # ~/workspace/whatsapp-groups-site/scraped
OUT = os.path.join(BASE, "team101-dirH.json")
GROUPS_JSON = os.path.join(os.path.dirname(BASE), "groups.json")

def norm(invite):
    return invite.strip().rstrip("/")

def load_existing():
    d = json.load(open(GROUPS_JSON))
    s = set()
    for x in d:
        inv = x.get("invite", "")
        if inv:
            s.add(norm(inv).lower())
    return s

def load_out():
    if os.path.exists(OUT):
        try:
            return json.load(open(OUT))
        except Exception:
            return []
    return []

LINK_RE = re.compile(r"https://chat\.whatsapp\.com/([A-Za-z0-9]+)")

def extract_links(text):
    found = []
    for m in LINK_RE.finditer(text):
        found.append("https://chat.whatsapp.com/" + m.group(1))
    return found

def add_candidates(cands, existing, current):
    """cands: list of dicts with name/category/description/image/invite. Returns (added, skipped_dup)."""
    seen = {norm(x["invite"]).lower() for x in current}
    added = 0
    skipped = 0
    for c in cands:
        inv = norm(c.get("invite", ""))
        if not inv or not LINK_RE.fullmatch(inv):
            continue
        key = inv.lower()
        if key in existing or key in seen:
            skipped += 1
            continue
        c["invite"] = inv
        c.setdefault("image", "")
        current.append(c)
        seen.add(key)
        added += 1
    return added, skipped

def save(current):
    json.dump(current, open(OUT, "w"), ensure_ascii=False, indent=1)
