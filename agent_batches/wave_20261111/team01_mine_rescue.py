#!/usr/bin/env python3
"""TEAM 01 wave 20261111 — leads slice 1 miner + slow verifier.
Modes:
  mine   : fetch listing pages, extract candidates (direct codes, JSON-LD,
           groupizo verify-pages, groupsinvite slugs, linkado grupo ids)
  deep   : resolve groupsinvite slugs -> rules page (exact code+name);
           resolve linkado grupo ids -> grupo page (exact code+name)
  verify : slow-verify candidates (max 6 workers, >=0.5s delay), bank verified
All state lives in the wave dir. Never touches groups.json / generate.py.
"""
import json, re, html, time, sys, os, random, threading
from urllib.parse import urlparse, unquote, urljoin
import requests
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
LEADS_FILE = os.path.join(WAVE, "leads_slice1.json")
EXISTING_FILE = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"
CAND_FILE = os.path.join(WAVE, "team01-rescue-candidates.json")
PROG_FILE = os.path.join(WAVE, "team01-rescue-progress.json")
OUT_VER = os.path.join(WAVE, "team01-leads-slice1.json")
OUT_PEND = os.path.join(WAVE, "team01-leads-slice1-pending.json")
OUT_LEADS = os.path.join(WAVE, "team01-leads-slice1-leads.json")
OUT_SUM = os.path.join(WAVE, "team01-leads-slice1-summary.json")

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
CANON = ["Education","Jobs","Entertainment","Islamic","News","Sports","Technology","Health",
         "Business","Gaming","Friendship","Community & Social","Online Earning","Crypto",
         "Cooking","Poetry","Travel","Scholarship","Freelance","Real Estate","Buy Sell",
         "Finance","Funny"]

CAT_KW = [
    ("Islamic", ["islamic","quran","muslim","ramadan","madani","dawateislami","naat","hadees","hadith","tilawat"]),
    ("Scholarship", ["scholarship"]),
    ("Jobs", ["job","jobs","placement","career","govt-exam","govt exam","recruitment","rozgar","naukri","employment"]),
    ("Sports", ["cricket","football","psl","ipl","sports","hockey","kabaddi","wrestling"]),
    ("Crypto", ["crypto","bitcoin","binance","forex","trading"]),
    ("Online Earning", ["online earning","earn money","make money","earning","passive income"]),
    ("Education", ["education","study","stud","school","college","university","exam","admission","english learn","ielts","css","pms","nursing","medical stud","academy","coaching","homework","notes","mcqs"]),
    ("News", ["news","breaking","headlines","journalism"]),
    ("Technology", ["technology","tech","artificial intelligence","android","software","programming","coding","computer","photo editing","video editing"]),
    ("Health", ["health","fitness","gym","weight loss","doctor","yoga","medical"]),
    ("Business", ["business","startup","entrepreneur","marketing","digital marketing","ecommerce","dropship"]),
    ("Gaming", ["gaming","game","pubg","free fire","ludo","8ball","8 ball","call of duty","gta","minecraft","fortnite","fifa"]),
    ("Friendship", ["friendship","friend","amizade","amigos","dosti","girls","boys","chat group","make friend"]),
    ("Entertainment", ["movie","movies","music","song","drama","funny videos","entertainment","bollywood","hollywood","web series","netflix","tiktok","reels","status video"]),
    ("Cooking", ["cooking","recipe","food","chef","kitchen"]),
    ("Poetry", ["poetry","shayari","shayri","ghazal","urdu poetry","sad poetry"]),
    ("Travel", ["travel","tour","tourism","trip","visa","immigration"]),
    ("Freelance", ["freelance","freelancing","fiverr","upwork"]),
    ("Real Estate", ["real estate","property","plot","house sale","flat"]),
    ("Buy Sell", ["buy sell","buy-sell","buy & sell","shopping","sell purchase","olx","marketplace"]),
    ("Finance", ["finance","loan","bank","investment","insurance","stock"]),
    ("Funny", ["funny","meme","jokes","comedy","humor","humour"]),
]
COUNTRY_KW = {"pakistan":"PK","india":"IN","indian":"IN","bangladesh":"BD","nepal":"NP",
    "sri lanka":"LK","usa":"US","america":"US","united states":"US","uk":"GB","england":"GB",
    "london":"GB","canada":"CA","australia":"AU","indonesia":"ID","malaysia":"MY",
    "nigeria":"NG","kenya":"KE","uganda":"UG","ghana":"GH","tanzania":"TZ","zimbabwe":"ZW",
    "uae":"AE","dubai":"AE","saudi":"SA","qatar":"QA","kuwait":"KW","oman":"OM",
    "turkey":"TR","turkiye":"TR","brazil":"BR","brasil":"BR","portugal":"PT","spain":"ES",
    "france":"FR","germany":"DE","italy":"IT","netherlands":"NL","egypt":"EG","morocco":"MA",
    "south africa":"ZA","philippines":"PH","thailand":"TH","vietnam":"VN","myanmar":"MM",
    "afghanistan":"AF","iran":"IR","iraq":"IQ","islamabad":"PK","lahore":"PK","karachi":"PK",
    "punjab":"PK","sindh":"PK","tamil":"IN","kerala":"IN","gujarat":"IN","delhi":"IN","mumbai":"IN"}

