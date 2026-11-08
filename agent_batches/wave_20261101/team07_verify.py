#!/usr/bin/env python3
"""team07 verify: curl each candidate chat.whatsapp.com code with Chrome UA,
require non-empty og:title. Content-filter, dedupe-safe, checkpointed."""
import json, re, time, subprocess, html, os, sys

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261101")
PROG = "/tmp/team07_verify_progress.json"

BLOCK_RE = re.compile(r"(porn|pornhub|\bxxx\b|nude|sex video|escort|call girl|fuck|dick|pussy|boobs|anal|hentai|🥵|🍆|🍑|🔞|💦|👅|👄|💋)", re.I)
PHONE_RE = re.compile(r"\d[\d\s\-]{6,}\d")

COUNTRY_NAMES = {
    "IN": "India", "PK": "Pakistan", "NG": "Nigeria", "ID": "Indonesia", "EG": "Egypt",
    "BR": "Brazil", "US": "United States", "GB": "United Kingdom", "AE": "UAE",
    "SA": "Saudi Arabia", "BD": "Bangladesh", "PH": "Philippines", "MY": "Malaysia",
    "TR": "Turkey", "KE": "Kenya", "GH": "Ghana", "ZA": "South Africa", "MX": "Mexico",
    "ES": "Spain", "FR": "France", "DE": "Germany", "IT": "Italy", "CN": "China",
    "NP": "Nepal", "LK": "Sri Lanka", "MM": "Myanmar", "VN": "Vietnam", "TH": "Thailand",
    "AU": "Australia", "CA": "Canada", "AR": "Argentina", "CO": "Colombia", "PE": "Peru",
    "CL": "Chile", "QA": "Qatar", "KW": "Kuwait", "OM": "Oman", "BH": "Bahrain",
    "JO": "Jordan", "IQ": "Iraq", "IR": "Iran", "AF": "Afghanistan", "UZ": "Uzbekistan",
    "KZ": "Kazakhstan", "ET": "Ethiopia", "TZ": "Tanzania", "UG": "Uganda", "CM": "Cameroon",
    "SN": "Senegal", "MA": "Morocco", "DZ": "Algeria", "TN": "Tunisia", "LY": "Libya",
    "SD": "Sudan", "SO": "Somalia", "RW": "Rwanda", "ZM": "Zambia", "ZW": "Zimbabwe",
    "MW": "Malawi", "MZ": "Mozambique", "BW": "Botswana", "NA": "Namibia", "ML": "Mali",
    "CI": "Ivory Coast", "BJ": "Benin", "TG": "Togo", "BF": "Burkina Faso", "NE": "Niger",
    "TD": "Chad", "CF": "CAR", "CG": "Congo", "CD": "DR Congo", "GA": "Gabon",
    "GQ": "Equatorial Guinea", "ST": "Sao Tome", "CV": "Cape Verde", "GW": "Guinea-Bissau",
    "GN": "Guinea", "SL": "Sierra Leone", "LR": "Liberia", "MR": "Mauritania",
    "EH": "Western Sahara", "MU": "Mauritius", "SC": "Seychelles", "KM": "Comoros",
    "MG": "Madagascar", "DJ": "Djibouti", "ER": "Eritrea", "SS": "South Sudan",
    "NL": "Netherlands", "BE": "Belgium", "CH": "Switzerland", "AT": "Austria",
    "SE": "Sweden", "NO": "Norway", "DK": "Denmark", "FI": "Finland", "PL": "Poland",
    "PT": "Portugal", "GR": "Greece", "IE": "Ireland", "CZ": "Czechia", "HU": "Hungary",
    "RO": "Romania", "BG": "Bulgaria", "HR": "Croatia", "RS": "Serbia", "UA": "Ukraine",
    "RU": "Russia", "BY": "Belarus", "GE": "Georgia", "AM": "Armenia", "AZ": "Azerbaijan",
    "MD": "Moldova", "BA": "Bosnia", "AL": "Albania", "MK": "North Macedonia",
    "ME": "Montenegro", "XK": "Kosovo", "SK": "Slovakia", "SI": "Slovenia", "LV": "Latvia",
    "LT": "Lithuania", "EE": "Estonia", "IS": "Iceland", "LU": "Luxembourg", "MT": "Malta",
    "CY": "Cyprus", "NZ": "New Zealand", "FJ": "Fiji", "PG": "Papua New Guinea",
    "KH": "Cambodia", "LA": "Laos", "MN": "Mongolia", "KP": "North Korea", "KR": "South Korea",
    "JP": "Japan", "TW": "Taiwan", "HK": "Hong Kong", "MO": "Macau", "SG": "Singapore",
    "BN": "Brunei", "TL": "Timor-Leste", "MV": "Maldives", "BT": "Bhutan", "YE": "Yemen",
    "SY": "Syria", "LB": "Lebanon", "IL": "Israel", "PS": "Palestine", "TR": "Turkey",
    "DO": "Dominican Republic", "PR": "Puerto Rico", "JM": "Jamaica", "TT": "Trinidad",
    "BB": "Barbados", "BS": "Bahamas", "BZ": "Belize", "GT": "Guatemala", "SV": "El Salvador",
    "HN": "Honduras", "NI": "Nicaragua", "CR": "Costa Rica", "PA": "Panama", "CU": "Cuba",
    "HT": "Haiti", "EC": "Ecuador", "VE": "Venezuela", "GY": "Guyana", "SR": "Suriname",
    "UY": "Uruguay", "PY": "Paraguay", "BO": "Bolivia",
}

