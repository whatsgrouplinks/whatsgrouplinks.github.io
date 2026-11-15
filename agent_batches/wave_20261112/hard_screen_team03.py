# TEAM 03 — wave 20261112, hard content-screen pass (task DROP list).
# The inherited bank_team31 screen missed task-listed drops (call-girl,
# "Desi bhabhi", 18+ sexual groups, paid video-call services). This pass
# re-screens the banked candidates against the TASK's explicit DROP list
# and builds a purge-suspect list for live codes already merged into
# groups.json (flag only — never modifies groups.json / .existing_codes.json).
import json, re, collections

W = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/'
W11 = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/'
RAW = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110/team32_raw/'
BASE = '/home/hatch/workspace/whatsapp-groups-site/'

# --- hard DROP patterns (name + og:title, case-insensitive) ---
PATS = [
    (r'call.?girls?|call.?boys?|escort|onlyfans', 'call-girl/escort/OnlyFans service'),
    (r'\bbhabhi\b', 'Desi bhabhi'),
    (r'auntys?\b', 'aunty video-call/sex-service genre'),
    (r'\bhorny\b|\bxvideos\b|xnxx|brazzers|hentai|putaria|pundai|soothu|\bpenis\b|pussy|\bdick\b|\bcock\b|boobs|tites', 'explicit sexual content'),
    (r'\bsexy\b|\bsaxy\b', 'sexy/saxy sexualised title'),
    (r'paid\s+(girl|call|service|vc|video|tamil|telugu)|paid\s+\w*\s*girl|\bgirl\b.*\bpaid\b|\bpaid\b.*\bservice\b', 'paid girl/service'),
    (r'video.?call|vidio|vid\s*call|\bvc\b', 'video-call sex service'),
    (r'\bitem\b', 'item-girl sexualised trope'),
    (r'18\s*\+\s*(xvideo|pics?|video|vidio|call|aunty|bhabhi|hot|ullu|sexy|adult)', '18+ sexual group'),
    (r'18\s*\+.*[💦👅🍌🍑😘]|💋.*💦|💦.*💋', '18+/sexual emoji title'),
    (r'hot\s+(girl|boy|aunty|bhabhi|tamil|telugu|ullu|item)|top\s+girls?', 'hot-girls sexualised title'),
    (r'naughty\s+(girl|ladies|vid|call|teen)|teens?\s+(vid|call)|vid\s*calls?\s+with\s+teens?', 'naughty/teen video-call sexual content'),
    (r'unsatisfied|full\s*neud|full\s*open\s*video|genuine\s+girl\s+demo|girl\s+demo', 'sexual-service listing'),
    (r'\bgirl\b.*(💋|👅|💦)', 'girls + sexual emojis'),
    (r'services?\s*(❤️|😘|💋)', 'service + kiss/heart emojis (sex service)'),
]
RX = [(re.compile(p, re.I), why) for p, why in PATS]

def hard_drop(text):
    t = text or ''
    for rx, why in RX:
        if rx.search(t):
            return why
    return None

# --- load candidates + og titles ---
cands = json.load(open(W + 'team03-tglinkhub-candidates.json'))
bycode = {}
for path in (f'{RAW}verify2_results.jsonl', f'{W11}verify2_results_20261111.jsonl',
             f'{W}verify2_results_20261112.jsonl'):
    try:
        for line in open(path):
            d = json.loads(line); bycode[d['code']] = d
    except FileNotFoundError:
        pass

kept, dropped = [], []
for c in cands:
    code = c['invite'].rsplit('/', 1)[-1]
    og = (bycode.get(code) or {}).get('og_title') or ''
    text = c['name'] + ' || ' + og
    why = hard_drop(text)
    if why:
        dropped.append({'code': code, 'name': c['name'], 'og_title': og,
                        'reason': 'hard-screen DROP: ' + why})
    else:
        kept.append(c)
print(f"candidates in: {len(cands)} kept: {len(kept)} hard-dropped: {len(dropped)}")

# --- purge suspects: live codes already inside .existing_codes.json ---
existing = set(json.load(open(BASE + '.existing_codes.json')))
suspects = []
for code, r in bycode.items():
    if r.get('status') != 'live' or code not in existing:
        continue
    og = r.get('og_title') or ''
    why = hard_drop(og)
    if why:
        suspects.append({'code': code, 'og_title': og,
                         'reason': 'hard-screen DROP: ' + why + ' (already in groups.json — purge candidate)'})
print(f"purge suspects already in groups.json: {len(suspects)}")
print("suspect reasons:", collections.Counter(s['reason'].split(':')[1].strip().split(' (')[0] for s in suspects).most_common())

json.dump(kept, open(W + 'team03-tglinkhub-candidates.json', 'w'), ensure_ascii=False, indent=1)
json.dump(suspects, open(W + 'team03-purge-suspects.json', 'w'), ensure_ascii=False, indent=1)

# --- update summary: verified count, exclusions extended, notes ---
summ = json.load(open(W + 'team03-tglinkhub-summary.json'))
summ['verified'] = len(kept)
summ['exclusions'] = summ['exclusions'] + dropped
summ['notes'] = summ['notes'] + [
    f"Hard-screen pass (task DROP list) AFTER banking: {len(dropped)} more dropped from candidates "
    "(call-girl/escort, Desi bhabhi, aunty genre, paid video-call services, 18+ sexual, "
    "OnlyFans/horny/xvideos) — the inherited bank_team31 screen did not cover these patterns. "
    f"Final verified candidates: {len(kept)}.",
    f"MERGE NOTE: .existing_codes.json grew 112,070 -> 119,266 at ~10:34 UTC during this run "
    "(coordinator merged wave_20261112 candidates incl. this team's earlier partial banks of "
    "654/760/855/1,009/1,325/1,718/2,197/2,571/3,018/3,609/4,026 items). Final 'verified' counts "
    "only live+clean codes NOT in groups.json as of the final bank; cumulative live codes found "
    "by this team across the whole pool: 6,763 (checked 13,147 = full pool).",
    f"Purge suspects: {len(suspects)} live codes matching the hard DROP list are ALREADY in "
    "groups.json (merged 10:34 UTC) — listed in team03-purge-suspects.json for the coordinator "
    "to purge; this team did not modify groups.json.",
    "Kept per false-positive restores: 18+ age gates on non-porn girls groups ('Only girls 18+', "
    "'Only For Girls 18+', 'Teen 18+ only', bare '18+'), plain girls/friendship groups "
    "('Tamil Girls Group', 'UK Girl Group', 'USA girls'), lesbian/gay friendship groups, "
    "and 'service/paid' false positives (UPSC Civil Services, car rental, gaming scrims, photo editing).",
]
json.dump(summ, open(W + 'team03-tglinkhub-summary.json', 'w'), ensure_ascii=False, indent=1)
print("summary updated: verified", summ['verified'], "exclusions total", len(summ['exclusions']))
print("drop reasons:", collections.Counter(d['reason'] for d in dropped).most_common())