SCAM_TOKENS = ["b-love","blove","b love","forsage","sheyi","holiverse","meta whale","metawhale",
    "1win","91club","91 club","aviator predictor","double money","investment plan"]
PORN_TOKENS = ["xxx","porn","sex video","sexy video","hot video","nude","desi sex","adult video",
    "blue film","porn video","sex group","xxx video","hot girls video","sex chat"]
NEG_RE = re.compile(r"[^.!?\n]*(?:no\s+(?:porn|xxx|sex|adult|nude)|porn\s+not\s+allowed|no\s+adult\s+content|strictly\s+no\s+porn)[^.!?\n]*[.!?]?", re.I)

def strip_neg(text):
    return NEG_RE.sub(" ", text or "")

def screen_text(text):
    """Return exclusion reason or None. Screens name AND og:title text."""
    t = (text or "").lower()
    t2 = strip_neg(t)
    for tok in SCAM_TOKENS:
        if tok in t2:
            return f"scam:{tok}"
    for tok in PORN_TOKENS:
        if tok in t2:
            return f"adult:{tok}"
    return None

def clean_name(n):
    if not n: return ""
    n = html.unescape(n)
    n = re.sub(r"<[^>]+>", "", n)
    n = re.sub(r"\s+", " ", n).strip(" -|—–·•\t:\"'“”")
    # drop site suffixes
    n = re.sub(r"\s*\|\s*(GroupsInvite|Groupizo|Linkado|GroupsNest|WhatsApp Groups?|WhatsApp Group Links?|Group Links?)$", "", n, flags=re.I)
    n = re.sub(r"\s+(WhatsApp Group|WhatsApp Groups|Group Link|Group Links|Invite Link|Join.*)$", "", n, flags=re.I) if len(n) > 25 else n
    n = re.sub(r"^Join\s+", "", n, flags=re.I)
    n = n.strip(" -|—–·•\t:\"'“”")
    if len(n) > 120: n = n[:120].rsplit(" ", 1)[0]
    return n

def infer_category(text):
    t = " " + re.sub(r"[^a-z0-9 ]", " ", (text or "").lower()) + " "
    for cat, kws in CAT_KW:
        for k in kws:
            kk = " " + re.sub(r"[^a-z0-9 ]", " ", k) + " "
            if kk in t:
                return cat
    return "Community & Social"

def infer_country(text):
    t = (" " + (text or "").lower() + " ")
    for k, c in COUNTRY_KW.items():
        if k in t:
            return c
    return ""

def make_desc(name, cat, country):
    base = f"Join {name}, an active WhatsApp group for {cat.lower()}."
    return base + " Connect with members, share updates and stay in touch."

def load_json(path, default):
    try:
        with open(path) as f: return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as f: json.dump(data, f, ensure_ascii=False)
    os.replace(tmp, path)

def fetch(url, timeout=30):
    r = requests.get(url, headers=UA, timeout=timeout)
    r.raise_for_status()
    return r.text

def page_title(t):
    m = re.search(r"<title>(.*?)</title>", t, re.S | re.I)
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""

