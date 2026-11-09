#!/usr/bin/env python3
"""Team 01 - extract invite codes + context from fetched linkado detail pages."""
import re, glob, json, os, html as htmlmod

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
CODE_RE = re.compile(r"chat\.whatsapp\.com(?:/|\\u002f|\\/|%2F)+([A-Za-z0-9_\-]{8,})")
existing = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
wk_fresh = set(json.load(open(os.path.join(WAVE, "team01_fresh_codes.json"))).keys())

# category pages: idx -> (slug, site category)
CAT = {
    64: ("categorias", "Community & Social"), 65: ("populares", "Community & Social"),
    66: ("amizade", "Friendship"), 67: ("carros", "Community & Social"),
    68: ("cidades", "Community & Social"), 69: ("comprar-e-venda", "Buy Sell"),
    70: ("dinheiro", "Finance"), 71: ("educacao", "Education"),
    72: ("esportes", "Sports"), 73: ("figurinhas", "Entertainment"),
    74: ("games", "Gaming"), 75: ("lgbt", "Community & Social"),
    76: ("links", "Community & Social"), 77: ("moda-e-beleza", "Community & Social"),
    78: ("musica", "Entertainment"), 79: ("namoro", "Friendship"),
    80: ("politica", "Community & Social"), 81: ("religiao", "Community & Social"),
    82: ("series", "Entertainment"), 83: ("status", "Entertainment"),
    84: ("tecnologia", "Technology"), 85: ("trabalho", "Jobs"),
}
grupo_to_cats = {}
for idx, (slug, cat) in CAT.items():
    try:
        h = open(os.path.join(WAVE, "team01_raw", f"p{idx:03d}.html"), encoding="utf-8", errors="ignore").read()
    except FileNotFoundError:
        continue
    for m in re.finditer(r"/grupo/([0-9a-f]{24})", h):
        u = "https://linkado.app/grupo/" + m.group(1)
        grupo_to_cats.setdefault(u, []).append(cat)

urls = [l.strip() for l in open(os.path.join(WAVE, "team01_linkado_grupo_urls.txt")) if l.strip()]
out = {}
no_code = []
for i, u in enumerate(urls, start=1):
    f = os.path.join(WAVE, "team01_raw_linkado", f"g{i}.html")
    if not os.path.exists(f) or os.path.getsize(f) < 1000:
        continue
    h = open(f, encoding="utf-8", errors="ignore").read()
    codes = set()
    for m in CODE_RE.finditer(h):
        c = m.group(1)
        if len(c) > 22:
            c = c[:22]
        codes.add(c)
    if not codes:
        no_code.append(u)
        continue
    tm = re.search(r"<title>([^<]*)</title>", h)
    title = htmlmod.unescape(tm.group(1)).strip() if tm else ""
    # linkado title form: "Grupo de WhatsApp <NAME> - <cat>"
    name = title
    if name.startswith("Grupo de WhatsApp "):
        name = name[len("Grupo de WhatsApp "):]
    if " - " in name:
        name = name.rsplit(" - ", 1)[0]
    dm = re.search(r'<meta name="description" content="([^"]*)"', h)
    desc = htmlmod.unescape(dm.group(1)).strip() if dm else ""
    cats = sorted(set(grupo_to_cats.get(u, ["Community & Social"])))
    for c in codes:
        if c in existing or c in wk_fresh:
            continue
        out.setdefault(c, {"grupo_url": u, "categories": cats,
                           "linkado_name": name, "linkado_desc": desc})
print("detail pages present:", len([1 for i in range(1, len(urls)+1) if os.path.exists(os.path.join(WAVE, "team01_raw_linkado", f"g{i}.html"))]))
print("pages with no code:", len(no_code))
print("fresh codes from linkado:", len(out))
json.dump(out, open(os.path.join(WAVE, "team01_linkado_codes.json"), "w"), indent=1, ensure_ascii=False)
json.dump(no_code, open(os.path.join(WAVE, "team01_linkado_nocode.json"), "w"), indent=1)
