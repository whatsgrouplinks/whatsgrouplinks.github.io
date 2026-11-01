#!/usr/bin/env python3
"""TEAM 25 (wave_20261030) — listicle harvest on NEW domains.
Sandbox limits found during the run:
- exec/curl egress to chat.whatsapp.com times out (proxy blocked); cannot run the
  required curl verification.
- browser_open to chat.whatsapp.com/* is 403-blocked upstream; invite codes sit
  behind Join-button outlinks and cannot be resolved via text fetch.
- wp-json on whtsagrouplinks.com returned 401 on posts endpoint; groupwa.link
  wp-json renders but the long homepage content is truncated before the codes.
Result: no 22-char codes extractable -> fresh=[] and pending=[] are honest.
All harvested group names + exact page + Join-button outlink index go to
team25-leads.json so a browser-capable agent can resolve + verify + dedupe.
"""
import json, os

WAVE = os.path.dirname(os.path.abspath(__file__))
leads = []

def add(domain_url, source_page, section, entries, country_hint, cat_hint):
    for name, idx, cat, country, extra in entries:
        leads.append({
            "name": name,
            "code_or_invite": f"Join-button outlink idx {idx} on {source_page} (code needs browser-capable resolution)",
            "source_page": source_page,
            "note": f"section={section} | category={cat or cat_hint} | country={country or country_hint} | domain discovery: new domain, not in retired list"
                    + (f" | {extra}" if extra else "")
                    + " | UNVERIFIED: sandbox cannot fetch chat.whatsapp.com; apply porn-block + dedupe on resolve",
        })

# ---------------- whtsagrouplinks.com homepage ----------------
W = "https://www.whtsagrouplinks.com/"
def e(items, cat, country):
    return [(n, i, cat, country, None) for n, i in items]

add(W, W, "Indian WhatsApp Group", e([
    ("MAKE MONEY", 1), ("Crypto & Forex Gold Free Signals", 2), ("Freelancers", 4),
    ("Kanpur manpower all over India", 5), ("GenAI", 6), ("Claude Pro (Free)", 7),
    ("Gishkori AI & Pro Store", 8), ("Story box", 9), ("Wolfxteam", 10),
    ("WE TALK A LOT", 11), ("Jujutsu Kaisen Stuffs", 12), ("MultiTok", 13),
    ("Arsenal Funs Only", 14), ("Asha consultants", 15),
    ("Healthy india & weight loss from Home", 16), ("Home Med Suppliers", 17),
    ("Fire Alarm & CCTV Services", 18), ("Berozgar ADDA (Indian Only)", 19),
    ("Brainrott Refugees", 20), ("Indian Arts & Crafts", 21), ("SK FAMILY BROAD", 22),
    ("ClixoApp Sales & Marketing", 23), ("SMP MC", 24), ("Anime Nexus", 25),
], "Community & Social", "IN"), None, None)

add(W, W, "Pakistani WhatsApp Group", e([
    ("سب کو سب نہیں ملتا", 29), ("Dast-e-Taawun Foundation", 30), ("Team work", 32),
    ("KNIGHTS' TAVERN", 33), ("Sofia_Success_Point", 34), ("Only Permanent here", 35),
    ("AHMAD OPEN CHAT", 36), ("Faizan E Jamia Tul Madina", 37),
    ("JAMAL UL QURAN ACADEMY", 38), ("Sasta Bazar pk", 39), ("ADEL ELHAM", 40),
    ("Qurano Hadeesh Islamic Post", 41), ("Daily Qur'an-o-Hadees", 42),
    ("Ghazi Islamic Institute (GII)", 43), ("Cricket Fans (کرکٹ کے دیوانے)", 44),
    ("MaShaAllah Brand BoutiQue And Reseller Group", 45), ("ADEEL ALAHMAR", 46),
    ("Varun kumar SEO agency India", 47), ("Vogue Garments", 48),
], "Community & Social", "PK"), None, None)

add(W, W, "Girls WhatsApp Group", e([
    ("ONLY CHAT", 52), ("International Friendship group 2026 New", 53),
    ("CHILL MASTI", 55), ("Katseye Fandom to the world", 56), ("Just Fun", 57),
    ("Lovely_Lilies", 58), ("Just us girlsss GO TEAM", 59), ("Girls Group", 60),
    ("Friendship group", 61), ("Only girls status group", 63), ("Only girls club", 66),
    ("USA Girls", 67),
], "Friendship", "XX"), None, None)

add(W, W, "Make Money Online WhatsApp Group", e([
    ("Real Online Earning", 71), ("Gmail Online Earnings", 73), ("Earning", 74),
    ("Free Earnings Website", 75), ("Learn with Earn", 76),
    ("No Loss Crew | Profit Team FREE VIP", 77), ("EarnUp", 78), ("Earners", 79),
    ("Flash sale Online link", 80), ("Online earning without Investment", 81),
    ("SMART MONEY TRADER", 82), ("Money Vibes", 83), ("Online Earning", 84),
    ("Earn Money", 85), ("EARN MONEY", 86), ("Free Online Earning", 87),
    ("Binance Earning", 88), ("Barakah Glow Hub", 89), ("Online work", 90),
], "Online Earning", "XX"), None, None)

add(W, W, "Movie WhatsApp Group", e([
    ("Movie's", 92), ("Family Home Entertainment", 93), ("MOVIES BOX (G2)", 95),
    ("Bigg boss S20 all Ep", 96), ("Movie and Anime", 97), ("ANIME ZONE", 98),
    ("FILMY Duniya", 99), ("Movies Wala", 100), ("Movies Hub", 101),
    ("Movies & Drama club", 102), ("Movie zone", 103), ("CINEFLIX HQ - MOVIE 1", 104),
    ("Free Movie Group (1)", 105), ("Theatre daily", 107), ("Blood Moon Corporation", 108),
    ("Super AmaFlix Demo Group", 109),
], "Entertainment", "XX"), None, None)

add(W, W, "Share Market WhatsApp group", e([
    ("UK STOCK CRIPTO MARKET NIFTY BANKNIFTY Update", 110),
    ("STOCK /NIFTY /BANKNIFTY /MCX", 111), ("Shyam Traders", 113),
    ("Trading passion", 114), ("Trading Experts - By Armaan", 115),
    ("Stock market trader", 116), ("Trading", 117),
], "Business", "XX"), None, None)

