#!/usr/bin/env python3
"""Team 34 (wave 20261104): re-verify Nov-3 ongrupos.com pending candidates (Brazil).

Stage 1 (--prep): offline dedupe + content filtering + description build.
Stage 2 (--verify): live og:title verification with keep-alive sessions.
Stage 3 (--finalize): assemble final output files.
"""
import json, re, os, sys, html, time, threading, random
from concurrent.futures import ThreadPoolExecutor
import requests

WDIR = os.path.dirname(os.path.abspath(__file__))
SCRATCH = "/tmp/t34_scratch"
os.makedirs(SCRATCH, exist_ok=True)
W3 = os.path.join(os.path.expanduser("~"), "workspace/whatsapp-groups-site/agent_batches/wave_20261103")

UNION = os.path.join(WDIR, "dedupe_union.json")
PEND_A = os.path.join(W3, "team39b-unverified-pending.json")  # newest first
PEND_B = os.path.join(W3, "team39R-unverified-pending.json")
WORK = os.path.join(SCRATCH, "team34_candidates_work.json")
CKPT = os.path.join(SCRATCH, "team34_verify_checkpoint.jsonl")
FINAL_V = os.path.join(SCRATCH, "team34-pending-retry.json")
FINAL_P = os.path.join(SCRATCH, "team34-unverified-pending.json")

CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})\b")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

PORN_RE = re.compile(r"(porn|pornhub|xxx|nude|sex\s*video|escort|call\s*girl|acompanhante|fuck|dick|pussy|boobs?|anal|bokep|"
                     r"buceta|xota|pelad[ao]s?\b|punheta|siririca|boquete|putaria|suruba|peitos|tes[ãa]o|"
                     r"(minha|sua)\s+rola|rola\s+(grossa|grande|dura|enorme)|"
                     r"garota\s+de\s+programa|conte[úu]do\s+adulto|sugar\s+baby|porn[ôo]|"
                     r"🥵|🍆|🍑|🔞|💦|👅|👄|💋)", re.I | re.U)
# NOTE (fixed Nov-4): bare rola\b REMOVED — false-positives on Portuguese "Pérola",
# "Corrola", and verb "rolar" (to happen, "aqui só rola um bate-papo"). Only
# clearly sexual rola-phrases (minha/sua rola, rola grossa/grande/...) are dropped.
MINORS_RE = re.compile(r"novinh[ao]s?", re.I)
SCAM_RE = re.compile(r"(paypal\s+receiver|money\s+loader|hyip|doubler|satta|matka|"
                     r"triplic?a.*dinheiro|dinheiro.*f[áa]cil.*garant)", re.I)
PHONE_RE = re.compile(r"\d{10,}")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")

