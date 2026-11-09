"""Team 09 slow verifier for 704 codes in team08_codes.json.
curl-only (never python requests on chat.whatsapp.com), 3 workers,
0.6s sleep per worker between requests, up to 3 attempts for empty og:title.
Resumable: appends one JSON line per code to team09_verify_raw.jsonl.
"""
import json, re, subprocess, html, time, os, sys
from concurrent.futures import ThreadPoolExecutor

WAVE = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
RAW = os.path.join(WAVE, "team09_verify_raw.jsonl")

OG_TITLE = re.compile(r'<meta property="og:title" content="([^"]*)"', re.I)

def fetch_once(code):
    url = "https://chat.whatsapp.com/" + code
    try:
        r = subprocess.run(
            ["curl", "-sL", "--max-time", "25", "-A", UA, "-o", "-", "-w", "\n%{http_code}", url],
            capture_output=True, text=True, timeout=35)
        out = r.stdout or ""
        # last line is http code
        if "\n" in out:
            body, http = out.rsplit("\n", 1)
        else:
            body, http = out, ""
        m = OG_TITLE.search(body)
        title = html.unescape(m.group(1)).strip() if m else ""
        return http.strip(), title, len(body)
    except Exception as e:
        return "ERR", "", 0

def work(code):
    attempts = []
    title = ""
    http = ""
    for i in range(3):
        http, title, size = fetch_once(code)
        attempts.append({"http": http, "title": title, "size": size})
        if title:
            break
        if i < 2:
            time.sleep(4)
    time.sleep(0.6)
    return {"code": code, "http": http, "title": title,
            "attempts": len(attempts), "sizes": [a["size"] for a in attempts]}

def main():
    codes = json.load(open(os.path.join(WAVE, "team08_codes.json")))
    existing = set(json.load(open(os.path.join(WAVE, "../../.existing_codes.json"))))
    fresh = [c for c in dict.fromkeys(codes) if c not in existing]
    print("total", len(codes), "union-dup", len(codes) - len(fresh), "fresh", len(fresh), flush=True)
    done = set()
    if os.path.exists(RAW):
        with open(RAW) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        done.add(json.loads(line)["code"])
                    except Exception:
                        pass
    todo = [c for c in fresh if c not in done]
    print("already done", len(done), "todo", len(todo), flush=True)
    n = 0
    with open(RAW, "a") as out:
        with ThreadPoolExecutor(max_workers=3) as ex:
            for res in ex.map(work, todo):
                out.write(json.dumps(res, ensure_ascii=False) + "\n")
                out.flush()
                n += 1
                if n % 25 == 0:
                    print(f"checked {n}/{len(todo)} live-so-far-title-nonempty...",
                          flush=True)
    print("DONE checked", n, flush=True)

if __name__ == "__main__":
    main()