add(W, W, "USA WhatsApp Group", [
    ("Manga Manhwa Hub", 119, "Entertainment", "US", None),
    ("Gilgit Baltistan and K2 Tourism and Guiding", 121, "Travel", "PK", "listed under USA section; travel group"),
    ("TS & AP Real estate Advisors", 122, "Real Estate", "US", "listed under USA section"),
], None, None)

add(W, W, "Jobs WhatsApp Group", e([
    ("Active Job openings", 125), ("EVENT - JOB - MODELLING ASSIGNMENT DELHI NCR ONLY GENUINE", 126),
    ("Canada amazon warehouse jobs", 127), ("Jobs in Lahore", 128), ("Daily Job Alerts", 129),
    ("Hiring Online Brand Promoting work for Direct Company in Bangalore", 130),
    ("Kashi banaras security job", 131), ("Sarkari Vacancy 09", 132), ("Job's available", 133),
    ("Job Vacancy's Group Bangalore", 134), ("Rafa international (JOB VACANCY)", 135),
    ("jobs4u", 136), ("Sunhr job group 1", 137), ("Baidesik Rojgari", 138),
], "Jobs", "XX"), None, None)

add(W, W, "Students WhatsApp Group", e([
    ("NEET 2027", 139), ("AHMEDABAD GARBA PASS 2026", 140), ("72 BPSC STUDENTS", 142),
    ("SAP ABAP Training", 143), ("Learn Pro Academy Batch#176", 144), ("Programmers", 145),
    ("Learn german with each other", 146), ("Goethe exam Countdown", 147),
    ("Student Union of India (SUI) Non Political", 148),
], "Education", "XX"), None, None)

add(W, W, "Cryptocurrency Whatsapp Group", e([
    ("BIRDEYE CRYPTO CLUB", 150), ("Ryan GOLD Master", 152), ("Gold & BTC -FX", 153),
    ("Crypto Trading Guide", 154), ("Crypto Free Airdrop King", 155),
], "Crypto", "XX"), None, None)

add(W, W, "Trading WhatsApp Groups", e([
    ("NOMETVE TRADER MASTER", 157), ("PIPS FINDER", 158), ("BDG WIN Trading", 159),
    ("GOLD SNIPER", 160), ("PIPS VIEW TRADING", 161), ("Trade with Hamza", 162),
    ("Gold Trading", 163), ("HB Traders", 164), ("The Trading Classroom", 165),
    ("SHAH JAHAN FX TRADER$", 166), ("Traders Terminal - Group", 167),
], "Business", "XX"), None, None)

add(W, W, "Forex Trading WhatsApp Group", e([
    ("Mineral Forex", 169), ("FX TRADERS", 170), ("Master Gold Trading", 171),
    ("Prime FX", 172), ("FOREX SWISS TRADING HUB", 173), ("GOLD PRIME FX", 174),
    ("No1 Forex Trader", 175), ("The Forex Beacon", 176), ("AmirForexStudio- General", 177),
], "Business", "XX"), None, None)

add(W, W, "News WhatsApp Group", e([
    ("M P NEWS", 178), ("TRP News", 179), ("All India Jobs News", 181), ("BREAKING NEWS", 182),
    ("Education Dept News (शिक्षा विभाग समाचार)", 183), ("Raj. All Exam News", 184),
    ("Education and political news", 185), ("First Bihari News", 186),
    ("Daily Newspaper", 187), ("ATH NEWS 11 & Patrika", 188),
], "News", "XX"), None, None)

add(W, W, "Gaming WhatsApp Group", e([
    ("CSA CLUB", 189), ("xM PUBG", 190), ("SHOOTER GAMING FILE", 192),
    ("BGMI TOURNAMENT", 193), ("Malik Sports 05", 194), ("Alfa Gaming Company", 195),
], "Gaming", "XX"), None, None)

add(W, W, "Poetry WhatsApp Group", e([
    ("Poetry group", 197), ("poetry group", 198), ("Noor-e-Shariat (نورِ شریعت)", 200),
    ("Romantic Poetry", 201), ("Noor-e-Wilayat", 202), ("POTREY (LINES)", 203),
    ("Tanha Musafir Sad Poetry (تنہا مسافر)", 204), ("T&F SMART EARNING", 205),
    ("Mareez-e-Ishq (مریض عشق)", 206), ("POETRY LOVERS", 207),
], "Poetry", "XX"), None, None)

add(W, W, "Friendship WhatsApp Group", e([
    ("New Group new friends", 209), ("True chat", 210), ("Lovetalks", 211),
    ("Chatpate chat", 212), ("Gup shap", 213), ("INTERNATIONAL FRIENDS", 214),
    ("Make a best friend", 215), ("Bhaichara on top", 216), ("The Strangers", 217),
], "Friendship", "XX"), None, None)

add(W, W, "Sub4Sub WhatsApp Group", e([
    ("Free subscribers", 219), ("Viral Youtube Short", 220),
    ("YOUTUBE GENUINE INCREASE SUBSCRIBE", 221), ("YouTube Helper Official Group", 222),
], "Community & Social", "XX"), None, None)

add(W, W, "International WhatsApp Group Links", e([
    ("Women's Empower Hub", 225), ("Noble Embassy", 226), ("All World Chat", 228),
    ("DocuPoint", 229), ("MALLU IN GULF OVERSEAS", 230), ("UNIVERSAL FUN HOUSE (UFH)", 231),
    ("Aprender Español", 232), ("LEOPARD BATTLE HUB", 233), ("Hayday Global Community", 234),
    ("PTI INSAF BRIGADES", 235), ("The population", 236), ("JAHNAGIR AGENCY", 237),
    ("welcome to the world", 238), ("G.E.L Group", 239),
    ("Aircity international consultants pvt Ltd", 240), ("NOPMO GLOBAL", 241),
    ("Global English Learning Hub", 242), ("OTT SUBSCRIPTION SERVICES", 243),
], "Community & Social", "XX"), None, None)

add(W, W, "Youtube WhatsApp Groups", e([
    ("Youtube Subscriber Free 1k", 244), ("Get 1k Youtube Subscribe", 245),
    ("YouTube Growth Community", 246),
], "Community & Social", "XX"), None, None)

