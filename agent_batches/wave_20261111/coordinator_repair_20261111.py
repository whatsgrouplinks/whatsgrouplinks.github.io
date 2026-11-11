#!/usr/bin/env python3
"""Wave 20261111 coordinator repair pass.
1. Restores 22 false-positive coordinator-screen drops (prohibition sentences
   the strip missed — Portuguese 'Proibido/Sem/Não pode pornografia',
   'sexta-feira' Friday containing 'sex', 'chuta' verb containing 'chut',
   and 18+/🔞 age-gate markers on non-porn groups: hookah, LGBTQ social,
   friendship/chat age gate per team17's judgement).
2. Re-labels 3 kept exclusions with their real pattern (cheat sales =
   paid hack; 2x betting-platform promo).
3. Drops KkKQsWHSNibIMTA1wPN3h8 from clean (team28-flagged AI-trading
   daily-profits scam; team26 had banked it as Gaming).
Writes updated wave_20261111_clean.json / clean_teams.json / excluded.json.
"""
import json, os

WAVE_DIR = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111'

RESTORE = {
    # team03
    'Jil8DbQnabEEq8Q8V0wdoM': (3, 'team03-leads-slice3.json'),
    'F9ERzi3KAWS831WI3zetmC': (3, 'team03-leads-slice3.json'),
    'BtSpkdBEmkWGZfE5eYjJNk': (3, 'team03-leads-slice3.json'),
    'KIHOLHORne3BFwzTMJAYd1': (3, 'team03-leads-slice3.json'),
    'LF8XXj85F4rA7EQBP0af7R': (3, 'team03-leads-slice3.json'),
    # team04
    'LhktPHMyVIw3HNGzgs3WLG': (4, 'team04-leads-slice4.json'),
    'Bse3e4WDI7R2FFqomlklEV': (4, 'team04-leads-slice4.json'),
    'Jwslr0PlKdNDyoWduTRuFp': (4, 'team04-leads-slice4.json'),
    'CWNsFSjM1FCD51Fe705U0I': (4, 'team04-leads-slice4.json'),
    'H8M6k6YoQsg3iLvQDzOZPq': (4, 'team04-leads-slice4.json'),
    'DlhIqjNtMOvFE26DF7fKo8': (4, 'team04-leads-slice4.json'),
    # team05
    'BIUNWmABlm0Agd8qYLjyqQ': (5, 'team05-leads-slice5.json'),
    'CFZBIB19gX24b9QwNZNvAx': (5, 'team05-leads-slice5.json'),
    'KqcWLEjfkUU84L5QTM96pc': (5, 'team05-leads-slice5.json'),
    'HzGvwRdSQZQGY0hrETLxhc': (5, 'team05-leads-slice5.json'),
    'I9HhmnH68zk1iw2ph0GW5g': (5, 'team05-leads-slice5.json'),
    'Ljc2puafaEc9Q4tI1GmKTe': (5, 'team05-leads-slice5.json'),
    'KPtxBr3AOvQ6qeEgm25W5X': (5, 'team05-leads-slice5.json'),
    'IeEe3m1TGG52iz1y2KgqLH': (5, 'team05-leads-slice5.json'),
    # team06
    'C4wmS1nMmjMKoB7m95HFuh': (6, 'team06-leads-slice6.json'),
    'FeB3NezgPxRK3SDXSc7Qjt': (6, 'team06-leads-slice6.json'),
    # team17
    'FeCmIEiMupt8ahCwcW71Ee': (17, 'team17-groupssor.json'),
}

RELABEL = {
    'G9jiD1qGnuF5ntO7hAxrAS': 'scam:paid-hack-equivalent — VENDA DE XIT cheat sales + 18+ (coordinator: cheat sales = paid hack)',
    'I4f9o1FRgil21n15Y60tkW': 'scam:betting-platform promo pattern — Divulgação De Plataformas 🤑🔞 (coordinator; same pattern team10 excluded as betting)',
    'J8wrWf07YtkLS0xZl5SST7': 'scam:betting-platform promo pattern — Melhor plataforma do Brasil 🔞 (coordinator; team10 also flagged as betting)',
}

DROP_FROM_CLEAN = {
    'KkKQsWHSNibIMTA1wPN3h8': 'scam:AI-trading daily-profits scheme (team28 flag; Arabic name = daily profits from AI trading; team26 had banked it as Gaming)',
}

clean = json.load(open(os.path.join(WAVE_DIR, 'wave_20261111_clean.json')))
teams = json.load(open(os.path.join(WAVE_DIR, 'wave_20261111_clean_teams.json')))
excluded = json.load(open(os.path.join(WAVE_DIR, 'wave_20261111_excluded.json')))

# 1. restores
restored = []
for code, (n, f) in RESTORE.items():
    items = json.load(open(os.path.join(WAVE_DIR, f)))
    hit = [it for it in items if it.get('invite', '').rsplit('/', 1)[-1] == code]
    assert len(hit) == 1, (code, len(hit))
    it = hit[0]
    assert not any(c['invite'].rsplit('/', 1)[-1] == code for c in clean), code
    clean.append({k: v for k, v in it.items()})
    teams[code] = n
    restored.append(code)
excluded = [e for e in excluded if e['code'] not in RESTORE]
print('restored:', len(restored))

# 2. relabels
for e in excluded:
    if e['code'] in RELABEL:
        e['reason'] = RELABEL[e['code']]
        print('relabeled:', e['code'])

# 3. drop from clean
for code, reason in DROP_FROM_CLEAN.items():
    hit = [c for c in clean if c['invite'].rsplit('/', 1)[-1] == code]
    print('drop target in clean:', code, hit)
    if hit:
        rec = hit[0]
        clean = [c for c in clean if c['invite'].rsplit('/', 1)[-1] != code]
        teams.pop(code, None)
        excluded.append({'team': 26, 'code': code, 'name': rec['name'], 'reason': reason})
        print('dropped from clean:', code, rec['name'])

json.dump(clean, open(os.path.join(WAVE_DIR, 'wave_20261111_clean.json'), 'w'), indent=1, ensure_ascii=False)
json.dump(teams, open(os.path.join(WAVE_DIR, 'wave_20261111_clean_teams.json'), 'w'), indent=1)
json.dump(excluded, open(os.path.join(WAVE_DIR, 'wave_20261111_excluded.json'), 'w'), indent=1, ensure_ascii=False)
print('clean now:', len(clean), 'excluded now:', len(excluded))
