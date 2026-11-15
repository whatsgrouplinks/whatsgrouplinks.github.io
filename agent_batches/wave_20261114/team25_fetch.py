import requests, re, sys, json, html

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}

CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')

def fetch(url):
    s = requests.Session()
    try:
        r = s.get(url, headers=UA, timeout=60)
        return r.status_code, r.text
    except requests.RequestException as e:
        return None, f"ERR {type(e).__name__}: {e}"

if __name__ == "__main__":
    out = sys.argv[1]
    urls = sys.argv[2:]
    results = {}
    for u in urls:
        st, body = fetch(u)
        codes = sorted(set(CODE_RE.findall(body))) if st == 200 else []
        results[u] = {"status": st, "codes": codes, "len": len(body)}
        print(f"{u}\n  status={st} len={len(body)} codes={len(codes)}", flush=True)
        fn = "team25_raw/" + re.sub(r'[^A-Za-z0-9]+','_',u)[:80] + ".html"
        with open(fn, "w") as f: f.write(body if isinstance(body,str) else "")
    json.dump(results, open(out,"w"), indent=1)
