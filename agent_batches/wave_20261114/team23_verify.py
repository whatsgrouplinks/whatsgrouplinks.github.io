#!/usr/bin/env python3
"""team23 verification helper: one requests.Session, browser UA, og:title check."""
import re, sys, time, json, requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}

def og_title(html):
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)["\']', html, re.I)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', html, re.I)
    return (m.group(1).strip() if m else "")

def verify(sess, code, retries=3):
    url = f"https://chat.whatsapp.com/{code}"
    for attempt in range(retries):
        try:
            r = sess.get(url, headers=UA, timeout=75, allow_redirects=True)
            if r.status_code == 429:
                return ("pending", "HTTP 429", "")
            if r.status_code != 200:
                time.sleep(2)
                continue
            t = og_title(r.text)
            if t:
                return ("live", t, "")
            time.sleep(3 + attempt * 3)
        except requests.RequestException as e:
            time.sleep(3 + attempt * 3)
            last = str(e)
    return ("dead", "", last if 'last' in dir() else "empty og:title after retries")

if __name__ == "__main__":
    sess = requests.Session()
    for code in ["KrDwdK8EIkB6vgauHg5M7N", "ZzZzZzZzZzZzZzZzZzZzZzZzZz"]:
        st, title, err = verify(sess, code)
        print(code, "=>", st, "|", title, "|", err)
