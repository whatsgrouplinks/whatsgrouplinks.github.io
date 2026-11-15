import requests, re, html as htmllib, json, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"}

def og_title(page):
    m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', page)
    if not m:
        m = re.search(r'<meta\s+content="([^"]*)"\s+property="og:title"', page)
    return htmllib.unescape(m.group(1)).strip() if m else ""

def og_desc(page):
    m = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', page)
    return htmllib.unescape(m.group(1)).strip() if m else ""

def wa_check(session, code, timeout=75):
    """Returns (status, ogtitle) where status in live/dead/pending(reason)."""
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = session.get(url, headers=UA, timeout=timeout)
        if r.status_code == 429:
            return ("pending", "", f"HTTP 429 on {code}")
        t = og_title(r.text or "")
        if t:
            return ("live", t, "")
        return ("dead", "", "")
    except requests.exceptions.RequestException as e:
        return ("pending", "", f"transport {type(e).__name__}: {str(e)[:120]}")

def wa_check_retry(session, code, attempts=3, gap=20):
    last = ("dead", "", "")
    for i in range(attempts):
        st, title, reason = wa_check(session, code)
        if st == "live":
            return st, title, ""
        if st == "pending":
            return st, "", reason
        last = (st, title, reason)
        if i < attempts - 1:
            time.sleep(gap)
    return last
