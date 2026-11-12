import json, re, sys, time, requests
from pathlib import Path

WAVE = Path("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112")
BUILD = Path("/home/hatch/workspace/whatsapp-groups-site")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9", "Accept": "text/html,application/xhtml+xml"}
S = requests.Session(); S.headers.update(UA)

GENERIC_TITLES = {"whatsapp group invite", "whatsapp group", "join group on whatsapp", "whatsapp"}

def og_title(html):
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)', html, re.I)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', html, re.I)
    t = m.group(1).strip() if m else ""
    if not t:
        m = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']*)', html, re.I)
        if not m:
            m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:description["\']', html, re.I)
        t = m.group(1).strip() if m else ""
    return t

def check(code, timeout=75):
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = S.get(url, timeout=timeout, allow_redirects=True)
        t = og_title(r.text)
        import html as _h
        t = _h.unescape(t).strip()
        live = bool(t) and t.lower() not in GENERIC_TITLES
        return ("live" if live else "dead", r.status_code, t)
    except Exception as e:
        return ("transport", 0, f"{type(e).__name__}: {e}")

if __name__ == "__main__":
    # CONTROLS FIRST
    g = json.load(open(BUILD/"groups.json"))
    live_code = g[0]["invite"].split("/")[-1]
    print("CONTROL live code:", live_code, "->", check(live_code))
    print("CONTROL fabricated code: ZzZzZzZzZzZzZzZzZzZzZz ->", check("ZzZzZzZzZzZzZzZzZzZzZz"))