def check(code):
    r = subprocess.run(["curl", "-sL", "--max-time", "25", "-A", UA,
                        "-w", "\n%{http_code}", f"https://chat.whatsapp.com/{code}"],
                       capture_output=True, text=True, timeout=60)
    out = r.stdout or ""
    if not out.strip():
        return ("transport", "")
    http = out.rsplit("\n", 1)[-1].strip()
    body = out.rsplit("\n", 1)[0]
    if http == "429":
        return ("ratelimited", "")
    if r.returncode != 0 and not body:
        return ("transport", "")
    m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', body, re.I)
    title = html.unescape(m.group(1)).strip() if m else ""
    return ("ok", title)

def clean_title(t):
    t = re.sub(r"\s+", " ", t or "").strip()
    t = re.sub(r"^(Join\s+)?(this\s+)?(WhatsApp\s+)?[Gg]roup(\s*[:-])?\s*", "", t)
    return t.strip()

def build_item(c, og_title):
    name = clean_title(og_title) or clean_title(c["title"])
    if not name:
        name = clean_title(c["title"])
    if BLOCK_RE.search(name + " " + c["desc"]):
        return None
    if PHONE_RE.search(name):
        return None
    if not name or len(name) > 120:
        return None
    cat = c["category"]
    catword = cat.lower()
    cname = COUNTRY_NAMES.get(c["country"], c["country"] or "the world")
    dshort = re.sub(r"\s+", " ", c["desc"])[:140].strip()
    if dshort:
        desc = f"Join {name}, an active {catword} WhatsApp group. {dshort} Connect with {catword} members from {cname}."
    else:
        tags = ", ".join(c["tags"][:4])
        if tags:
            desc = f"Join {name}, an active {catword} WhatsApp group for {tags}. Connect and chat with {catword} fans from {cname}."
        else:
            desc = f"Join {name}, an active {catword} WhatsApp group. Share and discuss {catword} topics with members from {cname}."
    img = c["img"] if "pps.whatsapp.net" in (c["img"] or "") else ""
    return {
        "name": name,
        "category": cat,
        "description": desc,
        "image": img,
        "invite": f"https://chat.whatsapp.com/{c['code']}",
        "country": c["country"] if c["country"] else "XX",
    }

def main():
    cands = json.load(open("/tmp/team07_candidates.json"))["candidates"]
    prog = json.load(open(PROG)) if os.path.exists(PROG) else {}
    verified, pending = prog.get("verified", []), prog.get("pending", [])
    done_codes = set(prog.get("done", []))
    idx = prog.get("next_idx", 0)
    rate_stopped = prog.get("rate_stopped", False)

    if rate_stopped:
        print("Previously rate-limited; marking remaining as pending.", flush=True)
        for c in cands[idx:]:
            if c["code"] not in done_codes:
                pending.append({**c, "note": "rate-limited (resume point)"})
        finalize(verified, pending)
        return

    for i in range(idx, len(cands)):
        c = cands[i]
        if c["code"] in done_codes:
            continue
        st, og = check(c["code"])
        time.sleep(0.7)
        if st == "ratelimited":
            print(f"RATE LIMITED at index {i}; banking rest as pending", flush=True)
            prog = {"verified": verified, "pending": pending, "done": list(done_codes),
                    "next_idx": i, "rate_stopped": True}
            json.dump(prog, open(PROG, "w"))
            main_ratelimit_bank(cands, i, verified, pending, done_codes)
            return
        done_codes.add(c["code"])
        if st == "transport":
            pending.append({"code": c["code"], "title": c["title"], "category": c["category"],
                            "country": c["country"], "note": "transport failure"})
        elif og:
            item = build_item(c, og)
            if item:
                verified.append(item)
        # dead (empty og:title): skip
        if i % 50 == 49:
            prog = {"verified": verified, "pending": pending, "done": list(done_codes),
                    "next_idx": i + 1, "rate_stopped": False}
            json.dump(prog, open(PROG, "w"))
            print(f"progress: {i+1}/{len(cands)} verified={len(verified)} pending={len(pending)}", flush=True)

    finalize(verified, pending)
    prog = {"verified": verified, "pending": pending, "done": list(done_codes),
            "next_idx": len(cands), "rate_stopped": False}
    json.dump(prog, open(PROG, "w"))
    print(f"DONE: verified={len(verified)} pending={len(pending)}", flush=True)

def main_ratelimit_bank(cands, i, verified, pending, done_codes):
    for c in cands[i:]:
        if c["code"] not in done_codes:
            pending.append({"code": c["code"], "title": c["title"], "category": c["category"],
                            "country": c["country"], "note": "rate-limited (resume at verify index %d)" % i})
    finalize(verified, pending)

def finalize(verified, pending):
    json.dump(verified, open(os.path.join(WAVE, "team07-gjl-cat-entertainment.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(pending, open(os.path.join(WAVE, "team07-unverified-pending.json"), "w"), ensure_ascii=False, indent=1)
    leads = [{
        "domain": "groupjoin.link",
        "url": "https://www.groupjoin.link/category/online-shopping?page=PAGE&limit=20&safeSearch=blur",
        "why": "resume point for this team's verify phase (candidates file at /tmp/team07_candidates.json)"
    }] if False else []
    json.dump(leads, open(os.path.join(WAVE, "team07-leads.json"), "w"), ensure_ascii=False, indent=1)
    print(f"FINAL: verified={len(verified)} pending={len(pending)}", flush=True)

if __name__ == "__main__":
    main()
