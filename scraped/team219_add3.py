#!/usr/bin/env python3
"""TEAM 219 add-on batch 3."""
import json, os, pickle, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPED = os.path.join(BASE, 'scraped')
OUT = os.path.join(SCRAPED, 'team219-friendship.json')
PKL = os.path.join(SCRAPED, '_seen_all_codes.pkl')

seen = pickle.load(open(PKL, 'rb'))
existing = json.load(open(OUT, encoding='utf-8'))
have = set(seen) | {e['invite'].rsplit('/', 1)[-1] for e in existing}

ADD = [
("Need a girlfriend", "L1niLqSVFsFB0KmRuTT8hi", "Telugu girls friendship group"),
("Bangalore telugu people", "HMYqR1iGQwO9QCF0jEeALr", "Telugu community social group in Bangalore"),
("cute Pakistani boys", "Hkh74wtjK8gEfMBME5ch5u", "Pakistani boys friendship group"),
("Love Express", "H6JjQVX4eEe192W0naJN8S", "Fun and friendship group"),
("Ishq", "JXtBRH2JEi48t3V6QXOLyk", "Social and friendship group"),
("Makki TV Community Group 1", "KqBCFYhdqpBHhtk26Fyo4M", "Community social group"),
("Makki TV Community Group 2", "IXrkfC9JdHB7DyosF3inHx", "Community social group"),
("Makki TV Community Group 3", "IcIoTyK6pXXBtzYCIvS7Sc", "Community social group"),
("Makki TV Community Group 4", "ETdU4XnSdPuHkX8CGSwMNp", "Community social group"),
("Makki TV Community Group 5", "DrSUsQuLz261COargcJdgQ", "Community social group"),
("Makki TV Community Group 6", "LPrrCYOILwwJA0uoD7K24c", "Community social group"),
("Makki TV Community Group 7", "JbMz1MM0PSXDUWtciCe1Oe", "Community social group"),
("Makki TV Community Group 8", "J875tWUfawwG8795Q69KDp", "Community social group"),
("Makki TV Community Group 9", "GkC3sBgdYu3C7Ls3r4V901", "Community social group"),
("Makki TV Community Group 10", "BiRP9TiPber3vrtmxBDCrQ", "Community social group"),
("Makki TV Community Group 11", "E28VLxoMU9b51or9ZZELZB", "Community social group"),
("Makki TV Community Group 12", "CxZBDXOAHqdIDWW259oqDl", "Community social group"),
("Makki TV Community Group 13", "CCU6mZgKx6JEw6cqKxFUpy", "Community social group"),
("Makki TV Community Group 14", "BOnPtPRIWPnDjdsJ5WBHwp", "Community social group"),
("Makki TV Community Group 15", "G4Q24RqSNsY2pV6zqKL7H7", "Community social group"),
("Makki TV Community Group 16", "JYQPTxT0MC2EEEWMlhwdNx", "Community social group"),
("Makki TV Community Group 17", "C7X6ieNFQ9HD2KGRyDOErO", "Community social group"),
("Makki TV Community Group 18", "KaQVOm45VRABttUxzfM37p", "Community social group"),
("College girls", "CnBb42stLyp38BxM1LaHCN", "College girls friendship group"),
("queens only", "BAcl0xpcOLUBnmO44Eepm6", "Girls only friendship group"),
("Crush", "KP77NlW1dcx8sQwSptEGVw", "Friendship and crush chat group"),
]

PORN = re.compile(r'(?i)\b(porn|pornhub|xxx|sexy|nudes?\b|escorts?|call\s*girls?|adult\s*(video|chat|dating)|hentai|onlyfans|cam\s*girls?|paid\s*girl|hotel\s*girl|girl\s*(photo|number|phone))\b')
added = skipped_seen = 0
for name, code, desc in ADD:
    code = code.strip()
    if code in have:
        skipped_seen += 1
        continue
    if PORN.search(name + ' ' + desc):
        continue
    have.add(code)
    existing.append({"name": name, "invite": f"https://chat.whatsapp.com/{code}", "desc": desc, "cat": "Friendship"})
    added += 1

json.dump(existing, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"added={added} skipped_seen={skipped_seen} total={len(existing)}")
