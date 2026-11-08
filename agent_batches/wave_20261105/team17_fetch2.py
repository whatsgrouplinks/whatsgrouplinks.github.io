#!/usr/bin/env python3
"""team17 v2: fetch whatsappkanali.com pages (bodies cached to /tmp/t17_pages/),
extract group cards from RSC flight data with correct unescaping.
"""
import re, json, subprocess, os, html as htmlmod
from concurrent.futures import ThreadPoolExecutor
from collections import Counter

BASE = 'https://whatsappkanali.com'
CITIES = ['adana','ankara','antalya','bursa','diyarbakir','gaziantep','istanbul','izmir','kayseri','konya','samsun','trabzon']
TYPES = ['sohbet','tanisma','arkadaslik']
CITY_URLS = [f'{BASE}/sehir/{c}/{t}' for c in CITIES for t in TYPES]
EXCLUDED_TAGS = {
    'whatsapp-18-grup-linkleri','whatsapp-yetiskin-sohbet-gruplari',
    'whatsapp-bahis-gruplari','whatsapp-iddaa-tahmin-kanallari',
    'whatsapp-airdrop-gruplari','whatsapp-altcoin-gruplari','whatsapp-binance-gruplari',
    'whatsapp-bist-gruplari','whatsapp-bitcoin-gruplari','whatsapp-defi-gruplari',
    'whatsapp-ethereum-gruplari','whatsapp-kripto-gruplari','whatsapp-memecoin-gruplari',
    'whatsapp-nft-gruplari','whatsapp-solana-gruplari','whatsapp-trading-gruplari',
    'whatsapp-usdt-gruplari','whatsapp-web3-gruplari',
    'whatsapp-para-kazanma-kanallari','whatsapp-bedava-hesap-gruplari',
    'whatsapp-canli-mac-skor-kanallari','whatsapp-canli-skor-uygulama-kanallari',
    'whatsapp-canli-tv-haber-kanallari','whatsapp-eurolig-basketbol-kanallari',
    'whatsapp-film-onerileri-kanallari','whatsapp-milli-takim-kanallari',
    'whatsapp-mma-ufc-kanallari','whatsapp-sampiyonlar-ligi-kanallari',
    'whatsapp-spor-haber-kanallari','whatsapp-super-lig-haber-kanallari',
    'whatsapp-tv-dizi-bolum-kanallari',
}
SITEMAP_TAGS = """whatsapp-airdrop-gruplari whatsapp-alanyaspor-gruplari whatsapp-ales-yds-gruplari
whatsapp-altcoin-gruplari whatsapp-ankara-sohbet-gruplari whatsapp-anne-bebek-gruplari
whatsapp-antalyaspor-gruplari whatsapp-astroloji-gruplari whatsapp-bahis-gruplari
whatsapp-basaksehir-gruplari whatsapp-basketbol-gruplari whatsapp-bayan-gruplari
whatsapp-bedava-hesap-gruplari whatsapp-besiktas-gruplari whatsapp-binance-gruplari
whatsapp-bist-gruplari whatsapp-bodrumfk-gruplari whatsapp-burc-gruplari
whatsapp-canli-mac-skor-kanallari whatsapp-canli-skor-uygulama-kanallari
whatsapp-canli-tv-haber-kanallari whatsapp-clash-royale-gruplari whatsapp-defi-gruplari
whatsapp-derbi-sohbet-gruplari whatsapp-doktor-gruplari whatsapp-egeliler-gruplari
whatsapp-egitim-sinav-gruplari whatsapp-emekli-gruplari whatsapp-emlak-gruplari
whatsapp-ethereum-gruplari whatsapp-eurolig-basketbol-kanallari whatsapp-evli-cift-gruplari
whatsapp-eyupspor-gruplari whatsapp-fal-gruplari whatsapp-fenerbahce-gruplari
whatsapp-film-dizi-gruplari whatsapp-film-onerileri-kanallari whatsapp-fitness-gruplari
whatsapp-formula1-gruplari whatsapp-fortnite-gruplari whatsapp-fotograf-gruplari
whatsapp-futbol-gruplari whatsapp-gabile-gruplari whatsapp-galatasaray-gruplari
whatsapp-gaziantepfk-gruplari whatsapp-genc-gruplari whatsapp-goztepe-gruplari
whatsapp-iddaa-tahmin-kanallari whatsapp-indirim-kupon-gruplari whatsapp-istanbul-sohbet-gruplari
whatsapp-karadenizliler-gruplari whatsapp-kasimpasa-gruplari whatsapp-kayserispor-gruplari
whatsapp-kitap-gruplari whatsapp-kitap-pdf-gruplari whatsapp-konyaspor-gruplari
whatsapp-kosu-gruplari whatsapp-kpss-2026-gruplari whatsapp-kpss-gruplari
whatsapp-kripto-gruplari whatsapp-memecoin-gruplari whatsapp-milli-takim-kanallari
whatsapp-mma-ufc-kanallari whatsapp-mobile-legends-gruplari whatsapp-musik-gruplari
whatsapp-nft-gruplari whatsapp-ogretmen-gruplari whatsapp-oyun-gruplari
whatsapp-para-kazanma-kanallari whatsapp-pdf-kanallari whatsapp-pendikspor-gruplari
whatsapp-pubg-gruplari whatsapp-rizespor-gruplari whatsapp-saglik-gruplari
whatsapp-sampiyonlar-ligi-kanallari whatsapp-samsunspor-gruplari whatsapp-sivasspor-gruplari
whatsapp-spor-haber-kanallari whatsapp-super-lig-haber-kanallari whatsapp-tarot-gruplari
whatsapp-trabzonspor-gruplari whatsapp-trading-gruplari whatsapp-tv-dizi-bolum-kanallari
whatsapp-valorant-gruplari whatsapp-voleybol-kanallari whatsapp-web3-gruplari
whatsapp-yapay-zeka-gruplari whatsapp-yemek-tarif-gruplari whatsapp-yetiskin-sohbet-gruplari
whatsapp-yks-gruplari whatsapp-yoga-gruplari""".split()
EXTRA_TAGS = ['whatsapp-dating-gruplari','whatsapp-flort-gruplari']
TAG_URLS = [f'{BASE}/etiket/{t}' for t in sorted(set(SITEMAP_TAGS + EXTRA_TAGS) - EXCLUDED_TAGS)]
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
CACHE = '/tmp/t17_pages'
os.makedirs(CACHE, exist_ok=True)

