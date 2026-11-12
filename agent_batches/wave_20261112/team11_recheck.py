#!/usr/bin/env python3
"""TEAM11 wave_20261112 — slice 6 failed-listing retry.
Re-fetch the 241 no-code linkado.app listing pages from wave_20261111 team06,
extract any invite codes now visible, verify fresh codes, screen, bank candidates.
Pages still code-less stay as leads (with the button-href reason, e.g. Telegram link).
Checkpoints frequently; resumable via team11-stageA-checkpoint.json / progress JSONL.
"""
import json, re, os, sys, time, html, threading, unicodedata
from concurrent.futures import ThreadPoolExecutor
import requests

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
PREV = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
BUILD = "/home/hatch/workspace/whatsapp-groups-site"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{10,40})")
TITLE_RE = re.compile(r"<title>([^<]{3,200})</title>", re.I)
CAT_RE = re.compile(r"na categoria ([^.\"<]{2,60})", re.I)
DESC_RE = re.compile(r'property=\\"og:description\\",\\"content\\":\\"((?:[^\\"\\\\]|\\\\.)*)', re.I)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.S | re.I)
# green "Entrar no Grupo" anchor href
BTN_RE = re.compile(r'<a[^>]*href="([^"]+)"[^>]*bg-green-600[^>]*>.*?Entrar no Grupo', re.S | re.I)
BTN_RE2 = re.compile(r'href=\\"([^\\"]+)\\"[^}]{0,400}?Entrar no Grupo', re.S)
OG_RE = re.compile(r'<meta\s+property="og:title"\s+content="([^"]*)"', re.I)
OG_RE2 = re.compile(r'<meta\s+content="([^"]*)"\s+property="og:title"', re.I)
OGD_RE = re.compile(r'<meta\s+property="og:description"\s+content="([^"]*)"', re.I)

sys.path.insert(0, PREV)
from team06_stage2 import is_scam_or_porn, classify, clean_name  # reuse screening + classify

def fetch(url, session):
    for attempt in range(2):
        try:
            r = session.get(url, timeout=30)
            if r.status_code == 200 and len(r.text) > 500:
                return r.text
            time.sleep(1.0)
        except Exception:
            time.sleep(1.0)
    return None

def parse(html_text, url):
    codes = sorted(set(CODE_RE.findall(html_text)))
    title = ""
    m = TITLE_RE.search(html_text)
    if m:
        title = m.group(1).strip()
    cat = ""
    m = CAT_RE.search(html_text)
    if m:
        cat = m.group(1).strip()
    desc = ""
    m = DESC_RE.search(html_text)
    if m:
        desc = m.group(1).replace('\\"', '"').strip()
    btn = ""
    m = BTN_RE.search(html_text)
    if m:
        btn = html.unescape(m.group(1))
    else:
        m = BTN_RE2.search(html_text)
        if m:
            btn = html.unescape(m.group(1)).replace("\\/", "/")
    return {"codes": codes, "title": title, "cat": cat, "desc": desc, "btn": btn}

def verify(code, session):
    """Returns (status, og_title). live|dead|transport."""
    url = f"https://chat.whatsapp.com/{code}"
    for attempt in range(2):
        try:
            r = session.get(url, timeout=60)
            if r.status_code != 200:
                if attempt == 0:
                    time.sleep(5.0); continue
                return ("dead", "")
            m = OG_RE.search(r.text) or OG_RE2.search(r.text)
            title = (m.group(1).strip() if m else "")
            if title:
                return ("live", title)
            if attempt == 0:
                time.sleep(5.0); continue
            return ("dead", "")
        except Exception:
            if attempt == 0:
                time.sleep(5.0); continue
            return ("transport", "")
    return ("dead", "")