add(W, W, "UK WhatsApp Group", [
    ("Andaman Tour With SJ", 247, "Travel", "GB", "listed under UK section; travel"),
    ("UK Property Buy Rent Sell", 248, "Real Estate", "GB", "listed under UK section"),
    ("UK online", 250, "Community & Social", "GB", None),
    ("Timebucks Tips and tricks", 251, "Online Earning", "GB", "listed under UK section"),
    ("Global Consultant 1", 252, "Business", "GB", "listed under UK section"),
    ("E-Commerce business", 253, "Business", "GB", "listed under UK section"),
    ("AFFILIATE DISCUSSION", 254, "Business", "GB", "listed under UK section"),
    ("Real Job Updates", 255, "Jobs", "GB", "listed under UK section"),
    ("GADGETS SPHERE", 256, "Buy & Sell", "GB", "listed under UK section"),
    ("UniQue Bull Official Community", 257, "Business", "GB", "listed under UK section"),
    ("Avenue tous vendre (237)", 258, "Buy & Sell", "GB", "listed under UK section; French text"),
], None, None)

add(W, W, "Shopping WhatsApp Group", e([
    ("MT MART", 260), ("ShoesKartel Only for India", 261), ("StyleBox One Shopping", 263),
    ("M Fazan Online Shopping Center", 264), ("Vtradebiz.shop Grp-10", 265),
    ("SHOPPING CORE", 266), ("Cloth Store", 267), ("Kitchen/Customize And Fabrics Items", 268),
    ("Shopi Hub", 269), ("BLACK PEARL COLLECTION", 270), ("Aliyan Online Store", 271),
    ("Kaawish Boutique", 272), ("Shopdeal Customers", 273),
    ("Faiza Hyderabadi Jadau Jewellery", 274), ("Best Loot Deals 1", 275),
    ("All Types Clothes & Dress's", 276), ("OUTVERRA MEN'S WHOLESALE RESELLING (FSD)", 277),
    ("AY Online Selling Store", 278), ("Tulip Charm Collection", 279), ("KASHMIRI JEWELRY", 280),
    ("online products sell", 281), ("MUZAMMIL COLLECTION", 282),
    ("10K INSTAGRAM INDIAN FOLLOWERS", 286), ("INSTAGRAM INDIAN FOLLOWERS", 287),
    ("INSTAGRAM CHEAPEST FOLLOWERS", 289), ("INSTAGRAM REAL FOLLOWERS", 290),
    ("SHANKAR ONLINE SERVICES", 291), ("TikTok Growth", 292), ("DigitalDealWay", 293),
    ("social market", 294), ("Videos Pakistani", 295), ("TIKTOK FORYOU", 296),
    ("AYSH TikTok Sellers", 297),
], "Buy & Sell", "XX"), None, None)

# ---------------- whtsagrouplinks.com friendship page ----------------
WF = "https://www.whtsagrouplinks.com/friendship-whatsapp-group-links/"
add(WF, WF, "Active Friendship WhatsApp group links", e([
    ("International Friends", 1), ("Friends", 2), ("New Group new friends", 4),
    ("True chat", 5), ("Lovetalks", 6), ("Chatpate chat", 7), ("Gup shap", 8),
    ("INTERNATIONAL FRIENDS", 9), ("Make a best friend", 10), ("Bhaichara on top", 11),
    ("Friendship", 12), ("Friend you", 13), ("Global Friends", 14),
    ("Shetkari Mitra Parivar (शेतकरी मित्र परिवार)", 15), ("Friends Chatting Group", 16),
    ("Global friend group", 17), ("Relationship + Friendship", 18),
    ("Only girls and boy friendship group", 19), ("Friends Forever LK", 20),
    ("Friends Across Borders", 21), ("CHATTING CLOWNS", 23),
], "Friendship", "XX"), None, None)

