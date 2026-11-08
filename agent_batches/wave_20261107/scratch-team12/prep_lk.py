#!/usr/bin/env python3
"""Team 12: repair Linkado raw names/categories (mojibake, truncation, PT suffix)."""
import json, re, html

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261107/"
SCRATCH = WAVE + "scratch-team12/"

PT_CAT = {"comprar e venda": "Buy & Sell", "amizade": "Friendship", "namoro": "Friendship",
          "dinheiro": "Finance", "games": "Gaming", "figurinhas": "Funny", "trabalho": "Jobs",
          "educação": "Education", "educacao": "Education", "tecnologia": "Technology",
          "esportes": "Sports", "música": "Entertainment", "musica": "Entertainment",
          "séries": "Entertainment", "series": "Entertainment", "fitness": "Health",
          "religião": "Community & Social", "religiao": "Community & Social",
          "links": "Community & Social", "carros": "Community & Social",
          "cidades": "Community & Social", "lgbt": "Community & Social",
          "moda e beleza": "Community & Social", "política": "News", "politica": "News",
          "status": "Community & Social"}

def fix_mojibake(s):
    if not s:
        return s
    # only attempt when mojibake markers present
    if not re.search(r"[Ãðâ€]", s):
        return s
    try:
        fixed = s.encode("latin-1").decode("utf-8")
    except Exception:
        return s
    # accept if it removed the markers
    if re.search(r"[Ãð]", fixed):
        return s
    return fixed

def clean(s):
    s = fix_mojibake(html.unescape(s or "").strip())
    return re.sub(r"\s+", " ", s)

lk = json.load(open(SCRATCH + "lk_raw.json"))
out = {}
stats = {"trunc_fixed": 0, "suffix_stripped": 0, "cat_fixed": 0, "dropped": 0}
for code, r in lk.items():
    name = clean(r.get("name", ""))
    desc = clean(r.get("desc", ""))
    cat = r.get("category", "Community & Social")
    # category from og:description "na categoria X"
    m = re.search(r"na categoria ([^.]+)\.", desc, re.I)
    if m:
        pt = m.group(1).strip().lower()
        if pt in PT_CAT and PT_CAT[pt] != cat:
            cat = PT_CAT[pt]
            stats["cat_fixed"] += 1
    # full name from description: "Grupo de WhatsApp <NAME>, na categoria"
    dm = re.match(r"Grupo de WhatsApp (.+?), na categoria", desc, re.I)
    desc_name = clean(dm.group(1)) if dm else ""
    if (not name) or name.endswith("...") or " - " in name:
        if desc_name and not desc_name.endswith("..."):
            name = desc_name
            stats["trunc_fixed"] += 1
    # strip trailing " - <PT category label>"
    sm = re.search(r"\s+-\s+([A-Za-zÀ-ú ]+)$", name)
    if sm and sm.group(1).strip().lower() in PT_CAT:
        name = name[:sm.start()].strip()
        stats["suffix_stripped"] += 1
    name = re.sub(r"^Grupo de WhatsApp\s+", "", name, flags=re.I).strip()
    if not name or name.endswith("..."):
        stats["dropped"] += 1
        continue
    out[code] = {"name": name, "category": cat, "code": code, "desc": desc}
print("in:", len(lk), "out:", len(out), "stats:", stats)
json.dump(out, open(SCRATCH + "lk_raw2.json", "w"), ensure_ascii=False, indent=1)
for c, r in list(out.items())[:10]:
    print(c, r["name"], "|", r["category"])
