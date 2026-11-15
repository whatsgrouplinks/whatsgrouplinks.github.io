#!/usr/bin/env python3
"""team24 verification helper: persistent session, og:title extraction."""
import json, re, sys, time, requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9,es;q=0.8,pt;q=0.7"}

def og_title(html):
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)["\']', html, re.I)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', html, re.I)
    return m.group(1).strip() if m else ""

def check(session, code, retries=3):
    url = f"https://chat.whatsapp.com/{code}"
    last_err = ""
    for attempt in range(retries):
        try:
            r = session.get(url, headers=UA, timeout=75)
            if r.status_code == 429:
                return ("pending", "", f"HTTP 429 attempt {attempt+1}")
            t = og_title(r.text)
            if t:
                return ("live", t, "")
            last_err = f"empty og:title (HTTP {r.status_code})"
        except requests.RequestException as e:
            last_err = f"transport: {type(e).__name__}: {e}"
            return ("pending", "", last_err)
        if attempt < retries - 1:
            time.sleep(20)
    return ("dead", "", last_err)

if __name__ == "__main__":
    s = requests.Session()
    for code in ["KrDwdK8EIkB6vgauHg5M7N", "ZzZzZzZzZzZzZzZzZzZzZzZz"]:
        st, t, err = check(s, code)
        print(code, "->", st, repr(t), err)
