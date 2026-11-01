import subprocess, re, json, time, sys, os
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
def verify(code):
    try:
        p = subprocess.run(['curl','-sL','-m','60','-A',UA,'https://chat.whatsapp.com/'+code],
                           capture_output=True, text=True, timeout=70)
        html = p.stdout
        m = re.search(r'<meta property="og:title" content="([^"]*)"', html)
        title = m.group(1) if m else ''
        low = html.lower()
        if not title or "couldn't look up link" in title.lower() or "couldn't look up the invite link" in low[:3000]:
            return False, title or 'DEAD'
        return True, title
    except Exception as e:
        return False, 'ERR:'+str(e)[:60]
if __name__ == '__main__':
    jobs = json.load(open(sys.argv[1]))  # list of {code,name,category,country,description}
    out_path = sys.argv[2]
    done = {}
    if os.path.exists(out_path):
        done = json.load(open(out_path))
    for j in jobs:
        c = j['code']
        if c in done:
            print('skip', c); continue
        ok, t = verify(c)
        j['live'] = ok; j['og_title'] = t
        done[c] = j
        json.dump(done, open(out_path,'w'), indent=1)
        print(c, ok, '|', t, '|', j['name'])
        time.sleep(0.5)
