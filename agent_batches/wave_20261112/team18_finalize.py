#!/usr/bin/env python3
"""TEAM18 finalize: restore gid 527217, fix 2 candidate records, assemble the 4 output files."""
import json, re

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"

# --- 1. igrupos leads: restore 527217 (full desc has no lemon), flag 527138 ---
leads = json.load(open(f"{WAVE}/team18-igrupos-leads-raw.json"))
recs = {json.loads(l)["gid"]: json.loads(l) for l in open(f"{WAVE}/team18-igrupos-mined.jsonl")}
r217 = recs[527217]
leads.append({
    "url": r217["url"], "source": "igrupos.com", "kind": "detail",
    "gid": 527217, "name": r217["title"], "description": r217["description"],
    "country": r217.get("country", ""), "country_flag_unverified": True,
    "tags": r217.get("tags", []), "category_guess": "Gaming",
    "note": "RESTORED after full-desc check: combat/world roleplay, no erotic ('lemon') content in the full description (unlike sister post gid 527262 which was dropped). Invite code NOT in static HTML; browser leg must click through.",
})
leads.sort(key=lambda x: x["gid"])
for l in leads:
    if l["gid"] == 527138:
        l["note"] = "FLAG FOR BROWSER LEG: 'Mundo Crypto - Estrategias para aplicar en cualquier instrumento en particular crypto' = trading-strategies group. Screen before banking: drop if it is an airdrop / binary-option / daily-profits promo; keep only if a plain crypto-discussion group. Invite code NOT in static HTML; browser leg must click through."

# --- 2. fallback leads (grupodewhatsapp + gruposwhats.app), all new vs team32 ---
fallback = [
    {"url": "https://app.grupodewhatsapp.com/group/mj-vagas-de-trabalho", "source": "grupodewhatsapp.com", "kind": "detail",
     "name": "MJ Vagas de Trabalho", "description": "Quem busca oportunidades de emprego encontra aqui diversas vagas de trabalho divulgadas por empresas e recrutadores. 1011+ membros. Criado em 4 de janeiro de 2026. Verificado em 12 de novembro de 2026.",
     "country": "BR", "category_guess": "Jobs",
     "note": "Invite code NOT in text fetch (join button is JS-gated); browser leg must open the detail page and click through. 'Also joined' graph on this page links 6 more Jobs groups (see below)."},
    {"url": "https://app.grupodewhatsapp.com/group/conecta-emprego-rj-5-suas-habilidades-sao-reconhecidas", "source": "grupodewhatsapp.com", "kind": "detail",
     "name": "Conecta Emprego RJ 5 - Suas Habilidades São Reconhecidas", "description": "Vagas de emprego no Rio de Janeiro. 1800+ seguidores. Verificado em 11 de novembro de 2026.",
     "country": "BR", "category_guess": "Jobs",
     "note": "Invite code NOT in text fetch; browser leg must click through."},
    {"url": "https://app.grupodewhatsapp.com/group/noticias-emprego-rj", "source": "grupodewhatsapp.com", "kind": "detail",
     "name": "Notícias & Emprego RJ", "description": "Notícias atualizadas e vagas de emprego no Rio de Janeiro. 1018+ membros. Entrada com aprovação. Verificado em 11 de novembro de 2026. Criado em 15 de novembro de 2024.",
     "country": "BR", "category_guess": "Jobs",
     "note": "Invite code NOT in text fetch; browser leg must click through."},
    {"url": "https://app.grupodewhatsapp.com/group/vagas-de-freelancer-e-clt", "source": "grupodewhatsapp.com", "kind": "detail",
     "name": "vagas de freelancer e CLT", "description": "Vagas de freelancer e posições CLT. 5600+ seguidores. Verificado em 12 de novembro de 2026.",
     "country": "BR", "category_guess": "Jobs",
     "note": "Invite code NOT in text fetch; browser leg must click through."},
]
graph_names = [
    ("Dani Vagas De Emprego - RJ", "Vagas de emprego no Rio de Janeiro. 1K membros, entrada com aprovação. Linked from the 'also joined' graph on the MJ Vagas de Trabalho page."),
    ("Conecta Emprego RJ - Suas Habilidades São Reconhecidas", "Vagas de emprego e cursos no Rio de Janeiro. 50K seguidores. Linked from the 'also joined' graph on the MJ Vagas de Trabalho page."),
    ("Bora Trabalhar Maceió e Região", "Vagas de emprego em Maceió e região. 982 membros. Linked from the 'also joined' graph on the MJ Vagas de Trabalho page."),
    ("EMPREGOS MANAUS", "Vagas de emprego em Manaus. 5.5K seguidores. Linked from the 'also joined' graph on the MJ Vagas de Trabalho page."),
    ("R&V Empregos e Oportunidades RJ-OFICIAL", "Vagas de emprego e dicas de carreira no Rio de Janeiro. 51K seguidores. Linked from the 'also joined' graph on the MJ Vagas de Trabalho page."),
    ("Mj Vagas De Trabalho (2nd listing)", "Vagas de emprego. 525 membros. Second listing with the same name, linked from the 'also joined' graph on the MJ Vagas de Trabalho page."),
]
for name, desc in graph_names:
    fallback.append({"url": "https://app.grupodewhatsapp.com/group/mj-vagas-de-trabalho", "source": "grupodewhatsapp.com", "kind": "detail-via-graph",
                     "name": name, "description": desc, "country": "BR", "category_guess": "Jobs",
                     "note": "No exact detail URL captured (graph outlink only) - resolve the slug via site search for the exact name before opening. Invite code NOT in text fetch; browser leg must click through."})
