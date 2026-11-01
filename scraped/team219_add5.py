#!/usr/bin/env python3
"""TEAM 219 add-on batch 5 (technoearning.in codes)."""
import json, os, pickle, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPED = os.path.join(BASE, 'scraped')
OUT = os.path.join(SCRAPED, 'team219-friendship.json')
PKL = os.path.join(SCRAPED, '_seen_all_codes.pkl')

seen = pickle.load(open(PKL, 'rb'))
existing = json.load(open(OUT, encoding='utf-8'))
have = set(seen) | {e['invite'].rsplit('/', 1)[-1] for e in existing}

ADD = [
("friendship WhatsApp group", "Casp1KjfTZAHs2FBf3wPVa", "Friendship WhatsApp group"),
("girl WhatsApp group join", "DAnbPFDAXD83juydnX9WT0", "Girls friendship group"),
("friendship WhatsApp group", "FX81ZMYmAHuHnXHIBVvGLf", "Friendship WhatsApp group"),
("friendship WhatsApp group", "CqUEDE6XCJ81WPEVFgEHKj", "Friendship WhatsApp group"),
("girl WhatsApp group join", "Kq9Vim42BEBLD5CRFVk7mZ", "Girls friendship group"),
("WhatsApp Social Group 1", "JlWkvZWDAHsIBXTXItxTBq", "Social group"),
("WhatsApp Social Group 2", "KbJmdsPZwmZ1gmc7o6Yj0B", "Social group"),
("WhatsApp Social Group 3", "I2yVKC52yIx7Y1B7et4vNQ", "Social group"),
("WhatsApp Social Group 4", "ELyWQ8hcVKPJ29tIMyZhtl", "Social group"),
("WhatsApp Social Group 5", "L9KXcdqoG1o7OOI1UPMwwi", "Social group"),
("WhatsApp Social Group 6", "GnHrceT2psbFAPtAtj4j3R", "Social group"),
("WhatsApp Social Group 7", "LKNAkhVgITNJb6QKM8slkl", "Social group"),
("WhatsApp Social Group 8", "C47v6hrHR6QBsAVpYCP0X0", "Social group"),
("WhatsApp Social Group 9", "Jg6qEtuUFRvFduGvLBQKPX", "Social group"),
("WhatsApp Social Group 10", "EzcjuMwz6WN652lCnEsZpV", "Social group"),
("WhatsApp Social Group 11", "KXqHKFXCCl28kYWejNV66Ho", "Social group"),
("WhatsApp Social Group 12", "EMrZxpV9B4v5o0Ude3jQ3h", "Social group"),
("WhatsApp Social Group 13", "JKg8o21xv9H4ACxoukzR4O", "Social group"),
("WhatsApp Social Group 14", "EE0xPeuSNvcCgud0ZASc24", "Social group"),
("WhatsApp Social Group 15", "Ddf2aHNpGdw3pQ393hy17v", "Social group"),
("WhatsApp Social Group 16", "LKDViFdFWQ3JIM8ved3guS", "Social group"),
("WhatsApp Social Group 17", "BcU76pWiMlULsEQMc3xV4O", "Social group"),
("WhatsApp Social Group 18", "INfjJMxohIPCPnvEoxfK4O", "Social group"),
("WhatsApp Social Group 19", "IHlzCYBkgP0Av5EqdRORCr", "Social group"),
("WhatsApp Social Group 20", "BClnXRaJTKYLso9vPOyy2k", "Social group"),
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
