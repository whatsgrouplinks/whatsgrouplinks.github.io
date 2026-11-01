#!/usr/bin/env python3
"""TEAM 219 add-on: merge additional entries into team219-friendship.json with dedupe."""
import json, os, pickle, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPED = os.path.join(BASE, 'scraped')
OUT = os.path.join(SCRAPED, 'team219-friendship.json')
PKL = os.path.join(SCRAPED, '_seen_all_codes.pkl')

seen = pickle.load(open(PKL, 'rb'))
existing = json.load(open(OUT, encoding='utf-8'))
have = set(seen) | {e['invite'].rsplit('/', 1)[-1] for e in existing}

ADD = [
("Utrechters", "GopSuzuFKRBKeYVKQrX4pE", "Social community in Utrecht for locals and expats"),
("Amsterdam International Expat Guild", "FEYVSvlUYsZJkF60I5zIhI", "International expat social events in Amsterdam"),
("New Zealand Connect and Support", "FSjW5rPwcBSBQdRwexnxME", "Newcomers support and friendship community in New Zealand"),
("Attractive", "LQudCCQ7msO542urRvFkMl", "Pakistani girls friendship group"),
("Feelings", "Hb2Au4NxbwR2OtcSdvWv73", "Pakistani girls chat and friendship group"),
("Mehfil-e-Ishq", "E2Ig5xADIdEEkDElHhBHuz", "Pakistani girls social gathering group"),
("Main Pakistan Hoon", "DNZBa2tHa2l2Tq0SbBoGJa", "Pakistani community friendship group"),
("All my Jigar", "IShmjxNylUnEfSn1pejylI", "Friends chat group in Lahore"),
("Friends Lahore", "6WZAFy0jhj9DnhRWVmZlU3", "Friends chat group in Lahore"),
("Rock stars", "4fINZk8tBuqGrOpyEtFLcF", "Social group in Lahore"),
("Pakistan Community", "63jNy98YaQkGPTCqh29z0g", "Pakistani community friendship group"),
("Kerala Girls Group", "KJMeeUgPsds8rb7GuYGD0y", "Kerala girls friendship group"),
("Kerala Girls Group 2", "DIyAGbqUAw10fOWEa5FKBo", "Kerala girls friendship group"),
("Yadav Samaj", "LpNCUcoYZWp2Mu5Zt05r0u", "Yadav community friendship group"),
("Pyaar Tune Kya Kiya", "JMg9uMzoiai8f6eY74AHX2", "Friendship and love chat group"),
("Lovely Gals", "7lHMvuwylszEcQcROeflMK", "Girls friendship group"),
("GIRLFRIENDS", "4MIObDm6EOs6ihV5iAAMYl", "Girls friendship group"),
("Waqas Shah Group Boy", "CK63p68R2xO00ZbSWSqjzU", "Boys friendship group"),
("Love is Friendship", "0bsOwX5YKhCA3rQnZHijoJ", "Friendship chat group"),
("Group me koi Galti Nahi", "7yf9wefBEXxLoZmLsUFwPG", "Friendship chat group"),
("Girl WhatsApp Group Link", "BRFnRqNCcvdHH2ebgsx1sy", "Girls friendship group"),
("Girl WhatsApp Group Link 2", "80dYUNUgMbPGHPukFVe79W", "Girls friendship group"),
("College Students", "1GdJRPhXXgX9KAy6UcvxiK", "College students friendship group"),
("FRIENDS INDIA", "1X17op7NCyp9r6SgZB2xm0", "Indian friendship group"),
("Hum Jaat Ke Chore", "BFbL10wgeOoDn2iy2NgMY8", "Jaat community friendship group"),
("Beautiful Group", "9oOTJn6xo9LBbO9V78xV8F", "Girls friendship group"),
("Only Indian Girl", "ICpkYHEwhlK0DTFyxc1F83", "Indian girls friendship group"),
("Girl WhatsApp Group Join", "4Qm7RkXXzkDKd2a9uVtRjJ", "Girls friendship group"),
("Fun for Everyone", "JY8woxUmsOVJMGxGREw05E", "Fun and friendship chat group"),
("Teen Thrive Podcast Group", "LviHs81wjbKK5Hpo56Mk5v", "Teen friendship and relationships community"),
]

PORN = re.compile(r'(?i)\b(porn|pornhub|xxx|sexy|nudes?\b|escorts?|call\s*girls?|adult\s*(video|chat|dating)|hentai|onlyfans|cam\s*girls?|paid\s*girl|hotel\s*girl|girl\s*(photo|number|phone))\b')
added = 0
for name, code, desc in ADD:
    code = code.strip()
    if code in have:
        continue
    if PORN.search(name + ' ' + desc):
        continue
    have.add(code)
    existing.append({"name": name, "invite": f"https://chat.whatsapp.com/{code}", "desc": desc, "cat": "Friendship"})
    added += 1

json.dump(existing, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"added={added} total={len(existing)}")
