import requests, re, json, sys, time
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
S = requests.Session()
def check(code):
    try:
        r = S.get("https://chat.whatsapp.com/"+code, headers=UA, timeout=75)
        html = r.text
        m = re.search(r'<meta property="og:title" content="([^"]*)"', html)
        title = m.group(1) if m else ""
        m2 = re.search(r'<meta property="og:description" content="([^"]*)"', html)
        desc = m2.group(1) if m2 else ""
        return {"code": code, "status": r.status_code, "og_title": title, "og_desc": desc, "live": bool(title.strip() or desc.strip())}
    except Exception as e:
        return {"code": code, "error": str(e)[:120], "live": None}
if __name__ == "__main__":
    for c in sys.argv[1:]:
        print(json.dumps(check(c)))
        time.sleep(1)