gw = [
    ("https://gruposwhats.app/group/1161011", "0️⃣9️⃣ VAGAS DE EMPREGO | MARANHÃO", "Vagas de emprego atualizadas todos os dias em Maranhão. Link conferido pelo GruposWhats em 11/11/2026. 7 cliques em Entrar."),
    ("https://gruposwhats.app/group/1165645", "VAGAS SP E REGIÃO #1", "Vagas para freelancer e fixas em São Paulo e região. 466 cliques em Entrar."),
    ("https://gruposwhats.app/group/1165219", "Oportunidades 2 - ADVs", "Grupo para divulgação de vaga de emprego. 27 cliques em Entrar."),
]
for url, name, desc in gw:
    fallback.append({"url": url, "source": "gruposwhats.app", "kind": "detail",
                     "name": name, "description": desc, "country": "BR", "category_guess": "Jobs",
                     "note": "Invite code NOT in text fetch (join button is JS-gated); browser leg must open the detail page and click through."})
gw_related = [
    ("Emprego Trindade, Goiânia e Região", "Vagas atualizadas todos os dias para Goiânia, Trindade e cidades adjacentes. Maior grupo de Goiás."),
    ("Home Office Jobs", "Objetivo de vagas de emprego (home office)."),
    ("Vagas de Emprego - Transportadoras Nível Brasil", "Grupo para vagas de emprego no setor da logística e Transportes."),
    ("Vem Ser CLT No Estreito MA!", "Grupo designado apenas para contratação de serviços CLT ou diaristas."),
    ("Vagas de Emprego Bahia e Região", "Vagas de emprego em diversas cidades da Bahia."),
    ("Conecta Empregos", "Grupo de emprego para todos os estados e regiões. Regras: foto de perfil obrigatória."),
]
for name, desc in gw_related:
    fallback.append({"url": "https://gruposwhats.app/group/1161011", "source": "gruposwhats.app", "kind": "detail-via-related",
                     "name": name, "description": desc, "country": "BR", "category_guess": "Jobs",
                     "note": "No exact detail URL captured (listed under 'Mais grupos da categoria' on the Maranhão group page) - resolve via site search for the exact name. Invite code NOT in text fetch; browser leg must click through."})

all_leads = leads + fallback
json.dump(all_leads, open(f"{WAVE}/team18-igrupos-leads.json", "w"), ensure_ascii=False, indent=1)