# ---------------- whatgroups.com Pakistan page ----------------
WG = "https://whatgroups.com/whatsapp-group-links-pakistan/"
add(WG, WG, "Active and Latest WhatsApp group Links Pakistan", [
    ("All Pakistan online shopping group", 1, "Buy & Sell", "PK", None),
    ("Pakistan Zindabad (پاکستان زندباد)", 2, "Community & Social", "PK", None),
    ("Online Earning Group", 3, "Online Earning", "PK", None),
    ("Technology Group", 4, "Technology", "PK", None),
    ("Islamic Group", 5, "Islamic", "PK", None),
    ("Ertugrul_lover1", 6, "Entertainment", "PK", None),
    ("Online Earning by Investm", 7, "Online Earning", "PK", None),
    ("WhatsApp Status", 8, "Entertainment", "PK", None),
    ("Programming Business", 9, "Business", "PK", None),
    ("King PUBG Account Seller", 10, "Gaming", "PK", None),
    ("Beauty Of Islam", 11, "Islamic", "PK", None),
    ("CLASSIC GIVEAWAY ROOM", 12, "Gaming", "PK", None),
    ("Resume (Cv) Maker", 13, "Jobs", "PK", None),
    ("Poetry & Novel Lover Group", 14, "Poetry", "PK", None),
    ("Without Investment Earning Group", 15, "Online Earning", "PK", None),
    ("Instagram Followers", 16, "Community & Social", "PK", None),
    ("Pubg low rate uc carding", 17, "Gaming", "PK", "CAUTION: 'carding' suggests fraud; vet before listing"),
    ("PTI and Pakistan News", 18, "News", "PK", None),
    ("Lahore Real State", 19, "Real Estate", "PK", None),
    ("Pakistan Earn Apps 2024", 22, "Online Earning", "PK", None),
    ("Kalamkar", 23, "Poetry", "PK", None),
    ("LEARN FREELANCING PAKISTAN", 24, "Freelance", "PK", None),
    ("Pak Online Rishta", 25, "Friendship", "PK", None),
    ("Pakistan online shopping market", 26, "Buy & Sell", "PK", None),
    ("SOCIAL MEDIA PAKISTAN", 27, "Community & Social", "PK", None),
    ("ISLAM PAKISTAN AUR AWAM", 28, "Islamic", "PK", None),
    ("Pakistani boys", 29, "Friendship", "PK", "shares Join button idx 29 with 'PAKISTAN GEET SANGEET'"),
    ("PAKISTAN GEET SANGEET", 29, "Entertainment", "PK", "shares Join button idx 29 with 'Pakistani boys'"),
    ("Pakistan Weather Dynamics", 30, "News", "PK", None),
    ("Online Holy Quran Academy", 31, "Islamic", "PK", None),
    ("Asan Rozgar Pakistan", 32, "Jobs", "PK", None),
    ("GYM Bodybuilding", 33, "Health", "PK", None),
    ("Digital Business Pakistan", 34, "Business", "PK", None),
    ("Grand Bazaar Jewellerys", 35, "Buy & Sell", "PK", None),
    ("AL Shifa Dawakhana", 36, "Health", "PK", None),
    ("EBL Pakistan", 37, "Online Earning", "PK", None),
    ("ZAHRA MEHAND", 38, "Buy & Sell", "PK", None),
    ("Only friends", 39, "Friendship", "PK", None),
    ("Job Enabler (Pak Govt+Private jobs)", 40, "Jobs", "PK", None),
    ("Dil Ka Rishta", 41, "Friendship", "PK", None),
    ("Muslim 2nd marriage", 42, "Friendship", "PK", "matchmaking group; social, non-porn"),
    ("ORANGI TOWN", 43, "Community & Social", "PK", None),
    ("Benazir Income Support Program (بینظیر انکم سپورٹ پروگرام)", 44, "Community & Social", "PK", None),
    ("Grand B. Cosmetics", 45, "Buy & Sell", "PK", None),
    ("Games members", 46, "Gaming", "PK", None),
    ("Love Balochistan", 47, "Community & Social", "PK", None),
    ("Job's Pakistan", 48, "Jobs", "PK", None),
    ("Grow Members Pk", 49, "Community & Social", "PK", None),
    ("Social Group Pakistan", 50, "Community & Social", "PK", None),
    ("Pakistani YouTubers", 51, "Community & Social", "PK", None),
    ("All Pakistan Govt Jobs", 52, "Jobs", "PK", None),
    ("Geo Official News Group (جیو آفیشل نیوز گروپ)", 53, "News", "PK", None),
    ("Pakistan journalist group", 54, "News", "PK", None),
    ("6 HNM Headline Darma", 55, "Entertainment", "PK", None),
    ("Pakistani Fashion Outlet", 56, "Buy & Sell", "PK", None),
    ("Rohani ilaj Dawateislami", 57, "Islamic", "PK", None),
    ("Pak On Top", 58, "Community & Social", "PK", None),
    ("Online Business Pakistan", 59, "Business", "PK", None),
    ("Pak Garments", 60, "Buy & Sell", "PK", None),
    ("Online shopping Pakistan", 61, "Buy & Sell", "PK", None),
    ("Pakistan online shopping markets", 62, "Buy & Sell", "PK", None),
    ("POLITICS of PAKISTAN", 63, "News", "PK", "Join button idx 63 points to sibling domain whatgrouplinks.org"),
    ("Pakistani Darame", 64, "Entertainment", "PK", "Join button idx 64 points to sibling domain whatgrouplinks.org"),
    ("Forsage Teem pakistan", 65, "Online Earning", "PK", "CAUTION: Forsage is a known crypto scam; vet before listing; idx 65 -> whatgrouplinks.org"),
    ("Maids in Pakistan", 66, "Jobs", "PK", "Join button idx 66 points to sibling domain whatgrouplinks.org"),
    ("Pakistani Friends Circle", 67, "Friendship", "PK", None),
    ("PK Women", 68, "Friendship", "PK", None),
    ("Viral Video Vibes", 69, "Entertainment", "PK", None),
    ("Palestine (فلسطین)", 70, "News", "PK", None),
], None, None)

add(WG, WG, "Online Earning WhatsApp group links Pakistan", [
    ("ONLINE EARNING PLATFORM", 76, "Online Earning", "PK", None),
    ("FUTURE EARNING", 77, "Online Earning", "PK", "shares Join button idx 77 with 'Cricket Lovers' (cricket section)"),
    ("Earning with Rashid", 78, "Online Earning", "PK", None),
    ("Trading Trusted Project", 79, "Online Earning", "PK", None),
    ("Online Earning With Khanzadi", 80, "Online Earning", "PK", None),
    ("Secret Of Earning", 81, "Online Earning", "PK", None),
    ("Make Money Online", 82, "Online Earning", "PK", None),
    ("Real Online PAKISTAN GROUP", 83, "Online Earning", "PK", "shares Join button idx 83 with 'Online Earning with Games'"),
    ("Online Earning with Games", 83, "Online Earning", "PK", "shares Join button idx 83 with 'Real Online PAKISTAN GROUP'"),
    ("Best Earning Apps", 84, "Online Earning", "PK", None),
    ("Earn Money 2024", 85, "Online Earning", "PK", None),
    ("Online Earning Group Pakistan", 86, "Online Earning", "PK", None),
    ("Money Making Skills", 87, "Online Earning", "PK", None),
    ("WhatsApp Earning Methods", 88, "Online Earning", "PK", None),
    ("ONLINE INCOME OPPORTUNITY", 89, "Online Earning", "PK", None),
    ("Pakistan Binance App", 90, "Crypto", "PK", None),
    ("Binance trade signals Pakistan", 91, "Crypto", "PK", None),
    ("UK Online work from Pakistan without investment", 92, "Online Earning", "PK", None),
    ("Play Game and Earn Money", 93, "Online Earning", "PK", None),
    ("Work From Home", 21, "Online Earning", "PK", "shares Join button idx 21 with 'PSL Live Updates' (cricket section)"),
    ("EBL PAKISTAN REAL ONLINE BUSINESS PAKISTAN NO.1", 94, "Online Earning", "PK", None),
    ("Freelancing", 95, "Freelance", "PK", None),
    ("Fiverr", 96, "Freelance", "PK", None),
    ("Fiverr Community", 97, "Freelance", "PK", None),
    ("Fiverr Buyer and Seller", 98, "Freelance", "PK", None),
    ("Pakistan earning platform", 99, "Online Earning", "PK", None),
    ("EBL PAKISTAN ONLINE WORK", 100, "Online Earning", "PK", None),
], None, None)

