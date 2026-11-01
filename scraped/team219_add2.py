#!/usr/bin/env python3
"""TEAM 219 add-on batch 2."""
import json, os, pickle, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPED = os.path.join(BASE, 'scraped')
OUT = os.path.join(SCRAPED, 'team219-friendship.json')
PKL = os.path.join(SCRAPED, '_seen_all_codes.pkl')

seen = pickle.load(open(PKL, 'rb'))
existing = json.load(open(OUT, encoding='utf-8'))
have = set(seen) | {e['invite'].rsplit('/', 1)[-1] for e in existing}

ADD = [
("Malwa Zone", "IfzpMEFKHtr3ndrxLIWgPd", "Malwa zone community social group"),
("Punjab Hub Zone", "J4Xal2W1oCg0qc69ytmqmj", "Punjab hub community group"),
("Sanjha Punjab Zindabad", "BV5rpIyrJfq2l9cK2dVjPb", "Punjabi community friendship group"),
("Jatt boys putt jatta da", "Lss3v6LBx6u8YVEourbLCE", "Jatt community social group"),
("Jatt", "6aXuV5Adx32A01KMKsdPBG", "Jatt community social group"),
("Teamex family group", "HMN700rYzUWL5BiZmLFLuv", "Family social group"),
("Gujarati preem", "IjACtBWelSP7PG7jahQzX3", "Gujarati love and friendship group"),
("Best Bangalore PG Girls", "7Bmqx4IOrlGAbpHU5Zc41I", "Bangalore PG girls friendship group"),
("Awesome Israeli Singles", "EKx28BajmsHCt8bSWGHlO2", "Israeli singles social group"),
("Bhavnagar College Girl", "BiDIdkLtNxl6XMOYuuAT4", "Bhavnagar college girls friendship group"),
("Bhavnagar Dating Girl", "GjVsIV74lScACa6JJtfHbF", "Bhavnagar dating and friendship group"),
("Bhavnagar Girl Chat Group", "J0FhjFYpAsOBABgzKj8oUe", "Bhavnagar girls chat group"),
("Bhavnagar Girl For Friendship", "6ovAnkly4VXHvnoA8Mim6p", "Bhavnagar friendship group"),
("Bhavnagar Girl Dating", "I2k898yA7hL34AUWcobQyj", "Bhavnagar dating group"),
("Bhavnagar Cute Girl", "HDkiotQGTV26A0F0TKw3E3", "Bhavnagar cute girls friendship group"),
("Bhavnagar Girl College", "GpxmNOLwCxX89zgEuUYFZh", "Bhavnagar college girls friendship group"),
("Bhavnagar Dating", "3qfg8t6KXSu3CvPB1Y5NnI", "Bhavnagar dating and friendship group"),
("Bhavnagar Girls", "1goz1ezQD7M48pLjDr6GCf", "Bhavnagar girls friendship group"),
("Beautiful Girls", "L7OmIWeQsCY6e0xLt5HLx4", "Beautiful girls friendship group"),
("Only girls status group", "JiF49f3QjSE5Z9PmBzmZBb", "Only girls status and friendship group"),
("Girl Chat", "C6YXq4oQIDeF26pGM0NGz8", "Girls chat and friendship group"),
("True Love Hub", "KkAZ8zL2ncUAgDp4EcGFvf", "True love and friendship hub"),
("Pakistani Cute Girl's", "Fe1dPKikn9I56os3Ofsx2j", "Pakistani cute girls friendship group"),
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
