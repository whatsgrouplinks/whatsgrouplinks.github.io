#!/usr/bin/env python3
"""TEAM 219 (friendship): friendship/social WhatsApp directory harvest.
Dedupes by invite code vs _seen_all_codes.pkl.
Output: scraped/team219-friendship.json  [{name, invite, desc, cat}]"""
import re, json, os, pickle

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPED = os.path.join(BASE, 'scraped')
OUT = os.path.join(SCRAPED, 'team219-friendship.json')
PKL = os.path.join(SCRAPED, '_seen_all_codes.pkl')

seen = pickle.load(open(PKL, 'rb'))

# (name, code, desc)
RAW = [
# --- meetup/eventbrite social communities ---
("Friendship Network UK", "FW8qb8v48J0LGcU0GuGujz", "Make new friends community in the UK"),
("International Friends Lisbon", "LS9Xf3IJJt1LlNDBjnmhDV", "International friends social community in Lisbon"),
("Make New Friends Barcelona", "K1wNcN4imNSDxbCPKo7FZi", "General group for meeting new friends in Barcelona"),
("Barcelona Girls Social", "FiOlvsLw5n39TQXNLoLMp9", "Girls-only social group for meeting new friends in Barcelona"),
("Barcelona Social Party Info", "L7CsDxU9Fel96XJrXYa1", "Free party info and social meetups in Barcelona"),
("Lisbon Zumba Party and Networking", "DNgG6sgxSJoIa0roUmQh28", "Weekly social meetup and networking in Lisbon"),
("Austell Pick-Up Soccer", "H1T99v6Qv9YCELAnHWjEPh", "Friendly co-ed soccer community for meeting new friends"),
("BMH Film Club", "DwqgDUBUwFMC6lm5uYsrj2", "Film club WhatsApp community for movie lovers"),
("Black Girls Hike Community", "D5JSU3vPGKBLdLfB6IwSIW", "Community for Black women who love hiking and social walks"),
("Expats in Tbilisi", "IUnd6m86Ado8R8FFaeGsdC", "Expats and internationals social chat in Tbilisi"),
("Internationals in Paris", "ITesisMThOFAyNRUJ6uECN", "International social community in Paris"),
("Socializus Paris Organizers", "KtR79S8Obfs3WTPTIBsoCm", "Social event organizers community in Paris"),
("Cardiff International Friends", "BgUuIQt5JokC7l6v87mIM1", "International friends community in Cardiff"),
("Linkar Manchester Social", "C6esyw19AuZ65iJwWb9AhV", "Social events and activities community in Manchester"),
("Looking for Friends Canada", "BzB8ShJaxJx73C4qFvhu33", "Meetup group for making new friends in Canada"),
("Cardiff Childfree Women", "KZmv4e5y7nxFKG53okayS6", "Women's social group for impromptu meetups in Cardiff"),
("New in Lima", "DNmzkmlYbWz8whoeAcof7R", "Expats and newcomers social community in Lima"),
("International Friends Nuremberg", "LUKQoDocPOf5YoAvBWd32S", "International social community in Nuremberg"),
("New in Barcelona Events", "FvnGj8W9tSK2mXyWTltgJo", "Social events WhatsApp group in Barcelona"),
("New in Barcelona Chat", "J98zxKDsjHA1qGcqdQOU6x", "Chat group for meeting people in Barcelona"),
("THECLUB Dubai Friends", "G1p2svvNGscK3rHVx5Hky0", "Poolside friends and social meetups in Dubai"),
("Single and Social UK", "CmembV4Us1t23glqolnuZw", "Singles social parties and events in Bucks Berks"),
("London Social Skills Chat", "H3mLsvkNJwpCcOELRX28nQ", "Social skills and conversation community in London"),
("LDN Social 20s-30s", "JZSwtzwePorF2gP2eZK2Qa", "London social community for people in their 20s and 30s"),
("Philosophy in the Park", "CdFaxJHbeOw9UOfuk7spiK", "Philosophy discussion community in London"),
# --- alatekno ladies page ---
("Girls Group", "L7OmIWeQsCY6e0xLt5HLx4", "Girls friendship and chat group"),
("Only Girls Status Group", "JiF49f3QjSE5Z9PmBzmZBb", "Girls-only status and chat group"),
("Girl Chat", "C6YXq4oQIDeF26pGM0NGz8", "Girls chat and friendship group"),
("True Love Hub", "KkAZ8zL2ncUAgDp4EcGFvf", "Friendship and love chat group"),
("Pakistani Cute Girls", "Fe1dPKikn9I56os3Ofsx2j", "Pakistani girls friendship group"),
# --- Bhavnagar ---
("Bhavnagar College Girl", "BiDIdkLtNxl6XMOYuuAT4", "College girls friendship group in Bhavnagar"),
("Bhavnagar Dating Girl", "GjVsIV74lScACa6JJtfHbF", "Dating and friendship group in Bhavnagar"),
("Bhavnagar Girl Facebook", "BICZtOF5YzXDtyQJ5zUm6J", "Girls social group in Bhavnagar"),
("Bhavnagar Girl Instagram", "Ioq7Q3kFSfRKyqjUHM7bDN", "Girls social group in Bhavnagar"),
("Bhavnagar Girl Chat Group", "J0FhjFYpAsOBABgzKj8oUe", "Girls chat and friendship group in Bhavnagar"),
("Bhavnagar Girl For Friendship", "6ovAnkly4VXHvnoA8Mim6p", "Friendship group for girls in Bhavnagar"),
("Bhavnagar Girl Twitter", "La2d2NVHxncAwEaqUdyHoA", "Girls social group in Bhavnagar"),
("Bhavnagar Girl Dating", "I2k898yA7hL34AUWcobQyj", "Dating and friendship group in Bhavnagar"),
("Bhavnagar Cute Girl", "HDkiotQGTV26A0F0TKw3E3", "Girls friendship group in Bhavnagar"),
("Bhavnagar Girl College", "GpxmNOLwCxX89zgEuUYFZh", "College girls friendship group in Bhavnagar"),
("Bhavnagar Dating", "3qfg8t6KXSu3CvPB1Y5NnI", "Dating and friendship group in Bhavnagar"),
("Bhavnagar Girls", "1goz1ezQD7M48pLjDr6GCf", "Girls friendship group in Bhavnagar"),
("Bhavnagar Lesbian", "GDIMirQjYObGdN139Lqhvb", "LGBT friendship community in Bhavnagar"),
("Bhavnagar Gay", "ES5zDCwEmaw1SQDq0844MA", "Gay friendship community in Bhavnagar"),
("Bhavnagar LGBT", "FMfGsH4DIIxI0ZTCExliX5", "LGBT friendship community in Bhavnagar"),
("Bhavnagar Boys", "LKlibbXxwCyBkEwm05gigV", "Boys friendship group in Bhavnagar"),
# --- Bangalore ---
("Friends", "FrlOJrBYr38HfTbJcxSSeW", "Friends chat group in Bangalore"),
("Bangalore Girls", "LjtD0nYXOBi7HsNUCCusOU", "Bangalore girls friendship group"),
("Best Bangalore PG Girls", "7Bmqx4IOrlGAbpHU5Zc41I", "Bangalore girls friendship group"),
("Best Bangalore PG Girls 2", "CrAjC59LSguDuisCVzix5x", "Bangalore girls friendship group"),
("Bengaluru Events", "LyCGQxAldya0onzuQWDy1N", "Events and social meetups in Bengaluru"),
("Gutsytribe Events", "7caOGKWIJms9F2SVb6eY1J", "Events and social community in Bengaluru"),
("Treks Bangalore", "GhPnLrWgdLD4URnlsy8yTk", "Trekking and outdoor social group in Bangalore"),
("Trikon Bangalore", "LaDyXey9uFH8lJr7pLZpJr", "Trekking community in Bangalore"),
("Metro Events Bangalore", "1DU3AsenyVLCuZfPvsSke1", "Events community in Bangalore"),
("New in City Time to Party", "7YxhYo7koTq5N1GDyv3SVi", "Party and social meetups for newcomers in Bangalore"),
("Bangalore Events 2", "39MhRBV8AhLDuqVHxjJux1", "Events and social group in Bangalore"),
("Only Bangalore Events", "JVQzokMAOxQ9Rl5Q9GBbgJ", "Events community in Bangalore"),
("Nightlife Party Bangalore", "Gddh2pS4smj0UqDkJtWj8I", "Nightlife party updates in Bangalore"),
("KA53 Mens Club", "JufBpgVTiAYGWh87naEDNq", "Men's social club in Bangalore"),
("DIVA", "L9zYeZ5KZgV8EasHnzitDD", "Girls social group in Bangalore"),
# --- Amritsar ---
("Sanjha Punjab Zindabad", "BV5rpIyrJfq2l9cK2dVjPb", "Punjabi community friendship group"),
("Jatt Boys Putt Jatta Da", "Lss3v6LBx6u8YVEourbLCE", "Punjabi boys friendship group"),
("Jatt", "6aXuV5Adx32A01KMKsdPBG", "Punjabi friendship group"),
("Dil De Halaat", "G5I56gz3Aqq0qfKIu9otvM", "Punjabi social chat group"),
("Malwa Zone", "IfzpMEFKHtr3ndrxLIWgPd", "Malwa region friendship group"),
("Punjab Hub Zone", "J4Xal2W1oCg0qc69ytmqmj", "Punjab community friendship group"),
]

