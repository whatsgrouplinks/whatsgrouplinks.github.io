import json, re, time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/"

def fetch_detail(gid):
    for attempt in range(3):
        s = requests.Session()
        s.headers.update({"User-Agent": UA})
        try:
            r = s.get("https://linkado.app/grupo/" + gid, timeout=90)
            if r.status_code == 200:
                t = r.text
                m = re.search(r'chat\.whatsapp\.com/([A-Za-z0-9]{20,24})', t)
                if not m:
                    return (gid, None, "no-code")
                title = desc = None
                mt = re.search(r'<meta property="og:title" content="([^"]*)"', t)
                if mt: title = mt.group(1)
                md = re.search(r'<meta property="og:description" content="([^"]*)"', t)
                if md: desc = md.group(1)
                return (gid, {"gid": gid, "code": m.group(1), "title": title, "desc": desc}, None)
            if r.status_code == 429:
                time.sleep(10)
        except Exception:
            time.sleep(5)
        finally:
            s.close()
    return (gid, None, "failed")

def main():
    all_ids = json.load(open(WAVE + "team10-ids.json"))
    print("Detail-fetching %d ids..." % len(all_ids), flush=True)
    cands, failed = [], []
    done = 0
    with ThreadPoolExecutor(max_workers=16) as ex:
        futs = {ex.submit(fetch_detail, g): g for g in all_ids}
        for f in as_completed(futs):
            gid, d, err = f.result()
            done += 1
            if d: cands.append(d)
            else: failed.append(gid)
            if done % 250 == 0:
                print("  %d/%d, %d with codes, %d failed" % (done, len(all_ids), len(cands), len(failed)), flush=True)
    json.dump(cands, open(WAVE + "team10-candidates.json", "w"), ensure_ascii=False)
    json.dump(failed, open(WAVE + "team10-detail-failed.json", "w"))
    print("CANDIDATES=%d DETAIL_FAILED=%d" % (len(cands), len(failed)), flush=True)

if __name__ == "__main__":
    main()
