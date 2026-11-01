import subprocess, time, re, sys

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

def check(code):
    url = "https://chat.whatsapp.com/" + code
    try:
        r = subprocess.run(
            ["curl","-sL","-A",UA,"-o","/tmp/_t16.html","-w","%{http_code}",
             "--max-time","25",url],
            capture_output=True, text=True, timeout=30)
        http = r.stdout.strip()
        html = open("/tmp/_t16.html", encoding="utf-8", errors="replace").read()
        m = re.search(r'<meta[^>]+property="og:title"[^>]+content="([^"]+)"', html) or \
            re.search(r'<meta[^>]+content="([^"]+)"[^>]+property="og:title"', html)
        title = m.group(1).strip() if m else ""
        dead = ("Couldn't look up link" in html) or ("Couldn't look up" in html) or ("404" in html and not title)
        alive = (http == "200" and title and not dead)
        return http, title, alive
    except Exception as e:
        return "ERR", str(e), False

if __name__ == "__main__":
    for code in sys.argv[1:]:
        http, title, alive = check(code)
        print(f"{code}\thttp={http}\talive={alive}\ttitle={title[:80]}")
        time.sleep(0.5)
