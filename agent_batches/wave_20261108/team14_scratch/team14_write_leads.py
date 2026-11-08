import json
WAVE="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108"
leads=[]
def add(url, note):
    leads.append({"url": url, "source": "groupjoin.link", "note": note})
# resume pointers (API tag totals as of Nov 8 07:00 UTC; harvested ranges noted)
add("https://www.groupjoin.link/tag/business?page=41", "RESUME team14: tag 'business' total 1690 (85 pp); harvested p1-40. Resume p41.")
add("https://www.groupjoin.link/tag/pakistan?page=29", "RESUME team14: tag 'pakistan' total 1353 (68 pp); harvested p1-28. Resume p29.")
add("https://www.groupjoin.link/tag/gaming?page=36", "RESUME team14: tag 'gaming' total 1172 (59 pp); harvested p1-35. Resume p36.")
add("https://www.groupjoin.link/tag/sports?page=31", "RESUME team14: tag 'sports' total 1041 (53 pp); harvested p1-30. Resume p31.")
add("https://www.groupjoin.link/tag/shopping?page=36", "RESUME team14: tag 'shopping' total 916 (46 pp); harvested p1-35. Resume p36.")
add("https://www.groupjoin.link/tag/urdu?page=36", "RESUME team14: tag 'urdu' total 763 (39 pp); harvested p1-35. Resume p36.")
add("https://www.groupjoin.link/tag/english?page=6", "RESUME team14: tag 'english' total 1995 (100 pp); harvested p1-5 only. Resume p6; front pages mostly in union, watch fresh rate.")
add("https://www.groupjoin.link/tag/hindi?page=3", "RESUME team14: tag 'hindi' total 2053 (103 pp); harvested p1-2 only. Adult-skewed per team15 — probe adult ratio before committing verify budget. Resume p3.")
add("https://www.groupjoin.link/tag/tamil", "UNHARVESTED team14: tag 'tamil' total 9560 (478 pp) — probed only; adult-saturated per Nov 4 team13. Probe adult ratio on p1-2 first; huge tag, low priority.")
add("https://www.groupjoin.link/tag/indonesia", "RE-PROBE ONLY team14: tag 'indonesia' total 4381 (was 4311 Nov 6); pages past p220 exhausted per brief. Harvest only if total grows past 4381.")
# new tags discovered in team14 tag arrays — never probed, probe totals first
for slug, note in [
 ("marketing","NEW TAG team14: seen 442x in harvested tag arrays; probe total first."),
 ("games","NEW TAG team14: seen 428x in harvested tag arrays; probe total first."),
 ("advertising","NEW TAG team14: seen 424x in harvested tag arrays; probe total first."),
 ("apps","NEW TAG team14: seen 399x in harvested tag arrays; probe total first."),
 ("sinhala","NEW TAG team14: seen 221x in harvested tag arrays; probe total first."),
 ("songs","NEW TAG team14: seen 216x in harvested tag arrays; probe total first."),
 ("audio","NEW TAG team14: seen 199x in harvested tag arrays; probe total first."),
 ("web-series","NEW TAG team14: seen 172x in harvested tag arrays; probe total first."),
 ("jokes","NEW TAG team14: seen 148x in harvested tag arrays; probe total first."),
 ("art","NEW TAG team14: seen 144x in harvested tag arrays; probe total first."),
 ("malay","NEW TAG team14: seen 137x in harvested tag arrays; probe total first."),
 ("hindi-movies","NEW TAG team14: seen 132x in harvested tag arrays; probe total first."),
 ("english-movies","NEW TAG team14: seen 128x in harvested tag arrays; probe total first."),
 ("dubbed-movies","NEW TAG team14: seen 128x in harvested tag arrays; probe total first."),
 ("dating","NEW TAG team14: seen 68x in harvested tag arrays; probe total first (watch adult skew)."),
 ("masti","NEW TAG team14: seen 53x in harvested tag arrays; probe total first."),
 ("online-business","NEW TAG team14: seen 35x in harvested tag arrays; probe total first."),
 ("binance","NEW TAG team14: seen 43x in harvested tag arrays; probe total first (watch scam skew)."),
 ("reels","NEW TAG team14: seen 42x in harvested tag arrays; probe total first."),
 ("shorts","NEW TAG team14: seen 42x in harvested tag arrays; probe total first."),
 ("comedy","NEW TAG team14: seen 42x in harvested tag arrays; probe total first."),
 ("chatting","NEW TAG team14: seen 37x in harvested tag arrays; probe total first."),
 ("hollywood-movies","NEW TAG team14: seen 35x in harvested tag arrays; probe total first."),
 ("indian-movies","NEW TAG team14: seen 34x in harvested tag arrays; probe total first."),
 ("nigeria","NEW TAG team14: seen 34x in harvested tag arrays; probe total first (country tag)."),
 ("korean-movies","NEW TAG team14: seen 33x in harvested tag arrays; probe total first."),
 ("chinese-movies","NEW TAG team14: seen 33x in harvested tag arrays; probe total first."),
 ("japanese-movies","NEW TAG team14: seen 33x in harvested tag arrays; probe total first."),
]:
    add(f"https://www.groupjoin.link/tag/{slug}", note)
for i in range(30):
    try:
        open(f"{WAVE}/team14-groupjoin-leads.json","wb",buffering=0).write(json.dumps(leads,ensure_ascii=False,indent=1).encode())
        print("wrote leads n=",len(leads)); break
    except PermissionError:
        import time; time.sleep(5)
