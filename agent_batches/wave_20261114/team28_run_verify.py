import json, time, requests
from team28_verify import check, UA

fresh = json.load(open('team28-fresh.json'))
done = {}
try:
    for line in open('team28-verify-results.jsonl'):
        d = json.loads(line)
        done[d['code']] = d
except FileNotFoundError:
    pass
print("already verified:", len(done), "remaining:", len(fresh)-len(done))
s = requests.Session()
with open('team28-verify-results.jsonl', 'a') as f:
    for item in fresh:
        code = item['code']
        if code in done:
            continue
        st, info = check(s, code)
        rec = {"code": code, "name_mined": item.get('name',''), "sources": item.get('sources',[]), "status": st, "title": info if st=='live' else '', "reason": info if st!='live' else ''}
        f.write(json.dumps(rec, ensure_ascii=False)+"\n"); f.flush()
        done[code] = rec
        print(code, st, (info or '')[:60], flush=True)
        time.sleep(1.2)
print("DONE. live:", sum(1 for d in done.values() if d['status']=='live'),
      "dead:", sum(1 for d in done.values() if d['status']=='dead'),
      "pending:", sum(1 for d in done.values() if d['status']=='pending'))
