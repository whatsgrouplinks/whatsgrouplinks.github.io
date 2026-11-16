#!/usr/bin/env python3
"""Wave 20261116 consolidation coordinator — PHASE 1: collect + classify.
Collects candidates from wave_20261115 team outputs + wave_20261112 stream items,
applies team-live verdicts, dedupes vs union, screens, and writes an
intermediate state for the verification phase. Does NOT touch groups.json,
.existing_codes.json, dedup_codes.pkl, groups/ or wgl-deploy/.
"""
import json, os, re, glob, pickle, sys
from collections import Counter, defaultdict

BASE = "/home/hatch/workspace/whatsapp-groups-site"
W15 = os.path.join(BASE, "agent_batches/wave_20261115")
W12 = os.path.join(BASE, "agent_batches/wave_20261112")
OUT = os.path.join(BASE, "agent_batches/wave_20261116")
os.makedirs(OUT, exist_ok=True)

GENERIC_TITLES = {"", "whatsapp group invite", "whatsapp", "join group on whatsapp",
                  "whatsapp group", "invite", "group invite"}
CONTROL_LIVE = "KrDwdK8EIkB6vgauHg5M7N"
CONTROL_FAB = "ZzZzZzZzZzZzZzZzZzZzZzZz"

def norm_code(code):
    if not code: return ""
    c = str(code).strip()
    c = re.sub(r'^https?://', '', c, flags=re.I)
    c = re.sub(r'^www\.', '', c, flags=re.I)
    c = re.sub(r'^chat\.whatsapp\.com/', '', c, flags=re.I)
    c = c.split('?')[0].split('#')[0].rstrip('/')
    return c.lower()

def code_from_invite(inv):
    if not inv: return ""
    m = re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_-]+)', str(inv))
    return m.group(1) if m else ""

def load_json_file(f):
    try:
        with open(f, encoding='utf-8') as fh:
            return json.load(fh)
    except Exception as e:
        return ("ERR", str(e))

# ---------- union ----------
union = set()
d = load_json_file(os.path.join(BASE, ".existing_codes.json"))
if isinstance(d, list):
    for c in d:
        union.add(norm_code(c))
print("union codes:", len(union), flush=True)

# ---------- team-live verdicts ----------
team_live = {}   # normcode -> title
team_dead = {}   # normcode -> err
team_pending = {}
verify_files = []
for pat in ["*verify*.json", "*verify*.jsonl", "*verified*.jsonl", "team16-reverify.json",
            "team15-pendingC-p1.jsonl", "team15-pendingC-p2.jsonl", "team06_verified_p161_260.tsv"]:
    verify_files += sorted(glob.glob(os.path.join(W15, pat)))
verify_files = sorted(set(verify_files))
print("verify files:", len(verify_files), flush=True)

def record_verdict(code, status, title, src):
    nc = norm_code(code)
    if not nc or nc in (norm_code(CONTROL_LIVE), norm_code(CONTROL_FAB)):
        return
    t = (title or "").strip()
    st = (status or "").strip().lower()
    if st == "live" and t and t.lower() not in GENERIC_TITLES:
        # keep first live title
        team_live.setdefault(nc, t)
    elif st in ("dead", "empty", "retry:empty"):
        team_dead.setdefault(nc, (status or "") + "|" + (title or ""))
    elif st in ("pending", "retry:pending"):
        team_pending.setdefault(nc, status or "")

corrupt = []
for vf in verify_files:
    name = os.path.basename(vf)
    try:
        if vf.endswith(".tsv"):
            for line in open(vf, encoding='utf-8'):
                parts = line.rstrip("\n").split("\t")
                if len(parts) >= 2:
                    record_verdict(parts[0], parts[1], parts[2] if len(parts) > 2 else "", name)
            continue
        if vf.endswith(".jsonl"):
            for line in open(vf, encoding='utf-8'):
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                code = r.get("code")
                status = r.get("status") or r.get("outcome") or ""
                title = r.get("title") or r.get("og_title") or r.get("info") or ""
                record_verdict(code, status, title, name)
            continue
        data = load_json_file(vf)
        if isinstance(data, tuple):
            corrupt.append((name, data[1])); continue
        if isinstance(data, list):
            for r in data:
                if not isinstance(r, dict):
                    continue
                code = r.get("code")
                status = r.get("status") or r.get("outcome") or ""
                title = r.get("title") or r.get("og_title") or r.get("info") or ""
                record_verdict(code, status, title, name)
        elif isinstance(data, dict):
            for code, v in data.items():
                if isinstance(v, dict):
                    record_verdict(code, v.get("status"), v.get("info") or v.get("title") or "", name)
                elif isinstance(v, str):
                    record_verdict(code, v, "", name)
    except Exception as e:
        corrupt.append((name, str(e)))
print("team-live codes:", len(team_live), "| team-dead:", len(team_dead),
      "| team-pending:", len(team_pending), flush=True)
print("corrupt/unreadable verify files:", corrupt, flush=True)

# ---------- pool collection ----------
pool = {}        # normcode -> record
pool_order = []
def add_record(code_raw, name, category, country, description, team, source):
    nc = norm_code(code_raw)
    if not nc:
        return "no-code"
    if nc in pool:
        return "dup-wave"
    # store the bare invite code, not the full URL
    bare = code_from_invite(code_raw) or str(code_raw).strip()
    rec = {"code": bare, "name": (name or "").strip(),
           "category": (category or "").strip(), "country": (country or "").strip(),
           "description": (description or "").strip(), "team": team, "source": source}
    pool[nc] = rec
    pool_order.append(nc)
    return "added"

