#!/usr/bin/env python3
"""Team32 verifier: dedupe + curl-verify WhatsApp group invite codes.

Usage: python3 team32_verify.py candidates.json
  candidates.json: list of {"code","name","category","country","description","source_page"}
Reads dedupe union file, skips known codes, curl-verifies the rest,
appends verified items to team32-fresh-arabic-gulf.json,
garbled/uncertain codes to team32-unverified-pending.json.
Also appends newly-verified codes to a local bank file so this run never re-verifies.
"""
import json, os, re, subprocess, sys, time

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261030"
DEDUPE = os.path.join(WAVE, "dedupe_union_codes.txt")
FRESH = os.path.join(WAVE, "team32-fresh-arabic-gulf.json")
PENDING = os.path.join(WAVE, "team32-unverified-pending.json")
LEADS = os.path.join(WAVE, "team32-leads.json")
BANK = os.path.join(WAVE, "team32_work", "banked_codes.txt")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

BAD_TITLES = {"couldn't look up link", "whatsapp", ""}

def load_json(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def og_title(html):
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)', html, re.I)
    if not m:
        m = re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.S)
        return (m.group(1).strip() if m else "")
    return m.group(1).strip()

def verify(code):
    url = f"https://chat.whatsapp.com/{code}"
    try:
        p = subprocess.run(
            ["curl", "-sL", "-A", UA, "--max-time", "25", "-o", "-", "-w", "\n%{http_code}",
             url],
            capture_output=True, text=True, timeout=40)
        out = p.stdout
        http = out.strip().split("\n")[-1].strip()
        body = "\n".join(out.strip().split("\n")[:-1])
        title = og_title(body)
        low = title.lower()
        live = (http == "200" and title and low not in BAD_TITLES
                and "couldn't look up" not in low)
        return live, http, title
    except Exception as e:
        return False, "ERR", str(e)

def main():
    cand_path = sys.argv[1]
    with open(cand_path, encoding="utf-8") as f:
        cands = json.load(f)
    with open(DEDUPE, encoding="utf-8") as f:
        dedupe = set(l.strip() for l in f if l.strip())
    os.makedirs(os.path.dirname(BANK), exist_ok=True)
    banked = set()
    if os.path.exists(BANK):
        with open(BANK, encoding="utf-8") as f:
            banked = set(l.strip() for l in f if l.strip())
    fresh = load_json(FRESH)
    pending = load_json(PENDING)
    seen_fresh_codes = set(i["invite"].rsplit("/", 1)[-1] for i in fresh)
    results = {"verified": 0, "dead": 0, "dup": 0, "pending_added": 0}
    new_bank = []
    for c in cands:
        code = (c.get("code") or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9]{22}", code):
            pending.append({"code": code, "source_page": c.get("source_page", "")})
            results["pending_added"] += 1
            continue
        if code in dedupe or code in banked or code in seen_fresh_codes:
            results["dup"] += 1
            continue
        time.sleep(0.5)
        live, http, title = verify(code)
        if live:
            item = {
                "name": c.get("name", ""),
                "category": c.get("category", ""),
                "country": c.get("country", ""),
                "description": (c.get("description") or "")[:220],
                "image": "",
                "invite": f"https://chat.whatsapp.com/{code}",
            }
            fresh.append(item)
            new_bank.append(code)
            seen_fresh_codes.add(code)
            results["verified"] += 1
            print(f"LIVE {code} :: {title[:60]} :: {c.get('name','')[:50]}", flush=True)
        else:
            results["dead"] += 1
            print(f"DEAD {code} :: http={http} title={title[:50]}", flush=True)
    save_json(FRESH, fresh)
    save_json(PENDING, pending)
    with open(BANK, "a", encoding="utf-8") as f:
        for code in new_bank:
            f.write(code + "\n")
    print("RESULTS:", json.dumps(results))

if __name__ == "__main__":
    main()
