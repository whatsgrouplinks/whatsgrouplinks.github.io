import requests, re, time, json, os
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
CANDIDATES = [
 "sheffield","bristol","nottingham","newcastle","edinburgh","glasgow","cardiff","oxford",
 "cambridge","york","hull","norwich","plymouth","exeter","portsmouth","leicester","coventry",
 "bradford","derby","sunderland","middlesbrough","stoke","wolverhampton","peterborough",
 "swindon","bath","brighton","canterbury","belfast","bournemouth","southend","colchester",
 "ipswich","luton","watford","slough","croydon","blackpool","stoke-on-trent","preston",
 "eastlondon","westlondon","northlondon","southlondon","central-london",
 "birminghamhouse","leedshouse","readinghouse","southamptonhouse","warringtonhouse",
 "miltonkeyneshouse","edinburghhouse","glasgowhouse","sheffieldhouse","cardiffhouse",
 "newcastlehouse","nottinghamhouse","eastmidlandshouse","scotlandhouse","southwestncardiffhouse",
 "kent","essex","surrey","yorkshire","wales","merseyside","lancashire","cheshire",
 "hampshire","devon","cornwall","somerset","gloucestershire","wiltshire","norfolk","suffolk",
]
state = json.load(open("probed.json")) if os.path.exists("probed.json") else {}
for s in CANDIDATES:
    if s in state:
        continue
    u = f"https://livinintheuk.com/whatsappgroup-city-{s}"
    found = []
    for attempt in range(2):
        try:
            r = requests.get(u, headers=UA, timeout=30, allow_redirects=True)
            if r.status_code == 200:
                codes = sorted(set(re.findall(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})', r.text + " " + r.url)))
                if codes or "chat.whatsapp.com" in r.text or "whatsapp" in r.url.lower():
                    found = codes
                    state[s] = {"status": 200, "final": r.url, "codes": codes}
                else:
                    state[s] = {"status": 200, "final": r.url, "codes": []}
                print(s, "-> 200", r.url[:60], "codes:", codes)
            elif r.status_code == 404:
                state[s] = {"status": 404}
                print(s, "-> 404")
            else:
                state[s] = {"status": r.status_code, "final": r.url}
                print(s, "->", r.status_code, r.url[:60])
            break
        except Exception as e:
            print(s, "try", attempt, "ERR", str(e)[:70]); time.sleep(2)
    else:
        state[s] = {"error": "transport failure"}
    json.dump(state, open("probed.json", "w"), indent=1)
    time.sleep(1)
print("PHASE2 DONE")
