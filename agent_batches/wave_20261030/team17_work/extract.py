import re, html, json, sys

def extract(page_file):
    with open(page_file, encoding='utf-8', errors='ignore') as f:
        raw = f.read()
    items = []
    pat = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{22})\b')
    for m in re.finditer(r'<li[^>]*>(.*?)</li>', raw, re.S | re.I):
        chunk = m.group(1)
        links = pat.findall(chunk)
        if not links:
            continue
        text = re.sub(r'<a[^>]*>.*?</a>', '', chunk, flags=re.S | re.I)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = html.unescape(text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[-–—\s]*Join$', '', text).strip()
        for code in links:
            items.append({'name': text, 'code': code})
    return items

if __name__ == '__main__':
    data = extract(sys.argv[1])
    json.dump(data, sys.stdout, ensure_ascii=False, indent=1)
    print(f"# total: {len(data)}", file=sys.stderr)
