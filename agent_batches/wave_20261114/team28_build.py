import json, re

recs = [json.loads(l) for l in open('team28-verify-results.jsonl')]
live = [r for r in recs if r['status'] == 'live']
dead = [r for r in recs if r['status'] == 'dead']
pending = [r for r in recs if r['status'] == 'pending']

# --- content screen on LIVE og:title ---
PORN = re.compile(r'\bxxx\b|porn|sex\s?video|nude|desi\s?bhabhi.*sex', re.I)
SCAM = re.compile(r'airdrop|binary\s?option|free\s?money|double\s?your\s?money|tigrinho|fortune\s?tiger|sinais|plataformas?\s+pagantes|wjbet|casino|slots|betting\s?signal|aviator\s?signal', re.I)

# manual category/country map by code (keyed decisions; default Education for uni societies)
CAT = {
 'FvgBQ0UvpdY21OzptJDZwU': ('Sports','GB'), 'FL2PD7GWwjd2aKyme7RACM': ('Sports','GB'),
 'E1ZaR5WofEz1C3xU2AzQ3U': ('Sports','GB'), 'CrDxzsZ3KiJ0emJkllUAve': ('Sports','GB'),
 'CDwNO2tf8AI9ZiutNM2kIV': ('Sports','GB'), 'LhDIOiEcwNN4na1aZrEI4P': ('Sports','GB'),
 'G0ooua3NTPH8i0RvzBkiX7': ('Sports','GB'), 'DZ3l556AGvuKNBpQTTwZtx': ('Sports','GB'),
 '1MKaWnKNVbnIRYx6wESqXe': ('Sports','GB'), 'HsUKztMf6SI55q24fb2LzI': ('Sports','GB'),
 'CsWE94WgCTMIfgiqzK7aP0': ('Sports','GB'),
 'F7aarfm6DcE7HKWqCCt5SZ': ('Education','GB'), 'EjfyIUFXUCRE4kcw2YnGkH': ('Education','GB'),
 'KqK9azIxO9jDsUuzeN3JkR': ('Education','GB'), 'DPsPMxOw7NCGhUaM7m8s9U': ('Entertainment','GB'),
 'C7KIqHiJD8SAY03fVUVTuH': ('Entertainment','GB'), 'LOebxtcsfnO34SGfasq7vM': ('Education','GB'),
 'DP2s94tbiie6LLVM7p3pyl': ('Education','GB'), 'B8qdidjr3WSJkBzkcS4tgl': ('Community & Social','GB'),
 'HWnbDYHsfwCFNbzpt9OVdl': ('Entertainment','GB'), 'Ig9IXrdn3mv7oI7WZBKReB': ('Education','GB'),
 'BfDoRpFqRLk8mPRETCCJ5L': ('Education','GB'), 'Fp5TiJChjCZLSagMZAqKOd': ('Education','GB'),
 'CSglcHBCH8ZF9uSJuUS852': ('Entertainment','GB'),
 'JgxUO9QNkigEQnOz28QCMe': ('Education','GB'), 'JkDOkCLM5dqLDPUlFk6NrU': ('Entertainment','GB'),
 'HrHKjGgaELjK6iBzA0dG5T': ('Community & Social','GB'), 'IErHlH6Rybu8yrTC0XhNrS': ('Education','GB'),
 'Cj5mresdsllLEcs7Qj09fl': ('Education','GB'), 'IT6yVEvAWxbEvT9wWfcTGv': ('Community & Social','GB'),
 'CG3HYYBpync5YOQEE9WQX1': ('Education','GB'),
 'GSMOeoUVJHvBeY2Sk7uQfo': ('Jobs','IN'), 'BV49KYsVkAQ6Ie4fRFs0zr': ('Technology',''),
 'KXe3DcSjZ518vPKper42Tu': ('Freelance',''), 'E6zh4BNRQ2pKhI6phQIS3G': ('Freelance',''),
 'KAejjcyhTKaJFBxm0WESnu': ('Community & Social',''), 'G2NrbLdUhQxID1fAiiga86': ('Community & Social',''),
 'IOMHbG75U6i06pmvqc4HMf': ('Education','GB'), 'EUoObOeObP5EvrhRfF2qFr': ('Education','GB'),
 'DyQIjm2U905KUUHIgXofJz': ('Education','GB'), 'Jn87GfxysCi5pyxdF67jYc': ('Education','GB'),
 'Iz0V5UhwDkPAMQYKfgSnRJ': ('Education','GB'), 'CKVWSMF4ql2ATSKLVHhmQz': ('Education','GB'),
 'HmEmd0BqlrI5Ld1OtSVWg3': ('Education','GB'), 'Kz7Hvh2NlgxJINncl9GHJF': ('Education','GB'),
 'DEgXDUP0YND17UHLRCGyyD': ('Education','GB'), 'EI2t7yR6Yyn4yQL7FN9PIb': ('Community & Social','GB'),
 'HTMpK1TykV68KDABw4oAe6': ('Community & Social','GB'), 'G7x084hGQ9A4IBAXIzXLML': ('Community & Social','GB'),
 'KfRy3jG0TmQ0TrVl0ezIkn': ('Community & Social','GB'),
}