add(WG, WG, "Pakistan Cricket WhatsApp Group Links", [
    ("Cricket Warrior", 101, "Sports", "PK", None),
    ("Cricket Lovers", 77, "Sports", "PK", "shares Join button idx 77 with 'FUTURE EARNING' (earning section)"),
    ("World Cup Discussion", 102, "Sports", "PK", None),
    ("Fantasy Cricket Group", 103, "Sports", "PK", None),
    ("PTV SPORTS", 104, "Sports", "PK", "shares Join button idx 104 with 'PSL UPDATES'"),
    ("Live Cricket News", 105, "Sports", "PK", None),
    ("Boom Boom", 106, "Sports", "PK", None),
    ("Cricket Pakistan", 107, "Sports", "PK", None),
    ("Pakistan Cricket", 108, "Sports", "PK", None),
    ("Pak TV Cricket News", 109, "Sports", "PK", None),
    ("PTV Sports Cricket Group", 110, "Sports", "PK", None),
    ("PSL UPDATES", 104, "Sports", "PK", "shares Join button idx 104 with 'PTV SPORTS'"),
    ("T20, ICC Match", 111, "Sports", "PK", None),
    ("Cricket streaming App", 112, "Sports", "PK", None),
    ("MEN IN GREEN", 113, "Sports", "PK", None),
    ("Pakistan Cricket (🎗️)", 114, "Sports", "PK", None),
    ("Cricket News", 115, "Sports", "PK", None),
    ("Cricket Ke Dunia", 116, "Sports", "PK", None),
    ("T20 World Cup 2024", 117, "Sports", "PK", None),
    ("PSL Live Updates", 21, "Sports", "PK", "shares Join button idx 21 with 'Work From Home' (earning section)"),
    ("Cricket Confirm Update", 118, "Sports", "PK", None),
    ("PSL 2024", 119, "Sports", "PK", None),
    ("PCB Trial Info", 120, "Sports", "PK", None),
    ("Tape Ball Match Highlight", 121, "Sports", "PK", None),
    ("Islamabad United", 122, "Sports", "PK", None),
], None, None)

# ---------------- groupsnest.com ----------------
GN = "https://groupsnest.com/"
add(GN, GN, "Just added (newest per collection)", [
    ("Job Updates & Resources", 20, "Jobs", "PK", "411 members; collection: Jobs Pakistan"),
    ("Fashion Show Discussions", 23, "Community & Social", "XX", "348 members; collection: Fashion"),
    ("Group 181", 24, "Technology", "XX", "367 members; collection: Social Media"),
    ("Islamabad Photography Challenges", 25, "Community & Social", "PK", "340 members; collection: Islamabad"),
    ("Group 52", 26, "News", "PK", "519 members; collection: Breaking News Pakistan"),
    ("Sports Coaching Network", 28, "Sports", "XX", "482 members; collection: Sports"),
    ("Anime Series Watchlists", 29, "Entertainment", "XX", "684 members; collection: Anime"),
    ("Online Business Trends", 30, "Business", "PK", "353 members; collection: Online Business Pakistan"),
    ("Introduction to Coding", 31, "Education", "PK", "677 members; collection: Educational Pakistan"),
    ("BISP Empowerment Group", 33, "Community & Social", "PK", "698 members; collection: bisp pakistan"),
    ("Career Success in Banking", 34, "Jobs", "PK", "564 members; collection: bank jobs pakistan"),
], None, None)
add(GN, GN, "Direct WhatsApp group links by topic", [
    ("YouTube Content Hub", 35, "Technology", "XX", "1023 members; collection: Social Media"),
    ("Digital Marketing Creators", 36, "Technology", "XX", "1021 members; collection: Social Media"),
    ("Urdu Literary Lounge", 38, "Poetry", "PK", "950 members; collection: Urdu Poetry Pakistan"),
    ("Poets And Dreamers", 39, "Poetry", "PK", "940 members; collection: Urdu Poetry Pakistan"),
    ("Punjabi Relationships", 40, "Friendship", "XX", "681 members; collection: Punjabi"),
    ("Punjabi YouTubers Unite", 41, "Community & Social", "XX", "630 members; collection: Punjabi"),
    ("Online Buy Sell Pakistan", 43, "Buy & Sell", "PK", "1019 members; collection: Buy and Sell Pakistan"),
    ("Pakistan Client Leads", 45, "Real Estate", "PK", "1011 members; collection: Real Estate"),
    ("Pakistan Product Exchange", 46, "Buy & Sell", "PK", "997 members; collection: Buy and Sell Pakistan"),
    ("Device Repair Alerts", 48, "Technology", "PK", "982 members; collection: GSM"),
    ("Pakistan Agent Society", 49, "Real Estate", "PK", "977 members; collection: Real Estate"),
    ("Phone Service Training Room", 50, "Technology", "PK", "976 members; collection: GSM"),
    ("Future CSS Officers PK", 53, "Education", "PK", "1021 members; collection: CSS Pakistan"),
    ("Pak Exam Prep Team", 55, "Education", "PK", "1017 members; collection: General Knowledge Pakistan"),
    ("CSS Candidates Pakistan", 56, "Education", "PK", "1008 members; collection: CSS Pakistan"),
    ("Everyday Pakistan Trivia", 57, "Education", "PK", "978 members; collection: General Knowledge Pakistan"),
    ("Student Study Circle", 58, "Education", "PK", "921 members; collection: Educational Pakistan"),
    ("Knowledge Sharing Pakistan", 59, "Education", "PK", "917 members; collection: Educational Pakistan"),
    ("Pakistan Recruitment Network", 60, "Jobs", "PK", "991 members; collection: Jobs Pakistan"),
    ("Daily Jobs Update Pakistan", 61, "Jobs", "PK", "978 members; collection: Jobs Pakistan"),
    ("Interview Prep Hub", 63, "Jobs", "XX", "968 members; collection: Visa"),
    ("Daily Pay Jobs Hub", 65, "Jobs", "XX", "964 members; collection: Labour"),
    ("Worker Mutual Aid Space", 66, "Community & Social", "XX", "953 members; collection: Labour"),
    ("Travel And Visa Chatter", 67, "Travel", "XX", "937 members; collection: Visa"),
], None, None)

