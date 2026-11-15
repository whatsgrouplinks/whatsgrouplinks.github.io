import requests, re, sys, time, json

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}

def og_title(html):
    m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)["\']', html, re.I)
    if not m:
        m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]+property=["\']og:title["\']', html, re.I)
    return m.group(1).strip() if m else ""

def check(sess, code, retries=3):
    url = f"https://chat.whatsapp.com/{code}"
    for attempt in range(retries):
        try:
            r = sess.get(url, headers=UA, timeout=75, allow_redirects=True)
            if r.status_code == 429:
                return ("PENDING", "HTTP 429", "")
            title = og_title(r.text)
            if title:
                return ("LIVE", f"HTTP {r.status_code}", title)
            if attempt < retries-1:
                time.sleep(8)
        except requests.RequestException as e:
            if attempt < retries-1:
                time.sleep(8)
                continue
            return ("PENDING", f"transport: {type(e).__name__}", "")
    return ("DEAD", "empty og:title after retries", "")

if __name__ == "__main__":
    sess = requests.Session()
    for code in sys.argv[1:]:
        st, why, title = check(sess, code)
        print(f"{code}\t{st}\t{why}\t{title!r}", flush=True)
