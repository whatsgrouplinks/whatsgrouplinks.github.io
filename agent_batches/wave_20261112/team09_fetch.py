#!/usr/bin/env python3
"""TEAM 09 wave 20261112 slice 3 resume: re-fetch the 558 JS-gated linkado.app
listing URLs from team03 (wave_20261111). Extract the "Entrar no Grupo" button
href (present in static HTML / RSC payload — team03 only regexed chat.whatsapp.com)
plus any chat.whatsapp.com codes anywhere in the page.
Checkpoints every 50 pages. Resume-safe.
"""
import json, re, time, threading
from concurrent.futures import ThreadPoolExecutor
import requests

W11 = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
W12 = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
LEADS = f"{W11}/team03-leads-slice3-leads.json"
RAW = f"{W12}/team09-raw-extract.json"
PROG = f"{W12}/team09-fetch-progress.json"
FAILED = f"{W12}/team09-fetch-failed.json"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
      "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"}

CODE_RE = re.compile(r"chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})")
TITLE_RE = re.compile(r'og:title"\s+content="([^"]+)"')
DESC_RE = re.compile(r'og:description"\s+content="([^"]+)"')
# static HTML anchor: <a href="URL" ...>...Entrar no Grupo</a>
BTN_RE = re.compile(r'<a\s+href="([^"]+)"[^>]*>(?:(?!</a>).){0,1200}?Entrar no Grupo</a>', re.S)
# RSC escaped anchor: {\"href\":\"URL\",...\"Entrar no Grupo\"}
BTN_RSC_RE = re.compile(r'\\"href\\":\\"([^\\"]+)\\".{0,1500}?Entrar no Grupo', re.S)
HREF_RE = re.compile(r'href="([^"]+)"')

TLS = threading.local()

def session():
    s = getattr(TLS, "s", None)
    if s is None:
        s = requests.Session()
        s.headers.update(UA)
        TLS.s = s
    return s

def parse(html):
    codes = list(dict.fromkeys(CODE_RE.findall(html)))
    m = TITLE_RE.search(html)
    title = m.group(1) if m else ""
    m2 = DESC_RE.search(html)
    desc = m2.group(1) if m2 else ""
    name, cat = "", ""
    if title.startswith("Grupo de WhatsApp "):
        rest = title[len("Grupo de WhatsApp "):]
        if " - " in rest:
            name, cat = rest.rsplit(" - ", 1)
        else:
            name = rest
    btn = BTN_RE.findall(html)
    if not btn:
        btn = BTN_RSC_RE.findall(html)
    # all invite-like hrefs anywhere in page
    hrefs = HREF_RE.findall(html)
    invite_hrefs = [h for h in dict.fromkeys(hrefs)
                    if any(k in h for k in ("chat.whatsapp.com", "wa.me", "t.me",
                                            "api.whatsapp.com", "bit.ly", "tinyurl",
                                            "linktr.ee", "cutt.ly", "abre.ai"))]
    return codes, name.strip(), cat.strip(), desc.strip(), btn, invite_hrefs

def main():
    urls = json.load(open(LEADS))
    done = {}
    try:
        done = {r["url"]: r for r in json.load(open(RAW))}
    except Exception:
        pass
    todo = [u for u in urls if u not in done]
    print(f"total={len(urls)} done={len(done)} todo={len(todo)}", flush=True)
    lock = threading.Lock()
    results = list(done.values())
    failed = []
    counter = {"n": 0}

    def work(url):
        last = ""
        for attempt in range(3):
            try:
                r = session().get(url, timeout=90)
                time.sleep(0.5)
                if r.status_code != 200:
                    raise RuntimeError(f"HTTP {r.status_code}")
                codes, name, cat, desc, btn, ih = parse(r.text)
                rec = {"url": url, "codes": codes, "name": name, "category_pt": cat,
                       "desc_pt": desc, "btn_hrefs": btn, "invite_hrefs": ih}
                with lock:
                    results.append(rec)
                    counter["n"] += 1
                    if counter["n"] % 50 == 0:
                        json.dump(results, open(RAW, "w"), ensure_ascii=False)
                        json.dump({"fetched": len(results), "todo_left": len(todo) - counter["n"]},
                                  open(PROG, "w"))
                        print(f"fetched {len(results)}/{len(urls)}", flush=True)
                return
            except Exception as e:
                last = str(e)
                try:
                    TLS.s = None
                except Exception:
                    pass
                time.sleep(3)
        with lock:
            failed.append({"url": url, "reason": f"fetch failed: {last}"})
            counter["n"] += 1

    with ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(work, todo))
    json.dump(results, open(RAW, "w"), ensure_ascii=False)
    json.dump(failed, open(FAILED, "w"), ensure_ascii=False)
    json.dump({"fetched": len(results), "failed": len(failed), "todo_left": 0}, open(PROG, "w"))
    print(f"DONE fetched={len(results)} failed={len(failed)}", flush=True)

if __name__ == "__main__":
    main()