DESC_TPL = {
 "Friendship": ["Join {n}, a Brazilian WhatsApp friendship group to meet new people, chat daily and make friends across Brazil.",
                "Meet people in {n}, a Brazilian WhatsApp friendship group for daily conversation and new connections."],
 "Girls": ["Join {n}, a Brazilian WhatsApp group for girls and women to chat, share daily life and make new friends.",
           "{n} is a Brazilian WhatsApp girls' group for friendly chat, daily topics and meeting new friends."],
 "Gaming": ["Join {n}, a Brazilian WhatsApp gaming group to talk about games, share tips and play together.",
            "{n} brings Brazilian gamers together on WhatsApp to discuss games, strategies and new releases."],
 "Funny": ["Join {n}, a Brazilian WhatsApp humor group sharing funny memes, jokes and viral clips every day.",
           "{n} is a Brazilian WhatsApp group full of memes, jokes and funny videos shared daily."],
 "Movies": ["Join {n}, a Brazilian WhatsApp group for movie fans to chat about films, series and cinema news.",
            "{n} connects Brazilian cinema lovers on WhatsApp to talk films, series and releases."],
 "Music": ["Join {n}, a Brazilian WhatsApp music group to share songs, playlists and talk about favorite artists.",
           "{n} is a Brazilian WhatsApp group where music fans share songs, playlists and artist news."],
 "Sports": ["Join {n}, a Brazilian WhatsApp sports group for fans to follow matches, scores and sports news.",
            "{n} is a Brazilian WhatsApp group for sports fans to discuss matches, teams and results."],
 "Business": ["Join {n}, a Brazilian WhatsApp business group for entrepreneurs to network and share opportunities.",
              "{n} connects Brazilian entrepreneurs on WhatsApp to network, share ideas and grow."],
 "Education": ["Join {n}, a Brazilian WhatsApp study group to share school materials, tips and learn together.",
               "{n} is a Brazilian WhatsApp education group for students to share notes and study help."],
 "Jobs": ["Join {n}, a Brazilian WhatsApp jobs group sharing job openings and work opportunities across Brazil.",
          "{n} shares Brazilian job vacancies and work opportunities on WhatsApp every day."],
 "Buy-Sell": ["Join {n}, a Brazilian WhatsApp buy-and-sell group to advertise products and find good deals.",
              "{n} is a Brazilian WhatsApp marketplace group for buying and selling across Brazil."],
 "Entertainment": ["Join {n}, a Brazilian WhatsApp entertainment group for fun chats, news and viral content.",
                   "{n} is a Brazilian WhatsApp group for entertainment, viral posts and friendly chat."],
 "Food": ["Join {n}, a Brazilian WhatsApp food group to share recipes, cooking tips and tasty ideas.",
          "{n} is a Brazilian WhatsApp group for food lovers to share recipes and cooking tips."],
 "Technology": ["Join {n}, a Brazilian WhatsApp tech group to talk about gadgets, apps and technology news.",
                "{n} connects Brazilian tech fans on WhatsApp to discuss apps, gadgets and news."],
 "Health": ["Join {n}, a Brazilian WhatsApp health group to share wellness tips and healthy living ideas.",
            "{n} is a Brazilian WhatsApp group focused on health, fitness and wellness tips."],
 "Regional": ["Join {n}, a Brazilian WhatsApp regional group connecting people from the same area.",
              "{n} brings together people from the same Brazilian region for local chat and news."],
 "Other": ["Join {n}, a Brazilian WhatsApp group to chat, share ideas and meet new people.",
           "{n} is a Brazilian WhatsApp community group for chat and sharing daily topics."],
}

def prep():
    union = set(json.load(open(UNION)))
    print("union codes:", len(union), flush=True)
    seen = set()
    out, stats = [], {"input": 0, "badlen": 0, "channel": 0, "dup_union": 0, "dup_batch": 0,
                      "porn": 0, "minors": 0, "scam": 0, "pii": 0, "empty_name": 0, "kept": 0}
    for path in (PEND_A, PEND_B):
        items = json.load(open(path))
        for it in items:
            stats["input"] += 1
            url = it.get("invite") or ""
            if "/invite/" in url:
                stats["channel"] += 1; continue
            m = CODE_RE.search(url)
            if not m:
                stats["badlen"] += 1; continue
            code = m.group(1)
            if not (20 <= len(code) <= 24):
                stats["badlen"] += 1; continue
            if code in union:
                stats["dup_union"] += 1; continue
            if code in seen:
                stats["dup_batch"] += 1; continue
            seen.add(code)
            name = (it.get("name") or "").strip()
            desc = (it.get("description") or "").strip()
            blob = (name + " " + desc)
            if PORN_RE.search(blob):
                stats["porn"] += 1; continue
            if MINORS_RE.search(blob):
                stats["minors"] += 1; continue
            if SCAM_RE.search(blob):
                stats["scam"] += 1; continue
            if not name or name.lower().startswith("http") or PHONE_RE.search(name) or EMAIL_RE.search(name):
                stats["pii"] += 1; continue
            cat = it.get("category") or "Other"
            if cat not in DESC_TPL: cat = "Other"
            tpls = DESC_TPL[cat]
            desc_new = tpls[hash(code) % len(tpls)].format(n=name)
            out.append({"name": name, "category": cat, "country": "BR",
                        "description": desc_new, "invite": f"https://chat.whatsapp.com/{code}",
                        "image": "", "_code": code, "_src": os.path.basename(path)})
            stats["kept"] += 1
    json.dump(out, open(WORK, "w"), ensure_ascii=False)
    print(json.dumps(stats, indent=1), flush=True)
    print("kept candidates:", len(out), "->", WORK, flush=True)

TITLE_RE = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]*content=["\']([^"\']*)', re.I | re.S)
TITLE_RE2 = re.compile(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]*property=["\']og:title["\']', re.I | re.S)

def og_title(page_text):
    for rx in (TITLE_RE, TITLE_RE2):
        m = rx.search(page_text)
        if m:
            return html.unescape(m.group(1)).strip()
    return ""

