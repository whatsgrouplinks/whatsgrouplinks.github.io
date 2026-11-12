#!/usr/bin/env python3
"""TEAM32 wave_20261112: controls + re-verify 2 Ramadhan pending codes."""
import json, re, subprocess, sys, time, html, os
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

def og_title(html_text):
    m = re.search(r'<meta\s+property=["\']og:title["\']\s+content=["\'](.*?)["\']', html_text, re.I | re.S)
    if not m:
        m = re.search(r'<meta\s+content=["\'](.*?)["\']\s+property=["\']og:title["\']', html_text, re.I | re.S)
    if m:
        return html.unescape(m.group(1)).strip()
    m = re.search(r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\']', html_text, re.I | re.S)
    if m:
        return html.unescape(m.group(1)).strip()
    return ""

def curl_check(code, timeout=90):
    """Returns (status, title, err)."""
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = subprocess.run(["curl", "-sS", "-L", "--max-time", str(timeout),
                            "-A", UA["User-Agent"], "-o", "-", url],
                           capture_output=True, text=True, timeout=timeout+15)
        body = r.stdout or ""
        if r.returncode != 0 and not body:
            return ("transport", "", f"curl rc={r.returncode} {r.stderr.strip()[:200]}")
        return ("http", og_title(body), f"rc={r.returncode} len={len(body)}")
    except subprocess.TimeoutExpired:
        return ("transport", "", "curl timeout")

def session_check(sess, code, timeout=90):
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = sess.get(url, timeout=timeout, allow_redirects=True)
        return ("http", og_title(r.text), f"status={r.status_code} len={len(r.text)}")
    except Exception as e:
        return ("transport", "", f"{type(e).__name__}: {e}")

def main():
    log = open(WAVE + "team32_run.log", "a")
    def say(s):
        print(s, flush=True); log.write(s + "\n"); log.flush()

    sess = requests.Session()
    sess.headers.update(UA)

    # --- CONTROLS ---
    groups = json.load(open("/home/hatch/workspace/whatsapp-groups-site/groups.json"))
    live_code = None
    for g in groups:
        m = re.search(r"chat\.whatsapp\.com/([A-Za-z0-9_-]+)", g.get("invite", ""))
        if m:
            live_code = m.group(1); break
    say(f"CONTROL live code from groups.json: {live_code} (group: {g.get('name')})")
    st, title, err = session_check(sess, live_code)
    say(f"CONTROL live via session: {st} title={title!r} {err}")
    if not title:
        st, title, err = curl_check(live_code)
        say(f"CONTROL live via curl: {st} title={title!r} {err}")
    fake = "ZZZZZZZZZZZZZZZZZZZZZZ"
    st2, title2, err2 = session_check(sess, fake)
    say(f"CONTROL fake via session: {st2} title={title2!r} {err2}")
    if title2:
        st2, title2, err2 = curl_check(fake)
        say(f"CONTROL fake via curl: {st2} title={title2!r} {err2}")

    # --- RAMADHAN RE-VERIFY (spaced retries) ---
    pending = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/team27-newdirs-seasia-pending.json"))
    results = []
    for item in pending:
        code = item["invite"].split("/")[-1]
        say(f"\nRE-VERIFY {code} ({item['name']})")
        verdict = None
        for attempt in range(3):
            if attempt:
                time.sleep(45)
            st, title, err = session_check(sess, code)
            say(f"  attempt {attempt+1} session: {st} title={title!r} {err}")
            if st == "http" and title:
                verdict = ("live", title); break
            if st == "http" and not title:
                # confirm with curl before calling dead
                stc, titlec, errc = curl_check(code)
                say(f"  confirm curl: {stc} title={titlec!r} {errc}")
                if stc == "http" and titlec:
                    verdict = ("live", titlec); break
                if stc == "http":
                    verdict = ("dead", ""); break
                # curl transport -> keep retrying
            if attempt < 2:
                say("  transport failure, spacing retry...")
        if verdict is None:
            verdict = ("pending", "")
        results.append({"code": code, "name": item["name"], "category": item["category"],
                        "country": item["country"], "verdict": verdict[0], "og_title": verdict[1],
                        "invite": item["invite"]})
        say(f"  => {verdict[0]}")
        json.dump(results, open(WAVE + "team32_ramadhan_recheck.json", "w"), indent=1, ensure_ascii=False)
    say("\nDONE ramadhan recheck")
    log.close()

if __name__ == "__main__":
    main()
