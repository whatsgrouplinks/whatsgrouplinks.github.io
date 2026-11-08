#!/usr/bin/env python3
"""TEAM 42 - dedupe, verify (og:title), write team42-turkey.json."""
import re, json, os, time, html
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(BASE)
UA = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}

CATMAP = {
 'sohbet':'Friendship','tanisma-arkadas':'Friendship','dating':'Girls','flort':'Girls',
 'evlilik-iliski':'Friendship','gezi-seyahat':'Travel','tatil':'Travel',
 'is-ilanlari':'Jobs','freelance-is':'Jobs','meslek-gruplari':'Jobs','uzaktan-calisma-dijital-gocebe':'Jobs',
 'indirim':'Buy-Sell','alisveris':'Buy-Sell','sifir-ikinciel':'Buy-Sell','e-ticaret':'Business',
 'kripto-para-borsa':'Crypto','kripto-airdrop':'Crypto',
 'egitim':'Education','egitim-ders':'Education','universite':'Education','ogrenci':'Education',
 'kitap':'Education','ingilizce-konuma-kulubu':'Education',
 'haber':'News','spor':'Sports','futbol':'Sports','at-yarisi':'Sports','beyzbol':'Sports',
 'ragbi-amerikan-futbolu':'Sports','okculuk':'Sports','paintball':'Sports','airsoft':'Sports',
 'kutu-oyunlari':'Gaming','oyun':'Gaming','oyuncular':'Gaming',
 'din':'Islamic','ticaret':'Business','girisimcilik':'Business','para-kazanma':'Finance',
 'evden-para-kazanma':'Finance','finans':'Finance','saglik':'Health','diyet-beslenme':'Health',
 'kilo-verme':'Health','teknoloji':'Technology','donanim-yazilim':'Technology','webmaster':'Technology',
 'muzik':'Music','kpop-kore':'Music','rap-hiphop':'Music','sinema':'Movies','film-dizi':'Movies','tv':'Movies',
 'yemek':'Food','astroloji-burc':'Entertainment','eglence':'Entertainment','anime-manga':'Entertainment',
 'cosplay':'Entertainment','ruya-tabiri':'Entertainment','kultur-sanat':'Entertainment',
 'survivor-yarismalar':'Entertainment','sosyal-medya':'Entertainment','instagram-buyume':'Entertainment',
 'tiktok-icerik':'Entertainment','canli-yayin':'Entertainment','fotografcilik':'Entertainment',
 'grafik-video':'Entertainment','hobi':'Entertainment','asmr-rahatlama':'Entertainment',
 'kahve-kulturu':'Food','makyaj-guzellik':'Other','cilt-bakimi':'Health','dovme-piercing':'Other',
 'hayvanlar':'Pets','anne-baba':'Community','bebek-anne':'Community','topluluk':'Community',
 'yardimlasma':'Community','emekliler':'Community','askerlik':'Community','arastirma':'Education',
 'yasal-danismanlik':'Other','hizmetler':'Other','emlak':'Business','vasita':'Other',
 'araba-modifiye':'Other','elektrikli-arac':'Other','antika-koleksiyon':'Other','drone-hobi-pilot':'Other',
 'lgbt':'Community','motivasyon':'Other','kisisel-gelisim':'Education','x':'Other',
 'whisky-icki-kulturu':'Other','diger':'Other','iddaa':'Other','spor-bahisleri-oran-analizi':'Other',
 'kumar-sans-oyunlari':'Other','kumar-slot':'Other','casino-canli-casino':'Other','yoga-pilates':'Health',
 'sstrofotografcilik':'Entertainment',
}