# Ahmedabad page anonymous raw codes (all from a girls friendship page)
AHMEDABAD_CODES = """8pScR8YgiKU8spvEZ77q5q HcI3tGiNIYTLi3Iqn9PIdB KRS5X9nMbwYF2Opb6xpPyM
KjRXmDO5mCyAqzjjfotcjZ J2KgTydCzhC6gnt3Xw3TFk L1epPiKqbzq0XiprkLvUG1 9okeRIr2f0BL7dqN6RjScU
I2RBaAKgjKG5bv0zgrdyd2 FRdNJMNSs6UEbi4LxCdUid KGVqt85a2HRF34nn8TN03g KEhxpJuE1fv2zrBii9UTiE
GDl3XS5YmtWALk5NTjFP3B DkOg25N3Ar5BS0Hh5BggDp 5yOzE1iVL5vJWpK9Y5cobh 9sy2BKrxjHw2HEMpmxNGqU
GkvT57UxuCn66SdKVs5KHg IqG75YugkPWAK2Q4yzq3pz K9PQPfmi52uCqbqA1BWY4g KSN4fgAu9naEb2g9BbSemt
EDHR9DmJkfgKbA32IqBoeB GWCozldv84j5s1jEvJzrKG EGGWukWwdqlA0cDIPOpKWu KWLJTxbkpwdJXxQYlJnbLR
HixzXfAUpW9CkCGkWkeHqb JvWMS3QQKCO7V9ibvypcGi 0v3wGTcOBC3BFoAbzBitQo AbGZ1nsW61P4SehsJxRbpk
2VKnappjTl7JNJ4U5luDpy 9hC0zf5hVw63hOA1VY2B9A 67OgM0bO4XP2G9P1Ze6Q7d G179OZ5WA6p7MmfXK5FBga
DOCVYl8qs1WG8NL0zToAaT FiDNXVsqfPiEY1RMXA2IWM Gs0cS3ihPGA5OEuZNcFxQG J5xjy8Vbj2mC5te8DsEnuj
FXrJDU3UdN84jILCFCMava LnRsQHHbQxF580yDvL6k8b KqRDUkfY12F61aFScr8kG3 HhkEh7GXE7SDvjWV6emmcw
3A8zgvxpuXjKXL8g0Zpmbz G8h7sLHcEPm8N6zEAyRU9t HZ4gj7gpG9oLnxLLHXRB9i IIrpiYE1o0r84Mva6mTtAo
CW7KbM2mSrm86TMNGxBpOB Fx01vAgt6SsHZ8Yr1o48gT HlYab3RGNOE7AWAkLiPsfX BtJAy4bmyMlBgmxfHaFU3f
B8gwDnqCJZZ3FjknOAYsS8 1qRdJ3PJDHUFQ2p7QpQ29U 0cmOhJSppgTIBDZ6bRwQ2p CSj49b7RAvi4JwSX1PgP2a
4754jA8bFyM5FkSJ7KarLo G72DRQQF4ak8UEBslT4sQ7 BODegzT65iF0q4oetSVkff Hi0DX69ofCU9ONjdrJIZ40
DbNwkHb5NMY1KUg8I8Is0Z EB2xHBeg1mr0OvMsaV6y8r 43ISNYEMyRSLvNiCsf4esy GL6GYldTK1gElzMXAocQlY
HxoYyOs5Tb6813tDyuNasE Bi0mbYNigij9NurYx2fc1n LNz1FvPK1MoEIr1wwze60U""".split()
for i, code in enumerate(AHMEDABAD_CODES, 1):
    RAW.append((f"Ahmedabad Girls Group {i}", code, "Ahmedabad girls friendship and social chat group"))

CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{16,})')
PORN = re.compile(r'(?i)\b(porn|pornhub|xxx|sexy|nudes?\b|escorts?|call\s*girls?|adult\s*(video|chat|dating)|hentai|onlyfans|cam\s*girls?|paid\s*girl|hotel\s*girl|girl\s*(photo|number|phone))\b')

out, seen_here = [], set()
skipped_porn, skipped_seen, skipped_dup = 0, 0, 0
for name, code, desc in RAW:
    code = code.strip()
    if not code:
        continue
    if code in seen or code in seen_here:
        skipped_seen += 1
        continue
    if PORN.search(name + ' ' + desc):
        skipped_porn += 1
        continue
    seen_here.add(code)
    out.append({"name": name.strip(),
                "invite": f"https://chat.whatsapp.com/{code}",
                "desc": desc.strip(),
                "cat": "Friendship"})

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print(f"raw={len(RAW)} new={len(out)} skipped_seen={skipped_seen} skipped_porn={skipped_porn} dup_in_batch={skipped_dup}")
print("saved", OUT)