# ---------------- groupwa.link ----------------
GL = "https://groupwa.link/"
add(GL, GL, "Pakistani Girls WhatsApp Group", [
    ("Only girls", 1, "Friendship", "PK", None),
    ("Baby Pink", 2, "Friendship", "PK", None),
    ("Desi Gril", 4, "Friendship", "PK", None),
    ("Only girls club", 7, "Friendship", "PK", None),
    ("USA Girls", 8, "Friendship", "PK", "listed under Pakistani Girls section"),
    ("Pakistani girls group", 9, "Friendship", "PK", None),
    ("Full Masti Group", 10, "Friendship", "PK", None),
    ("Enjoy", 11, "Friendship", "PK", None),
    ("Love Girls", 12, "Friendship", "PK", None),
], None, None)
add(GL, GL, "Indian WhatsApp Group", e([
    ("ROCK STORE", 13), ("STATUS FINDER", 14), ("SP MART", 15), ("Lucky 2026", 16),
    ("TM MYTHIC MART", 17), ("Berozgar ADDA (Indian Only)", 18), ("GCHI FUN ZONE", 19),
    ("PATLU CARDER", 20), ("Free Healing 01", 21), ("Olympus rise", 22),
    ("Brainrott Refugees", 23), ("Indian Arts & Crafts", 24), ("SK FAMILY BROAD", 25),
    ("ClixoApp Sales & Marketing", 26), ("Hridoyer Spondon (হৃদয়ের স্পন্দন)", 27),
    ("SMP MC", 28), ("Anime Nexus", 29),
], "Community & Social", "IN"), None, None)
add(GL, GL, "Pakistani WhatsApp Group", [
    ("Qurano Hadeesh Islamic Post", 30, "Islamic", "PK", "also listed on whtsagrouplinks.com - dedupe by code on resolve"),
    ("LEGEND HUBB", 31, "Community & Social", "PK", None),
    ("hidden leaf village", 32, "Community & Social", "PK", None),
    ("4.5-6 FREE FILES", 33, "Community & Social", "PK", None),
    ("MR UZAIR SQUAD", 34, "Community & Social", "PK", None),
    ("SHAHZAIB SALLER", 35, "Community & Social", "PK", None),
    ("Social Ali Services", 36, "Community & Social", "PK", None),
    ("Daily Qur'an-o-Hadees", 37, "Islamic", "PK", "also listed on whtsagrouplinks.com - dedupe by code on resolve"),
    ("Ghazi Islamic Institute (GII)", 38, "Islamic", "PK", "also listed on whtsagrouplinks.com - dedupe by code on resolve"),
    ("Cricket Fans (کرکٹ کے دیوانے)", 39, "Sports", "PK", "also listed on whtsagrouplinks.com - dedupe by code on resolve"),
    ("MaShaAllah Brand Boutique And Reseller Group", 40, "Buy & Sell", "PK", "also listed on whtsagrouplinks.com - dedupe by code on resolve"),
    ("Alhamd Islamic Academy (الحمد اسلامک اکیڈمی)", 41, "Islamic", "PK", None),
    ("ADEEL ALAHMAR", 42, "Community & Social", "PK", "also listed on whtsagrouplinks.com - dedupe by code on resolve"),
    ("Varun kumar SEO agency India", 43, "Community & Social", "PK", None),
    ("Vogue Garments", 44, "Buy & Sell", "PK", "also listed on whtsagrouplinks.com - dedupe by code on resolve"),
], None, None)
add(GL, GL, "Make Money Online WhatsApp Group", e([
    ("EARN MONEY ONLINE", 45), ("Earn With Asif Team", 46), ("EARN WITH SHOZI", 47),
    ("Earn with Shakibhai", 48), ("ONLINE WORK.", 49), ("Money Club India", 50),
    ("Barakah Glow Hub", 51), ("ROYAL EARN OR GAMING COMMUNITY", 52),
    ("Online eArNinG learning FREE", 53), ("Work", 54), ("Online work", 55),
], "Online Earning", "XX"), None, None)
add(GL, GL, "Movie WhatsApp Group", e([
    ("NETFLIX Free Movie", 56), ("Movie Verse PK", 57), ("Movie group", 58),
    ("Company Movie's 420", 59), ("movie group", 60), ("Theatre daily", 61),
    ("Paid movies group", 62), ("Blood Moon Corporation", 63), ("Super AmaFlix Demo Group", 64),
], "Entertainment", "XX"), None, None)
add(GL, GL, "Share Market WhatsApp Group", e([
    ("US Stock Market Seminar", 65), ("Index Nifty Banknifty", 66), ("The Stock Bull", 67),
    ("Trading Experts - By Armaan", 68), ("Stock market trader", 69), ("Trading", 70),
], "Business", "XX"), None, None)
add(GL, GL, "USA WhatsApp Group", [
    ("ALEX EVENTS", 71, "Community & Social", "US", None),
    ("USA WhatsApp Group Links", 72, "Community & Social", "US", None),
    ("Manga Manhwa Hub", 73, "Entertainment", "US", None),
    ("Cheapest travel", 74, "Travel", "US", "listed under USA section; travel"),
    ("Gilgit Baltistan and K2 Tourism and Guiding", 75, "Travel", "PK", "listed under USA section; travel; also on whtsagrouplinks - dedupe on resolve"),
    ("TS & AP Real Estate Advisors", 76, "Real Estate", "US", "listed under USA section; also on whtsagrouplinks - dedupe on resolve"),
], None, None)
add(GL, GL, "Jobs WhatsApp Group", e([
    ("Gulf job vacancy", 77), ("Kashi Banaras security job", 78), ("Sarkari Vacancy 09", 79),
    ("Jobs available", 80), ("Job Vacancy's Group Bangalore", 81),
    ("Rafa International (JOB VACANCY)", 82), ("jobs4u", 83), ("Sunhr job group 1", 84),
    ("Baidesik Rojgari", 85),
], "Jobs", "XX"), None, None)
add(GL, GL, "Students WhatsApp Group", e([
    ("Learn German with each other", 86), ("Goethe exam Countdown", 87),
    ("Student Union of India (SUI) Non-Political", 88),
    ("Udemy On-Demand Trading Courses @99/- Only!", 90),
], "Education", "XX"), None, None)
leads.append({"name": "Ngfdopufdf", "code_or_invite": "Join-button outlink idx 89 on https://groupwa.link/ (code needs browser-capable resolution)",
              "source_page": GL, "note": "section=Students WhatsApp Group | category=Education | country=XX | name is gibberish; verify group title before listing"})