DESC_TAIL = {
 'Sports': 'Share match talk, scores and updates with fellow supporters.',
 'Education': 'Share notes, doubts and updates with fellow students.',
 'Entertainment': 'Share and discuss the latest posts, shows and updates with members.',
 'Community & Social': 'Chat, share updates and meet new people in the community.',
 'Jobs': 'Share job openings, career tips and updates with members.',
 'Technology': 'Share tech news, tips and discussions with members.',
 'Freelance': 'Share gigs, clients and tips with fellow freelancers.',
}

def clean_name(t):
    t = re.sub(r'\s+', ' ', t or '').strip(' -|')
    return t

candidates, excluded = [], []
for r in live:
    code, title = r['code'], clean_name(r['title'])
    if PORN.search(title) or SCAM.search(title):
        excluded.append({"code": code, "name": title, "reason": "excluded: 'xxx'/porn in live og:title" if PORN.search(title) else "excluded: scam/casino signal in live og:title", "source": ",".join(r['sources'])})
        continue
    cat, country = CAT.get(code, ('Community & Social', ''))
    tail = DESC_TAIL[cat]
    desc = "Join %s, an active WhatsApp group for %s. %s" % (title, cat.lower(), tail)
    candidates.append({"name": title, "category": cat, "country": country, "description": desc,
                       "invite": "https://chat.whatsapp.com/" + code})

# sanity: no dup codes, valid schema
assert len({c['invite'] for c in candidates}) == len(candidates)
valid_cats = {"Education","Entertainment","Sports","Funny","Community & Social","Finance","Buy Sell","Islamic","Health","News","Jobs","Technology","Gaming","Business","Cooking","Crypto","Poetry","Real Estate","Travel","Scholarship","Freelance","Earning"}
assert all(c['category'] in valid_cats for c in candidates), [c for c in candidates if c['category'] not in valid_cats]
assert all(re.match(r'^[A-Za-z0-9_-]{15,30}$', c['invite'].rsplit('/',1)[-1]) for c in candidates)

json.dump(candidates, open('team28-candidates.json','w'), ensure_ascii=False, indent=1)
json.dump([{"code": r['code'], "reason": r['reason']} for r in pending], open('team28-pending.json','w'), ensure_ascii=False, indent=1)

leads = [
 {"kind":"url","value":"https://www.whtsagroupslinks.com/","note":"Directory homepage returned HTTP 403 on 3 attempts via curl (Nov 14); 0 codes extracted. Needs browser fetch."},
 {"kind":"url","value":"https://grouplinks.co.uk/all-whatsapp-groups/","note":"Fetched OK but page carries 0 direct chat.whatsapp.com codes (hub page linking to topic lists, which were mined directly). No further action."},
 {"kind":"url","value":"https://whatgroups.com/","note":"Carried from team31 (Nov 13): homepage Cloudflare-blocked via curl. Its /islamic-whatsapp-group-link/ subpage fetched fine this wave (169 codes, 3 fresh, all dead). Homepage still needs browser fetch."},
]
json.dump(leads, open('team28-leads.json','w'), ensure_ascii=False, indent=1)

mined = json.load(open('team28-mined.json'))
from collections import Counter
print("candidates:", len(candidates), "| excluded:", len(excluded), "| dead:", len(dead), "| pending:", len(pending))
print("categories:", dict(Counter(c['category'] for c in candidates)))
print("countries:", dict(Counter(c['country'] for c in candidates)))
for e in excluded: print("EXCLUDED:", e)
json.dump({"candidates_n": len(candidates), "excluded": excluded,
           "dead_codes": [r['code'] for r in dead],
           "sources": mined['sources']}, open('team28-build-meta.json','w'), ensure_ascii=False, indent=1)
