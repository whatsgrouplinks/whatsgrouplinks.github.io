#!/usr/bin/env python3
"""Team33: assemble final outputs. Verification impossible (egress stalled) ->
all clean candidates banked as 'transport failure' pending."""
import json, re, os

WORK = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261104/')
SRC3 = os.path.expanduser('~/workspace/whatsapp-groups-site/agent_batches/wave_20261103/')

def chunked_write(path, text, chunk=4000):
    with open(path, 'w') as f:
        for i in range(0, len(text), chunk):
            f.write(text[i:i+chunk])

CATMAP = {
 'Money':'Finance','Entertainment':'Entertainment','Business':'Business','Comedy':'Funny',
 'Education':'Education','News & Politics':'News','Jobs':'Jobs','Online Shopping':'Buy-Sell',
 'Health':'Health','Friendship':'Friendship','Sports & Fitness':'Sports','Gaming':'Gaming',
 'Travel & Tourism':'Travel','Beauty & Fashion':'Other','Quotes':'Other','Flirting':'Friendship',
 'Love & Relationship':'Friendship','Pets & Animals':'Pets','Photography':'Other','Music':'Music',
 'Science & Technology':'Technology','Spiritual':'Other','Earn Money Online':'Finance',
 'Autos & Vehicles':'Other','Food & Recipes':'Food','Fan Club':'Entertainment','Other':'Other',
 'Advertising':'Business','Investment':'Finance','Comics':'Funny','Art & Design':'Other',
 'E':'Other','Deals & Offers':'Buy-Sell',
}
CNAMES = {'PK':'Pakistani','IN':'Indian','LK':'Sri Lankan','ID':'Indonesian','NG':'Nigerian',
 'MY':'Malaysian','BD':'Bangladeshi','US':'American','AE':'Emirati','CA':'Canadian','GB':'British',
 'UG':'Ugandan','JM':'Jamaican','MA':'Moroccan','BR':'Brazilian','SA':'Saudi','ZA':'South African',
 'GH':'Ghanaian','KE':'Kenyan','NP':'Nepali','AU':'Australian','PH':'Filipino','SG':'Singaporean',
 'EG':'Egyptian'}
CWORDS = {'Sports':'sports fans','Gaming':'gamers','Jobs':'job seekers','Education':'learners',
 'Entertainment':'entertainment lovers','Friendship':'friends','News':'news followers',
 'Business':'entrepreneurs','Finance':'finance enthusiasts','Buy-Sell':'buyers and sellers',
 'Health':'health-conscious members','Community':'community members','Technology':'tech enthusiasts',
 'Crypto':'crypto enthusiasts','Travel':'travellers','Music':'music lovers','Movies':'movie fans',
 'Food':'food lovers','Pets':'pet lovers','Funny':'fun lovers','Girls':'members',
 'Regional':'community members','Islamic':'members','Other':'members'}

PORN = re.compile(r'pornhub|xxx|nude|sex video|escort|call girl|fuck|dick|pussy|boobs|\banal\b|\bbokep\b|\bporn\b|\bporno\b|\berotic\b|مزا دینے|مزہ دینے|🥵|🍆|🍑|🔞|💦|👅|👄|💋', re.I)
SCAM = re.compile(r'\bsatta\b|\bmatka\b|money\s*double|double\s*(your|the)\s*money|hyip|paypal\s*(receiver|loader)|free\s*money|investment\s*double|crypto\s*doubl|loan\s*without|earn\s*lakhs|work\s*from\s*home\s*earn', re.I)
MINORS = re.compile(r'\b(teen|teens|school\s*(girl|boy|kid)|under\s*18|underage|minor)\b.{0,40}\b(dating|love|romance|girlfriend|boyfriend)\b|\b(dating|love|romance|girlfriend|boyfriend)\b.{0,40}\b(teen|school\s*(girl|boy)|under\s*18|underage)\b', re.I)

def clean_title(t):
    t = re.sub(r'[^\x00-\x7F\u0600-\u06FF\u0900-\u097F\u0E00-\u0E7F\u00A0-\u024F]+', ' ', t or '')
    return re.sub(r'\s+', ' ', t).strip()[:120]

def make_desc(name, cat, cc):
    nat = CNAMES.get(cc, 'international')
    art = 'an' if nat[0].lower() in 'aeiou' else 'a'
    who = CWORDS.get(cat, 'members')
    words = [w for w in re.findall(r'[A-Za-z\u0600-\u06FF\u0900-\u097F\u0E00-\u0E7F]{3,}', name) if len(w) > 2][:8]
    topic = ' '.join(words[:5]) if words else 'general chat'
    return (f"{art.capitalize()} {nat} WhatsApp group about {topic} where {who} connect and chat every day. "
            f"Active {cat.lower()} discussions, updates and friendly conversation in one lively group.")

