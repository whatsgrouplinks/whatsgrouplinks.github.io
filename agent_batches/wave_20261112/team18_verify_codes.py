#!/usr/bin/env python3
"""TEAM18 verify harvested codes: dedupe vs .existing_codes.json, check og:title,
screen titles, write candidates/pending + checkpoint JSONL."""
import requests, re, json, time, html as htmllib

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
S = requests.Session()

# (code, provisional name, category, country, source-note)
HARVEST = [
 ("KSM9yEUxixxGMM68h2AowG", "Vagas Abertas - RH Conectado", "Jobs", "BR", "rhconectado.com.br jobs page"),
 ("CjrKVjLcHV66cT6D6NBAbo", "", "Community & Social", "", "youtube Palavra de Deus"),
 ("HC7YwDrApGT70mQOP5P9qw", "", "Community & Social", "", "sites.google CVL"),
 ("HXTgGNcF2ySCciMg2wPYSg", "", "Community & Social", "", "youtube prayer group"),
 ("Fh820JTzF1W0lepsibfM7z", "", "Community & Social", "", "youtube garimpagem"),
 ("lancamentoCvl30", "", "Community & Social", "", "sites.google CVL lancamento"),
 ("CXsl7j1F7Jd31qTgm7VJbC", "Egresados Psicologia UAG Alumni", "Education", "MX", "uag.mx alumni"),
 ("CyBWkDdhHtN6TKc2XOnsTz", "Copa de Espana ILCA 7", "Sports", "ES", "cyberaltura.com sailing"),
 ("FZt9wuBXqNy91raDXyuMFN", "Rotary Mentor & Coach", "Community & Social", "ES", "rotary2202.es"),
 ("IlPuIJFrQtT1bMU27cCvcT", "Rotary Agarrate a la Vida", "Community & Social", "ES", "rotary2202.es"),
 ("DG0SP0zfR4AG68f134zsPm", "Rotary Pasion por la Enologia", "Community & Social", "ES", "rotary2202.es"),
 ("BAHfB5sLzUo3ewu8ihrx7X", "Rotary Presente y Futuro Criptos", "Finance", "ES", "rotary2202.es"),
 ("DuQxRBuqtMaEl6suPuxMw8", "Rotary Foro Amigos Rotarios", "Community & Social", "ES", "rotary2202.es"),
 ("1Ghusk055PQ2SchaIrCIpr", "Rotary Foro Transacciones", "Buy & Sell", "ES", "rotary2202.es"),
 ("EnsphpRuiLs9VR8YyEv50q", "Rotary Bolsa en Rotary", "Finance", "ES", "rotary2202.es"),
 ("JJT9cvlv3iZKCEMpg4jh6e", "Rotary Canal Viajar Rotarios", "Community & Social", "ES", "rotary2202.es"),
 ("CdupqBAqkaJ1GPHe4wJyvD", "Rotary IA en espanol", "Technology", "ES", "rotary2202.es"),
 ("E7VAZKqdcsn1HMP88WftwY", "Rotary Foro de Rotarios Libres", "Community & Social", "ES", "rotary2202.es"),
 ("JYXd5WC5ih94EgvZFw8JJ4", "Rotary ESRAG", "Community & Social", "ES", "esrag.org via rotary2202"),
 ("CAJkxi2EWAKKwlw9jpJwVN", "AESFAS Asociaciones y Delegados", "Community & Social", "ES", "aesfas.org"),
 ("J13HBw433fr2YYP7coVs91", "AESFAS Asociados", "Community & Social", "ES", "aesfas.org"),
 ("LwetVXDg2z62I4Jt21Ol8l", "AESFAS Termalismo", "Community & Social", "ES", "aesfas.org"),
 ("CIXmQbEvjCC9UV2TblqPUI", "AESFAS Redes y Canales", "Community & Social", "ES", "aesfas.org"),
 ("CyycfKEeehSEUawdDYHAbq", "TeldeActualidad Noticias", "News", "ES", "teldeactualidad.com"),
 ("EpN7sLPb4o9FbPfzGmizQr", "Hacking Etico y Ciberseguridad", "Technology", "ES", "forum.elhacker.net"),
 ("LmzDCrYgFJP4p238831Pto", "Amistades FIFAS - Futbolera", "Sports", "MX", "ivoox Futbolera"),
 ("K2Q67f941oo2SLSnMtLv3l", "Grupo de quedada Malaga 2026", "Friendship", "ES", "eventbrite Malaga"),
 ("JwTdxtBPAsn9LKVB1pHT94", "F8 Visoria Porteros", "Sports", "MX", "localgymsandfitness F8"),
 ("LdmMOtgch128E1l9WRZc3O", "Noticias Canals y la Region", "News", "AR", "infoeccos.com"),
 ("Bm85uxTOV0v6z0bBfoigcB", "Noticias Laborde y la Region", "News", "AR", "infoeccos.com"),
 ("BhyAVhHyvci6FHIhOPGxZr", "Taller de Huerta Familiar UNRN", "Education", "AR", "docs.google UNRN"),
 ("BBfmivT6RniClZ1UeoItCE", "Juegos LGBTI 2026", "Sports", "CO", "idrd.gov.co"),
 ("EvIhddU2hAp9TExwdiN9q3", "Clase 2AM1", "Education", "", "google sheets class groups"),
 ("IYUIC28eqas7W7L4Ti9sFF", "Clase 2AM2", "Education", "", "google sheets class groups"),
 ("KjoEVoI8n336lWgV33AvgF", "Clase 2AM3", "Education", "", "google sheets class groups"),
 ("HDhsB4kqvbW19A5cac58cz", "Clase 2AV1", "Education", "", "google sheets class groups"),
 ("B5Cf5l0stQzCByJ4Ifa1wn", "Clase 2AV2", "Education", "", "google sheets class groups"),
 ("CBUlnubCP0Y6ybzr99oFj9", "Clase 2AV3", "Education", "", "google sheets class groups"),
 ("DwIUKUJUXKFBKHrZy46t41", "Clase 3AM2", "Education", "", "google sheets class groups"),
 ("EN1JamuUgx8C4ra5joIV8p", "Clase 3AM3", "Education", "", "google sheets class groups"),
 ("C0Kf3uhaVZwJgH7OFG3YJ0", "Clase 3AV1", "Education", "", "google sheets class groups"),
 ("IQl8Dd1XdFuKSCQRGU39i4", "Clase 4AM1", "Education", "", "google sheets class groups"),
 ("C5HKljeCkZCKFQRTl12ZvM", "Clase 4AM2", "Education", "", "google sheets class groups"),
 ("KNYrKEAyd8SFje3uL0B0sa", "Clase 5AM1", "Education", "", "google sheets class groups"),
 ("D7w840da9bCKhPiKQdeDdr", "Clase 6AM1", "Education", "", "google sheets class groups"),
 ("KpKFsisYfZHBFt1woLoA5X", "Clase 7AM1", "Education", "", "google sheets class groups"),
 ("DqQgKK7s4WqBI9BiIKodCT", "Semestre 1 General", "Education", "ES", "wuolah semester groups"),
 ("JXCgDMxSqvbFWy1pBgcXbb", "Semestre 1 General", "Education", "ES", "wuolah semester groups"),
 ("E2DJ4n13hhe500EvhLcaDw", "Semestre 2 General", "Education", "ES", "wuolah semester groups"),
 ("Ki92BbyVDcH2u17ITMZAkS", "Semestre 2 Sintesis", "Education", "ES", "wuolah semester groups"),
 ("L9akdRIU8MiExQ4hC8XXOD", "Semestre 2 Sintesis", "Education", "ES", "wuolah semester groups"),
 ("ICZqrYyVsIpDtQ1DnACbIo", "Semestre 3 General", "Education", "ES", "wuolah semester groups"),
 ("Kp3e0zoRZGpEQDXUnwdtnG", "Semestre 3 Practicas", "Education", "ES", "wuolah semester groups"),
 ("JJwTlPugEuyBj54jlVs0b8", "Semestre 3", "Education", "ES", "wuolah semester groups"),
 ("JseOx4iUfekCASAGokvzei", "Semestre", "Education", "ES", "wuolah semester groups"),
 ("D4kVigoFQCrEeMJMfB8l", "Semestre", "Education", "ES", "wuolah semester groups"),
]

