import json, re, subprocess, time, sys
from concurrent.futures import ThreadPoolExecutor

UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"

def check(code):
    try:
        r = subprocess.run(["curl","-sL","--max-time","25","-A",UA,
                            f"https://chat.whatsapp.com/{code}"],
                           capture_output=True, text=True, timeout=40)
        body = r.stdout or ""
        m = re.search(r'<meta property="og:title" content="([^"]*)"', body)
        title = m.group(1) if m else ""
        md = re.search(r'<meta property="og:description" content="([^"]*)"', body)
        desc = md.group(1) if md else ""
        return {"code": code, "http": 200 if body else 0, "og_title": title, "og_desc": desc}
    except Exception as e:
        return {"code": code, "http": 0, "og_title": "", "og_desc": "", "error": str(e)}

def main(infile, outfile):
    items = json.load(open(infile))
    codes = [i["code"] for i in items]
    results = {}
    try:
        results = json.load(open(outfile))
    except Exception:
        pass
    todo = [c for c in codes if c not in results]
    print(f"resuming: {len(results)} already done, {len(todo)} to do", flush=True)
    def worker(code):
        res = check(code)
        time.sleep(0.7)
        return res
    with ThreadPoolExecutor(max_workers=3) as ex:
        for res in ex.map(worker, todo):
            results[res["code"]] = res
            json.dump(results, open(outfile, "w"), indent=1, ensure_ascii=False)
            print(res["code"], res["http"], repr(res["og_title"][:60]), flush=True)
    live = sum(1 for v in results.values() if v["http"]==200 and v["og_title"].strip())
    amb = sum(1 for v in results.values() if v["http"]==200 and not v["og_title"].strip())
    fail = sum(1 for v in results.values() if v["http"]!=200)
    print(f"LIVE={live} AMBIGUOUS={amb} FAIL={fail} TOTAL={len(results)}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