def og_title_of_chat(code):
    """Live check per rules: 200 + non-empty og:title. Returns (status, ogtitle, err)."""
    url = f"https://chat.whatsapp.com/{code}"
    try:
        r = requests.get(url, headers=UA, timeout=30)
        if r.status_code != 200:
            return (r.status_code, "", f"http_{r.status_code}")
        m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', r.text)
        if not m:
            m = re.search(r"<meta\s+property='og:title'\s+content='([^']*)'", r.text)
        return (200, html.unescape(m.group(1)).strip() if m else "", "")
    except Exception as e:
        return (0, "", f"transport:{type(e).__name__}")

# ---------------- extraction ----------------
def extract_jsonld(t):
    """ItemList name/url pairs."""
    out = []
    for m in re.finditer(r'"name"\s*:\s*"([^"]+)"\s*,\s*"url"\s*:\s*"(https://chat\.whatsapp\.com/([A-Za-z0-9]+))"', t):
        out.append((m.group(3), clean_name(m.group(1))))
    for m in re.finditer(r'"url"\s*:\s*"(https://chat\.whatsapp\.com/([A-Za-z0-9]+))"\s*,\s*"name"\s*:\s*"([^"]+)"', t):
        out.append((m.group(2), clean_name(m.group(3))))
    return out

def extract_anchors(t):
    out = []
    for m in re.finditer(r'<a[^>]+href="(https://chat\.whatsapp\.com/([A-Za-z0-9]+))"[^>]*>(.*?)</a>', t, re.S | re.I):
        txt = clean_name(re.sub(r"<[^>]+>", " ", m.group(3)))
        if txt and txt.lower() not in ("join", "join group", "join now", "click here"):
            out.append((m.group(2), txt))
    return out

def context_name(t, pos):
    """Best-effort name from text preceding a code occurrence (table cells etc.)."""
    seg = t[max(0, pos - 1200):pos]
    seg = re.sub(r"<script.*?</script>", " ", seg, flags=re.S | re.I)
    seg = re.sub(r"<style.*?</style>", " ", seg, flags=re.S | re.I)
    seg = re.sub(r"<[^>]+>", "\n", seg)
    seg = html.unescape(seg)
    lines = [re.sub(r"\s+", " ", ln).strip(" -|•·\t") for ln in seg.split("\n")]
    lines = [ln for ln in lines if 3 <= len(ln) <= 90]
    bad = ("join", "whatsapp group links", "whatsapp groups", "click", "home", "menu",
           "privacy", "terms", "disclaimer", "contact", "share", "category", "categories",
           "search", "advertisement", "copyright")
    for ln in reversed(lines):
        ll = ln.lower()
        if any(b in ll for b in bad): continue
        if re.fullmatch(r"[0-9+\- ]{8,}", ln): continue
        if len(ln.split()) > 8: continue  # description sentences, not names
        if ll.endswith("!") or ll.startswith(("dive into", "discover", "join our", "welcome to")): continue
        return clean_name(ln)
    return ""

def extract_generic(t, page_url, page_title_text):
    """Direct chat codes + names via JSON-LD, anchors, context."""
    cands = {}
    for code, name in extract_jsonld(t) + extract_anchors(t):
        if name: cands.setdefault(code, name)
    for m in re.finditer(r"https://chat\.whatsapp\.com/([A-Za-z0-9]{10,30})", t):
        code = m.group(1)
        if code in cands: continue
        name = context_name(t, m.start())
        if name: cands[code] = name
    return cands

def parse_listing(url, t):
    """Returns (candidates dict code->name, sublinks dict kind->[urls], page_title)."""
    title = page_title(t)
    host = urlparse(url).netloc
    cands = extract_generic(t, url, title)
    subs = {"groupsinvite_slug": [], "linkado_grupo": [], "groupizo_verify": []}
    if "groupsinvite.link" in host:
        slugs = re.findall(r"/group/link/([A-Za-z0-9]+)/", t)
        subs["groupsinvite_slug"] = sorted(set(slugs))
        # also rules-page slugs already present
        slugs2 = re.findall(r"/group/rules/([A-Za-z0-9]+)/", t)
        subs["groupsinvite_slug"] = sorted(set(subs["groupsinvite_slug"]) | set(slugs2))
    if "linkado.app" in host:
        ids = re.findall(r"/grupo/([0-9a-f]{20,})", t)
        subs["linkado_grupo"] = sorted(set(ids))
    if "groupizo.com" in host:
        # single-group page: h1 name + verify link
        m = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S)
        name = clean_name(m.group(1)) if m else ""
        vm = re.search(r"window\.location\.href='(/verify/[^']+)'", t)
        if name and vm:
            subs["groupizo_verify"] = [(name, "https://groupizo.com" + vm.group(1), title)]
    return cands, subs, title