add(GL, GL, "Cricket WhatsApp Groups 2026", [
    ("DCZ ESPORTS COMMUNITY", 91, "Gaming", "XX", None),
    ("Cricket ~", 92, "Sports", "XX", None),
    ("Malik Sports Updates 56", 93, "Sports", "XX", None),
    ("MK SURE FIXED MATCH", 94, "Sports", "XX", "CAUTION: 'fixed match' suggests betting scam; vet before listing"),
], None, None)
add(GL, GL, "Cryptocurrency WhatsApp Group", e([
    ("Nawabz Crypto Updates", 95), ("CRYPTO TRADING High Level", 96),
    ("Gold & BTC Signals -FX FLASH", 97), ("Crypto Trading Guide", 98),
    ("Crypto Free Airdrop King", 99), ("free crypto airdrop", 100),
], "Crypto", "XX"), None, None)
add(GL, GL, "Trading WhatsApp Groups", e([
    ("KING OF DERIV SYNTHETIC MARKET", 101), ("Gold Sniper", 102),
    ("GOLD TRADING MASTER", 103), ("MR SUNNY TRADER", 104), ("Trade with Hamza", 105),
    ("Gold Trading Experts", 106), ("Prime Trade Institute", 107), ("HB Traders", 108),
    ("The Trading Classroom", 109), ("SHAH JAHAN FX TRADER$", 110),
    ("Fire stick subscription", 111), ("Share Market and Crypto trending", 112),
    ("Traders Terminal - Group", 113),
], "Business", "XX"), None, None)
add(GL, GL, "Forex Trading WhatsApp Group", e([
    ("FOREX TRADING GROUP", 114), ("The Forex Beacon", 115),
    ("AmirForexStudio- General", 116), ("FX GOLD KILLER", 117), ("Forex free", 118),
    ("TRADE GOLD MASTER", 119),
], "Business", "XX"), None, None)
add(GL, GL, "News WhatsApp Group", [
    ("Dawn newspaper group (3)", 120, "News", "PK", None),
    ("News Channel", 121, "News", "XX", None),
    ("First Bihari News", 122, "News", "IN", None),
    ("Daily Newspaper", 123, "News", "XX", None),
    ("ATH NEWS 11 & Patrika", 124, "News", "IN", None),
    ("Jankari", 125, "News", "IN", None),
    ("News Crime & Tech", 126, "News", "XX", None),
    ("Daily News update", 127, "News", "XX", None),
    ("Daily Hindi news", 128, "News", "IN", None),
    ("PAK JOBS", 129, "Jobs", "PK", "listed under News section"),
], None, None)
add(GL, GL, "Gaming WhatsApp Group", e([
    ("BGMI TOURNAMENT", 130), ("Malik Sports 05", 131), ("BGMI PAID HACK", 132),
    ("PRINCE NIAZI ARMY STORE 1", 133), ("Alfa Gaming Company", 134), ("Cricket Updates", 135),
    ("Hammad PUBG Store", 136), ("BGMI TOURNAMENT", 137),
    ("Sheeno Gaming ff / xs Afridi ff group", 138), ("FC MOBILE Weekend League Tournament", 139),
], "Gaming", "XX"), None, None)
add(GL, GL, "Poetry WhatsApp Group", e([
    ("LEGEND ANEES KI HAWELI", 140), ("HD Status Poetry 2023", 141),
    ("Urdu Shayari (اردو شعروشاعری)", 142), ("Pakeeza Ishq (پاکیزہ عشق)", 143),
    ("Romantic Poetry", 144), ("Noor-e-Wilayat", 145), ("POETRY (LINES)", 146),
    ("Photo editing group (فوٹو ایڈیٹنگ گروپ)", 147), ("Husn-e-Jahan (حسن جہاں)", 148),
    ("Poetry club", 149), ("Tanha Musafir Sad Poetry (تنہا مسافر)", 150),
    ("T&F SMART EARNING", 151), ("Mareez-e-Ishq (مریض عشق)", 152), ("Janaan (جاناں)", 153),
    ("Dastan-e-Ishq (داستان عشق)", 154), ("POETRY LOVERS", 155),
], "Poetry", "XX"), None, None)
add(GL, GL, "Friendship WhatsApp Group", e([
    ("Global friend group", 156), ("Friends group", 157), ("The Strangers", 158),
], "Friendship", "XX"), None, None)
add(GL, GL, "Sub4Sub WhatsApp Group", e([
    ("YOUTUBE FULL MONETIZATION GROWTH", 159), ("Chamet Agency Group", 160),
    ("YOUTUBE INDIAN SERVICE", 161), ("YouTube income generator", 162),
    ("YOUTUBE REAL SUBSCRIBE BUY", 163), ("Crescimento no YouTube", 164),
    ("YOUTUBE SUBSCRIBE AND MONETIZATION", 165), ("SUB TO SUB GROUP", 166),
    ("New YouTuber Supporter", 167),
], "Community & Social", "XX"), None, None)
add(GL, GL, "International WhatsApp Group Links", [
    ("International News", 168, "News", "XX", "listed under International section"),
    ("KAGE NO KLAN", 169, "Community & Social", "XX", None),
    ("Bisp Information", 170, "Community & Social", "PK", None),
    ("The population", 171, "Community & Social", "XX", None),
    ("JAHNAGIR AGENCY", 172, "Community & Social", "US", "listed under International section"),
    ("Welcome to the world", 173, "Community & Social", "XX", None),
    ("G.E.L Group", 174, "Community & Social", "XX", None),
    ("Global Friends Hub", 175, "Community & Social", "XX", None),
    ("Aircity International Consultants Pvt Ltd", 176, "Community & Social", "XX", None),
    ("NOPMO GLOBAL", 177, "Community & Social", "XX", None),
    ("Global English Learning Hub", 178, "Education", "XX", "listed under International section"),
    ("OTT SUBSCRIPTION SERVICES", 179, "Community & Social", "XX", None),
], None, None)
add(GL, GL, "YouTube WhatsApp Groups", e([
    ("Get 1k Youtube Subscribe", 180), ("YOUTUBE REAL WATCH TIME GROWTH", 181),
    ("YouTube subscriber", 182), ("YouTube Growth Community", 183),
    ("YOUTUBE REAL INDIAN SUBSCRIBERS", 184),
], "Community & Social", "XX"), None, None)
add(GL, GL, "UK WhatsApp Group", [
    ("UK online", 185, "Community & Social", "GB", None),
    ("Chat 'n chill", 186, "Community & Social", "GB", None),
    ("Timebucks Tips and tricks", 187, "Online Earning", "GB", "listed under UK section"),
    ("International Online Business", 188, "Business", "GB", "listed under UK section"),
    ("Global Consultant 1", 189, "Business", "GB", "listed under UK section"),
    ("E-Commerce business", 190, "Business", "GB", "listed under UK section"),
    ("AFFILIATE DISCUSSION", 191, "Business", "GB", "listed under UK section"),
    ("Real Job Updates", 192, "Jobs", "GB", "listed under UK section"),
    ("GADGETS SPHERE", 193, "Buy & Sell", "GB", "listed under UK section"),
    ("UniQue Bull Official Community", 194, "Business", "GB", "listed under UK section"),
    ("Avenue tous vendre (237)", 195, "Buy & Sell", "GB", "listed under UK section; French text"),
    ("Money earn tricks", 196, "Online Earning", "GB", "listed under UK section"),
], None, None)
add(GL, GL, "Shopping WhatsApp Group", e([
    ("Vtradebiz.shop Grp-10", 197), ("StyleBox One Shopping", 198), ("SHOPPING CORE", 199),
    ("Cloth Store", 200), ("Kitchen/Customize and Fabric Items", 201), ("Shopi Hub", 202),
    ("BLACK PEARL COLLECTION", 203), ("Aliyan Online Store", 204), ("Kaawish Boutique", 205),
    ("Shopdeal Customers", 206), ("DealZone [BUY] 3", 207),
    ("Faiza Hyderabadi Jadau Jewellery", 208), ("Best Loot Deals 1", 209),
    ("All Types Clothes & Dresses", 210), ("OUTVERRA MEN'S WHOLESALE RESELLING (FSD)", 211),
    ("AY Online Selling Store", 212), ("Tulip Charm Collection", 213), ("KASHMIRI JEWELRY", 214),
    ("online products sell", 215), ("MUZAMMIL COLLECTION", 216), ("Soft look store", 217),
], "Buy & Sell", "XX"), None, None)
add(GL, GL, "Social Media WhatsApp Groups", e([
    ("SHANKAR ONLINE SERVICES", 218), ("Anshu digital service", 219), ("Ahmad TikTok Shop", 220),
    ("Social media Growth hub", 221), ("DigitalDealWay", 222), ("Social Market", 223),
    ("Videos Pakistani", 224), ("TIKTOK FORYOU", 225), ("Social Media Promoter", 226),
    ("Cheap insta followers", 227), ("INSTAGRAM FOLLOWERS GROUP", 228),
    ("AYSH TikTok Sellers", 229), ("Insta Grow", 230),
], "Community & Social", "XX"), None, None)