DROP_PATTERNS = [
    (r"(?i)\b(porn|xxx|sexo|call.?girl|escort|hentai|brazzers|hookup)\b", "porn/sexual content"),
    (r"(?i)(airdrop|binary.?option|opciones binarias|paid.?hack|venda de xit|apuestas|betting|sinais.*(mina|mine)|robo.*mine|trading.*lucro|daily.?profit|ganhe dinheiro)", "scam/betting-promo name"),
    (r"(?i)\b(sexual home|desi bhabhi|lemon ?18|onlyfans)\b", "explicit sexual group"),
]
# false-positive restores: negated prohibitions, weekday sexta-feira, chuta, 18+ age gate alone
KEEP_NEGATIONS = re.compile(r"(?i)(proibido|prohibido|sem|não pode|no |not allowed|porn not allowed|pornografia.*proib)")

def screen(title):
    t = title or ""
    for pat, reason in DROP_PATTERNS:
        if re.search(pat, t):
            if KEEP_NEGATIONS.search(t):
                return None  # negated prohibition -> keep
            return reason
    return None

def check(code):
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = S.get(url, headers=UA, timeout=75)
        m = re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
        title = htmllib.unescape(m.group(1)).strip() if m else ""
        return {"code": code, "status": r.status_code, "title": title, "live": bool(title)}
    except Exception as e:
        return {"code": code, "status": "ERR", "error": str(e)[:120], "live": None}

