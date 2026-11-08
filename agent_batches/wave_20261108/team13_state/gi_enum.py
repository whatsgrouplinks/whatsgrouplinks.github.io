"""Team 13: enumerate groupsinvite.link via its own AJAX endpoint
GET /wp-admin/admin-ajax.php?action=gi_fetch_groups&scope=all&after_id=<cursor>&limit=N
Returns JSON {success, data:{html, has_more, next_cursor/last_id...}} — parse items from HTML.
Saves team13_state/gi_enum.json : {slug: {name, category, country, language, link_slug, tags}}
"""
import requests, re, time, json, os, html as ihtml

WORK = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
OUT = os.path.join(WORK, "gi_enum.json")
AJAX = "https://groupsinvite.link/wp-admin/admin-ajax.php"

def parse_items(html):
    items = {}
    # split on group-item blocks
    blocks = re.split(r'<div class="group-item"', html)
    for b in blocks[1:]:
        lm = re.search(r'/group/link/([A-Za-z0-9]+)/', b)
        if not lm:
            continue
        slug = lm.group(1)
        nm = re.search(r'class="group-name"[^>]*>(.*?)</', b, re.S)
        name = re.sub(r'<[^>]+>', '', nm.group(1)).strip() if nm else ""
        name = ihtml.unescape(name)
        cm = re.search(r'group/category/([^/"]+)/', b)
        cat = cm.group(1) if cm else ""
        coun = re.search(r'/group/country/([^/"]+)/', b)
        country = coun.group(1) if coun else ""
        desc = re.search(r'data-full-description="([^"]*)"', b)
        full = ihtml.unescape(desc.group(1)).strip() if desc else ""
        pv = re.search(r'class="group-preview"[^>]*>(.*?)</div>', b, re.S)
        preview = re.sub(r'<[^>]+>', '', pv.group(1)).strip() if pv else ""
        preview = ihtml.unescape(preview)
        items[slug] = {
            "name": name,
            "category_slug": cat,
            "country_slug": country,
            "description": full or preview,
            "link_slug": slug,
        }
    return items

def main():
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9",
                      "X-Requested-With": "XMLHttpRequest",
                      "Referer": "https://groupsinvite.link/"})
    # seed from homepage already fetched: parse it too
    state = {}
    if os.path.exists(OUT):
        state = json.load(open(OUT))
    home = open('/tmp/gi_home.html').read()
    state.update(parse_items(home))
    print("seeded from homepage:", len(state), flush=True)

    cursor = "0029VbDKsIw8vd1PwJt7ib1S"  # initialCursor from homepage config
    seen_cursors = set()
    rounds = 0
    while cursor and cursor not in seen_cursors and rounds < 200:
        seen_cursors.add(cursor)
        params = {"action": "gi_fetch_groups", "scope": "all", "scope_value": "",
                  "shuffle_seed": "", "after_id": cursor, "limit": "35"}
        try:
            r = s.get(AJAX, params=params, timeout=60)
        except Exception as e:
            print("AJAX ERR", e, flush=True)
            time.sleep(5)
            continue
        if r.status_code != 200:
            print("AJAX HTTP", r.status_code, flush=True)
            time.sleep(5)
            continue
        try:
            j = r.json()
        except Exception:
            print("AJAX non-JSON len", len(r.text), r.text[:200], flush=True)
            break
        data = j.get("data", {}) if isinstance(j, dict) else {}
        htmlfrag = data.get("html", "") if isinstance(data, dict) else ""
        new_items = parse_items(htmlfrag)
        before = len(state)
        state.update(new_items)
        nxt = None
        for k in ("lastId", "next_cursor", "cursor", "nextCursor", "after_id"):
            if data.get(k):
                nxt = data[k]
                break
        # fallback: last link slug in this batch
        if not nxt and new_items:
            nxt = list(new_items.keys())[-1]
        has_more = data.get("has_more", True)
        rounds += 1
        print("round %d: +%d items (total %d) has_more=%s next=%s keys=%s" % (
            rounds, len(state) - before, len(state), has_more, str(nxt)[:30],
            list(data.keys()) if isinstance(data, dict) else "?"), flush=True)
        json.dump(state, open(OUT, "w"))
        if not has_more or not new_items:
            break
        cursor = nxt
        time.sleep(0.6)
    print("DONE total enumerated:", len(state), flush=True)

if __name__ == "__main__":
    main()
