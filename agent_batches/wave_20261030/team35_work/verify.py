#!/usr/bin/env python3
"""Verify WhatsApp invite codes: HTTP 200 + meaningful og:title."""
import sys, re, time, subprocess, json

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

def verify(code):
    url = f"https://chat.whatsapp.com/{code}"
    try:
        p = subprocess.run(
            ["curl", "-sL", "-A", UA, "--max-time", "30", "-o", "-", "-w", "\nHTTP_CODE:%{http_code}", url],
            capture_output=True, text=True, timeout=45)
        out = p.stdout
        m = re.search(r"HTTP_CODE:(\d+)", out)
        http = int(m.group(1)) if m else 0
        body = out[:m.start()] if m else out
        title = ""
        tm = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', body)
        if tm:
            title = tm.group(1)
        if http == 200 and title and "Couldn't look up link" not in title and len(title) > 1:
            return True, title.strip()
        return False, f"http={http} title={title[:60]!r}"
    except Exception as e:
        return False, f"error {e}"

if __name__ == "__main__":
    codes = [c.strip() for c in sys.stdin if c.strip()]
    results = {}
    for i, c in enumerate(codes):
        ok, info = verify(c)
        results[c] = {"ok": ok, "title": info if ok else "", "reason": "" if ok else info}
        print(json.dumps({c: results[c]}), flush=True)
        time.sleep(0.5)
    with open(sys.argv[1] if len(sys.argv) > 1 else "/dev/null", "w") as f:
        json.dump(results, f, indent=1)
