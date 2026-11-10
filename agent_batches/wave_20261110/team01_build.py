#!/usr/bin/env python3
"""Team 01 wave 20261110 slice 1 - build the four exact output files."""
import json, os, re, html as htmlmod

BASE = "/home/hatch/workspace/whatsapp-groups-site"
WAVE = os.path.join(BASE, "agent_batches/wave_20261110")

existing = set(json.load(open(os.path.join(BASE, ".existing_codes.json"))))
groups = json.load(open(os.path.join(BASE, "groups.json")))
for it in groups:
    m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_\-]+)', it.get('invite', ''))
    if m:
        existing.add(m.group(1))

ver_slice = json.load(open(os.path.join(WAVE, "team01_verify.json")))
ver_grupo = json.load(open(os.path.join(WAVE, "team01_grupo_verify.json")))
ctx_grupo = json.load(open(os.path.join(WAVE, "team01_grupo_context.json")))
ctx_slice = json.load(open(os.path.join(WAVE, "team01_context.json")))
discovered = json.load(open(os.path.join(WAVE, "team01_discovered_raw.json")))

ADULT_RE = re.compile(r'🔞|🥵|\bsexy\b|\bhookup\b|escort|\bporn\b|\bxxx\b', re.I)
SCAM_RE = re.compile(r'b-?love|forsage|s?heyi\b|airdrop|paypal loader|bitfinex|counterfeit currency|crypto.?doubling|carding|double (your )?money|free money', re.I)

def clean_name(t):
    t = htmlmod.unescape(t or "")
    t = re.sub(r'^\s*Grupo de WhatsApp\s+', '', t, flags=re.I)
    t = re.sub(r'\s+-\s*(Amizade|Comprar e venda|Carros|Cidades|Cidades|Dinheiro|Educação|Esportes|Games|Moda e Beleza|Música|Namoro|Política|Religião|Séries|Status|Tecnologia|Trabalho|Figurinhas|Links|LGBT)\s*$', '', t)
    t = t.strip(' *_~`•')
    t = t.lstrip('•').strip()
    t = re.sub(r'\s+', ' ', t).strip()
    return t

SALES_RE = re.compile(r'venda|oferta|compra|achado|vitrine|divulga|econômic|promo|desconto|cupom', re.I)

def category_for(code, ctx):
    raw = (ctx.get("category_raw") or "").lower()
    name = ctx.get("name", "")
    if raw == "comprar-e-venda" or SALES_RE.search(name):
        return "Buy Sell"
    return "Community & Social"

DESCRIPTIONS = {
    "BBeKu36aCGSDB4RMxR0GVN": "A friendship group for couples to share love and affection. Join to connect with other couples and chat.",
    "Ccgaf5S2xQ1AlN2eW0Kqdn": "A friendship group for chatting, joking and hanging out with new friends. Respect and togetherness are the house rules.",
    "D99O7w1NFNF16JMn1TDjEM": "A deals group sharing today's best finds and offers. Join to see what is on offer today.",
    "DO2NR2xIo4DAV5IuZPDY8t": "A friendship group for making new friends and chatting. Join to meet people and connect.",
    "DSKVgDI5VLs2mni1vm8T32": "A showcase of exclusive offers on electronics, accessories, style and household items. Join for promotions and discounts.",
    "GK4rYkZr7JgKosqaYsls6o": "A friendship group for chatting and meeting new people. Read the group rules after joining.",
    "IBoQfLGYKcgJvGDD6M89GP": "A friendship group without borders for making friends from anywhere. Join to chat and connect with new people.",
    "IlKDOFhxkek6uWtN71xIn6": "A friendship group for making new friends. Join to chat and connect with other members.",
    "J9RrYpCQft39KsA2CPBsFd": "A friendship group for chatting and joking around with new friends. Join to meet people and have fun.",
    "Jo5HQ3RlEJ6GfhvWVKcIJR": "A deals club sharing hand-picked finds, discounts and coupons. Join for your favourite offers.",
    "KW12eG0sSxHGkpzrEP1mqg": "A light, friendly chat group for making friends and conversation. Join to meet new people and chat.",
}

verified = []
pending = []
exclusions = []
dead = 0

for r in ver_slice + ver_grupo:
    code = r["code"]
    if r["status"] == "pending":
        pending.append({"code": code, "reason": r.get("reason", "transport-fail"),
                        "invite": f"https://chat.whatsapp.com/{code}"})
        continue
    if r["status"] == "dead":
        dead += 1
        continue
    # live
    if code in existing:
        exclusions.append({"code": code, "reason": "code already in existing union on final re-check (not banked)"})
        continue
    title = (r.get("title") or "").strip()
    ctx = r.get("ctx") or {}
    name = clean_name(title) or clean_name(ctx.get("name", ""))
    blob = f"{title} {name} {ctx.get('description','')}"
    if ADULT_RE.search(blob):
        exclusions.append({"code": code, "reason": "adult-sexual signal in og:title/name (dropped)", "name": name})
        continue
    if SCAM_RE.search(blob):
        exclusions.append({"code": code, "reason": "scam signal in title/description (dropped)", "name": name})
        continue
    desc = DESCRIPTIONS.get(code)
    if not desc:
        desc = f"Join this WhatsApp group to chat and connect with other members about {name}." if name else "Join this WhatsApp group to chat and connect with other members."
    desc = re.sub(r'https?://\S+', '', desc)
    desc = re.sub(r'\+\d[\d\s\-()]{9,}', '', desc)
    verified.append({"name": name, "category": category_for(code, ctx),
                     "country": "BR" if "linkado" in (ctx.get("listing_url") or "") else (ctx.get("country") or "International"),
                     "description": desc.strip(),
                     "invite": f"https://chat.whatsapp.com/{code}"})

