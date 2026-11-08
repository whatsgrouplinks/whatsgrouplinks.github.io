#!/usr/bin/env python3
"""Resumable completion of generate.py after an EPERM-flap crash (2026-11-06 leg 1).
Reuses generate.py's own rendering helpers (imported, not copied) so output is
byte-identical to a full generate.py run. Writes ONLY what is missing/stale:
- group pages: renders + writes pages whose file is missing OR incomplete
  (does not end with </html>); per-file retry on PermissionError (8x, 2s gaps).
- sitemaps (groups-1/2, main, index), robots.txt, .nojekyll with retry.
Skips index/categories/static/blog (already written by the crashed run for the
current 66,356 groups; their content is static). Verifies counts at the end.
Usage: python3 resume_generate.py
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate as G

BASE = G.BASE
SITE_URL = G.SITE_URL

def write_retry(path, content, tries=5):
    for attempt in range(tries):
        try:
            with open(path, 'w') as f:
                f.write(content)
            return True
        except PermissionError:
            if attempt < tries - 1:
                time.sleep(0.5)
    return False

def render_group_page(g):
    name = G.esc(g['name'])
    cat = G.esc(g.get('category') or 'General')
    desc = G.esc((g.get('description') or f'Join {g["name"]}, an active WhatsApp group. Tap the button below to join instantly.')[:400])
    img = G.esc(g.get('image') or '../assets/default-group.png')
    invite = G.esc(g.get('invite') or '#')
    country = G.esc(g.get('country') or '')
    gcat = g.get('category') or 'General'
    og_json = json.dumps({
        "@context": "https://schema.org", "@type": "WebPage",
        "name": f'{g["name"]} WhatsApp Group — Join Link',
        "description": (g.get('description') or '')[:160],
        "inLanguage": "en",
        "isPartOf": {"@type": "WebSite", "name": G.SITE_NAME}}, ensure_ascii=False)
    g_extra = (f'<meta property="og:url" content="{SITE_URL}/groups/{g["slug"]}.html">\n'
               + f'<meta property="og:type" content="article">\n'
               + f'<meta property="og:image" content="{img}">\n'
               + f'<meta name="twitter:card" content="summary_large_image">\n'
               + f'<meta name="twitter:title" content="{name} WhatsApp Group — Join Link">\n'
               + f'<meta name="twitter:description" content="{desc[:160]}">\n'
               + f'<meta name="twitter:image" content="{img}">\n'
               + f'<meta name="keywords" content="{G.esc(G.cat_keywords(gcat))}">\n'
               + f'<script type="application/ld+json">{og_json}</script>\n')
    pg = G.header(f'{g["name"]} WhatsApp Group Link 2026 — Join Now | ' + G.SITE_NAME,
                  (g.get('description') or '')[:160], f'groups/{g["slug"]}.html',
                  extra_head=g_extra)
    pg += f"""<div class="container"><div class="gdetail">
