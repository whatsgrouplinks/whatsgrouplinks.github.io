#!/usr/bin/env python3
"""team29: controls + grupbul re-check + overflow mining for wave 20261114."""
import json, re, time, sys, os, html
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114"
UNION = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})

def og_title(page):
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']',
                  page, re.I | re.S)
    if not m:
        m = re.search(r'<meta[^>]+content=["\'](.*?)["\'][^>]+property=["\']og:title["\']',
                      page, re.I | re.S)
    return html.unescape(m.group(1).strip()) if m else ""

def verify_code(code, attempts=3):
    """Returns (status, title, http). status in live/dead/pending."""
    url = f"https://chat.whatsapp.com/{code}"
    title = ""
    last_http = None
    for i in range(attempts):
        try:
            r = S.get(url, timeout=75)
            last_http = r.status_code
            title = og_title(r.text)
            if title:
                return "live", title, last_http
            time.sleep(2 + i * 2)
        except requests.exceptions.RequestException as e:
            return "pending", "", str(type(e).__name__)
    if last_http == 429:
        return "pending", "", "429"
    return "dead", "", last_http

def fetch(url, timeout=60):
    r = S.get(url, timeout=timeout)
    return r

if __name__ == "__main__":
    # ---- controls ----
    t, title, http = verify_code("KrDwdK8EIkB6vgauHg5M7N", attempts=2)
    print("CONTROL live:", t, repr(title), http, flush=True)
    assert t == "live" and title == "JAY - PHP & Python Full Stack Developer", "LIVE CONTROL FAILED"
    t2, title2, http2 = verify_code("ZzZzZzZzZzZzZzZzZzZzZz", attempts=2)
    print("CONTROL fab:", t2, repr(title2), http2, flush=True)
    assert t2 == "dead" and title2 == "", "FABRICATED CONTROL FAILED"
    print("CONTROLS PASS", flush=True)
    json.dump({"live": [t, title, http], "fab": [t2, title2, http2]},
              open(os.path.join(WAVE, "team29-controls.json"), "w"))
