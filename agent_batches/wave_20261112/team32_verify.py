#!/usr/bin/env python3
"""TEAM32 step 6: verify final pool (131 codes) with curl, 4 workers, checkpoint TSV+JSONL."""
import json, re, html, os, subprocess, time
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
RAW = WAVE + "team32_raw/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
TSV = WAVE + "team32_verify.tsv"
JSONL = WAVE + "team32_verify.jsonl"

def og_title(body):
    m = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\'](.*?)["\']', body, re.I | re.S)
    if not m:
        m = re.search(r'<meta\s+content=["\'](.*?)["\']\s+property=["\']og:title["\']', body, re.I | re.S)
    if m:
        return html.unescape(m.group(1)).strip()
    m = re.search(r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\']', body, re.I | re.S)
    if m:
        return html.unescape(m.group(1)).strip()
    return ""

def curl_once(code, timeout=90):
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = subprocess.run(["curl", "-sS", "-L", "--max-time", str(timeout),
                            "-A", UA, "-o", "-", url],
                           capture_output=True, text=True, timeout=timeout + 15)
        body = r.stdout or ""
        if r.returncode != 0 and not body:
            return ("transport", "", body, f"rc={r.returncode} {r.stderr.strip()[:150]}")
        return ("http", og_title(body), body, f"rc={r.returncode} len={len(body)}")
    except subprocess.TimeoutExpired:
        return ("transport", "", "", "curl timeout")

def check(code):
    """Returns dict with verdict: live/dead/pending."""
    attempts = []
    for attempt in range(3):
        st, title, body, note = curl_once(code)
        attempts.append(f"a{attempt+1}:{st}:{title[:40]!r}:{note}")
        if st == "http" and title:
            return {"code": code, "verdict": "live", "og_title": title,
                    "attempts": attempts, "body_len": len(body)}
        if st == "http" and not title:
            # confirm empty with a spaced second fetch before calling dead
            time.sleep(30)
            st2, title2, body2, note2 = curl_once(code)
            attempts.append(f"confirm:{st2}:{title2[:40]!r}:{note2}")
            if st2 == "http" and title2:
                return {"code": code, "verdict": "live", "og_title": title2,
                        "attempts": attempts, "body_len": len(body2)}
            if st2 == "http":
                return {"code": code, "verdict": "dead", "og_title": "",
                        "attempts": attempts, "body_len": len(body2)}
            # confirm hit transport -> fall through to retry loop
        if attempt < 2:
            time.sleep(45)
    return {"code": code, "verdict": "pending", "og_title": "",
            "attempts": attempts, "body_len": 0}

def main():
    pool = json.load(open(WAVE + "team32_pool_final.json"))
    done = {}
    if os.path.exists(TSV):
        for line in open(TSV):
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 3:
                done[parts[0]] = parts[1]
    todo = [p for p in pool if p["code"] not in done]
    print(f"pool={len(pool)} done={len(done)} todo={len(todo)}", flush=True)
    log = open(WAVE + "team32_verify.log", "a")
    jl = open(JSONL, "a")
    tsv = open(TSV, "a")

    def run_one(p):
        res = check(p["code"])
        res["name_src"] = p.get("name", "")
        res["source"] = p.get("source", "")
        if res["verdict"] == "live":
            # save evidence html
            st, title, body, note = curl_once(p["code"])
            open(RAW + f"verify_{p['code']}.html", "w", encoding="utf-8", errors="ignore").write(body)
        line = f"{res['code']}\t{res['verdict']}\t{res['og_title']}\t{res['source']}\t{' | '.join(res['attempts'])}\n"
        return res, line

    with ThreadPoolExecutor(max_workers=4) as ex:
        for res, line in ex.map(run_one, todo):
            tsv.write(line); tsv.flush()
            jl.write(json.dumps(res, ensure_ascii=False) + "\n"); jl.flush()
            print(f"{res['code']} {res['verdict']} {res['og_title'][:60]}", flush=True)
            log.write(line); log.flush()
    print("VERIFY DONE", flush=True)
    log.close(); jl.close(); tsv.close()

if __name__ == "__main__":
    main()