def main():
    t14 = json.load(open(SRC3 + 'team14-unverified-pending.json'))
    t25 = json.load(open(SRC3 + 'team25R-unverified-pending.json'))
    union = set(json.load(open(WORK + 'dedupe_union.json')))
    code_rx = re.compile(r'^[A-Za-z0-9]{20,24}$')
    adult_rx = re.compile(r'adult|18\+|xxx|porn|erotic|nsfw|sexo|sexual', re.I)

    stats = {'adult_slug_drops': 0, 'porn_title_drops': 0, 'in_union': 0, 'bad_code': 0,
             'self_dup': 0, 'scam_flags': 0, 'minor_flags': 0}
    seen = set()
    pending = []
    n14 = n25 = 0

    for rec in t14:
        r = rec.get('record', {})
        cat_slug = str(r.get('cat_slug') or ''); tag = str(r.get('tag') or '')
        code = r.get('code') or rec.get('code')
        if adult_rx.search(cat_slug) or adult_rx.search(tag):
            stats['adult_slug_drops'] += 1; continue
        if not (code and code_rx.match(code)):
            stats['bad_code'] += 1; continue
        if code in union:
            stats['in_union'] += 1; continue
        if code in seen:
            stats['self_dup'] += 1; continue
        title = clean_title(r.get('title'))
        if PORN.search(r.get('title') or '') or PORN.search(title):
            stats['porn_title_drops'] += 1; continue
        seen.add(code)
        cat = CATMAP.get(r.get('cat_name') or '', 'Other')
        cc = (r.get('country') or 'International')[:2]
        cc = cc if (len(cc) == 2 and cc.isalpha()) else 'International'
        if SCAM.search(title): stats['scam_flags'] += 1
        if MINORS.search(title): stats['minor_flags'] += 1
        pending.append({'name': title or 'WhatsApp Group', 'category': cat, 'country': cc,
                        'description': make_desc(title, cat, cc),
                        'invite': 'https://chat.whatsapp.com/' + code, 'image': '',
                        'note': 'transport failure (wave 20261104 team33; egress stalled, og:title unreachable)'})
        n14 += 1

    for rec in t25:
        m = re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', rec.get('invite', ''))
        code = m.group(1) if m else None
        if not (code and code_rx.match(code)):
            stats['bad_code'] += 1; continue
        if code in union:
            stats['in_union'] += 1; continue
        if code in seen:
            stats['self_dup'] += 1; continue
        name = clean_title(rec.get('name'))
        if PORN.search(rec.get('name') or '') or PORN.search(name):
            stats['porn_title_drops'] += 1; continue
        seen.add(code)
        cat = rec.get('category') if rec.get('category') in CWORDS else 'Other'
        if SCAM.search(name): stats['scam_flags'] += 1
        if MINORS.search(name): stats['minor_flags'] += 1
        pending.append({'name': name or 'WhatsApp Group', 'category': cat,
                        'country': (rec.get('country') or 'International')[:2],
                        'description': rec.get('description') or make_desc(name, cat, 'BR'),
                        'invite': 'https://chat.whatsapp.com/' + code, 'image': '',
                        'note': 'transport failure (wave 20261104 team33; egress stalled, og:title unreachable)'})
        n25 += 1

    chunked_write(WORK + 'team33-pending-retry.json', '[]')
    chunked_write(WORK + 'team33-unverified-pending.json',
                  json.dumps(pending, ensure_ascii=False, indent=1))
    leads = [
        {'domain': 'chat.whatsapp.com', 'url': 'https://chat.whatsapp.com/',
         'why': 'RESUME POINT: wave 20261104 team33 could not verify ANY invites - egress proxy read-timed-out on all HTTPS from this VM and browser.open fetch returned HTTP 403 from chat.whatsapp.com. All clean candidates banked in team33-unverified-pending.json with note transport failure; retry og:title verification next wave from a host with working egress.'},
        {'domain': 'groupjoin.link', 'url': 'https://www.groupjoin.link/',
         'why': 'Source A provenance: team14 Nov-3 new-tag candidates. 334 records dropped for adult category/tag slugs per parent policy; 5 more dropped for pornographic titles. Resume: verify pending entries via og:title.'},
        {'domain': 'linkado.app', 'url': 'https://linkado.app/',
         'why': 'Source B provenance: team25R Nov-3 linkado.app detail-page codes. 9 dropped for pornographic titles (incl. emoji-flagged 18+ titles). Resume: verify pending entries via og:title.'},
    ]
    chunked_write(WORK + 'team33-leads.json', json.dumps(leads, ensure_ascii=False, indent=1))
    stats['pending_total'] = len(pending)
    stats['pending_t14'] = n14
    stats['pending_t25R'] = n25
    stats['porn_drops_total'] = stats['adult_slug_drops'] + stats['porn_title_drops']
    chunked_write(WORK + '_team33_final_stats.json', json.dumps(stats, indent=1))
    print('FINAL: ' + json.dumps(stats))

main()
