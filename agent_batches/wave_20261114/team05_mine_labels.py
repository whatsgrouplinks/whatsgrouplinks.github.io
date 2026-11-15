"""Mine groupslinks.com category/country label pages (page 1 of each label).
Label URLs extracted live from the listing page footer nav."""
import re, json, time, sys, os
import requests

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114/'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}

def fetch(sess, url):
    for i in range(3):
        try:
            r = sess.get(url, timeout=60)
            if r.status_code == 200:
                return r.text
            print(f'{url} HTTP {r.status_code}', flush=True)
        except Exception as e:
            print(f'{url} ERR {e}', flush=True)
        time.sleep(5)
    return None

def parse(h):
    out = []
    for c in re.findall(r'<article class="grplink-wa-related-card">(.*?)</article>', h, re.S):
        m = re.search(r'href="https://www\.groupslinks\.com/groups/([^/]+)/"', c)
        t = re.search(r'grplink-wa-related-card__title">([^<]+)</span>', c)
        co = re.search(r'badge--country">([^<]+)</span>', c)
        tp = re.search(r'badge--topic">([^<]+)</span>', c)
        inv = re.search(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})', c)
        out.append({
            'detail': m.group(1) if m else '',
            'name': (t.group(1).strip() if t else ''),
            'country_ar': (co.group(1).strip() if co else ''),
            'topic_ar': (tp.group(1).strip() if tp else ''),
            'code': (inv.group(1) if inv else ''),
        })
    return out

def main():
    sess = requests.Session()
    sess.headers.update(UA)
    h = fetch(sess, 'https://www.groupslinks.com/page/61/')
    labels = sorted(set(re.findall(r'href="(https://www\.groupslinks\.com/search/label/[^"]+)"', h or '')))
    print(f'label pages found: {len(labels)}', flush=True)
    allc = []
    for url in labels:
        hh = fetch(sess, url)
        if not hh:
            print(f'FAIL {url}', flush=True)
            continue
        cards = parse(hh)
        print(f'{url}: {len(cards)} cards, codes={sum(1 for c in cards if c["code"])}', flush=True)
        for c in cards:
            c['label_url'] = url
        allc += cards
        time.sleep(1.0)
    with open(os.path.join(WAVE, 'team05_cards_labels.json'), 'w', encoding='utf-8') as f:
        json.dump(allc, f, ensure_ascii=False, indent=1)
    print('TOTAL label cards', len(allc), flush=True)

if __name__ == '__main__':
    main()