# ---------------- modes ----------------
def cmd_mine(start=0, end=None):
    leads = load_json(LEADS_FILE, [])
    if end is None: end = len(leads)
    prog = load_json(PROG_FILE, {"mined_idx": [], "failed": [], "sub_groupsinvite": [], "sub_linkado": [], "sub_groupizo": []})
    done = set(prog.get("mined_idx", []))
    cands = load_json(CAND_FILE, {})
    existing = set(load_json(EXISTING_FILE, []))
    # skip junk: whatsapp share-api links, adult listing, non-http
    junk = []
    todo = [i for i in range(start, end) if i not in done]
    print(f"mine: {len(todo)} pages to fetch (total {len(leads)})", flush=True)
    def work(i):
        url = leads[i]
        host = urlparse(url).netloc
        if "api.whatsapp.com" in url or url.startswith("https://adult.") or "adult.grouplinks" in url:
            return (i, "junk", None)
        try:
            t = fetch(url)
        except Exception as e:
            return (i, "failed", str(type(e).__name__))
        try:
            c, subs, title = parse_listing(url, t)
        except Exception as e:
            return (i, "failed", f"parse:{type(e).__name__}")
        ctx = f"{url} {title}"
        recs = {}
        for code, name in c.items():
            if code in existing or code in cands: continue
            nm = clean_name(name) or clean_name(title)
            if not nm: continue
            cat = infer_category(ctx + " " + nm)
            recs[code] = {"name": nm, "category": cat, "country": infer_country(ctx + " " + nm),
                          "description": make_desc(nm, cat, infer_country(ctx + " " + nm)),
                          "invite": f"https://chat.whatsapp.com/{code}", "source": url}
        return (i, "ok", {"recs": recs, "subs": subs, "title": title})
    with ThreadPoolExecutor(max_workers=3) as ex:
        for n, (i, status, payload) in enumerate(ex.map(work, todo)):
            if status == "ok":
                cands.update(payload["recs"])
                prog["sub_groupsinvite"].extend(payload["subs"]["groupsinvite_slug"])
                prog["sub_linkado"].extend(payload["subs"]["linkado_grupo"])
                for name, vurl, ttl in payload["subs"]["groupizo_verify"]:
                    prog["sub_groupizo"].append({"name": name, "verify": vurl, "source": leads[i], "title": ttl})
            elif status == "failed":
                prog["failed"].append({"idx": i, "url": leads[i], "reason": payload})
            elif status == "junk":
                junk.append(leads[i])
            done.add(i)
            if (n + 1) % 100 == 0:
                prog["mined_idx"] = sorted(done)
                prog["sub_groupsinvite"] = sorted(set(prog["sub_groupsinvite"]))
                prog["sub_linkado"] = sorted(set(prog["sub_linkado"]))
                save_json(CAND_FILE, cands); save_json(PROG_FILE, prog)
                print(f"  mined {n+1}/{len(todo)} pages, candidates={len(cands)}, "
                      f"gi_slugs={len(prog['sub_groupsinvite'])}, linkado={len(prog['sub_linkado'])}, "
                      f"groupizo={len(prog['sub_groupizo'])}, failed={len(prog['failed'])}", flush=True)
    prog["mined_idx"] = sorted(done)
    prog["sub_groupsinvite"] = sorted(set(prog["sub_groupsinvite"]))
    prog["sub_linkado"] = sorted(set(prog["sub_linkado"]))
    prog["junk"] = junk
    save_json(CAND_FILE, cands); save_json(PROG_FILE, prog)
    print(f"MINE DONE: candidates={len(cands)} gi_slugs={len(prog['sub_groupsinvite'])} "
          f"linkado={len(prog['sub_linkado'])} groupizo={len(prog['sub_groupizo'])} failed={len(prog['failed'])} junk={len(junk)}", flush=True)

