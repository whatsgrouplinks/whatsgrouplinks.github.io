import subprocess, time, re, json
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
def fetch(url, timeout=30, tries=3):
    for i in range(tries):
        try:
            p=subprocess.run(['curl','-s','--max-time',str(timeout),'-A',UA,url],
                capture_output=True,text=True,timeout=timeout+10)
            if p.returncode==0 and p.stdout:
                return p.stdout
        except Exception:
            pass
        time.sleep(2)
    return None
def fetch_headers(url, timeout=20, tries=3):
    """returns (status, location) without following redirects"""
    for i in range(tries):
        try:
            p=subprocess.run(['curl','-s','--max-time',str(timeout),'-A',UA,'-D','-','-o','/dev/null',url],
                capture_output=True,text=True,timeout=timeout+10)
            m=re.search(r'HTTP/\S+ (\d+)',p.stdout)
            loc=re.search(r'^[Ll]ocation: (.+?)\s*$',p.stdout,re.M)
            if m: return int(m.group(1)), (loc.group(1).strip() if loc else '')
        except Exception:
            pass
        time.sleep(2)
    return 0,''
def verify(code, tries=2):
    """returns (status, ogtitle) status in live/dead/transport"""
    for attempt in range(tries):
        html=fetch(f'https://chat.whatsapp.com/{code}',timeout=25,tries=2)
        if html is None:
            if attempt==0: time.sleep(3); continue
            return 'transport',''
        m=re.search(r'<meta property="og:title" content="([^"]*)"',html)
        title=(m.group(1).strip() if m else '')
        if title and title not in ('WhatsApp Group','Join this group on WhatsApp'):
            return 'live',title
        if not title and attempt==0:
            time.sleep(3); continue
        return 'dead',title
    return 'dead',''
