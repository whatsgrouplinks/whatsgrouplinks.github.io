#!/usr/bin/env python3
"""Team 18: cricket/sports WhatsApp group harvest + verify."""
import re, json, pickle, subprocess, time, os

WORK = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(WORK)

def load_dedupe():
    with open(os.path.join(WORK, 'dedupe.pkl'), 'rb') as f:
        return pickle.load(f)

PORN = re.compile(r'porn|pornhub|xxx|nudes|sex[\s_-]?video|escort|call[\s_-]?girl|randi|fuck|dick|pussy|boobs|anal|[\U0001F51E\U0001F608\U0001F60D\U0001F618]', re.I)

def fold_basic(t):
    """Fold common math-alphanumeric unicode to ASCII."""
    blocks = [
        (0x1D400, 0x1D419, ord('A')), (0x1D41A, 0x1D433, ord('a')), (0x1D7CE, 0x1D7D7, ord('0')),
        (0x1D5A0, 0x1D5B9, ord('A')), (0x1D5BA, 0x1D5D3, ord('a')), (0x1D7E2, 0x1D7EB, ord('0')),
        (0x1D670, 0x1D689, ord('A')), (0x1D68A, 0x1D6A3, ord('a')), (0x1D7F6, 0x1D7FF, ord('0')),
        (0x1D538, 0x1D551, ord('A')), (0x1D552, 0x1D56B, ord('a')),
        (0x1D4D0, 0x1D4E9, ord('A')), (0x1D4EA, 0x1D503, ord('a')),
        (0x1D434, 0x1D44D, ord('A')), (0x1D44E, 0x1D467, ord('a')),
        (0x1D504, 0x1D51D, ord('A')), (0x1D51E, 0x1D537, ord('a')),
    ]
    singles = {0x2102: 'C', 0x210D: 'H', 0x2115: 'N', 0x2119: 'P', 0x211A: 'Q', 0x211D: 'R', 0x2124: 'Z', 0x2133: 'M'}
    out = []
    for ch in t:
        o = ord(ch)
        hit = None
        for lo, hi, base in blocks:
            if lo <= o <= hi:
                hit = chr(base + (o - lo)); break
        if hit is not None:
            out.append(hit)
        elif o in singles:
            out.append(singles[o])
        else:
            out.append(ch)
    return ''.join(out)

def clean_name(raw):
    # strip image markdown
    n = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', raw)
    n = n.replace('%', ' ')
    # strip markdown stars/pipes, leading table chars
    n = n.strip().lstrip('|- ').rstrip('*| ').strip('*').strip()
    # fold fancy unicode to ASCII
    n = fold_basic(n)
    out = []
    for ch in n:
        o = ord(ch)
        if o < 128:
            out.append(ch)
        elif ch in '🇵🇰🇮🇳🏏⚽🏆🎾❤💯💝🔥🥰😍⭐🌹💫✨🥎💗':
            out.append(' ')
    n = ''.join(out)
    n = re.sub(r'\s+', ' ', n).strip(' -:|')
    return n[:90]

def parse_jina(path, source_url, default_country):
    txt = open(path, encoding='utf-8', errors='ignore').read()
    rows = []
    for line in txt.splitlines():
        for m in re.finditer(r'https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{22})\b', line):
            code = m.group(1)
            before = line[:m.start()]
            # cut at link-text opener: '**[', '*[', '[Join', '[Link'
            nm = re.split(r'\*{0,2}\[', before)[0]
            name = clean_name(nm)
            rows.append({'code': code, 'name': name, 'source_page': source_url,
                         'raw': nm[:80], 'country_hint': default_country})
    return rows

def infer_country(name, hint):
    low = name.lower()
    if re.search(r'pakistan|🇵🇰', name) or re.search(r'\bpsl\b|\bptv\b', low): return 'PK'
    if re.search(r'\bindia\b|\bindian\b|🇮🇳', low + name): return 'IN'
    if 'sri lanka' in low: return 'LK'
    if 'bangladesh' in low: return 'BD'
    if 'england' in low or 'premier league' in low: return 'GB'
    if 'australia' in low: return 'AU'
    return hint

def describe(name):
    low = name.lower()
    if 'football' in low or 'soccer' in low:
        return 'A football fans group for match talk, live updates, transfer news and highlights.'
    if 'psl' in low:
        return 'A PSL fans group for live scores, match updates and Pakistan Super League discussions.'
    if 'ipl' in low:
        return 'An IPL fans group for live scores, match talk and team updates.'
    if 'prediction' in low or 'fantasy' in low or 'dream11' in low or 'betting' in low:
        return 'A cricket prediction and fantasy group sharing tips, match insights and score updates.'
    if 'live score' in low or 'live cricket' in low:
        return 'A cricket group sharing live scores, ball-by-ball updates and match news.'
    if 'world cup' in low or 't20' in low or 'icc' in low:
        return 'A cricket group for World Cup and international match updates, scores and fan discussions.'
    return 'A cricket fans group for live scores, match updates and team discussions.'

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

def verify(code):
    """Returns (alive, og_title)."""
    try:
        p = subprocess.run(['curl', '-sL', '--max-time', '20', '-A', UA,
                            '-o', '-', '-w', '\n%{http_code}',
                            f'https://chat.whatsapp.com/{code}'],
                           capture_output=True, timeout=40)
        out = p.stdout.decode('utf-8', errors='ignore')
        *body, http = out.rsplit('\n', 1)
        body = '\n'.join(body)
        if http.strip() != '200':
            return False, ''
        m = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']*)["\']', body)
        title = (m.group(1) if m else '').strip()
        if not title or "couldn" in title.lower():
            return False, title
        return True, title
    except Exception:
        return False, ''

def main():
    dedupe = load_dedupe()
    cand = []
    cand += parse_jina(os.path.join(WORK, 'whatgroups_jina.txt'),
                       'https://whatgroups.com/cricket-whatsapp-group-links/', 'XX')
    cand += parse_jina(os.path.join(WORK, 'minidea_jina.txt'),
                       'https://minidea.co.in/cricket-whatsapp-group-link/', 'IN')
    cand += parse_jina(os.path.join(WORK, 'wahublink_jina.txt'),
                       'https://wahublink.com/sports-whatsapp-group-links/', 'XX')
    cand.append({'code': 'HW4VpGfWp8aFeTRJOBU8Ow', 'name': 'San Ramon Tri-Valley Cricket',
                 'source_page': 'https://www.meetup.com/san-ramon-cricket-meetup-group/?action=join',
                 'raw': '', 'country_hint': 'US'})
    print('raw candidates:', len(cand))

    fresh, seen = [], set()
    skipped_dup, skipped_porn = 0, 0
    for c in cand:
        code = c['code']
        if code in dedupe or code in seen:
            skipped_dup += 1
            continue
        seen.add(code)
        if PORN.search(c['name']):
            skipped_porn += 1
            continue
        fresh.append(c)
    print('fresh:', len(fresh), 'dup:', skipped_dup, 'porn-blocked:', skipped_porn)
    json.dump(fresh, open(os.path.join(WORK, 'candidates.json'), 'w'), ensure_ascii=False, indent=1)

    results = []
    for i, c in enumerate(fresh):
        alive, title = verify(c['code'])
        results.append({**c, 'alive': alive, 'og_title': title})
        if (i + 1) % 25 == 0:
            print(f'verified {i+1}/{len(fresh)}')
        time.sleep(0.5)
    alive_n = sum(1 for r in results if r['alive'])
    print('alive:', alive_n)
    json.dump(results, open(os.path.join(WORK, 'verify_results.json'), 'w'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
