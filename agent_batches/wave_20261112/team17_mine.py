import re, json, time, sys, os, html
import requests

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/'
EXISTING = '/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}

COUNTRY = {
    'México': 'MX', 'Mexico': 'MX', 'Cuba': 'CU', 'España': 'ES', 'Argentina': 'AR',
    'Colombia': 'CO', 'Perú': 'PE', 'Peru': 'PE', 'Chile': 'CL', 'Venezuela': 'VE',
    'Ecuador': 'EC', 'Bolivia': 'BO', 'Uruguay': 'UY', 'Paraguay': 'PY',
    'República Dominicana': 'DO', 'Dominicana': 'DO', 'Guatemala': 'GT', 'Honduras': 'HN',
    'El Salvador': 'SV', 'Nicaragua': 'NI', 'Costa Rica': 'CR', 'Panamá': 'PA',
    'Puerto Rico': 'PR', 'Estados Unidos': 'US', 'Brasil': 'BR', 'Brazil': 'BR',
    'Portugal': 'PT', 'Mundial': '', 'Latinoamérica': '', 'Latinoamerica': '',
    'Alemania': 'DE', 'Francia': 'FR', 'Italia': 'IT', 'Reino Unido': 'GB',
    'Canadá': 'CA', 'Canada': 'CA', 'India': 'IN', 'Pakistán': 'PK', 'Filipinas': 'PH',
}
CAT = {
    'Amor': 'Friendship', 'Anime': 'Entertainment', 'Chat': 'Community & Social',
    'Destacados': 'Community & Social', 'Diversión': 'Entertainment', 'Juegos': 'Gaming',
    'Memes': 'Funny', 'Música': 'Entertainment', 'Musica': 'Entertainment',
    'Deportes': 'Sports', 'Trabajo': 'Jobs', 'Educación': 'Education',
    'Salud': 'Health', 'Noticias': 'News', 'Cocina': 'Cooking',
    'Tecnología': 'Technology', 'Negocios': 'Business', 'Finanzas': 'Finance',
    'Cristianos': 'Community & Social', 'Religión': 'Community & Social',
    'Ventas': 'Buy & Sell', 'Compras': 'Buy & Sell', 'Criptomonedas': 'Crypto',
    'Poesía': 'Poetry', 'Literatura': 'Community & Social', 'Mundial': 'Sports',
    'Stickers': 'Funny', 'Series': 'Entertainment', 'Películas': 'Entertainment',
    'Amistad': 'Friendship', 'Estudio': 'Education', 'Apoyo': 'Community & Social',
    'Rol': 'Entertainment', 'Diversion': 'Entertainment',
}
DROP_RE = re.compile(r'(?i)\b(xxx|porn|porno|hentai|brazzers|call.?girl|escort|sexo|sexual|onlyfans|desi bhabhi|hookup|putas?|tetas|culo|vergas?|pene|vagina|chicas calientes|videos calientes|18\+ ?(sex|porn|xxx)|sexual home)\b|airdrop|binary option|opci[oó]n binaria|venda de xit|apuestas|betting|ganancias diarias|ai trading|trading.*(ganancias|lucro)|inversi[oó]n.*(diaria|garantizada)|hack.*(pago|paid)|dinero f[aá]cil')
NEG_RE = re.compile(r'(?i)(no\s+(xxx|porn|porno|sexo)|porn\s+not\s+allowed|proibido.*porn|sem\s+porn|n[aã]o\s+pode.*porn|no\s+se\s+permite.*porn|sin\s+porn)')

def clean(s):
    return html.unescape(re.sub(r'\s+', ' ', s or '')).strip()

def fetch(sess, url, tries=3):
    """Fresh connection per attempt for tugrupo.online (shared keep-alive
    connections go stale / get proxy-closed on this host)."""
    for i in range(tries):
        s = requests.Session()
        s.headers.update(UA)
        try:
            r = s.get(url, timeout=75)
            if r.status_code == 200 and 'One moment, please' not in r.text and 'window.location.reload' not in r.text[:2000]:
                return r.text
            print(f'  fetch {url[:80]} HTTP {r.status_code} botcheck={("One moment" in r.text)} try {i+1}', flush=True)
        except Exception as e:
            print(f'  fetch ERR {url[:80]} {e} try {i+1}', flush=True)
        finally:
            s.close()
        time.sleep(6 + i * 8)
    return None

