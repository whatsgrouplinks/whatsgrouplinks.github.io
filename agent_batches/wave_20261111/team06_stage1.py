#!/usr/bin/env python3
"""TEAM 06 — Stage 1: mine linkado listing pages for invite codes.
Reads leads_slice6.json, fetches each page (6 workers), extracts codes + name + category + description.
Checkpoints to team06-stage1-checkpoint.json every 200 pages.
Outputs: team06-stage1-candidates.json, team06-stage1-failed.json
"""
import json, re, os, sys, time, threading
from concurrent.futures import ThreadPoolExecutor
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
CODE_RE = re.compile(r"chat\.whatsapp\.com/([A-Za-z0-9]{10,40})")
TITLE_RE = re.compile(r"<title>([^<]{3,200})</title>", re.I)
CAT_RE = re.compile(r"na categoria ([^.\"<]{2,60})", re.I)
DESC_RE = re.compile(r'property=\\"og:description\\",\\"content\\":\\"((?:[^\\"\\\\]|\\\\.)*)', re.I)

def fetch(url, session):
    for attempt in range(2):
        try:
            r = session.get(url, timeout=25)
            if r.status_code == 200 and len(r.text) > 500:
                return r.text
            time.sleep(1.0)
        except Exception:
            time.sleep(1.0)
    return None

def parse(html, url):
    codes = sorted(set(CODE_RE.findall(html)))
    title = ""
    m = TITLE_RE.search(html)
    if m:
        title = m.group(1).strip()
    cat = ""
    m = CAT_RE.search(html)
    if m:
        cat = m.group(1).strip()
    desc = ""
    m = DESC_RE.search(html)
    if m:
        desc = m.group(1).replace('\\"', '"').strip()
    return codes, title, cat, desc

def main():
    urls = json.load(open(os.path.join(WAVE, "leads_slice6.json")))
    ckpt_path = os.path.join(WAVE, "team06-stage1-checkpoint.json")
    done = {}
    if os.path.exists(ckpt_path):
        done = json.load(open(ckpt_path))
        print(f"resuming: {len(done)} pages already done", flush=True)
    session = requests.Session()
    session.headers.update(UA)
    lock = threading.Lock()
    results = {}   # url -> {codes, title, cat, desc}
    failed = []
    counter = [0]
    total = len(urls)

    def work(url):
        if url in done:
            with lock:
                results[url] = done[url]
            return
        html = fetch(url, session)
        time.sleep(0.6)
        with lock:
            counter[0] += 1
            n = counter[0]
        if html is None:
            with lock:
                failed.append(url)
                results[url] = None
        else:
            codes, title, cat, desc = parse(html, url)
            with lock:
                results[url] = {"codes": codes, "title": title, "cat": cat, "desc": desc}
                done[url] = results[url]
        if n % 200 == 0:
            with lock:
                json.dump(done, open(ckpt_path, "w"), ensure_ascii=False)
            print(f"{n}/{total} pages, failed so far: {len(failed)}", flush=True)

    with ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(work, urls))
    json.dump(done, open(ckpt_path, "w"), ensure_ascii=False)
    cands = []
    for url, rec in results.items():
        if rec:
            for c in rec["codes"]:
                cands.append({"code": c, "title": rec["title"], "cat_pt": rec["cat"],
                              "desc": rec["desc"], "source": url})
    json.dump(cands, open(os.path.join(WAVE, "team06-stage1-candidates.json"), "w"), ensure_ascii=False)
    json.dump(sorted(set(failed)), open(os.path.join(WAVE, "team06-stage1-failed.json"), "w"), ensure_ascii=False)
    print(f"DONE pages={total} failed={len(failed)} candidate-rows={len(cands)} unique-codes={len(set(c['code'] for c in cands))}", flush=True)

if __name__ == "__main__":
    main()
