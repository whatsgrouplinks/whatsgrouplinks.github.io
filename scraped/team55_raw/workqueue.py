import json, os, re
BASE = '/home/hatch/workspace/whatsapp-groups-site/scraped/team55_raw'
QPATH = os.path.join(BASE, 'queue.json')

def load():
    if os.path.exists(QPATH):
        with open(QPATH) as f: return json.load(f)
    return {"pages": []}

def save(q):
    with open(QPATH, 'w') as f: json.dump(q, f, ensure_ascii=False, indent=1)

def add_page(slug, page_id, url, groups):
    q = load()
    q["pages"].append({"slug": slug, "page_id": page_id, "url": url, "groups": groups})
    save(q)
    print(f"added page {slug}: {len(groups)} groups")

def set_invite(slug, outlink, invite):
    q = load()
    n = 0
    for p in q["pages"]:
        if p["slug"] == slug:
            for g in p["groups"]:
                if g["outlink"] == outlink and not g.get("invite"):
                    g["invite"] = invite; n += 1
    save(q)
    return n
