#!/usr/bin/env python3
"""Team14 wave 20261108: groupjoin.link harvest via api.groupjoin.link.
Stage 1: NEW tags (never harvested). Stage 2: resume ranges from team15 P5 leads.
Fetch: 3 workers, curl, retries. Raw JSONL snapshot per page (crash-safe)."""
import json, re, subprocess, time, urllib.parse, concurrent.futures, sys, os

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108"
RAW = os.path.join(WAVE, "team14_raw.jsonl")
LINK_RE = re.compile(r"https://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]{22})")

STAGE1 = [
 ("music",1,15),("movies",1,14),("love",1,14),("status",1,14),
 ("cricket",1,6),("poetry",1,8),("photography",1,8),("islamic",1,10),
 ("crypto",1,10),("forex",1,9),("pubg",1,10),("malaysia",1,9),
 ("mobile",1,7),("students",1,7),("travel",1,4),("fitness",1,4),
 ("lahore",1,4),("study",1,4),("punjabi",1,4),("quotes",1,5),
 ("beauty",1,5),("romantic",1,4),("football",1,3),("motivation",1,3),
 ("quran",1,2),("karachi",1,2),("food",1,2),("dubai",1,2),("cars",1,2),
 ("kenya",1,1),("shayari",1,1),("books",1,1),("university",1,1),
 ("nepal",1,1),("property",1,1),("hindi",1,2),("english",1,5),
 ("ludo",1,1),("cooking",1,1),("recipes",1,1),("freelancing",1,1),
 ("makeup",1,1),("islamabad",1,1),("ielts",1,1),("exams",1,1),
 ("scholarships",1,1),("sindhi",1,1),("pashto",1,1),("nursing",1,1),
 ("css",1,1),("wedding",1,1),("rishta",1,1),("ramadan",1,1),
]
STAGE2 = [
 ("business",21,40),("pakistan",9,28),("gaming",16,35),("sports",11,30),
 ("shopping",16,35),("youtube",13,23),("urdu",16,35),("school",13,22),
 ("career",11,17),("fashion",11,15),("trading",11,14),("clothing",9,11),
 ("online-shopping",12,12),("sri-lanka",17,36),("friendship",11,17),
 ("girls",31,37),("work-from-home",11,12),
]

def jobs_for(stage):
    jobs=[]
    for tag,a,b in stage:
        for p in range(a,b+1):
            jobs.append((tag,p))
    return jobs

def fetch_page(tag, page):
    url = ("https://api.groupjoin.link/groups?tag=" + urllib.parse.quote(tag)
           + f"&page={page}&limit=20&safeSearch=blur")
    for attempt in range(3):
        try:
            r = subprocess.run(["curl","-s","--max-time","45","-A",UA,url],
                               capture_output=True, text=True, timeout=50)
            d = json.loads(r.stdout)
            data = d.get("data", [])
            return tag, page, d.get("total"), data, None
        except Exception as e:
            time.sleep(5)
    return tag, page, None, [], "fetch-fail"

def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "1"
    jobs = jobs_for(STAGE1 if stage == "1" else STAGE2)
    print(f"STAGE {stage}: {len(jobs)} pages", flush=True)
    # resume: skip pages already in raw file
    done = set()
    if os.path.exists(RAW):
        with open(RAW) as f:
            for line in f:
                try:
                    o = json.loads(line)
                    done.add((o["tag"], o["page"]))
                except Exception:
                    pass
    todo = [j for j in jobs if j not in done]
    print(f"already have {len(done)} pages; todo {len(todo)}", flush=True)
    n_items = 0
    with open(RAW, "a") as out:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
            futs = {ex.submit(fetch_page, t, p): (t, p) for t, p in todo}
            done_n = 0
            for fut in concurrent.futures.as_completed(futs):
                tag, page, total, data, err = fut.result()
                done_n += 1
                if err:
                    print(f"  FAIL {tag} p{page}", flush=True)
                    continue
                recs = []
                for g in data:
                    m = LINK_RE.search(g.get("link","") or "")
                    if not m:
                        continue
                    recs.append({
                        "code": m.group(1),
                        "name": g.get("group_title","") or "",
                        "desc_raw": g.get("group_desc","") or "",
                        "cat_slug": (g.get("category") or {}).get("category_slug",""),
                        "cat_name": (g.get("category") or {}).get("category_name",""),
                        "country": ((g.get("country") or {}).get("iso2") or "International"),
                        "tags": g.get("tags") or [],
                        "nsfw": g.get("nsfw"),
                        "contentRating": g.get("contentRating"),
                        "tag": tag, "page": page, "total": total,
                    })
                n_items += len(recs)
                out.write("\n".join(json.dumps(r, ensure_ascii=False) for r in recs) + "\n")
                out.flush()
                if done_n % 20 == 0 or len(recs) == 0:
                    print(f"  {done_n}/{len(todo)} {tag} p{page}: {len(recs)} (total {total}) cum={n_items}", flush=True)
    print(f"STAGE {stage} DONE pages={len(todo)} items={n_items}", flush=True)

if __name__ == "__main__":
    main()
