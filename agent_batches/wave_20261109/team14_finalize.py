#!/usr/bin/env python3
"""Team14 finalize: post-screen live og:titles, build candidates/pending/leads/summary."""
import json, re

STATE = 'team14_verify_state.json'
W = '.'

# post-screen patterns applied to og:title (same rules as pre-screen)
PORN = re.compile(r"(?i)xxx|porn|sex|sexy|hookup|escort|cam[\s\-]?girl|nude|fuck|horny|"
                  r"🔞|🍑|🫦|🥵|سكس|سکس|ننگی|video[\s\-]?calls?\s+service|"
                  r"call[\s\-]?girl|leaked?\s+videos?|savita|bhabhi\s+lovers|"
                  r"tamil\s+akka|hot\s+girl|hot\s+video|video\s+call\s+sex")
SCAM = re.compile(r"(?i)b[\s\-]?love|forsage|shey(i|i)|airdrop[s]?|free[\s\-]?money|"
                  r"legit[\s\-]?online|paying[\s\-]?crypto")

CANDIDATES = {
    # code: (name=og:title, category, country, description)
    'D7ss3sCnysNLyHMKIzwnDC': ('Shilla Sanda & Sohba ❤️', 'Friendship', 'EG',
        'A friendly space for singles aged 30 to 45 in Cairo and Giza looking to build genuine, lasting friendships and a supportive community. Built on respect, honesty and safety, with clear group rules for all members.'),
    'INdSzTMhQy81bKF5ridud2': ('Faith & Wellbeing', 'Community & Social', 'US',
        'A supportive WhatsApp community for people navigating faith and wellbeing. Admin-approved joins keep the space safe and welcoming for everyone.'),
    'Jklg4MXkB9D6wUtkfDYxUt': ('Grief & Caregivers', 'Health', 'US',
        'A supportive WhatsApp community for people navigating grief and caregiving. Admin-approved joins keep the space safe and caring.'),
    'KEZJTIQPrz31nkZzzgfWcX': ('Depression & Low Mood', 'Health', 'US',
        'A supportive WhatsApp community for people navigating depression and low mood. Admin-approved joins keep the space safe and supportive.'),
    'Fu5mrCm4pcJGwSPXlJNZpG': ('Anxiety & Panic', 'Health', 'US',
        'A supportive WhatsApp community for people navigating anxiety and panic. Admin-approved joins keep the space safe and supportive.'),
    'LFym7UpHcKnLhwRkxpXq3G': ('OCD & Scrupulosity', 'Health', 'US',
        'A supportive WhatsApp community for people navigating OCD and scrupulosity. Admin-approved joins keep the space safe and supportive.'),
    'LYobx9EbTIG48c8Fj8MXAw': ('Grace in Minds', 'Health', 'US',
        'A supportive WhatsApp community for people navigating mental wellbeing. Admin-approved joins keep the space safe and welcoming for everyone.'),
    'GMeHPWLZtuWEtqQrP0Nrby': ('🌙✨ روشنی کا سفر ✨🌙', 'Islamic', 'PK',
        'An Urdu Islamic group sharing Quran and Hadith reminders, poetry and peaceful reflections. Members join for faith, comfort and learning together.'),
}