stats = Counter()
# 1. stream items FIRST
stream = load_json_file(os.path.join(W12, "team01-stream-verified.json"))
if isinstance(stream, list):
    for it in stream:
        stats[add_record(it.get("invite") or it.get("code"), it.get("name"), it.get("category"),
                         it.get("country"), it.get("description"), "stream-nov12",
                         "wave_20261112/team01-stream-verified.json")] += 1
print("stream:", len(stream) if isinstance(stream, list) else stream, flush=True)

# 2. *-candidates.json
for cf in sorted(glob.glob(os.path.join(W15, "*-candidates.json"))):
    data = load_json_file(cf)
    if isinstance(data, tuple):
        corrupt.append((os.path.basename(cf), data[1])); continue
    if not isinstance(data, list):
        continue
    team = os.path.basename(cf).split("-candidates")[0]
    for it in data:
        if not isinstance(it, dict):
            continue
        stats[add_record(it.get("invite") or it.get("code"), it.get("name"), it.get("category"),
                         it.get("country"), it.get("description"), team,
                         os.path.basename(cf))] += 1
print("after candidates, pool:", len(pool), dict(stats), flush=True)

# 3. team09 verified jsonl (has names + verdicts)
for line in open(os.path.join(W15, "team09_verified_p461_560.jsonl"), encoding='utf-8'):
    line = line.strip()
    if not line:
        continue
    r = json.loads(line)
    code = r.get("code")
    nc = norm_code(code)
    if not nc or nc in pool:
        if nc in pool: stats["dup-wave"] += 1
        continue
    add_record(code, r.get("name"), r.get("category"), r.get("country"),
               "", "team09", "team09_verified_p461_560.jsonl")
print("after team09, pool:", len(pool), flush=True)

# 4. team11 cards + mined (named, unverified)
for cf in sorted(glob.glob(os.path.join(W15, "team11_cards_p*.json"))):
    data = load_json_file(cf)
    if isinstance(data, tuple):
        corrupt.append((os.path.basename(cf), data[1])); continue
    if isinstance(data, list):
        for it in data:
            if isinstance(it, dict):
                add_record(it.get("code"), it.get("name"), "", it.get("country_ar") or "",
                           "", "team11", os.path.basename(cf))
for line in open(os.path.join(W15, "team11_mined.jsonl"), encoding='utf-8'):
    line = line.strip()
    if not line:
        continue
    r = json.loads(line)
    add_record(r.get("code"), r.get("name"), "", r.get("country_ar") or "", "", "team11",
               "team11_mined.jsonl")
print("after team11, pool:", len(pool), flush=True)

# 5. team06 cards (kind=groups only; channels excluded later as channel codes)
for cf in sorted(glob.glob(os.path.join(W15, "team06_cards_p*.json"))):
    data = load_json_file(cf)
    if isinstance(data, tuple):
        corrupt.append((os.path.basename(cf), data[1])); continue
    if isinstance(data, list):
        for it in data:
            if isinstance(it, dict) and it.get("kind") == "groups":
                add_record(it.get("code"), it.get("name"), "", it.get("country_ar") or "",
                           "", "team06", os.path.basename(cf))
print("after team06, pool:", len(pool), flush=True)

# 6. raw files as NAME LOOKUP for team-live codes not yet in pool
raw_lookup = {}
for rf in ["team02-linkado11000-raw.json", "team03-linkado13500-raw.json",
           "team04-raw.json", "team05-linkado18500-raw.json"]:
    data = load_json_file(os.path.join(W15, rf))
    if isinstance(data, list):
        for it in data:
            if isinstance(it, dict) and it.get("code"):
                nc = norm_code(it["code"])
                if nc not in raw_lookup:
                    raw_lookup[nc] = (it.get("name"), it.get("dircat"), it.get("telegram"))
print("raw lookup entries:", len(raw_lookup), flush=True)

# live codes from verify files missing from pool -> add with name from raw or og:title
added_live = 0
for nc, title in team_live.items():
    if nc in pool:
        continue
    name, cat, tg = raw_lookup.get(nc, (None, None, None))
    if tg:
        continue  # telegram, not whatsapp
    add_record(nc, name or title, cat or "", "", "", "verify-live-only",
               "verify-files")
    added_live += 1
print("added live-only from verify files:", added_live, "pool:", len(pool), flush=True)

# also live codes from team15 p1/p2 (og_title as name) — handled via team_live above
# team16-reverify live codes already in team_live

# ---------- team01 flagged-kept / undecided: names for live codes ----------
# (they are already in candidates if team01 emitted them; undecided codes w/o
#  candidate records: add as pool entries with prior_og_title as name)
for f in ["team01-tglinkhub-undecided.json"]:
    data = load_json_file(os.path.join(W15, f))
    if isinstance(data, list):
        for it in data:
            if isinstance(it, dict) and it.get("code"):
                nc = norm_code(it["code"])
                if nc in pool or nc not in team_live:
                    continue
                add_record(it["code"], it.get("prior_og_title") or "", "", "",
                           "", "team01", f)
print("after team01 undecided, pool:", len(pool), flush=True)

# ---------- save intermediate ----------
state = {
    "pool": pool, "pool_order": pool_order,
    "team_live": team_live, "team_dead": team_dead, "team_pending": team_pending,
    "union_size": len(union), "corrupt": corrupt,
}
with open(os.path.join(OUT, "phase1_state.json"), "w", encoding='utf-8') as fh:
    json.dump(state, fh, ensure_ascii=False)
with open(os.path.join(OUT, "union_codes.json"), "w", encoding='utf-8') as fh:
    json.dump(sorted(union), fh)
print("POOL TOTAL:", len(pool))
print("corrupt files:", corrupt)
