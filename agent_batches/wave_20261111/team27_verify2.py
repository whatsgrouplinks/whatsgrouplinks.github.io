#!/usr/bin/env python3
"""Team27 wave 20261111: curl-based verifier v2.
Fixes v1: urllib timeout=20s was below WhatsApp's ~18-25s response time here,
so slow-but-valid fetches died as URLError. curl --max-time 60 + 3 workers + 2s delay.
Re-checks: all transport-failed codes from v1 + all unchecked pool1/pool2 codes.
Definitive v1 live/dead results are kept as-is (dead already had 2 spaced attempts).
Usage: python3 team27_verify2.py"""
import json, re, os, sys, time, subprocess
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
RAW = os.path.join(WAVE, "team27_raw")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
OG_RE = re.compile(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"')

pool1 = json.load(open(os.path.join(WAVE, "team27_pool.json")))
pool2 = json.load(open(os.path.join(WAVE, "team27_pool2.json")))
pool = dict(pool1); pool.update(pool2)
if os.path.exists(os.path.join(WAVE, "team27_pool3.json")):
    pool.update(json.load(open(os.path.join(WAVE, "team27_pool3.json"))))

# load v1 results
done = {}  # code -> (http, title, note)
v1 = os.path.join(WAVE, "team27_verify.tsv")
if os.path.exists(v1):
    for line in open(v1, encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if len(p) >= 4:
            done[p[0]] = (p[1], p[2], p[3])

out_path = os.path.join(WAVE, "team27_verify2.tsv")
if os.path.exists(out_path):
    for line in open(out_path, encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if len(p) >= 4:
            done[p[0]] = (p[1], p[2], p[3])

def curl_check(code):
    url = "https://chat.whatsapp.com/" + code
    try:
        r = subprocess.run(["curl", "-s", "-A", UA, "--max-time", "60", "-w",
                            "\n%{http_code}", url],
                           capture_output=True, text=True, timeout=70)
        body = r.stdout
        http = body.rsplit("\n", 1)[-1].strip() if body else "000"
        m = OG_RE.search(body)
        title = m.group(1).strip() if m else ""
        if r.returncode != 0 or http == "000":
            return (code, 0, "", "transport:curl-%d" % r.returncode)
        if int(http) == 200 and title:
            with open(os.path.join(RAW, "verify_%s.html" % code), "w", encoding="utf-8") as f:
                f.write(body)
        return (code, int(http), title, "")
    except Exception as e:
        return (code, 0, "", "transport:" + type(e).__name__)

def check(code):
    time.sleep(1.5)
    res = curl_check(code)
    if res[1] == 200 and not res[2]:
        time.sleep(15)
        res2 = curl_check(code)
        if res2[1] == 200 and res2[2]:
            return res2
        return res2
    if res[1] == 0:
        time.sleep(15)
        res2 = curl_check(code)
        return res2
    return res

todo = [c for c in sorted(pool) if c not in done or done[c][0] == "0"]
print(f"pool {len(pool)} | definitive already {len([c for c in done if done[c][0] != '0'])} | to check {len(todo)}", flush=True)
n = 0
with ThreadPoolExecutor(max_workers=3) as ex:
    for res in ex.map(check, todo):
        n += 1
        with open(out_path, "a", encoding="utf-8") as f:
            f.write("\t".join([res[0], str(res[1]), res[2].replace("\t", " "), res[3]]) + "\n")
        if n % 10 == 0:
            print(f"checked {n}/{len(todo)}", flush=True)
print("v2 done", flush=True)