DESC_TPL = {
 'Friendship':'A friendly Turkey WhatsApp chat group for meeting new people, daily conversation and making friends across the country.',
 'Girls':'A Turkey WhatsApp social group for girls and guys to chat, flirt respectfully and build new friendships.',
 'Jobs':'A Turkey WhatsApp jobs group sharing fresh job postings, vacancies and employment opportunities.',
 'Buy-Sell':'A Turkey WhatsApp buy-and-sell group with deals, discounts and marketplace listings shared daily.',
 'Crypto':'A Turkey WhatsApp crypto group for Bitcoin, altcoin and market talk with fellow traders.',
 'Education':'A Turkey WhatsApp study group with exam prep, notes and learning resources for students.',
 'News':'A Turkey WhatsApp news group sharing daily headlines and current events updates.',
 'Sports':'A Turkey WhatsApp sports group for fans to discuss matches, teams and sporting news.',
 'Gaming':'A Turkey WhatsApp gaming group for players to team up, share tips and talk games.',
 'Islamic':'A Turkey WhatsApp Islamic group for religious discussion, reminders and community support.',
 'Business':'A Turkey WhatsApp business group for networking, trade talk and entrepreneurial ideas.',
 'Finance':'A Turkey WhatsApp finance group discussing money, investing and earning opportunities.',
 'Health':'A Turkey WhatsApp health group sharing wellness tips and healthy lifestyle discussion.',
 'Technology':'A Turkey WhatsApp technology group for tech news, gadgets and digital discussion.',
 'Music':'A Turkey WhatsApp music group for sharing songs, artists and music talk.',
 'Movies':'A Turkey WhatsApp movies group for film and series discussion and recommendations.',
 'Food':'A Turkey WhatsApp food group sharing recipes, cooking tips and foodie chat.',
 'Pets':'A Turkey WhatsApp pets group for animal lovers to share photos and care tips.',
 'Travel':'A Turkey WhatsApp travel group for trip ideas, destinations and travel buddies.',
 'Community':'A Turkey WhatsApp community group bringing people together around shared interests.',
 'Entertainment':'A Turkey WhatsApp entertainment group for fun chat, memes and light-hearted discussion.',
 'Other':'A Turkey WhatsApp group for members interested in this topic and daily conversation.',
}

PORN_WORDS = ['porn','pornhub','xxx','nude','sex video','escort','call girl','fuck','dick','pussy','boobs','anal']
PORN_EMOJI = ['🥵','🍆','🍑','💦','👅','👄','💋']
MULE = ['passcode','loader','money flip','counterfeit']

def check_live(code):
    url = 'https://chat.whatsapp.com/' + code
    try:
        r = requests.get(url, headers=UA, timeout=25)
        m = re.search(r'<meta property="og:title" content="([^"]*)"', r.text)
        title = html.unescape(m.group(1)).strip() if m else ''
        return ('live', title) if title else ('dead', '')
    except Exception as e:
        return ('transport', repr(e)[:80])

def main():
    union = set(json.load(open(os.path.join(WAVE,'dedupe_union.json'))))
    recs = {}
    for i in range(6):
        p = os.path.join(BASE, 'catrecs_W%d.json' % i)
        if os.path.exists(p):
            d = json.load(open(p, encoding='utf-8'))
            for k, v in d.items():
                recs.setdefault(k, v)
    print('raw records:', len(recs))
    cands, porn = [], 0
    seen = set()
    for code, r in recs.items():
        if code in union or code in seen: continue
        seen.add(code)
        t = (r.get('title') or '')
        tl = t.lower()
        if any(w in tl for w in PORN_WORDS) or any(e in t for e in PORN_EMOJI):
            porn += 1; continue
        if any(w in tl for w in MULE):
            print('MULE-FLAG:', t); continue
        cands.append((code, r))
    print('candidates:', len(cands), 'porn_drops:', porn)
    verified, pending = [], []
    for idx, (code, r) in enumerate(cands):
        status, og = check_live(code)
        print(idx, code, status, (og[:40] if og else ''), flush=True)
        if status == 'live':
            name = og if og else r['title']
            name = re.sub(r'\s+', ' ', name).strip()
            if not name or 'http' in name.lower(): name = r['title']
            cat = CATMAP.get(r.get('catslug',''), 'Other')
            verified.append({
                'name': name[:120],
                'category': cat,
                'country': 'TR',
                'description': DESC_TPL.get(cat, DESC_TPL['Other']),
                'invite': 'https://chat.whatsapp.com/' + code,
                'image': ''})
        elif status == 'transport':
            pending.append({'name': r['title'], 'category': CATMAP.get(r.get('catslug',''),'Other'),
                            'country': 'TR', 'description': 'Turkey WhatsApp group.',
                            'invite': 'https://chat.whatsapp.com/' + code, 'image': '',
                            'note': 'transport failure'})
        time.sleep(0.7)
    json.dump(verified, open(os.path.join(WAVE,'team42-turkey.json'),'w',encoding='utf-8'),
              ensure_ascii=False, indent=1)
    if pending:
        json.dump(pending, open(os.path.join(WAVE,'team42-unverified-pending.json'),'w',encoding='utf-8'),
                  ensure_ascii=False, indent=1)
    print('VERIFIED:', len(verified), 'PENDING:', len(pending), 'PORN:', porn)

if __name__ == '__main__':
    main()
