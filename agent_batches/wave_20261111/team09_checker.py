#!/usr/bin/env python3
"""TEAM 09 — pending recheck for wave 20261111.
Slow curl checker: max 6 workers, >=0.5s delay, retry-on-empty-og.
Writes checkpoint JSONL as it goes; final outputs written by a separate step.
"""
import json, re, subprocess, time, sys
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
PEND = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110/wave_20261110_pending_all.json"
EXIST = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"
CKPT = WAVE + "/team09-pending-recheck-checkpoint.jsonl"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

SCAM_PAT = re.compile(
    r"b-?love|forsage|sury|sheyi|holiverse|meta[\s\-]?whale|airdrop|"
    r"betway|betpawa|sure\s+odds|betting\s+tips|fixed\s+match|"
    r"double\s+(your\s+)?money|earn\s+\d|daily\s+profit", re.I)
PORN_PAT = re.compile(r"\b(xxx|porn|sex\s*video|nude|desi\s*sex|hot\s*girls?\s*xxx)\b", re.I)
NEG_PAT = re.compile(r"[^.!?\n]*(no|not|don't|dont|never|prohibit\w*|forbidden)[^.!?\n]*(porn|xxx|sex|nude)[^.!?\n]*[.!?\n]?", re.I)

def strip_negated(text):
    return NEG_PAT.sub(" ", text)

def og_title(html):
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)["\']', html, re.I)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', html, re.I)
    return (m.group(1).strip() if m else "")

def curl_once(code):
    url = "https://chat.whatsapp.com/" + code
    import tempfile, os
    fd, tmp = tempfile.mkstemp(prefix="team09_", suffix=".html")
    os.close(fd)
    try:
        p = subprocess.run(
            ["curl", "-sS", "-A", UA, "-L", "--max-time", "30",
             "-o", tmp, "-w", "%{http_code}", url],
            capture_output=True, text=True, timeout=40)
        http = p.stdout.strip()
        if p.returncode != 0 or http in ("", "000"):
            return None, "", f"transport failure: curl rc={p.returncode} http={http or '000'} ({(p.stderr or '').strip()[:120]})"
        with open(tmp, encoding="utf-8", errors="replace") as f:
            html = f.read()
        return int(http), og_title(html), ""
    except Exception as e:
        return None, "", f"transport failure: {type(e).__name__}: {e}"
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass

def check(entry):
    code = entry["invite"].rsplit("/", 1)[-1]
    browser_leg = entry.get("_team_file") == "team09-pending-recheck-pending.json"
    http, title, err = curl_once(code)
    if http is None:
        time.sleep(4)
        http, title, err = curl_once(code)
        if http is None:
            return {"status": "pending", "entry": entry,
                    "reason": "transport failure after 2 spaced attempts: " + err}
    if http == 200 and title:
        return {"status": "live", "entry": entry, "og_title": title}
    if http == 200 and not title:
        time.sleep(6)
        http2, title2, err2 = curl_once(code)
        if http2 == 200 and title2:
            return {"status": "live", "entry": entry, "og_title": title2}
        if http2 == 200 and not title2:
            if browser_leg:
                # Slice instruction: the 309 team09 browser-leg-only codes were
                # verified live in the browser; curl cannot verify them.
                # Keep pending, never mark dead on curl evidence alone.
                return {"status": "pending", "entry": entry,
                        "reason": "curl cannot verify (empty og:title after 2 spaced attempts); browser-leg-only code from Nov 10 — retained pending per slice instruction"}
            return {"status": "dead", "entry": entry,
                    "reason": "HTTP 200 but empty og:title on 2 spaced attempts"}
        if http2 is None:
            return {"status": "pending", "entry": entry,
                    "reason": "transport failure on retry after empty og:title: " + err2}
        return {"status": "pending", "entry": entry,
                "reason": f"non-200 on retry after empty og:title: HTTP {http2}"}
    return {"status": "pending", "entry": entry,
            "reason": f"HTTP {http} (not 200) on check"}

def main():
    pend = json.load(open(PEND))
    exist = set(json.load(open(EXIST)))
    done = set()
    try:
        with open(CKPT) as f:
            for line in f:
                try:
                    done.add(json.loads(line)["code"])
                except Exception:
                    pass
    except FileNotFoundError:
        pass

    exclusions = []
    todo = []
    for e in pend:
        code = e["invite"].rsplit("/", 1)[-1]
        if code in done:
            continue
        if code in exist:
            exclusions.append({"code": code, "reason": "duplicate: already in groups.json (.existing_codes.json)"})
            with open(CKPT, "a") as f:
                f.write(json.dumps({"code": code, "status": "excluded-duplicate"}) + "\n")
            continue
        if SCAM_PAT.search(e.get("name", "") or ""):
            exclusions.append({"code": code, "reason": "scam name dropped on sight: " + e.get("name", "")})
            with open(CKPT, "a") as f:
                f.write(json.dumps({"code": code, "status": "excluded-scam-name"}) + "\n")
            continue
        todo.append(e)

    print(f"total={len(pend)} already-done={len(done)} pre-excluded={len(exclusions)} to-check={len(todo)}", flush=True)
    with open(WAVE + "/team09-pending-recheck-exclusions-pre.json", "w") as f:
        json.dump(exclusions, f, indent=1, ensure_ascii=False)

    def worker(entry):
        time.sleep(0.6)
        r = check(entry)
        r["code"] = entry["invite"].rsplit("/", 1)[-1]
        with open(CKPT, "a") as f:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        return r

    results = []
    with ThreadPoolExecutor(max_workers=6) as ex:
        for r in ex.map(worker, todo):
            results.append(r)
            if len(results) % 50 == 0:
                print(f"checked {len(results)}/{len(todo)}", flush=True)
    print("DONE checked:", len(results), flush=True)

if __name__ == "__main__":
    main()
