#!/usr/bin/env python3
"""Team40: gaming residual. Waits for VM egress, extracts codes from
whtsagrouplinks.com gaming pages + groupjoin.link gaming tag/category pages,
dedupes vs union, verifies via og:title, writes output files."""
import re, sys, os, json, time, html, requests

WD = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261104')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
      'Accept-Language': 'en-US,en;q=0.9'}
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?!invite/)([A-Za-z0-9]{20,24})(?![A-Za-z0-9])')
INVITE_RE = re.compile(r'chat\.whatsapp\.com/invite/([A-Za-z0-9]{20,24})(?![A-Za-z0-9])')
PORN = ['porn', 'pornhub', 'xxx', 'nude', 'sex video', 'escort', 'call girl', 'fuck', 'dick',
        'pussy', 'boobs', 'anal', 'bokep', 'vcs', '18+', '🔞', '🥵', '🍆', '🍑', '💦', '👅', '👄', '💋']

def log(*a):
    print(*a, file=sys.stderr, flush=True)

def wait_egress(max_min=25):
    deadline = time.time() + max_min * 60
    while time.time() < deadline:
        try:
            r = requests.get('https://example.com', headers=UA, timeout=15)
            if r.status_code < 500:
                log('EGRESS OK')
                return True
        except Exception as e:
            log('egress down:', str(e)[:70])
        time.sleep(60)
    return False

