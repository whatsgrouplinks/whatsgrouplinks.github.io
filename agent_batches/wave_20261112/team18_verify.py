import requests, re, sys, json, time
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
S = requests.Session()
def check(code):
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = S.get(url, headers=UA, timeout=75)
        html = r.text
        m = re.search(r'<meta property="og:title" content="([^"]*)"', html)
        title = m.group(1) if m else ""
        m2 = re.search(r'<meta property="og:description" content="([^"]*)"', html)
        desc = m2.group(1) if m2 else ""
        return {"code": code, "status": r.status_code, "title": title, "desc": desc, "live": bool(title or desc)}
    except Exception as e:
        return {"code": code, "status": "ERR", "error": str(e), "live": None}
if __name__ == "__main__":
    for c in sys.argv[1:]:
        print(json.dumps(check(c), ensure_ascii=False))
        time.sleep(1)