def fetch(args):
    i, url = args
    p = os.path.join(CACHE, f'{i}.html')
    if os.path.exists(p) and os.path.getsize(p) > 5000:
        return url, open(p, encoding='utf-8', errors='ignore').read(), 0, True
    r = subprocess.run(['curl','-sL','-A',UA,'--max-time','30',url],
                       capture_output=True, text=True)
    if len(r.stdout) > 5000:
        open(p,'w',encoding='utf-8').write(r.stdout)
    return url, r.stdout, r.returncode, False

def clean(s):
    if s is None: return ''
    s = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1),16)), s)
    s = s.replace('\\r',' ').replace('\\n',' ').replace('\\"','"').replace("\\'", "'")
    s = re.sub(r'\s+',' ', s).strip()
    return htmlmod.unescape(s)

def extract_cards(body, source_url):
    # De-escape the RSC flight string layer once: \" -> " so JSON-ish parsing works.
    txt = body.replace('\\"', '"')
    cards = []
    for m in re.finditer(r'"inviteUrl":"https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_\-]{10,})', txt):
        code = m.group(1)
        if code.lower() == 'channel':
            continue
        start = max(0, m.start()-3000)
        seg = txt[start:m.start()]
        titles = re.findall(r'"title":"((?:[^"\\]|\\.)*)"', seg)
        cats = re.findall(r'"categoryName":"((?:[^"\\]|\\.)*)"', seg)
        cat_slugs = re.findall(r'"categorySlug":"((?:[^"\\]|\\.)*)"', seg)
        slugs = re.findall(r'"slug":"((?:[^"\\]|\\.)*)"', seg)
        descs = re.findall(r'"description":"((?:[^"\\]|\\.)*)"', seg)
        cards.append({
            'code': code,
            'title': clean(titles[-1]) if titles else '',
            'categoryName': clean(cats[-1]) if cats else '',
            'categorySlug': clean(cat_slugs[-1]) if cat_slugs else '',
            'slug': clean(slugs[-1]) if slugs else '',
            'description_raw': clean(descs[-1])[:300] if descs else '',
            'source': source_url,
        })
    return cards

def main():
    urls = CITY_URLS + TAG_URLS
    print(f'fetching {len(CITY_URLS)} city + {len(TAG_URLS)} tag pages = {len(urls)}', flush=True)
    failed = []
    all_cards = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        for url, body, rc, cached in ex.map(fetch, list(enumerate(urls))):
            if len(body) < 5000:
                failed.append({'url': url, 'bytes': len(body), 'rc': rc})
                print('FAILED/SHORT', url, len(body), flush=True)
                continue
            cs = extract_cards(body, url)
            print(f'{url} -> {len(cs)} cards (cached={cached})', flush=True)
            all_cards.extend(cs)
    print('failed:', len(failed), flush=True)
    seen = {}
    for c in all_cards:
        seen.setdefault(c['code'], c)
    print(f'total card hits {len(all_cards)}; unique codes {len(seen)}', flush=True)
    bad = [c for c in seen.values() if len(c['title']) > 80 or not c['title']]
    print('bad titles:', len(bad), flush=True)
    for c in bad[:10]:
        print('BAD', repr(c['title'][:150]), c['code'], flush=True)
    print(Counter(c['categoryName'] for c in seen.values()), flush=True)
    json.dump({'cards': list(seen.values()), 'failed': failed,
               'city_urls': CITY_URLS, 'tag_urls': TAG_URLS,
               'excluded_tags': sorted(EXCLUDED_TAGS)},
              open('/tmp/t17_raw2.json','w'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