def main():
    state = json.load(open(STATE))
    live = {c: v for c, v in state.items()
            if v['attempts'][-1]['http'] == 200 and v['attempts'][-1]['title']
            and v['attempts'][-1]['title'] != 'WhatsApp Group Invite'}
    pending = [v for v in state.values() if v['attempts'][-1]['http'] == 0]
    print(f'verified={len(state)} live-og={len(live)} transport-fail={len(pending)}')

    candidates, dropped_post = [], []
    for code, v in live.items():
        title = v['attempts'][-1]['title']
        listing = v['listing']
        hay = f"{title} {listing.get('name','')} {listing.get('description','')}"
        if PORN.search(hay) or SCAM.search(hay):
            dropped_post.append({'code': code, 'og_title': title,
                                 'listing_name': listing.get('name'),
                                 'reason': 'post-screen og:title/name/desc porn/scam'})
            continue
        if code not in CANDIDATES:
            dropped_post.append({'code': code, 'og_title': title,
                                 'listing_name': listing.get('name'),
                                 'reason': 'live but no curated candidate entry (unexpected)'})
            continue
        name, cat, ctry, desc = CANDIDATES[code]
        assert name == title, (name, title)
        # no phone numbers / personal info check
        assert not re.search(r'\d{7,}', desc), desc
        assert 'chat.whatsapp.com' not in desc and 'groupssor' not in desc.lower()
        candidates.append({'name': name, 'category': cat, 'country': ctry,
                           'description': desc,
                           'invite': f'https://chat.whatsapp.com/{code}'})
    candidates.sort(key=lambda c: c['invite'])
    dead = len(state) - len(live)
    print(f'candidates={len(candidates)} dropped_post={len(dropped_post)} dead={dead}')
    for d in dropped_post:
        print('  DROPPED-POST:', d)

    json.dump(candidates, open(f'{W}/team14-candidates.json', 'w'), indent=1, ensure_ascii=False)
    json.dump([{'code': v['code'], 'invite': f"https://chat.whatsapp.com/{v['code']}",
                'note': 'transport failure (http 0) — re-verify next wave',
                'attempts': v['attempts']} for v in pending],
              open(f'{W}/team14-pending.json', 'w'), indent=1, ensure_ascii=False)
    json.dump([
        {'url': 'https://groupssor-api.blog-99n.workers.dev/api/groups',
         'note': 'groupssor API latest-500 endpoint — re-poll next wave for new submissions; returns mixed WhatsApp/Telegram, heavy adult/spam content, needs strict porn/scam filtering and per-link verification'},
        {'url': 'https://groupssor.com',
         'note': 'groupssor directory homepage — check newest listing pages next run if API stalls'},
    ], open(f'{W}/team14-leads.json', 'w'), indent=1, ensure_ascii=False)
    json.dump({
        'team': 14,
        'slice': 'groupssor.com API — latest-500 only, re-poll for new submissions since Nov 8',
        'sources': ['https://groupssor-api.blog-99n.workers.dev/api/groups'],
        'verified': len(state),
        'pending': len(pending),
        'leads': 2,
        'dead': dead,
        'notes': (
            'API returned HTTP 200, fixed 500 entries (ignores limit/page params; limit=1000 still 500, page=2 timed out). '
            'Newest entry 2026-11-08T19:28:51Z; no submissions newer than that in this poll. '
            'Of 500 rows: 182 Telegram (excluded), 13 WhatsApp Channels (whatsapp.com/channel/..., not group invites, excluded), '
            '318 WhatsApp invites; 87 dup vs .existing_codes.json (106,883 codes); 216 fresh unique codes. '
            'Pre-screen dropped 123 of 216 (98 porn/sex, 12 scam-crypto/airdrop incl. SHEYI/airdrops/carding/KYC-data, 13 junk). '
            'Slow-verified 93 via curl (max 3 parallel, >=0.5s spacing; ambiguous 200+empty-og:title retried up to 3 attempts). '
            'All 93 returned HTTP 200 — dead links also return 200 with empty og:title, so dead=84 (empty title after 3 attempts), live=9. '
            'Post-screen on og:title dropped 1 live link (J6yVkaaOraRGBnzYLxuApi, og:title adult 🔞🍑 despite clean listing name). '
            'Final candidates=8, ALL created 2026-11-08; older fresh entries were almost all dead. '
            'Pending=0 (no transport failures). Verification was slow (~40 min) — many other wave teams were hitting chat.whatsapp.com concurrently.'
        ),
    }, open(f'{W}/team14-summary.json', 'w'), indent=1, ensure_ascii=False)
    print('wrote team14-candidates.json, team14-pending.json, team14-leads.json, team14-summary.json')

if __name__ == '__main__':
    main()
