#!/usr/bin/env python3
"""Parent verification for wave 20261030: re-curl every fresh candidate in own sandbox,
apply merge flags, write parent_verified.json."""
import json, re, os, sys, time, glob, html, subprocess

WAVE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(os.path.dirname(WAVE))
GROUPS = os.path.join(SITE, 'groups.json')
CODES_JSON = os.path.join(SITE, '.existing_codes.json')
STATE = os.path.join(WAVE, 'parent_verify_state.json')
OUT = os.path.join(WAVE, 'parent_verified.json')

CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]+)')
OG_RE = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']*)', re.I)
PORN_RE = re.compile(r'\b(porn|pornhub|xxx|nudes?|sex\s?video|escort|call\s?girl|randi|fuck|dick|pussy|boobs|anal)\b', re.I)
ADULT_EMOJI = set('🥵🍆🍑🔞💦👅👄💋')
DROP_CHANNEL = True  # exclude /invite/ channel-format items

# rescue: verified-live by team22 but excluded; re-verify here anyway
RESCUE = [
    {"name": "Islam Status", "category": "Islamic", "country": "PK",
     "description": "An Islamic group sharing religious status updates and reminders.",
     "image": "", "invite": "https://chat.whatsapp.com/JbU2xvAO72JB0seQKPCam0"},
    {"name": "Islam forever", "category": "Islamic", "country": "PK",
     "description": "An Islamic group sharing Islamic reminders and Islamic content.",
     "image": "", "invite": "https://chat.whatsapp.com/ITE018KuLvO8ticFwczRbX"},
    {"name": "اصلاح خواتین", "category": "Community & Social", "country": "PK",
     "description": "A community group for women's guidance and support.",
     "image": "", "invite": "https://chat.whatsapp.com/JRPGdICdSdEDNSpdOrxwi1"},
]
# team29's 5 French carpool codes excluded as phantom collisions; verify independently
CARPOOL = ["DSGtepNfaBiLb9nugtV8yy", "Fj0wU2LmB9LCFmgk0AN3y7", "FBABBI5kyH0JXUbQN7i9KI",
           "JPxBTeIkeom4vbs5Z9NWCS", "GKrbH9dGaP51qAmCfOAqHK"]
for c in CARPOOL:
    RESCUE.append({"name": "", "category": "Community & Social", "country": "FR",
                   "description": "A village carpooling group helping families organise shared rides to the leisure centre.",
                   "image": "", "invite": "https://chat.whatsapp.com/" + c})

def load_union():
    with open(GROUPS) as f:
        groups = json.load(f)
    gc = {CODE_RE.search(g.get('invite', '') or '').group(1)
          for g in groups if CODE_RE.search(g.get('invite', '') or '')}
    with open(CODES_JSON) as f:
        ec = set(json.load(f))
    return gc | ec

def check(code):
    """Return og:title or '' if dead/uncheckable. Empty string on failure."""
    try:
        p = subprocess.run(
            ['curl', '-sL', '--max-time', '25', '-A',
             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
             'https://chat.whatsapp.com/' + code],
            capture_output=True, text=True, timeout=30)
        if p.returncode != 0:
            return None  # transport failure -> retryable, not dead
        m = OG_RE.search(p.stdout or '')
        t = html.unescape(m.group(1)).strip() if m else ''
        if t.lower().startswith("couldn't look up"):
            return ''
        return t
    except Exception:
        return None

def main():
    union = load_union()
    print('union size:', len(union), flush=True)
    items, seen_wave = [], set()
    drops = {'channel': 0, 'dup_union': 0, 'dup_wave': 0, 'badcode': 0}
    for fn in sorted(glob.glob(os.path.join(WAVE, 'team*-fresh-*.json'))):
        try:
            data = json.load(open(fn))
        except Exception as e:
            print('SKIP unreadable', fn, e); continue
        lst = data if isinstance(data, list) else data.get('items', data.get('groups', []))
        for it in lst:
            inv = (it.get('invite') or '').strip()
            m = CODE_RE.search(inv)
            if not m:
                drops['badcode'] += 1; continue
            code = m.group(1)
            if len(code) != 22:
                drops['badcode'] += 1; continue
            if DROP_CHANNEL and '/invite/' in inv:
                drops['channel'] += 1; continue
            if code in union:
                drops['dup_union'] += 1; continue
            if code in seen_wave:
                drops['dup_wave'] += 1; continue
            seen_wave.add(code)
            items.append(it)
    for it in RESCUE:
        code = CODE_RE.search(it['invite']).group(1)
        if code in union or code in seen_wave:
            continue
        seen_wave.add(code); items.append(it)
    print('candidates:', len(items), 'drops:', drops, flush=True)

    state = {}
    if os.path.exists(STATE):
        state = json.load(open(STATE))
    verified, done = 0, 0
    for it in items:
        code = CODE_RE.search(it['invite']).group(1)
        if code in state:
            if state[code].get('title'):
                verified += 1
            done += 1; continue
        title = check(code)
        if title is None:  # transport failure: retry once after pause
            time.sleep(5); title = check(code)
        state[code] = {'title': title or '', 'live': bool(title)}
        if title:
            verified += 1
        done += 1
        if done % 50 == 0:
            json.dump(state, open(STATE, 'w'))
            print('progress', done, '/', len(items), 'live:', verified, flush=True)
        time.sleep(0.4)
    json.dump(state, open(STATE, 'w'))

    out = []
    screens = {'dead': 0, 'porn': 0, 'emptyname': 0}
    for it in items:
        code = CODE_RE.search(it['invite']).group(1)
        title = state[code].get('title', '')
        if not title:
            screens['dead'] += 1; continue
        name = (it.get('name') or '').strip()
        if not name:
            name = title
        if len(name) < 2:
            screens['emptyname'] += 1; continue
        if PORN_RE.search(name + ' ' + (it.get('description') or '')):
            screens['porn'] += 1; continue
        if any(e in name for e in ADULT_EMOJI):
            screens['porn'] += 1; continue
        it['name'] = name[:120]
        it['invite'] = 'https://chat.whatsapp.com/' + code
        out.append(it)
    json.dump(out, open(OUT, 'w'), ensure_ascii=False, indent=1)
    print('VERIFIED:', len(out), 'screens:', screens, flush=True)

if __name__ == '__main__':
    main()
