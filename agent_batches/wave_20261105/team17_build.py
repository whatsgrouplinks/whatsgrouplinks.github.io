#!/usr/bin/env python3
"""team17: build the three output files from verification results.
Verified = 6 exact fields. Pending = {code, name, note}. Leads = {url, what}.
"""
import json, html, os

BASE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261105'
items = {i['code']: i for i in json.load(open('/tmp/t17_verify_list.json'))}
res = json.load(open('/tmp/t17_verify.json'))
raw = json.load(open('/tmp/t17_raw2.json'))

verified_codes = sorted(c for c, v in res.items() if (v.get('og_title') or '').strip())
pending_codes = sorted(c for c, v in res.items() if not (v.get('og_title') or '').strip())

# Name overrides: use decoded og:title where the listing name carries a personal
# name (content rule) and og:title is the clean true group name.
NAME_OVERRIDE = {
    'LXRQJXIyqk95tQt1esfqzk': html.unescape(res['LXRQJXIyqk95tQt1esfqzk']['og_title']).strip(),
}
# Description fix for the one brand-new code (og:title shows it is buy-sell, not matchmaking).
DESC_OVERRIDE = {
    'LYDIQM8AVChCxUUBdVGV77': 'Turkish PUBG Mobile buy-and-sell WhatsApp group for players in Turkey to trade game accounts, skins and items with fellow gamers.',
}

verified = []
for c in verified_codes:
    it = items[c]
    verified.append({
        'name': NAME_OVERRIDE.get(c, it['name']),
        'category': it['category'],
        'country': it['country'],
        'description': DESC_OVERRIDE.get(c, it['description']),
        'invite': f'https://chat.whatsapp.com/{c}',
        'image': '',
    })

pending = []
for c in pending_codes:
    it = items[c]
    pending.append({
        'code': c,
        'name': it['name'],
        'note': ('og:title empty on 2026-11-05 re-check (2 attempts, curl UA Mozilla/5.0); '
                 'control live code returned non-empty og:title the same day, so the method works '
                 'and this code is likely dead/revoked; needs JS-capable browser leg to confirm. '
                 f"category: {it['category']}; source: {it['source']}"),
    })

EXCLUDED_TAGS = raw['excluded_tags']
TAG_REASON = {}
for t in EXCLUDED_TAGS:
    if t in ('whatsapp-18-grup-linkleri', 'whatsapp-yetiskin-sohbet-gruplari'):
        TAG_REASON[t] = 'SKIPPED BY RULE: adult tag; do not scrape.'
    elif t in ('whatsapp-bahis-gruplari', 'whatsapp-iddaa-tahmin-kanallari'):
        TAG_REASON[t] = 'SKIPPED BY RULE: betting/gambling tag; do not scrape.'
    elif t in ('whatsapp-airdrop-gruplari', 'whatsapp-altcoin-gruplari', 'whatsapp-binance-gruplari',
               'whatsapp-bist-gruplari', 'whatsapp-bitcoin-gruplari', 'whatsapp-defi-gruplari',
               'whatsapp-ethereum-gruplari', 'whatsapp-kripto-gruplari', 'whatsapp-memecoin-gruplari',
               'whatsapp-nft-gruplari', 'whatsapp-solana-gruplari', 'whatsapp-trading-gruplari',
               'whatsapp-usdt-gruplari', 'whatsapp-web3-gruplari'):
        TAG_REASON[t] = 'SKIPPED BY RULE: crypto/finance tag, pump/scam-prone; do not scrape.'
    elif t in ('whatsapp-para-kazanma-kanallari', 'whatsapp-bedava-hesap-gruplari'):
        TAG_REASON[t] = 'SKIPPED BY RULE: money-making / free-account tag, scam-prone; do not scrape.'
    else:
        TAG_REASON[t] = 'SKIPPED BY RULE: channel archive (kanallari), not groups; channels excluded.'

leads = []
leads.append({'url': 'https://whatsappkanali.com/grup/pubg-mobil',
              'what': 'Detail pages /grup/<slug> hide the MAIN group code behind a /go/<goId> client-side redirect (listing cards are only similar groups). A browser leg can resolve each /go/ link to the real chat.whatsapp.com code; ~80+ slugs harvestable from listing pages.'})
for t in sorted(EXCLUDED_TAGS):
    leads.append({'url': f'https://whatsappkanali.com/etiket/{t}', 'what': TAG_REASON[t]})
leads.append({'url': 'https://whatsappkanali.com/sehir/istanbul/oyun',
              'what': 'EXTRA CITY COVERAGE (beyond this slice of 36): sitemap lists 1,234 /sehir/ URLs (81 cities x ~15 types incl. oyun, alim-satim, is-ilanlari, emlak, etkinlik, fal, burc, ogrenci, kanallar). Same card structure as the 36 pages read. City types yetiskin/kripto/para-kazanma are excluded by content rules.'})
leads.append({'url': 'https://whatsappkanali.com/sehir/kocaeli/sohbet',
              'what': 'EXTRA CITY COVERAGE: /sehir/kocaeli/sohbet and /sehir/tekirdag/sohbet appear as links on city pages but are outside the 12-city slice; same card structure.'})
leads.append({'url': 'https://whatsappkanali.com/sehir/tekirdag/sohbet',
              'what': 'EXTRA CITY COVERAGE: see /sehir/kocaeli/sohbet entry; same card structure as the 36 pages read.'})
EMPTY_TAGS = ['whatsapp-anne-bebek-gruplari', 'whatsapp-basketbol-gruplari', 'whatsapp-dating-gruplari',
              'whatsapp-doktor-gruplari', 'whatsapp-kitap-gruplari', 'whatsapp-kosu-gruplari',
              'whatsapp-musik-gruplari', 'whatsapp-saglik-gruplari', 'whatsapp-voleybol-kanallari',
              'whatsapp-yapay-zeka-gruplari', 'whatsapp-yoga-gruplari']
for t in EMPTY_TAGS:
    leads.append({'url': f'https://whatsappkanali.com/etiket/{t}',
                  'what': 'READ 2026-11-05 via curl and browser text fetch: the site itself states no active groups are listed under this tag (empty archive, not JS-gated). Do not re-fetch unless the site changes.'})
leads.append({'url': 'https://chat.whatsapp.com/',
              'what': 'VERIFICATION METHOD WORKS AGAIN as of 2026-11-05: control live code KrDwdK8EIkB6vgauHg5M7N returns non-empty og:title, a fake code returns empty og:title (the opposite of the Nov 4 finding, when every code returned an empty og:title). The og:title check is usable again; 30/77 codes verified this run, 47 stayed empty on two attempts.'})
leads.append({'url': 'https://whatsappkanali.com/kategori/cinsel-fetis',
              'what': 'SKIPPED BY RULE (carried from team05): adult categories (cinsel-fetis, onlyfans-icerik, swinger-takas, fantezi-hikaye, cinsel-saglik) and gambling categories (iddaa, casino-canli-casino, kumar-sans-oyunlari, kumar-slot, spor-bahisleri-oran-analizi, at-yarisi) exist but are excluded per content rules. Do not scrape.'})

json.dump(verified, open(os.path.join(BASE, 'team17-whatsappkanali.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(pending, open(os.path.join(BASE, 'team17-unverified-pending.json'), 'w'), ensure_ascii=False, indent=1)
json.dump(leads, open(os.path.join(BASE, 'team17-leads.json'), 'w'), ensure_ascii=False, indent=1)
print(f'verified={len(verified)} pending={len(pending)} leads={len(leads)}')
