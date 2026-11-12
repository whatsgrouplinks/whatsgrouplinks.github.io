import re, json, time, sys, os, html
import requests

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}

def check(sess, code):
    """Returns (status, og_title). live = non-empty og:title; dead-empty = empty;
    pending = transport failure after spaced retry."""
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
            # empty title: re-check once more after a pause before calling dead
            if attempt < 2:
                time.sleep(8)
                continue
            # fallback: og:description — but WhatsApp serves the GENERIC
            # "WhatsApp Group Invite" description on dead/invalid links too,
            # so only a non-generic description counts as live.
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

    # CONTROLS FIRST
    print('CONTROL live code KrDwdK8EIkB6vgauHg5M7N ...', flush=True)
    st, title = check(sess, 'KrDwdK8EIkB6vgauHg5M7N')
    print(f'CONTROL live: {st} | {title[:80]}', flush=True)
    print('CONTROL fabricated code ZZZZZZZZZZZZZZZZZZZZZZ ...', flush=True)
    st2, title2 = check(sess, 'ZZZZZZZZZZZZZZZZZZZZZZ')
    print(f'CONTROL fabricated: {st2} | {title2[:80]}', flush=True)
    if st != 'live':
        print('WARNING: live control did NOT verify live — aborting', flush=True)
        return
    if st2 == 'live':
        print('WARNING: fabricated control verified live — aborting', flush=True)
        return

    res = []
    state_path = out_path + '.state.json'
    done = set()
    if os.path.exists(state_path):
        prev = json.load(open(state_path, encoding='utf-8'))
        res = prev
        done = {r['code'] for r in prev}
        print(f'resuming: {len(res)} already verified', flush=True)
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