def parse_listing(h):
    out = []
    for a in re.findall(r'<article.*?</article>', h, re.S):
        tm = re.search(r'<h[23][^>]*>\s*<a[^>]*href="(https://tugrupo\.online/whatsapp/[^"]+)"[^>]*>([^<]+)</a>', a)
        if not tm:
            continue
        detail, title = tm.group(1), clean(tm.group(2))
        if title == 'Grupos de WhatsApp':
            continue
        txt = re.sub(r'<[^>]+>', '|', a)
        parts = [clean(p) for p in txt.split('|') if clean(p)]
        if 'Categorías' in parts:
            continue
        cat_es = ''
        country_es = ''
        for p in parts[:2]:
            if p in COUNTRY or p in ('Latinoamérica', 'Latinoamerica'):
                country_es = p
            elif p in CAT or p in ('Rol', 'Destacados', 'Latinoamérica', 'Mundial'):
                if p in ('Latinoamérica', 'Mundial'):
                    country_es = p
                else:
                    cat_es = p
        if not cat_es and parts:
            cat_es = parts[0]
        if not country_es and len(parts) > 1:
            country_es = parts[1]
        excerpt = ''
        for p in parts:
            if p not in (cat_es, country_es, title, 'Ver Grupo') and len(p) > 10:
                excerpt = p
                break
        out.append({'detail': detail, 'cat_es': cat_es, 'country_es': country_es,
                    'title': title, 'excerpt': excerpt})
    return out

def og_title(h):
    m = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', h or '')
    if not m:
        m = re.search(r'<meta\s+content="([^"]*)"\s+property="og:title"', h or '')
    return clean(m.group(1)) if m else ''