def main():
    existing = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
    seen = set()
    cands, pend, excluded, dupes = [], [], [], []
    ckpt = open(f"{WAVE}/team18-verify.jsonl", "w")
    for code, name, cat, country, src in HARVEST:
        if code in seen:
            dupes.append((code, "dup within harvest")); continue
        seen.add(code)
        if code in existing:
            dupes.append((code, "already in groups.json")); continue
        res = check(code)
        res.update({"name_hint": name, "category": cat, "country": country, "source": src})
        ckpt.write(json.dumps(res, ensure_ascii=False) + "\n"); ckpt.flush()
        if res["live"] is None:
            pend.append({"code": code, "name": name, "category": cat, "country": country,
                         "invite": f"https://chat.whatsapp.com/{code}",
                         "reason": res.get("error", "transport failure"), "source": src})
        elif not res["live"]:
            excluded.append({"code": code, "name": name, "reason": "dead: empty og:title", "source": src})
        else:
            title = res["title"]
            drop = screen(title)
            if drop:
                excluded.append({"code": code, "name": title, "reason": f"screen: {drop}", "source": src})
            else:
                nm = title if title else name
                cands.append({"name": nm, "category": cat, "country": country,
                              "description": f"Join {nm}, a WhatsApp group.",
                              "invite": f"https://chat.whatsapp.com/{code}"})
        print(f"{code} live={res['live']} title={res.get('title','')[:60]}", flush=True)
        time.sleep(0.4)
    ckpt.close()
    json.dump(cands, open(f"{WAVE}/team18-search-candidates.json", "w"), ensure_ascii=False, indent=1)
    json.dump(pend, open(f"{WAVE}/team18-search-pending.json", "w"), ensure_ascii=False, indent=1)
    json.dump({"excluded": excluded, "dupes": [{"code": c, "reason": r} for c, r in dupes]},
              open(f"{WAVE}/team18-search-excluded.json", "w"), ensure_ascii=False, indent=1)
    print(f"DONE candidates={len(cands)} pending={len(pend)} excluded={len(excluded)} dupes={len(dupes)}", flush=True)

if __name__ == "__main__":
    main()
