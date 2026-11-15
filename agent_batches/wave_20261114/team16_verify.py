#!/usr/bin/env python3
"""team16 WhatsApp invite verification — wave 20261114.
Single keep-alive curl session (cookie jar), browser UA, 90s timeout.
LIVE only if NON-EMPTY, NON-GENERIC og:title.
Usage: python3 team16_verify.py <codes_file> <out_json> [retries]
codes_file: one code per line. out_json: results list.
"""
import json, re, subprocess, sys, time, os

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
JAR = os.path.join(WD, "team16-cookies.txt")
HTMLDIR = os.path.join(WD, "team16-html")
os.makedirs(HTMLDIR, exist_ok=True)

GENERIC = {"whatsapp group invite", "whatsapp", "join whatsapp group",
           "whatsapp group", "group invite"}

def og_title(html):
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']',
                  html, re.I | re.S)
    if not m:
        m = re.search(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']',
                      html, re.I | re.S)
    if not m:
        return ""
    t = m.group(1)
    t = (t.replace("&amp;", "&").replace("&quot;", '"').replace("&#039;", "'")
          .replace("&lt;", "<").replace("&gt;", ">").strip())
    return t

def fetch(code):
    """One curl fetch inside the shared cookie-jar session. Returns (http, html, elapsed)."""
    out = os.path.join(HTMLDIR, code + ".html")
    t0 = time.time()
    p = subprocess.run([
        "curl", "-sS", "-L", "--max-time", "90",
        "-A", UA,
        "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "-H", "Accept-Language: en-US,en;q=0.9",
        "-b", JAR, "-c", JAR,
        "-o", out, "-w", "%{http_code}",
        f"https://chat.whatsapp.com/{code}",
    ], capture_output=True, text=True, timeout=120)
    el = time.time() - t0
    http = p.stdout.strip()
    html = ""
    if os.path.exists(out):
        with open(out, encoding="utf-8", errors="ignore") as f:
            html = f.read()
    return http, html, el, p.stderr.strip()

def verify(code, max_rounds=3):
    """Returns result dict. Spaced retries on empty og:title."""
    for rnd in range(1, max_rounds + 1):
        http, html, el, err = fetch(code)
        title = og_title(html)
        if http == "429" or http == "000" or http == "":
            return {"code": code, "status": "pending",
                    "reason": f"HTTP {http or '000'} transport/rate-limit (round {rnd})",
                    "og_title": title, "http": http, "elapsed_s": round(el, 1),
                    "stderr": err[:200]}
        if title and title.lower() not in GENERIC:
            return {"code": code, "status": "live", "og_title": title,
                    "http": http, "elapsed_s": round(el, 1), "rounds": rnd}
        if rnd < max_rounds:
            time.sleep(15)
    return {"code": code, "status": "dead",
            "reason": "empty og:title after 3 spaced fetches",
            "og_title": "", "http": http, "elapsed_s": round(el, 1)}

if __name__ == "__main__":
    codes_file, out_json = sys.argv[1], sys.argv[2]
    with open(codes_file) as f:
        codes = [l.strip() for l in f if l.strip()]
    results = []
    for i, code in enumerate(codes):
        r = verify(code)
        results.append(r)
        print(f"[{i+1}/{len(codes)}] {code}: {r['status']} "
              f"og_title={r.get('og_title','')!r} http={r.get('http')}", flush=True)
        if i < len(codes) - 1:
            time.sleep(8)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print("saved", out_json)