def cmd_deep(kind, cap):
    """Resolve sublinks into candidates. kind=gi|linkado|groupizo"""
    prog = load_json(PROG_FILE, {})
    cands = load_json(CAND_FILE, {})
    existing = set(load_json(EXISTING_FILE, []))
    done_key = f"deep_{kind}_done"
    done = set(prog.get(done_key, []))
    if kind == "gi":
        items = [s for s in prog.get("sub_groupsinvite", []) if s not in done][:cap]
        def work(slug):
            try:
                t = fetch(f"https://groupsinvite.link/group/rules/{slug}/")
            except Exception as e:
                return (slug, None)
            m = re.search(r"https://chat\.whatsapp\.com/([A-Za-z0-9]{10,30})", t)
            if not m: return (slug, None)
            code = m.group(1)
            title = page_title(t)
            name = clean_name(re.sub(r"\s+WhatsApp Group Rules.*$", "", title, flags=re.I))
            return (slug, (code, name))
        with ThreadPoolExecutor(max_workers=6) as ex:
            for slug, res in ex.map(work, items):
                done.add(slug)
                if res:
                    code, name = res
                    if code in existing or code in cands or not name: continue
                    cat = infer_category(name)
                    cc = infer_country(name)
                    cands[code] = {"name": name, "category": cat, "country": cc,
                                   "description": make_desc(name, cat, cc),
                                   "invite": f"https://chat.whatsapp.com/{code}",
                                   "source": f"https://groupsinvite.link/group/rules/{slug}/"}
        prog[done_key] = sorted(done)
    elif kind == "linkado":
        items = [g for g in prog.get("sub_linkado", []) if g not in done][:cap]
        def work(gid):
            try:
                t = fetch(f"https://linkado.app/grupo/{gid}")
            except Exception:
                return (gid, None)
            m = re.search(r"https://chat\.whatsapp\.com/([A-Za-z0-9]{10,30})", t)
            if not m: return (gid, None)
            code = m.group(1)
            title = page_title(t)
            name = clean_name(re.sub(r"\s*-\s*[A-Za-zÀ-ÿ ]+$", "", title))
            return (gid, (code, name))
        with ThreadPoolExecutor(max_workers=6) as ex:
            for gid, res in ex.map(work, items):
                done.add(gid)
                if res:
                    code, name = res
                    if code in existing or code in cands or not name: continue
                    cat = infer_category(name + " linkado")
                    cc = infer_country(name)
                    cands[code] = {"name": name, "category": cat, "country": cc,
                                   "description": make_desc(name, cat, cc),
                                   "invite": f"https://chat.whatsapp.com/{code}",
                                   "source": f"https://linkado.app/grupo/{gid}"}
        prog[done_key] = sorted(done)
    elif kind == "groupizo":
        items = [x for x in prog.get("sub_groupizo", []) if x["verify"] not in done][:cap]
        def work(it):
            try:
                t = fetch(it["verify"])
            except Exception:
                return (it, None)
            m = re.search(r"https://chat\.whatsapp\.com/([A-Za-z0-9]{10,30})", t)
            if not m: return (it, None)
            return (it, m.group(1))
        with ThreadPoolExecutor(max_workers=6) as ex:
            for it, code in ex.map(work, items):
                done.add(it["verify"])
                if code:
                    if code in existing or code in cands: continue
                    name = clean_name(it["name"])
                    cat = infer_category(it["title"] + " " + name)
                    cc = infer_country(it["title"] + " " + name)
                    cands[code] = {"name": name, "category": cat, "country": cc,
                                   "description": make_desc(name, cat, cc),
                                   "invite": f"https://chat.whatsapp.com/{code}",
                                   "source": it["source"]}
        prog[done_key] = sorted(done)
    save_json(CAND_FILE, cands); save_json(PROG_FILE, prog)
    print(f"DEEP {kind} DONE: candidates={len(cands)}", flush=True)

