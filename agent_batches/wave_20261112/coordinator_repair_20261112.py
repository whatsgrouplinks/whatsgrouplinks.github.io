#!/usr/bin/env python3
"""Wave 20261112 coordinator repair — false-positive restores.
Mirrors coordinator_repair_20261111.py. The automated screen flagged 14 items
that are KEEP under the task rules; each was individually reviewed (name +
full description in the team file):
- 6x team05 'porn:porn' — descriptions are PROHIBITION sentences the stripper
  missed ('proibido' PT spelling not in strip list; 'sem porno' not in list;
  stylized-Unicode 'SEM PORNO'; '❌ porno/hentai' fragment): Amizade
  Verdadeira, Grupo de paranormal, Chat liberado, Estrelas Brilhantes,
  CAFEZINHO, CONVERSAS E NAMORO.
- team05 'House animes' [18+] — desc bans 18+ content ('não pode NADA que é 18+').
- team05 'GRUPO DARK' [🔞] + 'Compra de Bebidas alcoólicas' [🔞] — 18+/🔞 age
  gates on non-porn groups (dark-reality videos; alcohol sales) — last wave
  restored the same class (hookah, LGBTQ social, friendship/chat).
- team05 'ORG LAUGH MÉTODOS' [phone] — digit run is a URL id (1kkcpf.com
  ?id=11416035), not a phone number; description normalized to template.
- team16 'LGBTQ MUNDIAL 🚫NO NUDES' [nude] — prohibition is IN THE NAME.
- team16 'WATA Miau 😺🔞' [🔞] — cat group, 🔞 age gate, clean description.
- team32 'Shopee Tanam 🍇🍈🍉' [🍈] — fruit emojis in a plant-game context.
- team03 '🇳🇬 fun group 18+' [18+] — generic fun group, 18+ age gate only.
KEPT EXCLUDED (reviewed, not restored): 'Teen 18+ only' (teen+18+ ambiguity),
'Tiktok lite 2 K98505992' [phone] (8-digit run indistinguishable from a
personal number), and all explicitly adult/sexual names (call-girl, bokep,
Brazzers, Ullu/Alt Balaji, Putaria, video-call 18+, etc.).
"""
import json, os

WAVE_DIR = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112'
SITE = '/home/hatch/workspace/whatsapp-groups-site'
union = set(json.load(open(os.path.join(SITE, '.existing_codes.json'))))

RESTORES = {
    # code: (team, reason)
    'Dtg17f3Hryq1XM9XjcMhcw': (5, 'prohibition sentence: PROIBIDO QUALQUER TIPO DE PORNOGRAFIA'),
    'LTxVxNv8GMvAwJUmYTUBUx': (5, 'prohibition sentence: Proibido Assédio Pornografia Pedófila'),
    'J1yhn70VwgJCFDHu6aCaGN': (5, 'prohibition fragment: ❌ porno/hentai rules'),
    'C4JZhXXoy8e11AkmCkvH0P': (5, 'prohibition sentence: REGRAS DO GRUPO: SEM PORNO'),
    'LjLOytOdTJh8A1DlOvs4ul': (5, 'prohibition sentence: proibido:pornografia,hentai'),
    'KmZwA3bCT9O0vqgbxz4sqI': (5, 'prohibition sentence: sem porno'),
    'IFudvZ45gbiIwFSh4oKvGE': (5, 'prohibition: não pode NADA que é 18+ (18+ content banned)'),
    'BLwtFQt47paJqiQcZDN44W': (5, '18+/🔞 age gate on non-porn dark-reality-video group'),
    'B4ljS2IWJzzC7y7pqT7KwR': (5, '18+/🔞 age gate on non-porn alcohol-sales group'),
    'BNE0W90E6VE0WRlOyi8oyL': (5, 'digit run is a URL id, not a phone number; desc normalized'),
    'CYjh8YprII8GQ08sOuahLW': (16, 'prohibition in name: 🚫NO NUDES'),
    'EPlnJUwsPf6KaCDI4zuWXF': (16, '🔞 age gate on non-porn cat group'),
    'KDjyNz7lzt5BMotyWRlBmL': (32, 'fruit emojis in Shopee plant-game context'),
    'LtXOkOeUYi07UVHs6eEbEw': (3, '18+ age gate on generic fun group, no sexual content'),
}

TEAM_FILES = {
    3: 'team03-tglinkhub-candidates.json',
    5: 'team05-leads-slice4.json',
    16: 'team16-whtsclub-candidates.json',
    32: 'team32-newdirs-seasia-candidates.json',
}
bycode = {}
for t, f in TEAM_FILES.items():
    for it in json.load(open(os.path.join(WAVE_DIR, f))):
        bycode[it['invite'].split('/')[-1]] = (t, it)

clean = json.load(open(os.path.join(WAVE_DIR, 'wave_20261112_clean.json')))
clean_teams = json.load(open(os.path.join(WAVE_DIR, 'wave_20261112_clean_teams.json')))
excluded = json.load(open(os.path.join(WAVE_DIR, 'wave_20261112_excluded.json')))
clean_codes = {c['invite'].split('/')[-1] for c in clean}

restored = []
for code, (team, reason) in RESTORES.items():
    assert code not in union, f'{code} in union!'
    assert code not in clean_codes, f'{code} already clean!'
    t, it = bycode[code]
    assert t == team, f'{code} team mismatch {t} != {team}'
    name = str(it['name']).strip()
    desc = str(it.get('description', '')).strip()
    if not desc.startswith('Join '):
        desc = f"Join {name}, a WhatsApp group listed under {it['category']}."
    clean.append({'name': name, 'category': it['category'], 'country': str(it.get('country', '')).strip(),
                  'description': desc, 'invite': f'https://chat.whatsapp.com/{code}'})
    clean_teams[code] = team
    restored.append({'code': code, 'team': team, 'name': name, 'reason': reason})
    print('RESTORED', team, code, name, '-', reason)

excluded = [e for e in excluded if e['code'] not in RESTORES]
json.dump(clean, open(os.path.join(WAVE_DIR, 'wave_20261112_clean.json'), 'w'), indent=1, ensure_ascii=False)
json.dump(clean_teams, open(os.path.join(WAVE_DIR, 'wave_20261112_clean_teams.json'), 'w'), indent=1)
json.dump(excluded, open(os.path.join(WAVE_DIR, 'wave_20261112_excluded.json'), 'w'), indent=1, ensure_ascii=False)
json.dump(restored, open(os.path.join(WAVE_DIR, 'wave_20261112_restored.json'), 'w'), indent=1, ensure_ascii=False)
print('restored:', len(restored), '| clean now:', len(clean), '| excluded now:', len(excluded))
