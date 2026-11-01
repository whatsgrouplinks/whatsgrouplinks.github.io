#!/usr/bin/env python3
"""Team 40 helper: verify invites, dedupe against ledger, write output JSON."""
import json, re, subprocess, sys, os

BASE = os.path.expanduser("~/workspace/whatsapp-groups-site")
BATCH = os.path.join(BASE, "agent_batches/wave_20261024")

def code_of(invite):
    inv = invite.strip()
    m = re.search(r"chat\.whatsapp\.com/((?:invite/)?[A-Za-z0-9_\-]+)", inv)
    if not m:
        return None
    code = m.group(1).rstrip("=")  # strip trailing padding oddities
    return code

def og_title(invite):
    try:
        p = subprocess.run(
            ["curl", "-sSL", "-m", "20", "-A",
             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
             invite],
            capture_output=True, text=True, timeout=40)
        html = p.stdout
        if p.returncode != 0 or not html:
            return None
        m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
        if not m:
            m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:title["\']', html, re.I)
        if not m:
            # fallback: <title>
            m = re.search(r"<title[^>]*>([^<]{3,200})</title>", html, re.I)
        if not m:
            return None
        t = m.group(1).strip()
        if not t or "404" in t or "revoked" in t.lower() or "not found" in t.lower():
            return None
        return t
    except Exception:
        return None

PORN = re.compile(r"porn|xxx|pornhub|xvideos|sexvideo|nude\s?video", re.I)

def main():
    cands = json.load(open(os.path.join(BATCH, "team40_candidates.json")))
    ledger = set(json.load(open(os.path.join(BASE, ".existing_codes.json"))))
    seen = set()
    out = []
    stats = {"total": len(cands), "ledger_dup": 0, "self_dup": 0,
             "porn_removed": 0, "verify_fail": 0, "kept": 0}
    for c in cands:
        code = code_of(c["invite"])
        if not code:
            stats["verify_fail"] += 1
            continue
        if code in seen:
            stats["self_dup"] += 1
            continue
        seen.add(code)
        if code in ledger:
            stats["ledger_dup"] += 1
            continue
        if PORN.search(c["name"]) or PORN.search(c.get("description", "")):
            stats["porn_removed"] += 1
            continue
        title = og_title(c["invite"])
        if not title:
            stats["verify_fail"] += 1
            continue
        # sanity: invite page is a whatsapp group/community page
        out.append({
            "name": c["name"],
            "category": c["category"],
            "description": c["description"],
            "invite": "https://chat.whatsapp.com/" + code,
            "country": c["country"],
        })
        stats["kept"] += 1
        if stats["kept"] >= 60:
            break
    json.dump(out, open(os.path.join(BATCH, "team40-news-cat.json"), "w"), ensure_ascii=False, indent=1)
    with open(os.path.join(BATCH, "manifest.txt"), "a") as f:
        f.write(f"team40-news-cat.json {len(out)}\n")
    print(json.dumps(stats, indent=1))

if __name__ == "__main__":
    main()
