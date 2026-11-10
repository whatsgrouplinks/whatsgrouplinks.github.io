import json, subprocess, re, time
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
cands = json.load(open("team24_fresh_candidates.json"))
resolved = json.load(open("team24_resolved38.json"))
# NOTE: og_titles above were transcribed from printed output with entities decoded for readability;
# ERBl title was stylised unicode - directory name used instead. FyLY/GGEh/HuUR/Lo6e/BzCO/Lqp5/IUIw likewise
# normalised to plain text; the live verdict (200 + non-empty og:title) is what matters.
todo = [c for c in cands if c["code"] not in resolved or resolved[c["code"]]["status"]=="transport"]
print("todo:", len(todo), [c["code"] for c in todo], flush=True)

def check(code):
    url = f"https://chat.whatsapp.com/{code}"
    last_http = "000"
    for attempt in range(3):
        try:
            r = subprocess.run(["curl","-s","-A",UA,"--max-time","12","-w","\n%{http_code}",url],
                               capture_output=True, text=True, timeout=18)
            body = r.stdout
            m = re.search(r'\n(\d{3})\s*$', body)
            http = m.group(1) if m else "000"
            last_http = http
            html = body[:m.start()] if m else body
            t = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html)
            if not t:
                t = re.search(r"<meta\s+content=\"([^\"]*)\"\s+property=\"og:title\"", html)
            title = t.group(1).strip() if t else ""
            if http == "200" and title:
                return ("live", title, http, "")
            if http == "200" and not title:
                time.sleep(3)
                continue
            if http == "000":
                time.sleep(3)
                continue
            return ("dead", title, http, f"http {http}")
        except subprocess.TimeoutExpired:
            time.sleep(3)
            continue
        except Exception as e:
            return ("transport", "", "000", str(e)[:80])
    # after 3 attempts: 200-empty every time = dead; never got http = transport
    if last_http == "200":
        return ("dead", "", "200", "empty og:title after retries")
    return ("transport", "", "000", "no http status after 3 attempts")

for c in todo:
    st, title, http, err = check(c["code"])
    # if we exhausted attempts with 200-empty every time, check() above returns transport; fix:
    # re-run logic: if last attempt was 200-empty we can't know here; keep transport only when no http seen.
    resolved[c["code"]] = {"status": st, "og_title": title, "http": http, "error": err}
    json.dump(resolved, open("team24_verify_raw.json","w"), indent=1, ensure_ascii=False)
    print(c["code"], st, repr(title), http, err, flush=True)
    time.sleep(3)
live = sum(1 for v in resolved.values() if v["status"]=="live")
dead = sum(1 for v in resolved.values() if v["status"]=="dead")
pend = sum(1 for v in resolved.values() if v["status"]=="transport")
print(f"VERIFY2 DONE total={len(resolved)} LIVE={live} DEAD={dead} PENDING={pend}")
