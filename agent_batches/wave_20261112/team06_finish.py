#!/usr/bin/env python3
"""TEAM06 bounded finish: verify the remaining slice-7 pending codes, once each."""
import json, re, time, random, os
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
PREV = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/"
BUILD = "/home/hatch/workspace/whatsapp-groups-site/"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
OG_TITLE = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)', re.I)
OG_TITLE2 = re.compile(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', re.I)
PORN_RX = re.compile(r'\bporn\b|xxx|\bsex\b|hentai|escort|call.?girl|bhabhi|brazzers|hookup|sexy|nude|sexual home', re.I)
SCAM_RX = re.compile(r'airdrop|binary|venda de xit|betting|\bbet\b.*promo|daily.?profit|ai.?trading|hacker para|hack.*(ff|free fire)|buy.*hack|sell.*hack', re.I)
NEG_RX = re.compile(r'(no|not|proibido|sem|não pode|nao pode)[^a-z]{0,20}porn', re.I)
PROG_F = WAVE + "team06-leads-slice7-pending-progress.jsonl"

def screen(name):
    n = name or ""
    if NEG_RX.search(n):
        return None
    if PORN_RX.search(n):
        return "hard porn/sexual content in name"
    if SCAM_RX.search(n):
        return "scam name (hack/trading/airdrop/betting)"
    return None

def main():
    pending = json.load(open(PREV + "team07-leads-slice7-pending.json"))
    done = {}
    for line in open(PROG_F):
        try:
            r = json.loads(line)
            done[r["code"]] = r
        except Exception:
            pass
    remaining = [p for p in pending if p["invite"].rsplit("/", 1)[-1] not in done]
    print(f"remaining: {len(remaining)}", flush=True)
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})

    def fetch(code):
        try:
            r = s.get(f"https://chat.whatsapp.com/{code}", timeout=75, allow_redirects=True)
            if r.status_code == 429:
                return ("429", None)
            if r.status_code != 200:
                return (f"http{r.status_code}", None)
            m = OG_TITLE.search(r.text) or OG_TITLE2.search(r.text)
            t = m.group(1).strip() if m else ""
            return ("live", t) if t else ("empty", None)
        except requests.exceptions.Timeout:
            return ("timeout", None)
        except requests.exceptions.RequestException as e:
            return (f"err:{type(e).__name__}", None)

    for i, item in enumerate(remaining):
        code = item["invite"].rsplit("/", 1)[-1]
        reason = screen(item.get("name", ""))
        if reason:
            rec = {"code": code, "status": "excluded", "reason": reason}
        else:
            status, title = fetch(code)
            if status in ("429", "timeout") or status.startswith("err:"):
                time.sleep(20)
                status, title = fetch(code)
            if status.startswith("live"):
                rec = {"code": code, "status": "live", "title": title}
            elif status == "empty":
                rec = {"code": code, "status": "dead-empty"}
            else:
                rec = {"code": code, "status": "pending", "reason": status}
        done[code] = rec
        with open(PROG_F, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"[{i+1}/{len(remaining)}] {code[:8]} {rec['status']}", flush=True)
        time.sleep(random.uniform(2.0, 3.0))
    import collections
    print("DONE", collections.Counter(v["status"] for v in done.values()), flush=True)

if __name__ == "__main__":
    main()
