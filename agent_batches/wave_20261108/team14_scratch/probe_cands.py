import json, subprocess, time, urllib.parse
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
def total(tag):
    url="https://api.groupjoin.link/groups?tag="+urllib.parse.quote(tag)+"&page=1&limit=1&safeSearch=blur"
    try:
        r=subprocess.run(["curl","-s","--max-time","30","-A",UA,url],capture_output=True,text=True,timeout=35)
        d=json.loads(r.stdout)
        return d.get("total"), d.get("totalPages")
    except Exception as e:
        return f"ERR:{e}", None
cands=["music","movies","cricket","football","study","quran","islam","naat","poetry","shayari",
"recipes","cooking","travel","photography","books","novels","crypto","bitcoin","forex","freelancing",
"fiverr","digital-marketing","programming","python","ai","pubg","free-fire","ludo","love","status",
"quotes","motivation","fitness","gym","beauty","makeup","mehndi","mobile","cars","bikes","property",
"lahore","karachi","islamabad","dubai","uae","saudi-arabia","malaysia","nepal","kenya","ghana",
"south-africa","ethiopia","nigeria","usa","uk","canada","australia","germany","italy","spain","france",
"turkey","egypt","morocco","algeria","tunisia","jordan","lebanon","iraq","yemen","oman","qatar","kuwait",
"bahrain","palestine","sudan","somalia","tanzania","uganda","zambia","zimbabwe","cameroon","senegal",
"mali","exams","ielts","scholarships","online-earning","part-time","dropshipping","amazon","ecommerce",
"punjabi","sindhi","pashto","balochi","bengali","marathi","gujarati","telugu","kannada","nepali",
"sinhala","kashmiri","sad-poetry","romantic","attitude","whatsapp-status","dpz","jobs-alerts",
"css","nursing","engineering","medical","doctors","teachers","students","university","college",
"hockey","badminton","kabaddi","wrestling","boxing","tennis","golf","racing","fishing","hunting",
"gardening","farming","agriculture","animals","pets","dogs","cats","birds","fashion-design",
"interior-design","architecture","law","accounting","banking","insurance","real-estate","rent",
"plots","flats","houses","jobs-in-dubai","jobs-in-saudi","visa","immigration","ielts-preparation",
"english","urdu-poetry","islamic","ramadan","hajj","umrah","madrasa","hifz","tilawat","bayan",
"nasheed","hamd","durood","wazaif","taweez","astrology","horoscope","palmistry","dreams",
"cooking-recipes","food","fast-food","baking","cakes","mehndi-design","henna","bridal","wedding",
"marriage","rishta","dating","friendship-day","birthday","shadi","valentine"]
res={}
for t in cands:
    tot,pages=total(t)
    res[t]=(tot,pages)
    print(f"{t:25} total={tot} pages={pages}",flush=True)
    time.sleep(0.3)
json.dump(res,open("team14_tag_probe.json","w"),indent=1)
print("DONE")
