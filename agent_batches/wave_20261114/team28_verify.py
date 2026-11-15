import requests, re, time, json, sys, html

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

def og_title(page):
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]*content=["\']([^"\']*)["\']', page, re.I)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]*property=["\']og:title["\']', page, re.I)
    return html.unescape(m.group(1).strip()) if m else ""

def check(session, code, retries=3):
    url = f"https://chat.whatsapp.com/{code}"
    last_err = ""
    for attempt in range(retries):
        try:
            r = session.get(url, headers=UA, timeout=75)
            if r.status_code == 429:
                return ("pending", "HTTP 429")
            title = og_title(r.text)
            if title:
                return ("live", title)
            last_err = f"empty og:title (HTTP {r.status_code})"
        except Exception as e:
            last_err = f"transport: {type(e).__name__}: {str(e)[:80]}"
            return ("pending", last_err)
        if attempt < retries - 1:
            time.sleep(8)
    return ("dead", last_err)

if __name__ == "__main__":
    s = requests.Session()
    for code, expect in [("KrDwdK8EIkB6vgauHg5M7N", "JAY - PHP & Python Full Stack Developer"),
                         ("ZzZzZzZzZzZzZzZzZzZzZzZz", "")]:
        st, info = check(s, code)
        print(f"CONTROL {code}: status={st} title={info!r} expect={expect!r} -> {'PASS' if info==expect or (expect=='' and st=='dead') else 'FAIL'}")
