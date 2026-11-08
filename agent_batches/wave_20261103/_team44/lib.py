import re, html as h, requests, time
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
def fetch(url, timeout=22, tries=3, sleep=1.5):
    for i in range(tries):
        try:
            r=requests.get(url,headers=UA,timeout=timeout)
            if r.status_code==404: return None
            r.raise_for_status()
            return r.text
        except Exception:
            time.sleep(sleep*(i+1))
    return None
def extract_li_join(page_html):
    items=[]
    for m in re.finditer(r'<li[^>]*>(.*?)</li>', page_html, re.S|re.I):
        li=m.group(1)
        a=re.search(r'<a[^>]+href="(https?://chat\.whatsapp\.com/(?:invite/)?[A-Za-z0-9]{20,24})"[^>]*>', li)
        if not a: continue
        before=li[:a.start()]
        txt=' '.join(h.unescape(re.sub(r'<[^>]+>',' ',before)).split())
        name=re.sub(r'[\u2013\u2014-]\s*Join\s*$','',txt).strip(' \u2013\u2014-\u00a0')
        if name and 'whatsapp group links' not in name.lower(): items.append((name, a.group(1)))
    return items
def extract_table_join(page_html):
    items=[]
    for m in re.finditer(r'<tr[^>]*>(.*?)</tr>', page_html, re.S|re.I):
        tr=m.group(1)
        a=re.search(r'<a[^>]+href="(https?://chat\.whatsapp\.com/(?:invite/)?[A-Za-z0-9]{20,24})"[^>]*>', tr)
        if not a: continue
        tds=re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S|re.I)
        name=None
        for td in tds:
            txt=' '.join(h.unescape(re.sub(r'<[^>]+>',' ',td)).split())
            if 'chat.whatsapp.com' in txt or re.match(r'^(Click Here|Join|Join Group|Join Now)$',txt.strip(),re.I): continue
            if txt and len(txt)>2: name=txt; break
        if name: items.append((name, a.group(1)))
    return items
def code_of(url):
    m=re.search(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})$', url)
    return m.group(1) if m else None
