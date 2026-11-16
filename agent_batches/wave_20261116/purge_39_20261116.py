#!/usr/bin/env python3
"""Parent purge 2026-11-16: remove 39 wave-20261116 groups from groups.json.
24 live-verified violations (porn-brand xnxx, 1xbet betting, hashish drugs,
sex-service/jawani/bokep/meetandfuck, heil-hitler hate) + 15 porn-named
invites confirmed dead on 2 reads (brazzers x6, escort, sexchat, adult
videochat, etc.). Codes STAY in .existing_codes.json so they can never
re-enter. 8 bare '18+' age-gate groups KEPT (no explicit porn evidence;
girls groups protected by content rule)."""
import json, re, shutil, os
SITE = '/home/hatch/workspace/whatsapp-groups-site'
WAVE = os.path.join(SITE, 'agent_batches', 'wave_20261116')
REMOVE_SLUGS = """muslim-xnxx-aunty-84930 hot-adult-game-85185 1xbet-burundi-85212
1xbet-melbet-betin-sri-lanka-85235 1xbet-agent-85258 desi-bhabi-ki-jawani-85341
only-xnxx-85445 hashish-and-crystal-available-dubai-and-behrin-ect-85521
1xbet-sri-lanka-85542 18-ada-dideskripsi-85608 hot-tamil-item-service-85641
xnxx-85664 teen-18-only-85728 grup-berbagi-vidio-18-85769 xnxx-videos-85860
adults-18-aunty-groups-85912 group-bokep-18-85941 18-pics-85959
1xbet-burundi-code-promo-1xbuja-86024 xnxx-indonesia-86049 hasina-ki-mast-jawani-86114
meetandfucksa18-86129 group-bokep-18-86161 heil-hitler-93138
brazzers-90163 18-ullu-alt-balaji-hot-2-90167 hot-telugu-girls-only-90176
brazzers-90178 brazzers-video-90215 only-hot-girlz-90233 sex18-90234
indian-gay-18-90240 sexchat-for-nigerian-only-90244 adult-videochat-london-90245
brazzers-group-90251 brazzers-premium-videos-90261 brazzers-90268 hd-brazzers-90270
escortzimbabwe-com-90277""".split()
assert len(REMOVE_SLUGS) == 39, len(REMOVE_SLUGS)
groups = json.load(open(f'{SITE}/groups.json'))
before = len(groups)
by_slug = {g['slug']: g for g in groups}
missing = [s for s in REMOVE_SLUGS if s not in by_slug]
assert not missing, f"slugs not in groups.json: {missing}"
removed = [by_slug[s] for s in REMOVE_SLUGS]
shutil.copy(f'{SITE}/groups.json', os.path.join(WAVE, 'groups.json.bak-20261116-prepurge39'))
keep = [g for g in groups if g['slug'] not in set(REMOVE_SLUGS)]
assert len(keep) == before - 39
json.dump(keep, open(f'{SITE}/groups.json', 'w'), ensure_ascii=False)
after = len(json.load(open(f'{SITE}/groups.json')))
print('groups.json:', before, '->', after)
json.dump([{'slug': g['slug'], 'name': g['name'], 'invite': g['invite']} for g in removed],
          open(os.path.join(WAVE, 'purge39_report.json'), 'w'), indent=1, ensure_ascii=False)
print('PURGE OK: removed 39, new total', after)
