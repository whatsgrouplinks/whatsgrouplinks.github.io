"""Team24 wave 20261112 verifier: requests Session keep-alive, spaced retries.
Usage:
  python3 team24_verify12.py controls          -> runs controls only
  python3 team24_verify12.py <in.json> <out.json> [codes...]
in.json: {code: {name, page}} or [{"code":...}] or list of codes.
out.json: checkpoint {code: {status, og_title, http, error, name, page}}.
status: live (200 + non-empty og:title, og:description fallback),
        dead (200 + empty og after retries, or non-200/429-free http),
        transport (no http status / timeout / 429 after retries).
"""
import json, re, sys, time, os
import requests

W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9"}

S = requests.Session()
S.headers.update(UA)

OG_TITLE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
OG_TITLE2 = re.compile(r'<meta\s+content="([^"]*)"\s+property="og:title"', re.I)
OG_DESC = re.compile(r'<meta\s+property="og:description"\s+content="([^"]*)"', re.I)
OG_DESC2 = re.compile(r'<meta\s+content="([^"]*)"\s+property="og:description"', re.I)

def og_title(html):
    m = OG_TITLE.search(html) or OG_TITLE2.search(html)
    if m and m.group(1).strip():
        return m.group(1).strip()
    # NOTE: og:description is ALWAYS the generic "WhatsApp Group Invite" even
    # for dead/fabricated codes (verified on control ZZZZ...ZZZ), so it must
    # NOT be used as a fallback. LIVE = non-empty og:title only.
    return ""

def check(code, attempts=3, pause=8):
    url = f"https://chat.whatsapp.com/{code}"
    last_http = "000"
    last_err = ""
    for a in range(attempts):
        try:
            r = S.get(url, timeout=75)
            last_http = str(r.status_code)
            title = og_title(r.text)
            if r.status_code == 200 and title:
                return ("live", title, last_http, "")
            if r.status_code == 200:
                last_err = "empty og:title"
                time.sleep(pause)
                continue
            if r.status_code in (429, 500, 502, 503):
                last_err = f"http {r.status_code} (transport-ish)"
                time.sleep(pause * 2)
                continue
            return ("dead", title, last_http, f"http {r.status_code}")
        except requests.exceptions.RequestException as e:
            last_err = f"transport: {type(e).__name__}"
            time.sleep(pause)
            continue
    if last_http == "200":
        return ("dead", "", "200", "empty og:title after retries")
    return ("transport", "", last_http, last_err or "no http status after retries")

if __name__ == "__main__":
    if sys.argv[1] == "controls":
        print("CONTROL live (KrDwdK8EIkB6vgauHg5M7N from groups.json):", check("KrDwdK8EIkB6vgauHg5M7N"), flush=True)
        print("CONTROL fabricated (ZZZZZZZZZZZZZZZZZZZZZZ):", check("ZZZZZZZZZZZZZZZZZZZZZZ"), flush=True)
        sys.exit(0)
    infile, outfile = sys.argv[1], sys.argv[2]
    raw = json.load(open(W + infile)) if os.path.exists(W + infile) else json.load(open(infile))
    if isinstance(raw, dict):
        items = {k: v for k, v in raw.items()}
    elif isinstance(raw, list):
        items = {}
        for e in raw:
            if isinstance(e, dict):
                items[e["code"]] = e
            else:
                items[e] = {}
    else:
        items = {}
    codes = sys.argv[3:] if len(sys.argv) > 3 else list(items.keys())
    out = json.load(open(W + outfile)) if os.path.exists(W + outfile) else {}
    for code in codes:
        if code in out and out[code]["status"] in ("live", "dead"):
            print(code, "skip already", out[code]["status"], flush=True)
            continue
        v = items.get(code, {}) or {}
        st, title, http, err = check(code)
        out[code] = {"status": st, "og_title": title, "http": http, "error": err,
                     "name": v.get("name", ""), "page": v.get("page", "")}
        json.dump(out, open(W + outfile, "w"), indent=1, ensure_ascii=False)
        print(code, st, repr(title)[:90], http, err, flush=True)
        time.sleep(6)
    live = sum(1 for v in out.values() if v["status"] == "live")
    dead = sum(1 for v in out.values() if v["status"] == "dead")
    tr = sum(1 for v in out.values() if v["status"] == "transport")
    print(f"VERIFY DONE total={len(out)} LIVE={live} DEAD={dead} TRANSPORT={tr}")