def cmd_verify():
    cands = load_json(CAND_FILE, {})
    existing = set(load_json(EXISTING_FILE, []))
    verified = load_json(OUT_VER, [])
    pending_old = load_json(OUT_PEND, [])
    pending = []
    done_codes = {v["invite"].split("/")[-1] for v in verified}
    # pending codes are RETRIED (transport failures only), not skipped; dedupe by code
    by_code = {}
    for code, rec in cands.items():
        if code not in existing and code not in done_codes:
            by_code[code] = rec
    for p in pending_old:
        code = p["invite"].split("/")[-1]
        if code not in done_codes and code not in by_code:
            by_code[code] = {"name": p["name"], "category": p["category"],
                             "country": p["country"], "description": p["description"],
                             "invite": p["invite"], "source": ""}
    items = list(by_code.items())
    # pre-screen banked names
    exclusions = []
    todo = []
    for code, rec in items:
        r = screen_text(rec["name"])
        if r:
            exclusions.append({"code": code, "reason": r + " (name)"})
        else:
            todo.append((code, rec))
    print(f"verify: {len(todo)} to check, {len(exclusions)} pre-excluded, {len(done_codes)} already done", flush=True)
    lock = threading.Lock()
    dead = [0]
    def work(item):
        code, rec = item
        time.sleep(1.0)  # SEQUENTIAL: parallel chat.whatsapp.com fetches time out from this VM; 1 worker only
        status, og, err = og_title_of_chat(code)
        if status == 200 and og:
            r = screen_text(og)
            if r:
                return ("excluded", code, {"code": code, "reason": r + " (og:title)"})
            if screen_text(rec["name"]):
                return ("excluded", code, {"code": code, "reason": "scam/adult (name)"})
            out = {"name": clean_name(rec["name"]) or og, "category": rec["category"],
                   "country": rec["country"], "description": rec["description"],
                   "invite": f"https://chat.whatsapp.com/{code}"}
            return ("verified", code, out)
        if status == 200 and not og:
            time.sleep(2)
            status2, og2, err2 = og_title_of_chat(code)
            if status2 == 200 and og2:
                if screen_text(og2):
                    return ("excluded", code, {"code": code, "reason": "adult/scam (og:title retry)"})
                return ("verified", code, {"name": clean_name(rec["name"]) or og2, "category": rec["category"],
                        "country": rec["country"], "description": rec["description"],
                        "invite": f"https://chat.whatsapp.com/{code}"})
            if status2 == 200 and not og2:
                return ("dead", code, None)
            return ("pending", code, {"name": rec["name"], "category": rec["category"], "country": rec["country"],
                    "description": rec["description"], "invite": f"https://chat.whatsapp.com/{code}",
                    "reason": err2 or f"http_{status2}"})
        if status == 0 or status in (403, 429, 500, 502, 503):
            return ("pending", code, {"name": rec["name"], "category": rec["category"], "country": rec["country"],
                    "description": rec["description"], "invite": f"https://chat.whatsapp.com/{code}",
                    "reason": err or f"http_{status}"})
        return ("dead", code, None)
    n = 0
    with ThreadPoolExecutor(max_workers=1) as ex:
        for kind, code, payload in ex.map(work, todo):
            with lock:
                if kind == "verified": verified.append(payload)
                elif kind == "pending": pending.append(payload)
                elif kind == "excluded": exclusions.append(payload)
                elif kind == "dead": dead[0] += 1
                n += 1
                if n % 25 == 0:
                    save_json(OUT_VER, verified); save_json(OUT_PEND, pending)
                    print(f"  verified {n}/{len(todo)}: live={len(verified)} pending={len(pending)} dead={dead[0]} excl={len(exclusions)}", flush=True)
    save_json(OUT_VER, verified); save_json(OUT_PEND, pending)
    # stash counts for summary
    prog = load_json(PROG_FILE, {})
    prog["verify_dead"] = dead[0]
    prog["verify_exclusions"] = exclusions
    save_json(PROG_FILE, prog)
    print(f"VERIFY DONE: live={len(verified)} pending={len(pending)} dead={dead[0]} excl={len(exclusions)}", flush=True)

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "mine":
        cmd_mine(int(sys.argv[2]) if len(sys.argv) > 2 else 0,
                 int(sys.argv[3]) if len(sys.argv) > 3 else None)
    elif mode == "deep":
        cmd_deep(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 100000)
    elif mode == "verify":
        cmd_verify()
    else:
        print("usage: mine [start] [end] | deep gi|linkado|groupizo [cap] | verify")