# ---------------- domain discoveries ----------------
for d, pages, detail in [
    ("whtsagrouplinks.com", "homepage (7900+ listicle, updated 2026-10-28) + ~20 category subpages incl. friendship, tiktok, buy-and-sell, shopping, earn-money, work-from-home, youtube, urdu-poetry, indian, international, boys, rajasthan, farming, meditation, bhakti, business, pdf-books, gay, tamil-aunty",
     "WordPress; wp-json search endpoint worked once, posts endpoint 401s. Massive inventory, same template as whatsgroulink.com."),
    ("whatgroups.com", "whatsapp-group-links-pakistan/ (updated 2026-10-12) + homepage with movies/1000-member/YouTube sections + related pages (Dubai, USA, India, Online Earning)",
     "Table-format listicle; some Join buttons cross-link to sibling domain whatgrouplinks.org; idx 20 = www.whatsapp.com channel (skip)."),
    ("groupsnest.com", "homepage directory: 1,495 links in 33 collections across 18 categories with member counts + last-verified dates; collection pages not yet opened",
     "Structured directory with freshness dates; some collections last verified Oct 9, 2026. Collection pages likely hold more groups."),
    ("groupwa.link", "homepage (8000+ listicle) + 78 category pages (Jobs, Education, Cricket, Movies, Business, Islamic, News, Gaming, Online Earning, Health, Sports, Friendship...) + country pages (Pakistan, India, Worldwide)",
     "WordPress; wp-json open. CAUTION: page meta description says 'WhatsApp SexGroup links' and Girls section had adult-emoji names - apply porn filter per group on resolve."),
    ("whatspgroupslink.com", "foreign-whatsapp-group-links-join/ (555+ foreign groups; sections incl. Hot Aunty, Girls Vibes, channels)",
     "Not fetched yet; section names suggest mixed quality - vet before resolving."),
    ("whatgrouplinks.org", "sibling domain of whatgroups.com; receives Join-button cross-links from whatgroups.com Pakistan page (idx 63-66)",
     "Discovered via cross-links; likely single-group redirect pages."),
]:
    leads.append({
        "name": f"DOMAIN DISCOVERY: {d}",
        "code_or_invite": "n/a",
        "source_page": f"https://{d}/",
        "note": f"domain discovery | pages: {pages} | {detail}",
    })

with open(os.path.join(WAVE, "team25-fresh-listicles-new.json"), "w") as f:
    json.dump([], f, indent=1, ensure_ascii=False)
with open(os.path.join(WAVE, "team25-unverified-pending.json"), "w") as f:
    json.dump([], f, indent=1, ensure_ascii=False)
with open(os.path.join(WAVE, "team25-leads.json"), "w") as f:
    json.dump(leads, f, indent=1, ensure_ascii=False)

print("leads:", len(leads))
print("fresh: 0, pending: 0")