# exclusions from earlier stages
exclusions.append({"code": "BLwtFQt47paJqiQcZDN44W", "reason": "adult-signal in listing name (🔞) — not verified, not banked"})
for c in ["E51zHCiU0i", "E51zHCiU0ib1", "E51zHCiU0ib1M"]:
    exclusions.append({"code": c, "reason": "truncated invite-code artifact from whatsappkanali RSC payload (no 22-char full form in any raw file) — not verified, not banked"})
for c in ["KogmBdn7zKfGGb8zGaG", "KogmBdn7zKfGGb8zGaGt"]:
    exclusions.append({"code": c, "reason": "truncated prefix of already-banked code KogmBdn7zKfGGb8zGaGt7g — not verified, not banked"})

# leads file
def lead_note(u):
    if "linkado.app/grupo/" in u:
        return "linkado grupo detail page (invite code in HTML) — fetch for future waves"
    if "groupsinvite.link/group/link/" in u:
        return "groupsinvite detail page (related group) — invite is JS/click-gated; rules page sampled resolves to a WhatsApp channel link"
    if "groupsinvite.link/group/category/" in u or "groupsinvite.link/group/country/" in u:
        return "groupsinvite category/country listing page"
    if "whatsappkanali.com/sehir/" in u:
        return "whatsappkanali city/subcategory listing page"
    if "whatsappkanali.com/grup/" in u:
        return "whatsappkanali group detail page"
    if "linkado.app/categoria/" in u or "linkado.app/categorias" in u or "populares" in u:
        return "linkado category listing page"
    return "discovered listing page"

leads = [{"url": d["url"], "source": d["found_on"], "note": lead_note(d["url"])} for d in discovered]

json.dump(verified, open(os.path.join(WAVE, "team01-leads-slice1.json"), "w"), indent=1, ensure_ascii=False)
json.dump(pending, open(os.path.join(WAVE, "team01-leads-slice1-pending.json"), "w"), indent=1, ensure_ascii=False)
json.dump(leads, open(os.path.join(WAVE, "team01-leads-slice1-leads.json"), "w"), indent=1, ensure_ascii=False)

summary = {
    "team": 1,
    "slice": "leads slice 1",
    "sources": [
        "whatsappkanali.com (61 Turkish city/subcategory listing pages)",
        "linkado.app (23 pages: sitemap + categorias + populares + 20 category pages; plus 142 grupo detail pages fetched from those listings)",
        "groupsinvite.link (100 single-group detail pages)"
    ],
    "verified": len(verified),
    "pending": len(pending),
    "leads": len(leads),
    "dead": dead,
    "exclusions": exclusions,
    "resume": "Slice pages all fetched (184/184, 15 transient-000 retries all recovered). Remaining yield: 719 unfetched linkado /grupo/ detail pages found on the slice category/populares pages (150 fetched, 142 processed — their URLs are in the leads file via the sitemap set); 19,731 linkado sitemap grupo URLs banked as leads. Groupinvite own-codes NOT extractable via curl: detail HTML has no chat.whatsapp.com link and the /group/rules/<id>/ interstitial sampled (SHOESKARTEL) links to a WhatsApp CHANNEL (www.whatsapp.com/channel/0029VaB1bJF9WtC2mcjdng1m) — channels are dropped per rules; a browser leg would be needed to confirm whether any of the 100 resolve to real group invites. Whatsappkanali /grup/<slug> detail pages (e.g. girgir-samata, whose invite is truncated in listing JSON) are banked as leads for future waves.",
    "notes": "Checked 67 fresh codes in total: 23 from the 184 slice pages (all DEAD — HTTP 200 with empty og:title after spaced retries; control check on a known-live code returned a proper og:title, so the method is sound) + 44 from 142 linkado grupo detail pages (11 LIVE, 33 dead). 0 transport-pending. whatsappkanali listings are stale (same finding as wave 20261109 team01: its 27 fresh codes were all dead then too) and its RSC payload truncates invite URLs, producing prefix artifacts. Linkado category pages carry no invite codes themselves — codes live on /grupo/ detail pages. Network was heavily congested during the run (many wave teams fetching concurrently; single requests took 7-27s, several 000 timeouts that recovered on retry). Union dedupe base: 108,364 codes (.existing_codes.json + groups.json; groups.json codes are a subset, so union equals the .existing_codes.json count — the task brief said 108,365, off by one). No groupjoin.link Adult items in this slice."
}
json.dump(summary, open(os.path.join(WAVE, "team01-leads-slice1-summary.json"), "w"), indent=1, ensure_ascii=False)

print("verified:", len(verified))
for v in verified:
    print(" ", v["name"][:60], "|", v["category"], "|", v["country"], "|", v["invite"])
print("pending:", len(pending), "dead:", dead, "leads:", len(leads), "exclusions:", len(exclusions))
