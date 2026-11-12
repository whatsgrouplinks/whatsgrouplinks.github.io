import re, json, time, sys, os, html
import requests

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}

def check(sess, code):
    url = 'https://chat.whatsapp.com/' + code
    last_err = ''
    for attempt in range(3):
        try:
            r = sess.get(url, timeout=75)
            body = r.text
            m = re.search(r'<meta property="og:title" content="([^"]*)"', body)
            title = html.unescape(m.group(1)).strip() if m else ''
            if title:
                return ('live', title)
            if attempt < 2:
                time.sleep(8)
                continue
            d = re.search(r'<meta property="og:description" content="([^"]*)"', body)
            desc = html.unescape(d.group(1)).strip() if d else ''
            if desc and desc != 'WhatsApp Group Invite':
                return ('live', desc)
            return ('dead-empty', '')
        except Exception as e:
            last_err = str(e)[:100]
            print(f'  {code} transport err attempt {attempt+1}: {last_err}', flush=True)
            time.sleep(10)
    return ('pending', last_err)

def main():
    in_path, out_path = sys.argv[1], sys.argv[2]
    cands = json.load(open(in_path, encoding='utf-8'))
    sess = requests.Session()
    sess.headers.update(UA)
    res = []
    state_path = out_path + '.state.json'
    done = set()
    if os.path.exists(state_path):
        prev = json.load(open(state_path, encoding='utf-8'))
        res = prev
        done = {r['code'] for r in prev}
    for c in cands:
        if c['code'] in done:
            continue
        st, title = check(sess, c['code'])
        c['status'] = st
        c['og_title'] = title
        print(c['code'], st, '|', title[:70], '|', c['name'][:40], flush=True)
        res.append(c)
        done.add(c['code'])
        json.dump(res, open(state_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        time.sleep(0.7)
    json.dump(res, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    from collections import Counter
    print(Counter(r['status'] for r in res))

if __name__ == '__main__':
    main()