def main():
    leads = json.load(open(os.path.join(PREV, "team06-leads-slice6-leads.json")))
    prev_ckpt = json.load(open(os.path.join(PREV, "team06-stage1-checkpoint.json")))
    existing = set(json.load(open(os.path.join(BUILD, ".existing_codes.json"))))
    # codes already banked by team06 yesterday (avoid cross-wave dupes)
    t06_verified = json.load(open(os.path.join(PREV, "team06-leads-slice6.json")))
    t06_codes = {e["invite"].rsplit("/", 1)[-1] for e in t06_verified}
    groups = json.load(open(os.path.join(BUILD, "groups.json")))
    live_code = groups[0]["invite"].rsplit("/", 1)[-1]

    ckpt_path = os.path.join(WAVE, "team11-stageA-checkpoint.json")
    prog_path = os.path.join(WAVE, "team11-progress.jsonl")
    done = {}
    if os.path.exists(ckpt_path):
        done = json.load(open(ckpt_path))
        print(f"resuming stage A: {len(done)} pages already fetched", flush=True)

    session = requests.Session(); session.headers.update(UA)
    lock = threading.Lock()
    counter = [0]
    results = dict(done)

    def work(url):
        if url in results:
            return
        h = fetch(url, session)
        time.sleep(0.5)
        with lock:
            counter[0] += 1
            n = counter[0]
            if h is None:
                results[url] = {"fetch": "failed"}
            else:
                results[url] = parse(h, url)
            with open(prog_path, "a") as f:
                f.write(json.dumps({"url": url, "rec": results[url]}, ensure_ascii=False) + "\n")
            if n % 50 == 0:
                json.dump(results, open(ckpt_path, "w"), ensure_ascii=False)
                print(f"stageA {n}/{len(leads)} fetched", flush=True)

    with ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(work, leads))
    json.dump(results, open(ckpt_path, "w"), ensure_ascii=False)
    fetched_ok = sum(1 for v in results.values() if v.get("fetch") != "failed")
    with_code = {u: v for u, v in results.items() if v.get("codes")}
    print(f"STAGE A DONE fetched_ok={fetched_ok} fetch_failed={len(leads)-fetched_ok} pages_with_codes={len(with_code)}", flush=True)
    for u, v in sorted(with_code.items()):
        print("  CODE PAGE:", u, v["codes"], flush=True)

    # ---- controls ----
    vsession = requests.Session(); vsession.headers.update(UA)
    print("CONTROL live:", verify(live_code, vsession), flush=True)
    print("CONTROL fabricated:", verify("ZZZZZZZZZZZZZZZZZZZZ", vsession), flush=True)

    # ---- collect fresh codes ----
    by_code = {}
    for url, rec in results.items():
        if not rec.get("codes"):
            continue
        base = prev_ckpt.get(url) or {}
        for c in rec["codes"]:
            by_code.setdefault(c, {"title": rec.get("title") or base.get("title", ""),
                                   "cat_pt": rec.get("cat") or base.get("cat", ""),
                                   "desc": rec.get("desc") or base.get("desc", ""),
                                   "source": url})
    print(f"unique codes found: {len(by_code)}", flush=True)
    dup_existing = [c for c in by_code if c in existing]
    dup_t06 = [c for c in by_code if c in t06_codes]
    new_codes = [c for c in by_code if c not in existing and c not in t06_codes]
    print(f"dup vs existing: {len(dup_existing)}; dup vs team06 verified: {len(dup_t06)}; new to verify: {len(new_codes)}", flush=True)

    vckpt_path = os.path.join(WAVE, "team11-stageB-checkpoint.json")
    vresults = {}
    if os.path.exists(vckpt_path):
        vresults = json.load(open(vckpt_path))
        print(f"resuming stage B: {len(vresults)} verifications done", flush=True)
    vlock = threading.Lock()
    vcounter = [0]

    def vwork(code):
        if code in vresults:
            return
        status, og = verify(code, vsession)
        time.sleep(0.55)
        with vlock:
            vresults[code] = {"status": status, "og": og}
            vcounter[0] += 1
            n = vcounter[0]
            if n % 25 == 0:
                json.dump(vresults, open(vckpt_path, "w"), ensure_ascii=False)
                print(f"stageB {n}/{len(new_codes)} verified", flush=True)

    with ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(vwork, new_codes))
    json.dump(vresults, open(vckpt_path, "w"), ensure_ascii=False)

    # ---- build outputs ----
    verified, pending, exclusions = [], [], []
    dead = []
    for code, rec in by_code.items():
        if code in existing or code in t06_codes:
            continue
        r = vresults.get(code)
        if r is None:
            continue
        st = r["status"]
        name = html.unescape(clean_name(rec["title"])) or (html.unescape(r["og"]) or "WhatsApp Group")
        desc_raw = html.unescape((rec["desc"] or "").strip())
        # strip "Grupo de WhatsApp <name>, na categoria <cat>. " prefix if present
        desc_raw = re.sub(r"^grupo de whatsapp .{3,150}?,\s*na categoria [^.]{2,40}\.\s*", "", desc_raw, flags=re.I)
        cat = classify(rec["cat_pt"], name)
        if st == "live":
            reason = is_scam_or_porn(name + " " + r["og"] + " " + desc_raw)
            if reason:
                exclusions.append({"code": code, "reason": reason, "source": rec["source"]})
                continue
            desc = f"Join {name}, {desc_raw}"[:300] if desc_raw else f"Join {name} on WhatsApp."
            verified.append({"name": name, "category": cat, "country": "",
                             "description": desc, "invite": f"https://chat.whatsapp.com/{code}"})
        elif st == "transport":
            pending.append({"name": name, "category": cat, "country": "",
                            "description": (f"Join {name}, {desc_raw}"[:300] if desc_raw else f"Join {name} on WhatsApp."),
                            "invite": f"https://chat.whatsapp.com/{code}",
                            "reason": "transport failure during verification"})
        else:
            dead.append(code)

    # leads: pages still failing or still code-less (do not guess codes)
    still_leads = []
    lead_reasons = {}
    for url in leads:
        rec = results.get(url) or {}
        if rec.get("fetch") == "failed" or not rec.get("codes"):
            still_leads.append(url)
            if rec.get("fetch") == "failed":
                lead_reasons[url] = "fetch failed on retry"
            else:
                btn = rec.get("btn", "")
                if btn.startswith("https://t.me/") or btn.startswith("http://t.me/"):
                    lead_reasons[url] = f"no WhatsApp invite; join button points to Telegram ({btn})"
                elif btn:
                    lead_reasons[url] = f"no WhatsApp invite; join button points elsewhere ({btn[:120]})"
                else:
                    lead_reasons[url] = "no WhatsApp invite visible on page"

    json.dump(verified, open(os.path.join(WAVE, "team11-leads-slice6-candidates.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(pending, open(os.path.join(WAVE, "team11-leads-slice6-pending.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(still_leads, open(os.path.join(WAVE, "team11-leads-slice6-leads.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(lead_reasons, open(os.path.join(WAVE, "team11-leads-slice6-lead-reasons.json"), "w"), ensure_ascii=False, indent=1)

    summary = {
        "team": "team11",
        "slice": "leads_slice6",
        "task": "failed-listing retry of wave_20261111 team06 slice 6",
        "sources": ["linkado.app listing pages (241 failed/no-code pages from team06)"],
        "pages_retried": len(leads),
        "pages_fetch_ok": fetched_ok,
        "pages_fetch_failed": len(leads) - fetched_ok,
        "pages_with_codes_now": len(with_code),
        "codes_found": len(by_code),
        "dup_vs_existing": len(dup_existing),
        "dup_vs_team06_verified": len(dup_t06),
        "codes_verified": len(new_codes),
        "verified": len(verified),
        "pending": len(pending),
        "dead": len(dead),
        "leads": len(still_leads),
        "exclusions": exclusions,
        "lead_reasons_sample": {u: lead_reasons[u] for u in still_leads[:10]},
        "team06_pending_recheck": "team06-leads-slice6-pending.json was empty ([]); nothing to re-check",
        "resume": "complete: all 241 pages re-fetched; stageA checkpoint team11-stageA-checkpoint.json; stageB checkpoint team11-stageB-checkpoint.json; still-code-less pages in team11-leads-slice6-leads.json with reasons in team11-leads-slice6-lead-reasons.json",
        "notes": ("Retry of the 241 linkado.app pages that had no invite code on 2026-11-11. "
                  "Most still carry no WhatsApp invite: the green 'Entrar no Grupo' button links to a Telegram "
                  "channel (t.me/...) instead of chat.whatsapp.com, i.e. these listings are Telegram groups "
                  "mislabeled as WhatsApp groups, or the owner never supplied a WhatsApp invite. No codes guessed."),
    }
    json.dump(summary, open(os.path.join(WAVE, "team11-leads-slice6-summary.json"), "w"), ensure_ascii=False, indent=2)
    print(f"FINAL verified={len(verified)} pending={len(pending)} dead={len(dead)} leads={len(still_leads)} exclusions={len(exclusions)}", flush=True)

if __name__ == "__main__":
    main()
