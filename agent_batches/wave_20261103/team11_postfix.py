#!/usr/bin/env python3
"""team11 post-fix: clean image URLs + keyword re-categorize + regenerate descriptions."""
import json, re

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261103'
VF = WAVE + '/team11-gjl-sportsfitness.json'

CATMAP = [
    ('Gaming', r'free\s?fire|\bff\b|pubg|bgmi|gaming|gamer|esport|e-?sport|mobile legends|\bmlbb\b|valorant|\bcs\b|counter.?strike|cod\b|fortnite|roblox|minecraft|gta\b|clash|\bffc\b|ff id|akun ff'),
    ('Buy-Sell', r'\bseller\b|\bsell\b|\bbuy\b|buying|shopping|\bshop\b|\bstore\b|market|reseller|\bprice\b|\bprices\b|order|discount|dropship|preloved|jualan|jual|beli'),
    ('Jobs', r'\bjob(s)?\b|hiring|career|vacanc|recruit|employment|job alert|naukri|rozgar|lowongan'),
    ('Education', r'\bstudy\b|studying|\bexam\b|\bclass\b|\bcourse\b|school|college|university|education|\blearn\b|\blearners\b|\blearnings\b|notes|admission|syllabus|ielts|css|psc|board exam'),
    ('Movies', r'\bmovie\b|\bmovies\b|film|cinema|web series|netflix|bollywood|hollywood|tollywood|dramas?'),
    ('Music', r'\bmusic\b|\bsong\b|\bsongs\b|\bdj\b|remix|spotify|singer|audio'),
    ('News', r'\bnews\b|breaking|headline|\bupdates?\b|newspaper|journalis'),
    ('Health', r'\bhealth\b|medical|doctor|hospital|weight loss|diet plan|\byoga\b|ayurved|skin|hair fall'),
    ('Girls', r'\bgirls?\b|ladies|women only|girl group'),
    ('Friendship', r'\bfriend(s|ship)?\b|dosti|dating|meet new|chat group|add me|\bfriendzone\b|dil se'),
    ('Entertainment', r'entertainment|status|reels?|tiktok|viral|\bvideo(s)?\b|meme|jokes?|funny|comedy|shayari|poetry'),
    ('Funny', r'funny|comedy show|stand.?up|prank'),
    ('Crypto', r'crypto|bitcoin|\bbtc\b|binance|forex|trading|airdrops?'),
    ('Finance', r'\binvest\b|investing|investment|\bearn\b|earning|income|\bmoney\b|loan|finance|fintech|trading signals'),
    ('Business', r'business|startup|entrepreneur|marketing|affiliate|dropship|brand|e-?commerce'),
    ('Technology', r'tech|technology|\bai\b|coding|programming|developer|software|computer|laptop|mobile'),
    ('Islamic', r'islam|muslim|quran|dua|\bdeen\b|masjid|ramadan|allah|muhammad|prophet|hadith'),
    ('Food', r'\bfood\b|recipe|cooking|kitchen|restaurant|biryani|pizza'),
    ('Pets', r'\bpet(s)?\b|\bdog\b|\bcat\b|birds?|parrot|fish'),
    ('Travel', r'travel|tour|tourism|holiday|\btrip\b|umrah|hajj|flight|ticket'),
]

TOPIC = {
    'Sports': ('sports', 'Members follow sports news, discuss matches and share fitness tips.'),
    'Gaming': ('gaming', 'Members discuss gameplay, share tips and team up for matches.'),
    'Buy-Sell': ('buy and sell', 'Members post products, deals and trusted seller listings.'),
    'Jobs': ('jobs', 'Members share job openings, career tips and hiring updates.'),
    'Education': ('education', 'Members share study notes, exam tips and learning resources.'),
    'Movies': ('movies', 'Members share movie recommendations, trailers and film discussions.'),
    'Music': ('music', 'Members share songs, remixes and music discussions.'),
    'News': ('news', 'Members share breaking news, headlines and updates.'),
    'Health': ('health and wellness', 'Members share health tips, wellness advice and fitness routines.'),
    'Girls': ('girls community', 'A friendly community group for women to chat and connect.'),
    'Friendship': ('friendship', 'Members chat, make new friends and share daily moments.'),
    'Entertainment': ('entertainment', 'Members share fun videos, memes, status updates and viral content.'),
    'Funny': ('fun and comedy', 'Members share funny videos, memes and comedy clips.'),
    'Crypto': ('crypto and trading', 'Members discuss crypto markets, trading signals and airdrops.'),
    'Finance': ('finance', 'Members discuss earning ideas, investments and money tips.'),
    'Business': ('business', 'Members discuss business ideas, marketing and entrepreneurship.'),
    'Technology': ('technology', 'Members discuss tech news, gadgets, AI and software tips.'),
    'Islamic': ('Islamic', 'Members share Islamic reminders, duas and religious discussions.'),
    'Food': ('food', 'Members share recipes, food photos and restaurant finds.'),
    'Pets': ('pets', 'Members share pet photos, care tips and adoption posts.'),
    'Travel': ('travel', 'Members share travel plans, tips and destination ideas.'),
}

def cat_of(name):
    n = name.lower()
    for cat, pat in CATMAP:
        if re.search(pat, n):
            return cat
    return 'Sports'

def main():
    items = json.load(open(VF))
    fixed_img = 0
    remapped = 0
    for i in items:
        if i.get('image') and 'pps.whatsapp.net' not in i['image']:
            i['image'] = ''
            fixed_img += 1
        newcat = cat_of(i['name'])
        if newcat != i.get('category'):
            remapped += 1
            i['category'] = newcat
        topic, detail = TOPIC.get(i['category'], TOPIC['Sports'])
        c = i.get('country', 'International')
        cnames = {'PK': 'Pakistan', 'IN': 'India', 'NG': 'Nigeria', 'ID': 'Indonesia', 'BD': 'Bangladesh',
                  'EG': 'Egypt', 'BR': 'Brazil', 'MY': 'Malaysia', 'SA': 'Saudi Arabia', 'AE': 'the UAE',
                  'PH': 'the Philippines', 'NP': 'Nepal', 'LK': 'Sri Lanka', 'KE': 'Kenya', 'GH': 'Ghana',
                  'ZA': 'South Africa', 'US': 'the USA', 'UK': 'the UK', 'CA': 'Canada', 'AU': 'Australia',
                  'TR': 'Turkey', 'IR': 'Iran', 'IQ': 'Iraq', 'AF': 'Afghanistan'}
        cname = cnames.get(c, c)
        nm = i['name']
        if cname == 'International':
            i['description'] = 'Join %s, an active %s WhatsApp group with members from around the world. %s' % (nm, topic, detail)
        else:
            i['description'] = 'Join %s, an active %s WhatsApp group from %s. %s' % (nm, topic, cname, detail)
    json.dump(items, open(VF, 'w'), ensure_ascii=False)
    print('items=%d images_cleared=%d categories_remapped=%d' % (len(items), fixed_img, remapped))

if __name__ == '__main__':
    main()
