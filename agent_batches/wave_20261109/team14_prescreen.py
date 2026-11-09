#!/usr/bin/env python3
"""Team14 pre-screen: groupssor API fresh-unique entries -> to-verify list.
Drops hard porn/sex/hookup/escort/cam content and B-Love/Forsage/SHEYI-style
crypto-airdrop/free-money scams. Prohibition sentences are stripped BEFORE
screening so a rules line banning such content cannot flag the group.
"""
import json, re

SRC = 'team14_fresh_unique.json'
OUT_VERIFY = 'team14_to_verify.json'
OUT_DROPPED = 'team14_dropped_prescreen.json'

# sentences that PROHIBIT content -> strip before screening
PROHIB = re.compile(
    r"(don't|do not|dont|not allowed|no |never|prohibit|forbidden|strictly|mana|na karein|na karen|mat karein|not share|share na)\b.{0,60}"
    r"(porn|sex|xxx|adult|nude|abuse|galat|gandi|inappropriate|spam|link|advertis)",
    re.I)
PROHIB2 = re.compile(r"\b(no porn|no sex|no adult|no xxx|no nude|porn.*not allowed|sex.*not allowed)\b", re.I)

def strip_prohibitions(text):
    if not text:
        return ''
    parts = re.split(r'(?<=[\n.!?])\s+', text)
    kept = []
    for p in parts:
        if PROHIB.search(p) or PROHIB2.search(p):
            continue
        kept.append(p)
    return ' '.join(kept)

PORN = re.compile(r"""(?ix)
    \bxxx\b | \bxxxx\b | \bxxnxx\b | \bporn\b | porno | \bsex\b | sexy | \bsexy\b
  | hookup | escort | cam[\s\-]?girl | camgirl | video[\s\-]?call[\s\-]?girl
  | phone[\s\-]?sex | sex[\s\-]?chat | sex[\s\-]?video | sex[\s\-]?service
  | nude | nudes | \bfuck\b | horny | masturbat | pussy | \bdick\b
  | baise | \bhot\s+girl\b | \bgirl\s+sex\b | vc[\s\-]?service
  | sex\s+call | video\s+call\s+sex | desi\s+video | \bleaks?\b.*\bhot\b | \bhot\b.*\bleaks?\b
  | jerking | \borgasm\b | \bboobs\b | \bbhabhi\s+sex\b | \bcall\s+girl\b
  | \bsugar\s+daddy\b | \bplayboy\b.*\bsex\b | erotic | \b18\+\b.*\bvideo\b
  | \bxxx\s*video\b | adult[\s\-]?video | adult[\s\-]?content
  | سكس | سکس | جنسی | ننگی | ننگی
  | video[\s\-]?calls?[\s\-]?service | video\s+calls?\s+service | \U0001fac6
  | \bvc\s*\+\s*vd\b | vd\s+only | boys\s+vs\s+girls\s+vc
  | savita\s+bhabhi | सविता | भाभी | bhabhi\s+lovers | tamil\s+akka | tamil\s+ahh
  | leaked?\s+videos? | leak\s+videos? | viral\s+leak | viral\s+child
  | \bhot\s+video\b | vrial\s+video | hot\s+girl | 🥵 | 🔞 | ßex | \bsex\b
  | all[\s']*type\s+video | all\s+categories\s+available
  | ویڈیو\s+کال | وڈیو\s+کال | لڑکی.*(ہاٹ|سروس) | ہاٹ\s+لڑکی
  | photo\s+colection | video\s+call\s+chat\s+service
""")
# 'leaks' alone is ambiguous (exam leaks etc.) - only drop when paired with hot/sex/girl
LEAK_SEX = re.compile(r"(?i)(hot|sex|girl|nude|xxx|porn|desi).{0,30}leak|leak.{0,30}(hot|sex|girl|nude|xxx|porn)", re.I)

SCAM = re.compile(r"""(?ix)
    b[\s\-]?love | forsage | sheyi | \bairdrop[s]?\b | free[\s\-]?money
  | legit[\s\-]?online[\s\-]?update | paying[\s\-]?crypto | fcfs
  | sign[\s\-]?up[\s\-]?bonus | free[\s\-]?daily[\s\-]?updates
  | crypto[\s\-]?offers | giveaway.{0,40}crypto | crypto.{0,40}giveaway
  | earn.{0,30}crypto.{0,30}free | free.{0,30}crypto.{0,30}earn
  | double[\s\-]?your[\s\-]?money | invest.{0,20}\d+x | \bmlm\b
  | naira.{0,30}crypto.{0,30}(update|free|paying)
  | free[\s\-]?earn | zar\s+wallet | \bcarding\b
  | kyc.{0,30}(data|device|fresh|rate) | binance\s+millionaire
  | treasure\s+nova | uchevin | make\s+money\s+online.{0,20}investment
  | investment\s+platform.{0,30}millionaire
""")

JUNK_NAME = re.compile(r"^(xxx|sex|fuck|hot girl|hot|something|all link|hindi|fhhgt|test|asdf|xxx+|tamil|tanveer|tahir|whatsapp group|entertainment website|oo|tami|vrial video|hot video|viral video|new collection|group|join)$", re.I)

def screen(r):
    name = (r.get('name') or '').strip()
    desc = (r.get('description') or '')
    tags = ' '.join(r.get('tags') or [])
    cat = (r.get('category') or '')
    clean_desc = strip_prohibitions(desc)
    hay = f"{name} {clean_desc} {tags} {cat}"
    if PORN.search(hay) or LEAK_SEX.search(hay):
        return 'porn/sex'
    if SCAM.search(hay):
        return 'scam-crypto/airdrop'
    if JUNK_NAME.match(name) or (len(name) <= 3 and len(clean_desc.strip()) < 10):
        return 'junk-name/desc'
    if name.startswith('http'):
        return 'junk-name/desc'
    if len(clean_desc.strip()) < 20 and re.match(r'^(new collection|hi|oo|new|fun|tami|tamil|group|join|genuine|5000)$', clean_desc.strip(), re.I):
        return 'junk-name/desc'
    return None

def main():
    rows = json.load(open(SRC))
    keep, drop = [], []
    for r in rows:
        reason = screen(r)
        if reason:
            drop.append({**r, '_drop_reason': reason})
        else:
            keep.append(r)
    json.dump(keep, open(OUT_VERIFY, 'w'), indent=1, ensure_ascii=False)
    json.dump(drop, open(OUT_DROPPED, 'w'), indent=1, ensure_ascii=False)
    print(f"total={len(rows)} keep={len(keep)} drop={len(drop)}")
    from collections import Counter
    print(Counter(d['_drop_reason'] for d in drop))
    print("kept categories:", Counter(k.get('category') for k in keep))

if __name__ == '__main__':
    main()
