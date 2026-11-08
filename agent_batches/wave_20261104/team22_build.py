import json, re

union = set(json.load(open('dedupe_union.json')))

raw = [
("NewsDay Zimbabwe","BWa5Sldqx4zJNCWGzW4dNw","ZW","News","Zimbabwe breaking news and current events WhatsApp group sharing daily headlines and updates."),
("Agri Business Zimbabwe","FeD0axWKNCvJoYfuaSE351","ZW","Business","Zimbabwe agribusiness WhatsApp group for farmers and traders discussing markets and farm business."),
("Zimbabwe Youths in Agriculture","KILN6JyO2XDI65d2TYijTz","ZW","Community","Zimbabwe youth agriculture WhatsApp community sharing farming ideas and opportunities."),
("ZIMBABWE JOBS","Aq09aCco0M83xsfwv7WEsw","ZW","Jobs","Zimbabwe jobs WhatsApp group posting job vacancies and employment alerts."),
("Model Our Zimbabwe","E1TABizkEki8jVVVcWMuPi","ZW","Friendship","Zimbabwe social WhatsApp group for making friends and chatting about everyday life."),
("Zimbabwe Daily Updates","FnwZ8EWo9LdE6hww4kq7BW","ZW","News","Daily Zimbabwe news updates WhatsApp group with headlines and trending stories."),
("ZIMBABWE ZIDELE LEADERS","EuCy99nx4RN1UE31b5uLAI","ZW","Community","Zimbabwe community WhatsApp group for local discussions and neighbourhood matters."),
("B.E.B.F ZIMBABWE 5","Liz6WruCXjZFTLwj64bCMq","ZW","Community","Zimbabwe WhatsApp community group for networking and group conversations."),
("KETO ZIMBABWE","LlD2otOt19BBbJWfVlggZE","ZW","Health","Zimbabwe keto diet WhatsApp group sharing weight-loss tips and healthy eating ideas."),
("Zim To Poland Group","HYQgAB5G5rp1ALPhMOZUpI","ZW","Community","Zimbabwe WhatsApp group for Zimbabweans planning or living in Poland, sharing relocation advice."),
("Zimbabwe Teachers","AtovTYQzDKdCa0ztMDB4ji","ZW","Education","Zimbabwe teachers WhatsApp group for educators sharing resources and school updates."),
("ZIM GARDENER, MAIDS & Security Guards","IXEwC2YhB5L3xhIZ6RgPRV","ZW","Jobs","Zimbabwe WhatsApp group for gardener, maid and security guard job seekers and employers."),
("Mash Goat Zimbabwe","CBux2S2ZDi7LfquauDJcRH","ZW","Business","Zimbabwe goat farming WhatsApp group for buying, selling and rearing goats."),
("FARMERS IN ZIMBABWE","D664YPOyXadGmeRTsEWDPW","ZW","Community","Zimbabwe farmers WhatsApp group sharing crop tips, weather and farming advice."),
("Investment & Account Management Zim Group","C7KOxl6PClhBkap41PvqPn","ZW","Finance","Zimbabwe investment WhatsApp group discussing finance, savings and account management."),
("Jobs Zimbabwe","JIboEM3HXSp6S3CgzIVOuK","ZW","Jobs","Zimbabwe WhatsApp jobs group with vacancy alerts and career opportunities."),
("Culture of Zimbabwe","CY069MU5kIZAjKSgpWMyuI","ZW","Community","Zimbabwe culture WhatsApp group celebrating traditions, heritage and national identity."),
("ZOE WHOLESALE","HcL9FKHJS0W6qvNv24Jsmm","ZW","Buy-Sell","Zimbabwe wholesale WhatsApp group for bulk buying and selling of goods."),
("Accommodation Grp zim","Jtdqb4OGu7UFoMHY9Ilwr2","ZW","Community","Zimbabwe accommodation WhatsApp group sharing rental listings and housing help."),
("YHRI ZIMBABWE","Hoe6KsICzdQ7OhLJJhuZcH","ZW","Community","Zimbabwe WhatsApp community group for social networking and discussions."),
("Plum Crazy Boutique zw","JtzI3E3gryAHE2y2T3kLb4","ZW","Buy-Sell","Zimbabwe boutique WhatsApp group selling clothes and fashion items online."),
("Zimbabwe Botswana and south Africa","KyMzcIej6HR98sfNEDRdoP","ZW","Community","Zimbabweans in Botswana and South Africa WhatsApp group for diaspora chat and support."),
("ZIM MAIDS EMPLOYERS","B6ekNFFdmlxD5VgN7tCZCO","ZW","Jobs","Zimbabwe WhatsApp group connecting domestic-worker employers with maid job seekers."),
("Zim hotseat celeb show","IVQ9lbyWqXNFyTk1QGV22H","ZW","Entertainment","Zimbabwe entertainment WhatsApp group for celebrity news and hotseat show gossip."),
("PERFUMES & COSMETICS SHOP","KwO5exlD5BU9hiqCq1fBT3","ZW","Buy-Sell","Zimbabwe perfumes and cosmetics WhatsApp shop for beauty products."),
("Trucks & Loads in Zimbabwe","IkcnYs2yuMS8j3OXKH4slU","ZW","Business","Zimbabwe trucking WhatsApp group connecting truckers with loads and transport jobs."),
("Zim Vpn Updates","C0A4eY6tuHp3Cc6ZqstR1p","ZW","Technology","Zimbabwe VPN WhatsApp group sharing internet updates and connectivity tips."),
("Glamorous Zimbabwe","BsUCVum0gvTA3OaiWW4CiO","ZW","Entertainment","Zimbabwe lifestyle WhatsApp group sharing fashion, glamour and entertainment news."),
("STOP ZIMBABWE TRAFFICKERS","KB4BSVjVfk94x8rAAjXsK9","ZW","Community","Zimbabwe community WhatsApp group raising awareness against human trafficking."),
("ZIM MODELS","LBcpV9XKxQq4oqeYj73CU5","ZW","Entertainment","Zimbabwe modelling WhatsApp group for models, photographers and fashion events."),
("CATHOLIC YOUTH IN ZIM","GqrWbKIzf9n86Q6aLI4jJN","ZW","Community","Zimbabwe Catholic youth WhatsApp group for faith discussions and church activities."),
("Zim Reggae Music","BH8eH3cTHEYA4oTvc5D6QO","ZW","Music","Zimbabwe reggae WhatsApp group sharing reggae and dancehall music updates."),
("New Zimbabwe","LF54b4ZhrK201byEhtoaXg","ZW","News","Zimbabwe news WhatsApp group with fresh national updates and discussions."),
("ZIM MAIDS & EMPLOYERS","HwfOAgXSoG5KSBBxRKwrJp","ZW","Jobs","Zimbabwe WhatsApp group for maids and employers to find domestic work matches."),
("Travel Tribe Zimbabwe","DTiHRdhUdhtKu2obCTfnba","ZW","Travel","Zimbabwe travel WhatsApp group sharing trip ideas, tours and travel tips."),
("Zim Airtime in S.A","LHW3oF0YDiC8iG8NCPcyA4","ZW","Business","Zimbabweans in South Africa WhatsApp group for airtime and mobile services."),
("Ps Fencing Zimbabwe","ESGYNVtH6t27gioeVil6Ay","ZW","Business","Zimbabwe fencing services WhatsApp group for perimeter fencing jobs and quotes."),
("Zim dancehall & Reggae","Ksrtl0IdpHgJzByGXStily","ZW","Music","Zimbabwe dancehall and reggae WhatsApp group for music lovers and artists."),
("Zimboz in kappa","BPTUzMUdwlLJHLuaZ1JfZY","ZW","Community","Zimbabwe diaspora WhatsApp group for Zimbabweans living abroad."),
("Travel Zimbabwe","EIzgah3onXa1HoeynTQlwt","ZW","Travel","Zimbabwe tourism WhatsApp group sharing travel spots and holiday ideas."),
("JAPAN to ZIM cars","LxtMRu7oEq61rI0oPdotvc","ZW","Buy-Sell","Zimbabwe WhatsApp group for importing Japanese cars and auto deals."),
("ZIM MARKETING GRP","5MS99otB4V69gnQpMl6ELE","ZW","Business","Zimbabwe marketing WhatsApp group for promoting businesses and products."),
("ZIM CATHOLIC MUSIC","Fh2HMVuCvIY1WEt976NLdL","ZW","Music","Zimbabwe Catholic music WhatsApp group sharing gospel songs and choir music."),
("Compassion Zimbabwe","H9f7pFZDPZjE0S9uIA1IUe","ZW","Community","Zimbabwe charity WhatsApp group for compassionate giving and community support."),
("ZIM FARMERS FORUM","G3S6ibX40oYJERBPjFGZ7f","ZW","Community","Zimbabwe farmers forum WhatsApp group for agricultural discussion and advice."),
("Fuel Saver Cars Zimbabwe","Gx2ZhbfDHoY0tjXSMXTIvR","ZW","Business","Zimbabwe WhatsApp group discussing fuel-saving cars and auto deals."),
("Zim Online Car Sales","1RiULSG78xtDgQH6ogIaek","ZW","Buy-Sell","Zimbabwe online car sales WhatsApp group for buying and selling vehicles."),
("House Maid Zimbabwe","CGeW9VJevXPIVGH7i8er5V","ZW","Jobs","Zimbabwe WhatsApp group for house maid jobs and domestic work hiring."),
("Karry spices Zimbabwe","D6rQB2NwnO61iOkspbhkxb","ZW","Business","Zimbabwe spices WhatsApp group for selling curry spices and food products."),
("BREAKING NEWS ZIMBABWE GROUP","Df5b6JqPqtH5HnOQd8B2wA","ZW","News","Zimbabwe breaking news WhatsApp group with urgent national news alerts."),
("University of Ghana Students","ByIVd6hi0i0JGEIQj1dwJU","GH","Education","University of Ghana students WhatsApp group for campus chat and study help."),
("CONSTRUCTION JOBS IN GHANA","JMbetnxC3z7KXiDYpgj9OH","GH","Jobs","Ghana construction jobs WhatsApp group posting building site vacancies."),
("Ghana Football Fans Chat","DASensFXL5A0tGcSLH8Fjr","GH","Sports","Ghana football fans WhatsApp group for match chat and football news."),
("University of Ghana group chat","Eu8wn83D7FdFIfinPKsXGN","GH","Education","University of Ghana WhatsApp group chat for students and campus discussions."),
("FIFA & UEFA News Ghana Fans","HVAbBZJWafC1Ufyt2ODDLR","GH","Sports","Ghana WhatsApp group for FIFA and UEFA football news and fan discussions."),
("Ghana Government Jobs","IesGrKaKAo67i5ivZtt8ZS","GH","Jobs","Ghana government jobs WhatsApp group sharing public sector vacancy alerts."),
("Nurses Service Ghana","Fgh0mTNpsZK9DdgreRLc29","GH","Jobs","Ghana nurses WhatsApp group for nursing jobs and healthcare career updates."),
("Pindula News WhatsApp Group 4","BTNg4aFnwdv7l9vtDCok3L","ZW","News","Pindula News Zimbabwe WhatsApp group sharing top daily news updates."),
("Pindula News WhatsApp Group 5","IycmLwt1BsH1EqVVF3rlEJ","ZW","News","Pindula News Zimbabwe WhatsApp group with selected daily news highlights."),
("Pindula News WhatsApp Group 6","LEKCxcTGwfN6CKg1tvfkOL","ZW","News","Pindula News Zimbabwe WhatsApp group for the latest Zimbabwe news stories."),
("Pindula News WhatsApp Group 7","JvYZJJqRKNjAW6Xol6iJWR","ZW","News","Pindula News Zimbabwe WhatsApp group delivering daily news selections."),
("IAM Uganda Chapter WhatsApp Group","LM9Yj3YZkfs1EMO9E10lUm","UG","Business","Institute of Asset Management Uganda Chapter WhatsApp group for asset management professionals."),
]