def verify():
    cands = json.load(open(WORK))
    done_codes = set()
    verified, pending = [], []
    if os.path.exists(CKPT):
        for line in open(CKPT):
            line = line.strip()
            if not line: continue
            rec = json.loads(line)
            done_codes.add(rec["code"])
            if rec["verdict"] == "live": verified.append(rec["item"])
            elif rec["verdict"] == "pending": pending.append(rec["item"])
            elif rec["verdict"] == "porn": pass
    todo = [c for c in cands if c["_code"] not in done_codes]
    print(f"candidates={len(cands)} done={len(done_codes)} todo={len(todo)}", flush=True)
    if not todo:
        return
    stop = threading.Event()
    lock = threading.Lock()
    n_live = n_dead = n_trans = n_429 = 0
    ckpt_f = open(CKPT, "a")

    def check(c):
        nonlocal n_live, n_dead, n_trans, n_429
        if stop.is_set():
            return None
        code = c["_code"]
        url = f"https://chat.whatsapp.com/{code}"
        sess = requests.Session()
        sess.headers.update({"User-Agent": UA})
        verdict = "transport"
        title = ""
        try:
            for attempt in range(2):
                try:
                    r = sess.get(url, timeout=(30, 60), allow_redirects=True)
                    if r.status_code == 429:
                        verdict = "ratelimited"; stop.set(); break
                    title = og_title(r.text)
                    verdict = "live" if title else "dead"
                    break
                except requests.exceptions.RequestException:
                    sess = requests.Session(); sess.headers.update({"User-Agent": UA})
                    if attempt == 1: verdict = "transport"
                    else: time.sleep(1)
        finally:
            sess.close()
        with lock:
            if verdict == "live":
                name = title or c["name"]
                if PORN_RE.search(name):
                    verdict = "porn"; n_live_ = None
                else:
                    item = {"name": name, "category": c["category"], "country": "BR",
                            "description": c["description"], "invite": url, "image": ""}
                    ckpt_f.write(json.dumps({"code": code, "verdict": "live", "item": item}) + "\n"); ckpt_f.flush()
                    verified.append(item); n_live += 1
                    return item
            if verdict == "dead":
                ckpt_f.write(json.dumps({"code": code, "verdict": "dead"}) + "\n"); ckpt_f.flush()
                n_dead += 1
            elif verdict == "ratelimited":
                item = dict(c); item.pop("_code", None); item.pop("_src", None); item["note"] = "rate-limited"
                ckpt_f.write(json.dumps({"code": code, "verdict": "pending", "item": item}) + "\n"); ckpt_f.flush()
                pending.append(item); n_429 += 1
            elif verdict == "porn":
                ckpt_f.write(json.dumps({"code": code, "verdict": "porn"}) + "\n"); ckpt_f.flush()
            else:
                item = dict(c); item.pop("_code", None); item.pop("_src", None); item["note"] = "transport failure"
                ckpt_f.write(json.dumps({"code": code, "verdict": "pending", "item": item}) + "\n"); ckpt_f.flush()
                pending.append(item); n_trans += 1
        return None

    workers = 16
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for i, c in enumerate(todo):
            ex.submit(check, c)
            if stop.is_set(): break
    ckpt_f.close()
    # bank never-attempted rest (429 stop) as pending
    if stop.is_set():
        attempted = set()
        for line in open(CKPT):
            attempted.add(json.loads(line)["code"])
        rest = [c for c in cands if c["_code"] not in attempted and c["_code"] not in done_codes]
        for c in rest:
            item = dict(c); item.pop("_code", None); item.pop("_src", None); item["note"] = "rate-limited"
            pending.append(item)
        print(f"429 stop: banked {len(rest)} unattempted as rate-limited", flush=True)
    print(f"live={len(verified)} pending={len(pending)} dead_so_far={n_dead} transport={n_trans}", flush=True)
    with open(FINAL_V, "w") as f: f.write(json.dumps(verified, ensure_ascii=False, indent=1))
    with open(FINAL_P, "w") as f: f.write(json.dumps(pending, ensure_ascii=False, indent=1))
    print("wrote", FINAL_V, len(verified), "items;", FINAL_P, len(pending), "items", flush=True)

def finalize():
    # finalize is embedded in verify(); kept for CLI compat
    print("finalize: outputs written by verify()", flush=True)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "--prep"
    if mode == "--prep": prep()
    elif mode == "--verify": verify()
    elif mode == "--finalize": finalize()
    else: sys.exit("usage: team34_prep_verify.py [--prep|--verify|--finalize]")
