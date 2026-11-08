#!/usr/bin/env python3
"""Team 12: assemble final wave-dir outputs from scratch verified/pending."""
import json, re

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261107/"
SCRATCH = WAVE + "scratch-team12/"
CANON = {"Education","Jobs","Entertainment","Islamic","News","Sports","Technology","Health",
         "Business","Gaming","Friendship","Community & Social","Online Earning","Crypto","Cooking",
         "Poetry","Travel","Scholarship","Freelance","Real Estate","Buy & Sell","Finance","Funny"}
INVITE_RE = re.compile(r"^https://chat\.whatsapp.com/(invite/)?[A-Za-z0-9]{22}$")

union = set(json.load(open(WAVE + "dedupe_union.json")))
verified = json.load(open(SCRATCH + "verified.json"))
pending = json.load(open(SCRATCH + "pending.json"))

seen = set()
clean_v, clean_p = [], []
for v in verified:
    code = v["invite"].rsplit("/", 1)[-1]
    assert INVITE_RE.match(v["invite"]), v
    assert v["category"] in CANON, v
    assert v["country"] and v["country"] not in ("TR", "BR"), v
    assert v["name"] and "http" not in v["description"], v
    assert code not in union, v
    if code in seen:
        continue
    seen.add(code)
    clean_v.append({k: v[k] for k in ("name", "category", "country", "description", "invite", "image")})
for p in pending:
    code = p["invite"].rsplit("/", 1)[-1]
    assert INVITE_RE.match(p["invite"]), p
    assert code not in union, p
    if code in seen:
        continue
    seen.add(code)
    clean_p.append({k: p[k] for k in ("name", "category", "country", "description", "invite", "image")})

leads = [
 {"url": "https://whatsappkanali.com/?page=4",
  "what": "WhatsAppKanali homepage page 4 — next run; p1-p3 harvested 2026-11-07 (66 records, 39 fresh, 0 verified live — deeper pages are stale/dead-heavy)."},
 {"url": "https://whatsappkanali.com/kategori/sohbet?page=2",
  "what": "WhatsAppKanali Sohbet p2 — harvested 2026-11-06 (13 new codes then); re-check only for newly added listings, do not re-harvest as fresh."},
 {"url": "https://whatsappkanali.com/kategori/is-ilanlari?page=2",
  "what": "WhatsAppKanali jobs p2 — harvested 2026-11-06; re-check only for new listings."},
 {"url": "https://whatsappkanali.com/kategori/egitim?page=2",
  "what": "WhatsAppKanali education p2 — harvested 2026-11-06; re-check only for new listings."},
 {"url": "https://whatsappkanali.com/kategori/oyun?page=3",
  "what": "WhatsAppKanali gaming p3 — p2 returned 0 records 2026-11-07 (category may have <2 pages); low priority."},
 {"url": "https://linkado.app/?page=4",
  "what": "Linkado homepage page 4 onward — p1-p3 harvested 2026-11-07 (886 grupo pages fetched, 801 records); each page lists 24 groups, fetch grupo pages for invite codes."},
 {"url": "https://linkado.app/?page=5",
  "what": "Linkado homepage page 5 — same method as page 4 lead."},
 {"url": "https://linkado.app/?page=6",
  "what": "Linkado homepage page 6 — same method as page 4 lead."},
 {"url": "https://linkado.app/categoria/amizade?page=2",
  "what": "Linkado Amizade p2 — p1 harvested 2026-11-07; paginated listing, fresh groups daily. Same ?page=2 pattern applies to every /categoria/<slug> harvested this run (namoro, dinheiro, games, figurinhas, comprar-e-venda, trabalho, educacao, tecnologia, esportes, musica, series, fitness, religiao, links, carros, cidades, lgbt, moda-e-beleza, politica, status)."},
 {"url": "https://linkado.app/categorias",
  "what": "Linkado full category index — check for new categories next run."},
 {"url": "https://linkado.app/grupo/6aea63a7da5f4d7d145e84e6",
  "what": "METHOD NOTE 2026-11-07: Linkado invite codes ARE exposed — fetch /grupo/<id> with RSC:1 header (or plain page); the RSC payload carries chat.whatsapp.com/<code> plus og:title/og:description (breadcrumb JSON-LD position 4 = group name, double-escaped in RSC). Plain HTML meta og:title is truncated with '...' — prefer the og:description 'Grupo de WhatsApp <NAME>, na categoria <PT>' for the full name. RSC responses decode as latin-1 by default — decode content as UTF-8 or repair mojibake (Ã/ð markers). Prior runs wrongly called Linkado app-gated."},
 {"url": "https://whatsappkanali.com/",
  "what": "METHOD NOTE 2026-11-07: WhatsAppKanali listing RSC payloads expose inviteUrl directly; parse title/categorySlug/inviteUrl from the window before each inviteUrl. ~60% of records are whatsapp.com/channel links (excluded). Use requests (not curl — curl timed out repeatedly); 8-worker parallel fetch works, site is slow under shared-proxy load. NOTE: fresh WK codes verified 0/39 live this run (35 dead + 4 transport-then-dead on recheck) — deeper pages are stale; prioritise homepage p1 + category p1s next run."},
]

json.dump(clean_v, open(WAVE + "team12-whatsappkanali-linkado.json", "w"), ensure_ascii=False, indent=1)
json.dump(clean_p, open(WAVE + "team12-whatsappkanali-linkado-pending.json", "w"), ensure_ascii=False, indent=1)
json.dump(leads, open(WAVE + "team12-whatsappkanali-linkado-leads.json", "w"), ensure_ascii=False, indent=1)
print(f"VERIFIED {len(clean_v)} PENDING {len(clean_p)} LEADS {len(leads)}")
import collections
print("verified by country:", collections.Counter(v["country"] for v in clean_v))
print("verified by category:", collections.Counter(v["category"] for v in clean_v))
print("pending by country:", collections.Counter(p["country"] for p in clean_p))