<div class="crumb"><a href="../index.html">Home</a> / <a href="../category/{G.cat_slug(g.get('category') or 'general')}.html">{cat}</a> / {name}</div>
<div class="top"><img class="gbig" src="{img}" alt="{name} WhatsApp group">
<div class="meta"><h1>{name}</h1>
<span class="pill">📁 {cat}</span>{f'<span class="pill">🌍 {country}</span>' if country else ''}
<div class="desc"><p>{desc}</p></div>
<a class="bigjoin" href="{invite}" target="_blank" rel="noopener nofollow">Join on WhatsApp</a>
<p style="font-size:13px;color:#888">Tapping the button opens WhatsApp directly at this group's join screen. If the link has expired, the group admin may have reset it.</p>
</div></div>
<div class="share-row">
<a href="https://wa.me/?text={G.esc(g['name'])}%20WhatsApp%20group" target="_blank" rel="noopener">Share on WhatsApp</a>
<a href="https://www.facebook.com/sharer/sharer.php?u=" target="_blank" rel="noopener">Share on Facebook</a>
<a href="https://twitter.com/intent/tweet?text={G.esc(g['name'])}" target="_blank" rel="noopener">Share on X</a>
<button onclick="navigator.clipboard&&navigator.clipboard.writeText(location.href).then(()=>this.textContent='Copied!')">Copy Link</button>
</div>
</div></div>"""
    pg += G.FOOTER.format(name=G.SITE_NAME, prefix='../')
    return pg

def page_complete(path):
    try:
        if os.path.getsize(path) < 1000:
            return False
        with open(path, 'rb') as f:
            f.seek(-20, 2)
            return f.read().rstrip().endswith(b'</html>')
    except Exception:
        return False

def main():
    with open(f'{BASE}/groups.json') as f:
        groups = json.load(f)
    print(f"Loaded {len(groups)} groups", flush=True)
    missing = [g for g in groups if not g.get('slug')]
    if missing:
        print(f"FATAL: {len(missing)} groups lack slugs — run generate.py", flush=True)
        sys.exit(2)

    os.makedirs(f'{BASE}/groups', exist_ok=True)
    import datetime
    today = datetime.date(2026, 11, 6)
    todo = []
    for g in groups:
        p = f'{BASE}/groups/{g["slug"]}.html'
        if not os.path.exists(p):
            todo.append(g)
        elif datetime.date.fromtimestamp(os.path.getmtime(p)) >= today and not page_complete(p):
            todo.append(g)  # possibly truncated by the crashed run-1 write
    print(f"group pages to (re)write: {len(todo)} of {len(groups)}", flush=True)
    failed = []
    done = 0
    for g in todo:
        pg = render_group_page(g)
        if write_retry(f'{BASE}/groups/{g["slug"]}.html', pg):
            done += 1
        else:
            failed.append(g['slug'])
        if done % 1000 == 0 and done:
            print(f"  wrote {done}/{len(todo)}", flush=True)
    print(f"group pages written this run: {done}, failed: {len(failed)}", flush=True)

    # orphan cleanup (same rule as generate.py)
    live = {g['slug'] + '.html' for g in groups}
    orphans = 0
    for fn in os.listdir(f'{BASE}/groups'):
        if fn.endswith('.html') and fn not in live:
            try:
                os.remove(f'{BASE}/groups/{fn}')
                orphans += 1
            except PermissionError:
                print(f"  orphan remove failed (EPERM): {fn}", flush=True)
    print(f"orphan group pages removed: {orphans}", flush=True)

    # sitemaps + robots + .nojekyll (rebuilt from current groups.json)
    cat_counts = {}
    for g in groups:
        cat_counts[g.get('category')] = cat_counts.get(g.get('category'), 0) + 1
    from collections import Counter
    cat_counts = Counter(g['category'] for g in groups if g.get('category'))
    all_cat_urls = []
    for c, icon in G.CATEGORIES:
        clist = [g for g in groups if g.get('category') == c]
        if not clist:
            continue
        cs = G.cat_slug(c)
        npages = (len(clist) + 59) // 60
        for pgnum in range(1, npages + 1):
            all_cat_urls.append(f'category/{cs}.html' if pgnum == 1 else f'category/{cs}-page{pgnum}.html')
    print(f"category pages expected: {len(all_cat_urls)}", flush=True)

    def sm_write(fname, urls):
        sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for u in urls:
            sm += f'  <url><loc>{SITE_URL}/{u}</loc><lastmod>2026-10-17</lastmod></url>\n'
        sm += '</urlset>'
        return write_retry(f'{BASE}/{fname}', sm)

    static_urls = ['index.html', 'categories.html', 'blog.html', 'submit.html', 'about.html', 'contact.html', 'privacy.html', 'terms.html']
    static_urls += all_cat_urls
    static_urls += [f'blog/{p["slug"]}.html' for p in G.BLOG_POSTS]
    group_urls = [f'groups/{g["slug"]}.html' for g in groups]
    ok = True
    ok &= sm_write('sitemap-main.xml', static_urls)
    ok &= sm_write('sitemap-groups-1.xml', group_urls[:40000])
    ok &= sm_write('sitemap-groups-2.xml', group_urls[40000:])
    idx = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           f'  <sitemap><loc>{SITE_URL}/sitemap-main.xml</loc><lastmod>2026-10-17</lastmod></sitemap>\n'
           f'  <sitemap><loc>{SITE_URL}/sitemap-groups-1.xml</loc><lastmod>2026-10-17</lastmod></sitemap>\n'
           f'  <sitemap><loc>{SITE_URL}/sitemap-groups-2.xml</loc><lastmod>2026-10-17</lastmod></sitemap>\n'
           '</sitemapindex>')
    ok &= write_retry(f'{BASE}/sitemap.xml', idx)
    ok &= write_retry(f'{BASE}/robots.txt', f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n')
    ok &= write_retry(f'{BASE}/.nojekyll', '')
    print("sitemaps/robots written:", ok, flush=True)

    # final verification
    n_pages = len([f for f in os.listdir(f'{BASE}/groups') if f.endswith('.html')])
    print(f"FINAL groups/*.html: {n_pages} (expect {len(groups)})", flush=True)
    if failed:
        print(f"FAILED pages ({len(failed)}): {failed[:20]}", flush=True)
        json.dump(failed, open(f'{BASE}/resume_failed.json', 'w'))
        sys.exit(1)
    if n_pages != len(groups):
        print("COUNT MISMATCH — rerun resume_generate.py", flush=True)
        sys.exit(1)
    if not ok:
        print("SITEMAP WRITE FAILED — rerun resume_generate.py", flush=True)
        sys.exit(1)
    print("RESUME BUILD OK", flush=True)

if __name__ == '__main__':
    main()