# --- 3. candidates: fix 2 records ---
cands = json.load(open(f"{WAVE}/team18-search-candidates.json"))
for c in cands:
    if c["invite"].endswith("Fh820JTzF1W0lepsibfM7z"):
        c["category"] = "Buy & Sell"
        c["description"] = "Join SyeMiguel PROMOÇÃO e LEILÃO 💍💎, a WhatsApp group."
    if c["invite"].endswith("E7VAZKqdcsn1HMP88WftwY"):
        c["name"] = "Rotary (IA) - En Español"
        c["category"] = "Technology"
        c["description"] = "Join Rotary (IA) - En Español, a WhatsApp group."
json.dump(cands, open(f"{WAVE}/team18-igrupos-candidates.json", "w"), ensure_ascii=False, indent=1)
json.dump([], open(f"{WAVE}/team18-igrupos-pending.json", "w"), ensure_ascii=False, indent=1)

# --- 4. summary ---
excluded = json.load(open(f"{WAVE}/team18-search-excluded.json"))
igr_excluded = json.load(open(f"{WAVE}/team18-igrupos-excluded.json"))
summary = {
    "team": 18, "slice": "igrupos gids 526723-526885 + new above 527086; fallback grupodewhatsapp + gruposdewhatss.app (+gruposwhats.app)",
    "wave": "20261112", "date": "2026-11-12",
    "igrupos_reachable": True,
    "igrupos_reachability_detail": "Homepage AND detail pages reachable via curl/requests from this VM (homepage HTTP 200, 206KB, ~5.5s; detail pages HTTP 200 warm ~0.3-1s, first TLS ~30s). NOT geo-gated today, unlike Nov-10/11 reports. BUT: invite codes are NOT present in static HTML - no chat.whatsapp.com link, no join button, no QR on any detail page (verified on gids 527264, 526723). The join link is JS/login-gated, so igrupos yields leads only; codes need a live-browser click.",
    "controls": {
        "known_live": {"code": "KrDwdK8EIkB6vgauHg5M7N", "result": "og:title 'JAY - PHP & Python Full Stack Developer' - PASS"},
        "fabricated": {"code": "ZZZZZZZZZZZZZZZZZZZZZZ", "result": "empty og:title (generic og:description 'WhatsApp Group Invite' present) - correctly treated as DEAD; LIVE rule = non-empty og:title"},
    },
    "igrupos_mining": {
        "gids_attempted": 341,
        "gids_live_detail_pages": 249,
        "gids_404": 92,
        "gids_errors": 0,
        "gid_range_live": "526723-527264",
        "in_slice_526723_526885_live": 115,
        "above_527086_live": 134,
        "note": "Homepage 'Ultimos grupos y canales' showed 40 newest gids 527113-527264, all above 527086. Slice gids 526723-526885 had scrolled off the homepage and were fetched directly; 115 of 163 exist, 48 are 404.",
    },
    "verified_kept": len(cands),
    "pending": 0,
    "leads": len(all_leads),
    "leads_by_source": {"igrupos.com": len(leads), "grupodewhatsapp.com": 10, "gruposwhats.app": 9, "gruposdewhatss.app": 0},
    "candidates_source": "All 31 candidates came from search-index snippets (chat.whatsapp.com codes published on the group's own site/YouTube/PDF), NOT from igrupos detail pages. Each verified live via og:title with a warm requests Session.",
    "exclusions": [
        {"item": "gid 527262 DUNGEON OF MERILYN", "reason": "lemon 18 = erotic roleplay content - dropped per hard porn rule"},
        {"item": "gid 527217 DUNGEON OF MERILYN", "reason": "RESTORED (not excluded): full description checked - combat/world roleplay only, no lemon/erotic content"},
        {"item": "gid 527138 Mundo Crypto", "reason": "KEPT as lead with FLAG: trading-strategies group - browser leg must screen before banking (drop if airdrop/binary-option/daily-profits promo)"},
    ] + [{"code": x["code"], "reason": x["reason"]} for x in excluded["excluded"]] + [
        {"gid": x["gid"], "title": x["title"], "reason": x["reason"]} for x in igr_excluded],
    "dead_after_spaced_retry": 17,
    "dead_note": "17 harvested codes showed empty og:title on first check AND on a spaced retry - confirmed dead, 0 revived. Includes 8 wuolah semester groups and 5 Google-Sheets class groups (stale 2023-2025 listings).",
    "dupes_vs_existing_codes": [{"code": x["code"], "reason": x["reason"]} for x in excluded["dupes"]],
    "fallback_sites": {
        "grupodewhatsapp.com": "Direct curl 403 (Cloudflare 'Just a moment'). browser.open text fetch works and is FRESH (crawled <1 min ago): detail pages show name/desc/members/verified-date + 'also joined' graph (~6 more groups each), but NO invite code (JS-gated join button). 10 new leads banked, 0 overlap with team32's 31.",
        "gruposdewhatss.app": "Direct curl 403 ('Your country is not allowed to access this resource' - geo-block). browser.open returns a STALE crawler copy (Feb 2026 for the detail page checked) with no invite code. No new leads - team32's 7 leads from yesterday still stand, not re-banked.",
        "gruposwhats.app": "New directory found via search (distinct from gruposdewhatss.app). browser.open text fetch is FRESH (crawled <1 min ago) with name/desc/category/click counts + related-groups list, but NO invite code (JS-gated). 9 new leads banked (3 exact detail URLs + 6 related names).",
    },
    "resume": "Next run: re-open https://www.igrupos.com/ homepage 'Ultimos grupos y canales' and continue from the newest gid seen (527264); gids below 526723 are unmined territory only if the slice extends downward. Browser leg still needed for ALL 268 leads: open each detail page live, click the join button, capture the chat.whatsapp.com code, verify og:title, screen, bank. Priority: the 19 Jobs leads (grupodewhatsapp/gruposwhats.app, all BR, site-verified 11-12 Nov 2026) and the 249 igrupos leads in gid order.",
    "flags_for_browser_leg": [
        "gid 527086 'Mr Factss' (team32 flag) is a WhatsApp CHANNEL, not a group - still unconfirmed.",
        "igrupos 'country' on leads comes from the first flag image on the detail page and is UNVERIFIED (e.g. gid 526723 shows DM) - confirm country from the page's 'Grupo solo para gente de' section at bank time.",
        "gid 527192 'Bisex Asturias' kept: 18+ age gate on a friendship group (false-positive restore, not porn).",
        "Candidate 'PRESENTE Y FUTURO CRIPTOS!' (BAHfB5sLzUo3ewu8ihrx7X) is a Rotary crypto-discussion forum, kept as Finance - not an airdrop/trading-promo.",
        "No source name or source link stored in candidate fields; lead notes name the listing page only so the browser leg can find the group. No personal info collected.",
    ],
    "files": {
        "candidates": "team18-igrupos-candidates.json (31 verified clean items)",
        "pending": "team18-igrupos-pending.json (empty - 0 transport failures)",
        "leads": "team18-igrupos-leads.json (267 leads: 249 igrupos + 18 fallback)",
        "summary": "team18-igrupos-summary.json",
        "work_files": "team18_mine_igrupos.py, team18-igrupos-mined.jsonl (341 gid records), team18_verify_codes.py, team18-verify.jsonl, team18-search-candidates.json, team18-search-pending.json, team18-search-excluded.json, team18-igrupos-leads-raw.json, team18-igrupos-excluded.json, team18-retry-revived.json",
    },
}
json.dump(summary, open(f"{WAVE}/team18-igrupos-summary.json", "w"), ensure_ascii=False, indent=1)
print(f"leads total={len(all_leads)} (igrupos {len(leads)} + fallback {len(fallback)})")
print(f"candidates={len(cands)} pending=0")
print("files written")