def main():
    existing = set(json.load(open(EXISTING)))
    print('existing codes:', len(existing), flush=True)
    sess = requests.Session()
    sess.headers.update(UA)
    # CONTROLS
    known = 'KrDwdK8EIkB6vgauHg5M7N'
    h = fetch(sess, f'https://chat.whatsapp.com/{known}', tries=2)
    t = og_title(h)
    print(f'CONTROL live {known}: og:title={t!r} -> {"PASS" if t else "FAIL"}', flush=True)
    fake = 'ZZZZZZZZZZZZZZZZZZZZ'
    h2 = fetch(sess, f'https://chat.whatsapp.com/{fake}', tries=2)
    t2 = og_title(h2)
    print(f'CONTROL fake {fake}: og:title={t2!r} -> {"PASS" if not t2 else "FAIL"}', flush=True)

    ckpt = open(os.path.join(WAVE, 'team17_progress.jsonl'), 'a', encoding='utf-8')
    mined, seen_codes = [], set()
    # resume: skip detail URLs already mined in a previous run
    done_details = set()
    try:
        for line in open(os.path.join(WAVE, 'team17_progress.jsonl'), encoding='utf-8'):
            d = json.loads(line)
            done_details.add(d['detail'])
            mined.append(d)
    except FileNotFoundError:
        pass
    print(f'resumed {len(done_details)} already-mined details', flush=True)
    pages_done, pages_failed = [], []
    detail_fail = []
    for p in range(2, 11):
        url = f'https://tugrupo.online/whatsapp/?query-eb715b85={p}'
        h = fetch(sess, url)
        if not h:
            pages_failed.append(p)
            print(f'PAGE {p} FAILED (botcheck/transport)', flush=True)
            continue
        cards = parse_listing(h)
        print(f'PAGE {p}: {len(cards)} cards', flush=True)
        pages_done.append(p)
        for c in cards:
            if c['detail'] in done_details:
                continue
            dh = fetch(sess, c['detail'])
            if not dh:
                detail_fail.append(c['detail'])
                print(f'  detail FAIL {c["detail"]}', flush=True)
                continue
            m = re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{10,40})', dh)
            if not m:
                detail_fail.append(c['detail'])
                print(f'  detail NO CODE {c["detail"]} title={c["title"]!r}', flush=True)
                continue
            c['code'] = m.group(1)
            c['detail_title'] = og_title(dh)
            mined.append(c)
            ckpt.write(json.dumps(c, ensure_ascii=False) + '\n'); ckpt.flush()
            time.sleep(3)
        time.sleep(2)
    ckpt.close()
    json.dump({'pages_done': pages_done, 'pages_failed': pages_failed,
               'detail_fail': detail_fail, 'mined': len(mined)},
              open(os.path.join(WAVE, 'team17_mined_meta.json'), 'w'), indent=1)
    print(f'MINED total {len(mined)} pages_done={pages_done} pages_failed={pages_failed} detail_fail={len(detail_fail)}', flush=True)

    # dedupe + verify
    cands, pending, excluded, dead = [], [], [], []
    for c in mined:
        code = c['code']
        if code in existing or code in seen_codes:
            continue
        seen_codes.add(code)
        name = c['title'] or c.get('detail_title') or ''
        desc_src = (name + ' ' + c.get('excerpt', '')).lower()
        if DROP_RE.search(desc_src) and not NEG_RE.search(desc_src):
            excluded.append({**c, 'reason': 'content-screen drop: ' + DROP_RE.search(desc_src).group(0)})
            continue
        # verify
        live_title = None
        transport_fail = False
        for attempt in range(3):
            try:
                r = sess.get(f'https://chat.whatsapp.com/{code}', timeout=75)
                if r.status_code == 200:
                    live_title = og_title(r.text)
                    break
                else:
                    transport_fail = True
            except Exception as e:
                transport_fail = True
                print(f'  verify {code} attempt {attempt+1} ERR {e}', flush=True)
            time.sleep(5)
        if live_title is None and transport_fail:
            pending.append({**c, 'reason': 'transport failure on verify'})
            continue
        if not live_title:
            dead.append({**c, 'reason': 'no og:title (dead/expired)'})
            continue
        if not name:
            name = live_title
        cat = CAT.get(c['cat_es'], 'Community & Social')
        country = COUNTRY.get(c['country_es'], '')
        desc = f"Join {name}, a WhatsApp group listed under {cat}" + (f" from {c['country_es']}." if c['country_es'] and c['country_es'] != 'Mundial' else ".")
        if c.get('excerpt'):
            desc += ' ' + clean(c['excerpt'])[:200]
        cands.append({'name': name, 'category': cat, 'country': country,
                      'description': desc, 'invite': f'https://chat.whatsapp.com/{code}'})
        ckpt2 = open(os.path.join(WAVE, 'team17_verified.jsonl'), 'a', encoding='utf-8')
        ckpt2.write(json.dumps(cands[-1], ensure_ascii=False) + '\n'); ckpt2.close()
        print(f'  LIVE {code} {name!r}', flush=True)

    leads = []
    for p in pages_failed:
        leads.append(f'https://tugrupo.online/whatsapp/?query-eb715b85={p}')
    for d in detail_fail:
        leads.append(d)
    json.dump(cands, open(os.path.join(WAVE, 'team17-tugrupo-online-candidates.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(pending, open(os.path.join(WAVE, 'team17-tugrupo-online-pending.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(leads, open(os.path.join(WAVE, 'team17-tugrupo-online-leads.json'), 'w'), ensure_ascii=False, indent=1)
    summary = {
        'team': 17, 'slice': 'tugrupo.online /whatsapp/ pages 2-10',
        'controls': {'known_live_code': known, 'known_live_og_title': t,
                     'fabricated_code': fake, 'fabricated_og_title': t2},
        'pages_done': pages_done, 'pages_failed': pages_failed,
        'mined_listings': len(mined),
        'already_in_union_skipped': len(mined) - len(seen_codes),
        'verified_kept': len(cands), 'pending': len(pending),
        'dead_no_og_title': len(dead), 'exclusions': excluded,
        'detail_fail_count': len(detail_fail),
        'leads': len(leads),
        'resume': f"Last page mined: p{pages_done[-1] if pages_done else 'none'}; failed pages: {pages_failed}; detail pages without code/unfetchable: {len(detail_fail)} (in leads file).",
    }
    json.dump(summary, open(os.path.join(WAVE, 'team17-tugrupo-online-summary.json'), 'w'), ensure_ascii=False, indent=1)
    print('SUMMARY', json.dumps(summary, ensure_ascii=False)[:2000], flush=True)

if __name__ == '__main__':
    main()