def main():
    union = set(json.load(open(WD + '/dedupe_union.json')))
    log('union size:', len(union))
    if not wait_egress():
        log('EGRESS NEVER RECOVERED — aborting with empty output')
        json.dump([], open(WD + '/team40-gaming-residual.json', 'w'))
        json.dump([], open(WD + '/team40-unverified-pending.json', 'w'))
        return

    s = requests.Session(); s.headers.update(UA)
    seen = {}
    def add(code, name, src):
        if code in union or code in seen:
            return
        seen[code] = {'name': name.strip(), 'src': src}

    # 1) whtsagrouplinks.com gaming pages — extract code + nearby name from raw HTML
    whtsa_pages = [
        'https://www.whtsagrouplinks.com/',
        'https://www.whtsagrouplinks.com/gaming-whatsapp-group-links/',
        'https://www.whtsagrouplinks.com/pubg-whatsapp-group-links/',
        'https://www.whtsagrouplinks.com/free-fire-whatsapp-groups-links/',
    ]
    for url in whtsa_pages:
        try:
            r = s.get(url, timeout=60)
            log('WHTSA', url.split('whtsagrouplinks.com/')[1] or 'home', r.status_code, len(r.content))
            if r.status_code != 200:
                continue
            t = r.text
            # pair each Join href with the nearest preceding list-item text
            for m in CODE_RE.finditer(t):
                code = m.group(1)
                ctx = t[max(0, m.start()-600):m.start()]
                nm = re.findall(r'<li[^>]*>(.*?)<\s*a[^>]*$', ctx, re.S)
                name = ''
                if nm:
                    name = re.sub(r'<[^>]+>', '', nm[-1])
                    name = html.unescape(name).strip()
                    name = re.sub(r'\s*[–—-]\s*Join\s*$', '', name, flags=re.I).strip()
                if not name:
                    nm2 = re.findall(r'>([^<>]{2,80})$', ctx)
                    name = html.unescape(nm2[-1]).strip() if nm2 else ''
                add(code, name, url)
        except Exception as e:
            log('WHTSA FAIL', url, str(e)[:100])

    # 2) groupjoin.link gaming tag pages — collect group/<id>, resolve via API
    gjl_tags = ['-gaming-', 'gaming', 'GAMING', 'gamer']
    for tag in gjl_tags:
        page = 1
        while page <= 60:
            url = f'https://www.groupjoin.link/tag/{tag}/?page={page}&limit=20&safeSearch=blur'
            try:
                r = s.get(url, timeout=60, allow_redirects=True)
                if r.status_code != 200:
                    log('GJL', tag, page, 'HTTP', r.status_code); break
                ids = re.findall(r'/group/([A-Za-z0-9]{20,24})', r.text)
                uids = list(dict.fromkeys(ids))
                log('GJL', tag, 'p', page, 'ids:', len(uids))
                if not uids:
                    break  # past-last-page: 200 with ~0 records
                for gid in uids:
                    try:
                        ar = s.get(f'https://api.groupjoin.link/groups/{gid}',
                                   timeout=30, headers={**UA, 'Accept': 'application/json', 'Referer': 'https://www.groupjoin.link/'})
                        if ar.status_code == 200:
                            d = ar.json()
                            inv = d.get('invite') or d.get('inviteLink') or d.get('link') or ''
                            nm = d.get('name') or d.get('title') or ''
                            mc = CODE_RE.search(inv)
                            if mc:
                                add(mc.group(1), nm, url + '|' + gid)
                    except Exception:
                        pass
                page += 1
            except Exception as e:
                log('GJL FAIL', tag, page, str(e)[:90]); break

    # 3) groupjoin.link /category/gaming — direct codes from listing HTML
    try:
        r = s.get('https://www.groupjoin.link/category/gaming', timeout=60)
        log('GJL category/gaming', r.status_code, len(r.content))
        if r.status_code == 200:
            for m in CODE_RE.finditer(r.text):
                code = m.group(1)
                ctx = r.text[max(0, m.start()-500):m.start()]
                nm = re.findall(r'<h[1-4][^>]*>(.*?)</h[1-4]>', ctx, re.S)
                name = html.unescape(re.sub(r'<[^>]+>', '', nm[-1])).strip() if nm else ''
                add(code, name, 'category/gaming')
    except Exception as e:
        log('GJL cat FAIL', str(e)[:90])

    log('fresh candidates:', len(seen))
    json.dump(seen, open(WD + '/team40_stageA.json', 'w'), ensure_ascii=False, indent=1)

    # 4) verify via og:title
    verified, pending = [], []
    v = requests.Session(); v.headers.update(UA)
    items = list(seen.items())
    for i, (code, info) in enumerate(items):
        name0 = info['name']
        try:
            r = v.get('https://chat.whatsapp.com/' + code, timeout=60)
            m = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', r.text)
            title = html.unescape(m.group(1)).strip() if m else ''
            if not title:
                log(f'[{i}/{len(items)}] DEAD {code} ({name0[:40]})')
                continue
            if any(p in (title + ' ' + name0).lower() for p in PORN):
                log(f'[{i}/{len(items)}] PORN-DROP {code} {title[:40]}')
                continue
            name = name0 if name0 and len(name0) > 2 else title
            # country hint
            cc = 'International'
            combo = (name + ' ' + title).lower()
            if '🇵🇰' in name or 'pakistan' in combo or ' pak ' in combo:
                cc = 'PK'
            elif 'bgmi' in combo or '🇮🇳' in name or 'india' in combo:
                cc = 'IN'
            elif 'indonesia' in combo or '🇮🇩' in name:
                cc = 'ID'
            desc = f"Active {name} WhatsApp group for gamers in {cc}. Join the {name} gaming community to chat, team up, and share gameplay."
            verified.append({"name": name, "category": "Gaming", "country": cc,
                             "description": desc,
                             "invite": f"https://chat.whatsapp.com/{code}", "image": ""})
            log(f'[{i}/{len(items)}] OK {code} {title[:50]}')
        except Exception as e:
            pending.append({"name": name0, "category": "Gaming", "country": "International",
                            "description": f"Gaming WhatsApp group ({name0}) — pending liveness recheck.",
                            "invite": f"https://chat.whatsapp.com/{code}", "image": "",
                            "note": "transport failure"})
            log(f'[{i}/{len(items)}] TRANSPORT-FAIL {code}')

    json.dump(verified, open(WD + '/team40-gaming-residual.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(pending, open(WD + '/team40-unverified-pending.json', 'w'), ensure_ascii=False, indent=1)
    log(f'DONE: verified={len(verified)} pending={len(pending)}')

main()
