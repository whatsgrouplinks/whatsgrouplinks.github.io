#!/usr/bin/env python3
"""team17: fetch whatsappkanali.com city (36) + tag pages, extract group cards.
Writes raw extracted candidates to /tmp/t17_raw.json (NOT an output file).
"""
import re, json, subprocess, os, html as htmlmod
from concurrent.futures import ThreadPoolExecutor

BASE = 'https://whatsappkanali.com'
CITIES = ['adana','ankara','antalya','bursa','diyarbakir','gaziantep','istanbul','izmir','kayseri','konya','samsun','trabzon']
TYPES = ['sohbet','tanisma','arkadaslik']
CITY_URLS = [f'{BASE}/sehir/{c}/{t}' for c in CITIES for t in TYPES]

# whatsapp-* tags from sitemap (91) + homepage-only extras, minus excluded sets
EXCLUDED_TAGS = {
    # adult
    'whatsapp-18-grup-linkleri','whatsapp-yetiskin-sohbet-gruplari',
    # betting / gambling
    'whatsapp-bahis-gruplari','whatsapp-iddaa-tahmin-kanallari',
    # crypto / finance pump-prone
    'whatsapp-airdrop-gruplari','whatsapp-altcoin-gruplari','whatsapp-binance-gruplari',
    'whatsapp-bist-gruplari','whatsapp-bitcoin-gruplari','whatsapp-defi-gruplari',
    'whatsapp-ethereum-gruplari','whatsapp-kripto-gruplari','whatsapp-memecoin-gruplari',
    'whatsapp-nft-gruplari','whatsapp-solana-gruplari','whatsapp-trading-gruplari',
    'whatsapp-usdt-gruplari','whatsapp-web3-gruplari',
    # money-making / free-account scam-prone
    'whatsapp-para-kazanma-kanallari','whatsapp-bedava-hesap-gruplari',
    # channel archives (channels excluded by rule)
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
EXTRA_TAGS = ['whatsapp-dating-gruplari','whatsapp-flort-gruplari']  # homepage-only, allowed dating
TAG_URLS = [f'{BASE}/etiket/{t}' for t in sorted(set(SITEMAP_TAGS + EXTRA_TAGS) - EXCLUDED_TAGS)]

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'

def fetch(url):
    r = subprocess.run(['curl','-sL','-A',UA,'--max-time','30',url],
                       capture_output=True, text=True)
    return url, r.stdout, r.returncode

def unesc(s):
    if s is None: return ''
    s = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1),16)), s)
    s = s.replace('\\"','"').replace("\\'", "'").replace('\\\\','\\')
    return htmlmod.unescape(s)

def extract_cards(page_html, source_url):
    cards = []
    # every inviteUrl occurrence; walk backwards for title/categoryName/slug
    for m in re.finditer(r'\\"inviteUrl\\":\\"https://chat\.whatsapp\.com/([A-Za-z0-9_\-]+)', page_html):
        code = m.group(1)
        start = max(0, m.start()-4000)
        seg = page_html[start:m.start()]
        titles = re.findall(r'\\"title\\":\\"((?:[^"\\]|\\.)*)\\"', seg)
        cats = re.findall(r'\\"categoryName\\":\\"((?:[^"\\]|\\.)*)\\"', seg)
        slugs = re.findall(r'\\"slug\\":\\"((?:[^"\\]|\\.)*)\\"', seg)
        cat_slugs = re.findall(r'\\"categorySlug\\":\\"((?:[^"\\]|\\.)*)\\"', seg)
        # also plain (non-escaped) variants
        if not titles:
            titles = re.findall(r'"title":"((?:[^"\\]|\\.)*)"', seg)
        if not cats:
            cats = re.findall(r'"categoryName":"((?:[^"\\]|\\.)*)"', seg)
        if not slugs:
            slugs = re.findall(r'"slug":"((?:[^"\\]|\\.)*)"', seg)
        if not cat_slugs:
            cat_slugs = re.findall(r'"categorySlug":"((?:[^"\\]|\\.)*)"', seg)
        cards.append({
            'code': code,
            'title': unesc(titles[-1]) if titles else '',
            'categoryName': unesc(cats[-1]) if cats else '',
            'categorySlug': unesc(cat_slugs[-1]) if cat_slugs else '',
            'slug': unesc(slugs[-1]) if slugs else '',
            'source': source_url,
        })
    return cards

def main():
    urls = CITY_URLS + TAG_URLS
    print(f'fetching {len(CITY_URLS)} city + {len(TAG_URLS)} tag pages = {len(urls)}')
    results = {}
    failed = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        for url, body, rc in ex.map(fetch, urls):
            if len(body) < 5000:
                failed.append({'url': url, 'bytes': len(body), 'rc': rc})
                print('FAILED/SHORT', url, len(body))
            results[url] = body
    print('failed:', len(failed))
    all_cards = []
    for url, body in results.items():
        cs = extract_cards(body, url)
        print(f'{url} -> {len(cs)} cards')
        all_cards.extend(cs)
    # dedupe by code, keep first
    seen = {}
    for c in all_cards:
        seen.setdefault(c['code'], c)
    print(f'total card hits {len(all_cards)}; unique codes {len(seen)}')
    json.dump({'cards': list(seen.values()), 'failed': failed,
               'city_urls': CITY_URLS, 'tag_urls': TAG_URLS,
               'excluded_tags': sorted(EXCLUDED_TAGS)},
              open('/tmp/t17_raw.json','w'), ensure_ascii=False, indent=1)
    # category inventory
    from collections import Counter
    print(Counter((c['categoryName'], c['categorySlug']) for c in seen.values()))

if __name__ == '__main__':
    main()
