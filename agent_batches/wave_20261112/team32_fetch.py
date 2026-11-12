#!/usr/bin/env python3
"""TEAM32 step 2: fetch the 16 team27 leads, save raw, extract codes + bit.ly links."""
import json, re, os, subprocess, time
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
RAW = WAVE + "team32_raw/"
os.makedirs(RAW, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

LEADS = [
    ("tls_shopee", "https://www.thelastsurvivors.org/grup-wa-shopee-tanam/"),
    ("tls_cat_grup", "https://www.thelastsurvivors.org/category/grup/"),
    ("aussiesin", "https://aussiesin.com/"),
    ("joinnchat_ph_girl", "https://joinnchat.com/philippines-girl-whatsapp-group-link/"),
    ("virenial_yt", "https://virenial.com/teknologi/vr-11228/100-grup-wa-subscribe-youtube-yang-bisa-anda-ikuti"),
    ("helloworldawaits", "https://helloworldawaits.com/digital-nomad-travel/trusted-travel-whatsapp-channel/"),
    ("whtsgrouplink_travel", "https://whtsgrouplink.com/travel-whatsapp-group-links/"),
    ("grouplink_intl", "https://grouplink.com.in/1300-international-whatsapp-group-link/"),
    ("scribd_11rb_a", "https://www.scribd.com/document/578911793/11-Ribu-Link-Grup-WA-Dengan-Nama-Grup"),
    ("scribd_11rb_b", "https://www.scribd.com/document/423556831/11rb-Link-Group-WA-Dengan-Nama-Group"),
    ("grouplinksforyou_feed", "https://www.grouplinksforyou.com/feeds/posts/default?alt=json&max-results=50"),
    ("techsslash_ph", "https://techsslash.com/philippines-whatsapp-group-links/"),
    ("whtsagrouplinks_intl", "https://www.whtsagrouplinks.com/international-whatsapp-groups-links/"),
    ("groupwa_jobs", "https://groupwa.link/jobs/"),
    ("groupwa_education", "https://groupwa.link/education/"),
    ("groupwa_gaming", "https://groupwa.link/gaming/"),
]

def curl_fetch(url, timeout=90):
    try:
        r = subprocess.run(["curl", "-sS", "-L", "--max-time", str(timeout),
                            "-A", UA["User-Agent"], "-o", "-", url],
                           capture_output=True, text=True, timeout=timeout+15)
        return r.stdout or "", r.returncode, r.stderr.strip()[:200]
    except subprocess.TimeoutExpired:
        return "", -1, "timeout"

def main():
    sess = requests.Session(); sess.headers.update(UA)
    log = open(WAVE + "team32_fetch.log", "a")
    def say(s):
        print(s, flush=True); log.write(s + "\n"); log.flush()
    out = {}
    for key, url in LEADS:
        body, via, note = "", "", ""
        try:
            r = sess.get(url, timeout=90)
            body, via = r.text, f"requests status={r.status_code}"
        except Exception as e:
            body, via, note = "", "requests FAIL", f"{type(e).__name__}: {e}"
            b2, rc, err = curl_fetch(url)
            if b2:
                body, via = b2, f"curl rc={rc}"
                note = err
            else:
                note = f"curl also failed rc={rc} {err}"
        fn = RAW + key + ".html"
        open(fn, "w", encoding="utf-8", errors="ignore").write(body)
        codes = sorted(set(re.findall(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})", body)))
        bitlys = sorted(set(re.findall(r"https?://bit\.ly/[A-Za-z0-9_-]+", body)))
        shortlinks = sorted(set(re.findall(r"https?://(?:bit\.ly|tinyurl\.com|shorturl\.at|cutt\.ly|rb\.gy|is\.gd)/[A-Za-z0-9_-]+", body)))
        say(f"{key}: len={len(body)} via={via} {note} codes={len(codes)} bitly={len(bitlys)} short={len(shortlinks)}")
        out[key] = {"url": url, "len": len(body), "via": via, "note": note,
                    "codes": codes, "bitly": bitlys, "shortlinks": shortlinks,
                    "file": fn}
        json.dump(out, open(WAVE + "team32_fetch.json", "w"), indent=1, ensure_ascii=False)
        time.sleep(3)
    say("FETCH DONE")
    log.close()

if __name__ == "__main__":
    main()
