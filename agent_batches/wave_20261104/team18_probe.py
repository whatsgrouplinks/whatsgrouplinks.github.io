"""Team 18: appgrouplink.com scrape. Fetches listing pages, extracts name->join-url pairs,
resolves join URLs to real chat.whatsapp.com codes, dedupes vs union."""
import requests, re, time, json, os, sys

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
BASE = "https://appgrouplink.com"
WORK = os.path.dirname(os.path.abspath(__file__))

def make_session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*"})
    return s

def get(s, url, timeout=55, retries=3):
    for a in range(retries):
        try:
            r = s.get(url, timeout=timeout, allow_redirects=True)
            if r.status_code == 200 and len(r.text) > 1000:
                return r.text
            print(f"  [{url}] status={r.status_code} len={len(r.text)} attempt={a+1}")
        except Exception as e:
            print(f"  [{url}] {type(e).__name__} attempt={a+1}")
            time.sleep(2 + a * 3)
    return None

def parse_listing(html):
    """Return list of (group_name, join_url)."""
    # Find Join In / Join Group anchors and their hrefs
    out = []
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.S | re.I):
        href, inner = m.group(1), m.group(2)
        if re.search(r'Join\s*(In|Group|Now|Here)?', inner, re.I) or 'join' in inner.lower():
            txt = re.sub(r'<[^>]+>', '', inner).strip()
            if 'join' in txt.lower():
                out.append((href, txt))
    # Better: table rows <td>name</td><td><a href=join>...
    rows = []
    for m in re.finditer(r'<tr[^>]*>(.*?)</tr>', html, re.S | re.I):
        row = m.group(1)
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S | re.I)
        if len(cells) >= 2:
            name = re.sub(r'<[^>]+>', '', cells[0]).strip()
            hm = re.search(r'href="([^"]+)"', cells[1])
            if name and hm and len(name) < 120 and 'whatsapp group' not in name.lower() or True:
                rows.append((name, hm.group(1)))
    return out, rows

if __name__ == "__main__":
    s = make_session()
    url = sys.argv[1] if len(sys.argv) > 1 else BASE + "/pakistani-whatsapp-group-links/"
    html = get(s, url)
    if not html:
        print("FETCH FAILED")
        sys.exit(1)
    fn = os.path.join(WORK, "team18_page_probe.html")
    open(fn, "w").write(html)
    print("saved", fn, len(html))
    anchors, rows = parse_listing(html)
    print("anchor-join count:", len(anchors))
    for h, t in anchors[:8]: print("  ANCHOR:", t, "->", h)
    print("row count:", len(rows))
    for n, h in rows[:12]: print("  ROW:", repr(n), "->", h)