seen, kept, dup_union, dup_batch = set(), [], 0, 0
note = ("transport failure: subagent sandbox has no direct egress (curl CONNECT times out via proxy; "
        "browser fetcher returns 403 on chat.whatsapp.com) - og:title verification impossible here; retry with live-browser leg")
for title, code, country, cat, desc in raw:
    if not re.fullmatch(r"[A-Za-z0-9]{20,24}", code):
        continue
    if code in union:
        dup_union += 1
        continue
    if code in seen:
        dup_batch += 1
        continue
    seen.add(code)
    kept.append({"name": title, "category": cat, "country": country,
                 "description": desc,
                 "invite": "https://chat.whatsapp.com/" + code, "image": "",
                 "note": note})

print("PENDING-JSON-BEGIN")
print(json.dumps(kept, ensure_ascii=False))
print("PENDING-JSON-END")
print("kept:", len(kept), "| dup_union:", dup_union, "| dup_batch:", dup_batch)

leads = [
{"domain":"whatsagroupslinks.com","url":"https://whatsagroupslinks.com/zambia-whatsapp-group-links/","why":"Fresh ZM directory, scraped ZW+ZM; likely has NG/KE/GH country pages (Zambia page links Yemen internally) - other Africa pages unmined"},
{"domain":"whatsagroupslinks.com","url":"https://whatsagroupslinks.com/","why":"Same domain homepage - find Nigeria/Kenya/Ghana/Uganda country archive pages next wave"},
{"domain":"whatgroups.com","url":"https://whatgroups.com/zimbabwe-whatsapp-group-links/","why":"Fresh ZW domain, scraped (all-dup vs whatsagroupslinks); internal links: Nigeria WhatsApp Group Links, WhatsApp Kenya group links - both unmined"},
{"domain":"whtspgrouplink.com","url":"https://whtspgrouplink.com/ghana-whatsapp-group-links/","why":"GH page scraped (only SG/MY/Mekong retired for this domain); has Zimbabwe, Uganda, Angola, Cuba, Uruguay country pages - ZW/UG unmined"},
{"domain":"pkwhatsgrouplinks.com","url":"https://pkwhatsgrouplinks.com/zimbabwe-whatsapp-group-links/","why":"Fresh domain (Pakistan network) - ZW page is 100% /invite/ CHANNEL codes (all 16 excluded); may have real group pages for other countries, verify format before mining"},
{"domain":"lagoswiki.com.ng","url":"https://www.lagoswiki.com.ng/p/add-your-whatsapp-business-group-links.html","why":"Nigeria - embeds a live 'newest WhatsApp groups' list (Google Apps Script feed was erroring today; retry)"},
{"domain":"7hubent.com.ng","url":"https://www.7hubent.com.ng/2024/06/7hubent-whatsapp-tv-channel-and-group.html","why":"Nigeria - 7hubent Tech claims 10,000+ NG business groups; actual group-list pages carry chat.whatsapp.com codes"},
{"domain":"ghanainfo.net","url":"https://www.ghanainfo.net/category/international/","why":"Ghana - curated GH WhatsApp groups with CLICK TO JOIN links (Intercessors for Christ, Houses for Sale, etc.) - codes behind join buttons, needs browser leg"},
{"domain":"linktogroups.com","url":"https://linktogroups.com/en/blog/top-kenyan-telegram-whatsapp-groups-dating-socialites-2026","why":"Kenya - 4 KE listing pages (single mothers dating, hot girls group chat 18+, connections/funmates) - links go through linktogroups.com listings; browser leg needed"},
{"domain":"techsslash.com","url":"https://techsslash.com/kenya-whatsapp-group-links/","why":"Kenya - 520+ listicle (2024); link table needs browser-leg code resolution"},
{"domain":"news.pindula.co.zw","url":"https://news.pindula.co.zw/2022/06/08/join-a-pindula-news-whatsapp-group/","why":"ZW - Pindula News group codes published on page; 8 of 12 already in union, 4 banked pending"},
{"domain":"human-unity.org","url":"https://human-unity.org/wp-content/uploads/2026/01/LIST-OF-GROUPS-SUPPORTING-HUMAN-UNITY-AND-ENDING-MUTUAL-HARM.pdf","why":"UG - Human Unity Kampala/Kaliro codes already in union (other teams); skip re-scrape"},
]
print("LEADS-JSON-BEGIN")
print(json.dumps(leads, ensure_ascii=False))
print("LEADS-JSON-END")
print("leads:", len(leads))
print("VERIFIED-JSON-BEGIN")
print(json.dumps([], ensure_ascii=False))
print("VERIFIED-JSON-END")
print("verified: 0 (no live verification possible from this sandbox)")
