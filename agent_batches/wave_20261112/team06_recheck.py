#!/usr/bin/env python3
"""TEAM06 wave_20261112: gentle re-check of team07 slice7 599 pending codes."""
import json, re, time, random, sys, os
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
PREV = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/"
BUILD = "/home/hatch/workspace/whatsapp-groups-site/"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

CAND_F = WAVE + "team06-leads-slice7-pending-candidates.json"
PEND_F = WAVE + "team06-leads-slice7-pending-pending.json"
LEAD_F = WAVE + "team06-leads-slice7-pending-leads.json"
PROG_F = WAVE + "team06-leads-slice7-pending-progress.jsonl"
STATE_F = WAVE + "team06-leads-slice7-pending-state.json"

OG_TITLE = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)', re.I)
OG_TITLE2 = re.compile(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', re.I)
OG_DESC = re.compile(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']*)', re.I)

# hard screen patterns (word-boundary aware to avoid "Sohbet" false positive)
PORN_RX = re.compile(r'\bporn\b|xxx|\bsex\b|hentai|escort|call.?girl|bhabhi|brazzers|hookup|sexy|nude|sexual home', re.I)
SCAM_RX = re.compile(r'airdrop|binary|venda de xit|betting|\bbet\b.*promo|daily.?profit|ai.?trading|hacker para|hack.*(ff|free fire)|buy.*hack|sell.*hack', re.I)
NEG_RX = re.compile(r'(no|not|proibido|sem|não pode|nao pode)[^a-z]{0,20}porn', re.I)

def screen(name):
    n = name or ""
    if NEG_RX.search(n):
        return None  # negated prohibition -> keep
    if PORN_RX.search(n):
        return "hard porn/sexual content in name"
    if SCAM_RX.search(n):
        return "scam name (hack/trading/airdrop/betting)"
    return None

def og(html, rx1, rx2):
    m = rx1.search(html) or rx2.search(html)
    return m.group(1).strip() if m else ""

def main():
    pending = json.load(open(PREV + "team07-leads-slice7-pending.json"))
    existing = set(json.load(open(BUILD + ".existing_codes.json")))
    groups = json.load(open(BUILD + "groups.json"))
    live_code = groups[0]["invite"].rsplit("/", 1)[-1]

    # resume
    done = {}
    if os.path.exists(PROG_F):
        for line in open(PROG_F):
            try:
                r = json.loads(line)
                done[r["code"]] = r
            except Exception:
                pass
    print(f"resume: {len(done)} already processed", flush=True)

    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})

    def fetch(code):
        try:
            r = s.get(f"https://chat.whatsapp.com/{code}", timeout=75, allow_redirects=True)
            if r.status_code == 429:
                return ("429", None)
            if r.status_code != 200:
                return (f"http{r.status_code}", None)
            t = og(r.text, OG_TITLE, OG_TITLE2)
            if t:
                return ("live", t)
            # NOTE: og:description is ALWAYS the generic "WhatsApp Group Invite"
            # on both live and dead pages — it is NOT a live signal. Only a
            # non-empty og:title counts as live.
            return ("empty", None)
        except requests.exceptions.Timeout:
            return ("timeout", None)
        except requests.exceptions.RequestException as e:
            return (f"err:{type(e).__name__}", None)

    # ---- CONTROLS ----
    print("control live:", fetch(live_code), flush=True)
    print("control fabricated:", fetch("ZZZZZZZZZZZZZZZZZZZZ"), flush=True)

    candidates, still_pending, exclusions = [], [], []
    seen = set()
    consec_fail = 0
    wall_pause = False
    # reload partial outputs if present
    if os.path.exists(CAND_F):
        candidates = json.load(open(CAND_F))
        seen = {c["invite"].rsplit("/", 1)[-1] for c in candidates}
    if os.path.exists(PEND_F):
        still_pending = json.load(open(PEND_F))

    def save():
        json.dump(candidates, open(CAND_F, "w"), ensure_ascii=False, indent=1)
        json.dump(still_pending, open(PEND_F, "w"), ensure_ascii=False, indent=1)
        json.dump({"processed": len(done), "candidates": len(candidates),
                   "pending": len(still_pending), "exclusions": len(exclusions)},
                  open(STATE_F, "w"), indent=1)

    for idx, item in enumerate(pending):
        code = item["invite"].rsplit("/", 1)[-1]
        if code in done:
            continue
        if code in existing:
            done[code] = {"code": code, "status": "dup-existing"}
            continue
        reason = screen(item.get("name", ""))
        if reason:
            exclusions.append({"invite": item["invite"], "name": item.get("name"), "reason": reason})
            done[code] = {"code": code, "status": "excluded", "reason": reason}
            with open(PROG_F, "a") as f:
                f.write(json.dumps(done[code], ensure_ascii=False) + "\n")
            continue
        status, title = fetch(code)
        if status in ("429", "timeout") or status.startswith("err:"):
            time.sleep(random.uniform(30, 60))
            status2, title2 = fetch(code)
            if status2.startswith("live"):
                status, title = status2, title2
            else:
                status = status2
        # NOTE: a 200 with empty og:title is WhatsApp's standard invalid/revoked
        # invite page (220KB HTML, generic description). 30/30 such codes stayed
        # empty on re-fetch; the throttle signal is 429, not empty-200. No retry.
        if status.startswith("live"):
            name = (item.get("name") or "").strip()
            if not name:
                name = title
            if code not in seen:
                seen.add(code)
                candidates.append({
                    "name": name,
                    "category": item.get("category") or "Community & Social",
                    "country": item.get("country") or "",
                    "description": f"Join {name}, a WhatsApp group.",
                    "invite": f"https://chat.whatsapp.com/{code}",
                })
            done[code] = {"code": code, "status": "live", "title": title}
        elif status == "empty":
            done[code] = {"code": code, "status": "dead-empty"}
        else:
            still_pending.append({"name": item.get("name", ""), "category": item.get("category") or "Community & Social",
                                  "country": item.get("country") or "", "description": item.get("description") or "",
                                  "invite": item["invite"], "reason": f"transport failure {status}"})
            done[code] = {"code": code, "status": "pending", "reason": status}
            consec_fail += 1
            if consec_fail >= 3:
                wall_pause = True
        if status.startswith("live") or status == "empty":
            consec_fail = 0
        with open(PROG_F, "a") as f:
            f.write(json.dumps(done[code], ensure_ascii=False) + "\n")
        if (idx + 1) % 25 == 0:
            save()
            print(f"[{idx+1}/{len(pending)}] live={len(candidates)} pending={len(still_pending)} excl={len(exclusions)}", flush=True)
        time.sleep(random.uniform(2.0, 3.5))
        if wall_pause:
            wall_pause = False
            print(f"  429-wall: pausing 180s after 3 consecutive transport failures", flush=True)
            save()
            time.sleep(180)
            consec_fail = 0
            print("  resumed after wall-pause", flush=True)
            s.close()
            s = requests.Session()
            s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    save()
    # exclusions + summary written by finalize step
    json.dump(exclusions, open(WAVE + "team06-leads-slice7-pending-exclusions.json", "w"), ensure_ascii=False, indent=1)
    print(f"DONE live={len(candidates)} pending={len(still_pending)} excl={len(exclusions)} dead={sum(1 for v in done.values() if v.get('status')=='dead-empty')}", flush=True)

if __name__ == "__main__":
    main()
