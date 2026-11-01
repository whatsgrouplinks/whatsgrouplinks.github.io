#!/usr/bin/env python3
"""Generate the WhatsApp Groups Directory static site from groups.json."""
import json, re, os, html
from collections import Counter

BASE = '/home/hatch/workspace/whatsapp-groups-site'
SITE_NAME = 'WhatsGroupLinks'
TAGLINE = 'Find & Join WhatsApp Groups'
SITE_URL = 'https://whatsgrouplinks.github.io'

CATEGORIES = [
    ('Gaming', '🎮'), ('Education', '📚'), ('Online Earning', '💰'),
    ('Community & Social', '👥'), ('Business', '💼'), ('Friendship', '🤝'),
    ('Finance', '📈'), ('Buy Sell', '🛒'), ('Islamic', '☪️'),
    ('Entertainment', '🎬'), ('Jobs', '💻'), ('Technology', '⚙️'),
    ('Funny', '😂'), ('Sports', '⚽'), ('Health', '🏥'), ('News', '📰'),
]

def slugify(name, gid):
    s = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')[:50]
    return f"{s}-{gid}" if s else f"group-{gid}"

def esc(s):
    return html.escape(str(s or ''))

def header(title, desc, path='', extra_head=''):
    depth = path.count('/')
    prefix = '../' * depth
    absurl = SITE_URL + '/' + path if path else SITE_URL + '/'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc[:160])}">
<link rel="canonical" href="{esc(absurl)}">
<link rel="alternate" hreflang="en" href="{esc(absurl)}">
<link rel="alternate" hreflang="x-default" href="{esc(absurl)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc[:160])}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE_NAME}">
{extra_head}<link rel="stylesheet" href="{prefix}assets/style.css">
<link rel="icon" href="{prefix}assets/favicon.svg">
</head>
<body>
<header><div class="hwrap">
<a class="logo" href="{prefix}index.html"><span class="dot">💬</span> {SITE_NAME}</a>
<div class="live-clock" id="live-clock" title="Your local date & time">--</div>
<nav class="mainnav">
<a href="{prefix}index.html">Home</a>
<a href="{prefix}categories.html">Categories</a>
<a href="{prefix}blog.html">Guides</a>
<a href="{prefix}submit.html">Submit Group</a>
<a href="{prefix}about.html">About</a>
<a href="{prefix}contact.html">Contact</a>
</nav>
<a class="add-group-btn" href="{prefix}submit.html">➕ Add Your Group</a>
</div></header>
<script>(function(){{function tick(){{try{{var now=new Date();var tz="";try{{tz=Intl.DateTimeFormat().resolvedOptions().timeZone||"";}}catch(e){{}}var d=now.toLocaleDateString("en-US",{{weekday:"long",year:"numeric",month:"long",day:"numeric"}});var t=now.toLocaleTimeString("en-US",{{hour:"numeric",minute:"2-digit",second:"2-digit",hour12:true}});var el=document.getElementById("live-clock");if(el)el.textContent=d+" | "+t+(tz?" ("+tz+")":"");}}catch(e){{}}}}tick();setInterval(tick,1000);}})();</script>
"""

BASE_KEYWORDS = "whatsapp group links, whatsapp groups, join whatsapp group, whatsapp group invite link, whatsapp group link 2026, active whatsapp groups, #whatsappgroups, #whatsappgrouplink, #joingroups"

CAT_KEYWORDS = {
    'Gaming': 'gaming whatsapp groups, free fire whatsapp group link, pubg whatsapp group, bgmi whatsapp group, gaming community whatsapp, #gaminggroups, #freefiregroup',
    'Education': 'study whatsapp groups, education whatsapp group link, css whatsapp group, mdcat whatsapp group, upsc whatsapp group, exam preparation whatsapp, #studygroups, #educationgroup',
    'Online Earning': 'online earning whatsapp groups, freelancing whatsapp group, earn money whatsapp group, trading whatsapp group, #onlineearning, #earnmoneyonline',
    'Community & Social': 'community whatsapp groups, social whatsapp groups, city whatsapp groups, local community whatsapp, #communitygroups',
    'Business': 'business whatsapp groups, startup whatsapp group, entrepreneur whatsapp group, #businessgroups',
    'Friendship': 'friendship whatsapp groups, girls whatsapp groups, dosti whatsapp group, shayari whatsapp group, #friendshipgroup',
    'Finance': 'finance whatsapp groups, investment whatsapp group, crypto whatsapp group, stock market whatsapp group, #financegroup',
    'Buy Sell': 'buy sell whatsapp groups, shopping whatsapp groups, online shopping whatsapp, wholesale whatsapp group, #buysell',
    'Islamic': 'islamic whatsapp groups, quran whatsapp group, naat whatsapp group, islamic bayan whatsapp, ramadan whatsapp group, #islamicgroup',
    'Entertainment': 'entertainment whatsapp groups, movies whatsapp group, drama whatsapp group, memes whatsapp group, #entertainmentgroup',
    'Jobs': 'jobs whatsapp groups, government jobs whatsapp group, private jobs whatsapp, job alerts whatsapp, #jobsgroup, #governmentjobs',
    'Technology': 'technology whatsapp groups, tech whatsapp group, ai whatsapp group, coding whatsapp group, #techgroup',
    'Funny': 'funny whatsapp groups, comedy whatsapp group, jokes whatsapp group, #funnygroups',
    'Sports': 'sports whatsapp groups, cricket whatsapp group, football whatsapp group, psl whatsapp group, #cricketgroup, #sportsgroups',
    'Health': 'health whatsapp groups, fitness whatsapp group, health tips whatsapp, #healthgroup',
    'News': 'news whatsapp groups, breaking news whatsapp group, pakistan news whatsapp, geo news whatsapp group, ary news whatsapp, #newsgroup, #breakingnews',
}

def cat_keywords(c):
    return BASE_KEYWORDS + ', ' + CAT_KEYWORDS.get(c, c.lower() + ' whatsapp groups')

FOOTER = """<footer><div class="fgrid">
<div><h4>{name}</h4><p style="font-size:14px;color:#aaa">The fastest way to discover and join active WhatsApp groups across every topic and country. Every listing is reviewed before publishing.</p></div>
<div><h4>Explore</h4><a href="index.html">Home</a><a href="categories.html">All Categories</a><a href="blog.html">Guides & Tips</a><a href="submit.html">Submit a Group</a></div>
<div><h4>Company</h4><a href="about.html">About Us</a><a href="contact.html">Contact</a><a href="privacy.html">Privacy Policy</a><a href="terms.html">Terms of Service</a></div>
<div><h4>Popular</h4><a href="category/education.html">Education Groups</a><a href="category/jobs.html">Jobs Groups</a><a href="category/entertainment.html">Entertainment Groups</a><a href="category/islamic.html">Islamic Groups</a></div>
</div><div class="fbottom">© 2026 {name}. All rights reserved. WhatsApp is a trademark of WhatsApp LLC. This is an independent directory and is not affiliated with WhatsApp LLC.</div></footer>
<script src="{prefix}assets/app.js"></script>
</body></html>"""

def cat_slug(c):
    return re.sub(r'[^a-z0-9]+', '-', c.lower()).strip('-')

def pagination_html(cs, pgnum, npages):
    """Pagination nav for category pages. Page 1 = {cs}.html, rest = {cs}-page{N}.html."""
    def purl(n):
        return f'{cs}.html' if n == 1 else f'{cs}-page{n}.html'
    nums = {1, npages, pgnum}
    for i in range(pgnum - 2, pgnum + 3):
        if 1 <= i <= npages:
            nums.add(i)
    nums = sorted(nums)
    parts = []
    last = 0
    for n in nums:
        if n - last > 1:
            parts.append('<span class="pg-ellipsis">…</span>')
        cls = 'pg-num current' if n == pgnum else 'pg-num'
        parts.append(f'<a class="{cls}" href="{purl(n)}">{n}</a>')
        last = n
    prev = f'<a class="pg-prev" href="{purl(pgnum - 1)}">« Prev</a>' if pgnum > 1 else '<span class="pg-prev disabled">« Prev</span>'
    nxt = f'<a class="pg-next" href="{purl(pgnum + 1)}">Next »</a>' if pgnum < npages else '<span class="pg-next disabled">Next »</span>'
    return f'<nav class="pagination" aria-label="Category pages">{prev}{"".join(parts)}{nxt}<span class="pg-info">Page {pgnum} of {npages}</span></nav>'

BLOG_POSTS = [
    {
        'slug': 'how-to-join-whatsapp-groups',
        'title': 'How to Join WhatsApp Groups in 2026: Step-by-Step Guide',
        'desc': 'Learn how to join any WhatsApp group in 2026 — via invite link, QR code, or admin approval. Full step-by-step guide for Android, iPhone, and WhatsApp Web.',
        'keywords': 'how to join whatsapp group, join whatsapp group link, whatsapp group join 2026, whatsapp invite link, #whatsappgroups, #joingroups, #whatsappgrouplink',
        'hashtags': '#whatsappgroups #joingroups #whatsappgrouplink #whatsapptips #howtojoin',
        'paras': [
            'Joining a WhatsApp group in 2026 takes less than a minute — if you know where to tap. Most groups are joined through an <strong>invite link</strong> that looks like <em>chat.whatsapp.com/XXXX</em>. When you tap it, WhatsApp opens directly on the group\u2019s preview screen with the group name, photo, and member count, plus a green <strong>Join Group</strong> button.',
            'On <strong>Android</strong>: tap the invite link, review the group preview, then tap <em>Join Group</em>. You are in instantly — no approval needed for public invite links. On <strong>iPhone</strong>: the flow is identical — tap the link, tap <em>Join Group</em> in the preview. On <strong>WhatsApp Web</strong>: click the link in your browser, scan the QR if asked, then click <em>Join Group</em> in the web preview.',
            'Some groups require <strong>admin approval</strong>. In that case you will see a <em>Request to Join</em> button instead. Your request sits in a queue until an admin approves it — this can take minutes or days depending on the group.',
            'Before joining, always check three things: the <strong>group name and photo</strong> (does it match what you expected?), the <strong>member count</strong> (groups cap at 1,024 members — a full group will reject you), and the <strong>description</strong> (legitimate groups explain their purpose and rules).',
            'If a link says <strong>\u201cexpired\u201d or \u201crevoked\u201d</strong>, the admin reset the invite link. Old links die the moment a new one is generated. Your only fix is to get the fresh link from the admin or from an updated directory listing.',
            'Safety matters. Never share <strong>passwords, bank details, or one-time codes</strong> in any group — admins will never ask for them. Be cautious of groups promising free money or prizes; those are classic scam setups.',
            'Looking for groups to join? Browse our <a href="../category/education.html">Education</a>, <a href="../category/jobs.html">Jobs</a>, <a href="../category/entertainment.html">Entertainment</a>, and <a href="../category/islamic.html">Islamic</a> collections — every listing is reviewed and every link is checked.',
        ],
    },
    {
        'slug': 'best-study-whatsapp-groups-2026',
        'title': 'Best Study WhatsApp Groups 2026: CSS, MDCAT, UPSC, IELTS & More',
        'desc': 'Find the best study WhatsApp groups for 2026 — CSS, MDCAT, UPSC, IELTS, board exams and more. Free notes, past papers, and daily quizzes shared by toppers.',
        'keywords': 'study whatsapp groups, css whatsapp group, mdcat whatsapp group, upsc whatsapp group, ielts whatsapp group, exam preparation whatsapp, #studygroups, #csspreparation, #mdcat2026',
        'hashtags': '#studygroups #csspreparation #mdcat2026 #upsc #ielts #exampreparation #whatsappgroups',
        'paras': [
            'Study WhatsApp groups are the quiet backbone of exam preparation across Pakistan and India in 2026. Aspirants share <strong>PDF notes, past papers, solved MCQs, and daily quizzes</strong> — often within minutes of them being released.',
            '<strong>CSS & PMS groups</strong> focus on current affairs, essay outlines, and past-paper discussions. The best ones run <strong>daily current-affairs quizzes</strong> and weekly essay topics with peer review.',
            '<strong>MDCAT & ECAT groups</strong> are goldmines for <strong>chapter-wise MCQs, NUMS past papers, and video lecture links</strong>. Many are run by recent toppers who post their own handwritten notes for free.',
            '<strong>UPSC & SSC groups</strong> share NCERT summaries, The Hindu editorials, and monthly current-affairs compilations. Look for groups that pin a <strong>syllabus tracker</strong> so you always know what is covered.',
            '<strong>IELTS & English-learning groups</strong> run daily <strong>speaking practice, writing task corrections, and vocabulary drops</strong>. The most active ones pair members as speaking partners.',
            'How to pick a good study group: check that <strong>admins post regularly</strong>, that <strong>files are organized by topic</strong>, and that spam is deleted quickly. Leave groups that are 90% forwards and 10% study.',
            'Start with our <a href="../category/education.html">Education WhatsApp Groups</a> collection — hundreds of active study groups, every link verified.',
        ],
    },
    {
        'slug': 'whatsapp-group-rules-admins',
        'title': 'WhatsApp Group Rules: 15 Rules Every Admin Should Set in 2026',
        'desc': 'The 15 essential WhatsApp group rules every admin should set in 2026 — stop spam, forwards, and fights. Copy-paste ready rules in English.',
        'keywords': 'whatsapp group rules, group rules for whatsapp, admin rules whatsapp, whatsapp group description rules, #whatsappgroups, #groupadmin',
        'hashtags': '#whatsappgroups #groupadmin #whatsapprules #communitymanagement',
        'paras': [
            'A WhatsApp group without rules becomes a spam dump within a week. Admins who set <strong>clear rules on day one</strong> keep their groups useful for years. Here are the 15 rules that actually work.',
            '<strong>1. Stay on topic.</strong> Every message should relate to the group\u2019s purpose. Off-topic chatter goes to personal chat. <strong>2. No forwards without source.</strong> Unverified forwards — especially \u201cbreaking news\u201d — get deleted. <strong>3. No spam or ads.</strong> Promotions only with admin permission, in a dedicated promo thread.',
            '<strong>4. Respect everyone.</strong> No abuse, hate speech, or personal attacks — instant removal. <strong>5. No adult or illegal content.</strong> Zero tolerance, instant ban and report. <strong>6. Limit messages during quiet hours</strong> (e.g., 11 PM – 7 AM) so members can mute less and engage more.',
            '<strong>7. Use threads for long discussions.</strong> One topic, one thread — keeps the main chat readable. <strong>8. No chain messages or \u201cforward to 10 groups\u201d posts.</strong> <strong>9. Introduce yourself</strong> when you join: name, city, purpose.',
            '<strong>10. Files over screenshots.</strong> Share PDFs and documents, not 40 blurry screenshots. <strong>11. No political or religious fights.</strong> Discuss respectfully or take it elsewhere. <strong>12. Admins\u2019 word is final</strong> on disputes.',
            '<strong>13. Report problems privately</strong> to an admin instead of arguing in the group. <strong>14. Do not add members without asking</strong> — let people join via the invite link themselves. <strong>15. Three strikes:</strong> warning, mute, removal.',
            'Pin these rules in the <strong>group description</strong> so every new member sees them before their first message. Groups with pinned rules have dramatically less drama.',
            'Running a group? <a href="../submit.html">List it in our directory</a> for free and grow your community faster.',
        ],
    },
    {
        'slug': 'online-earning-whatsapp-groups-guide',
        'title': 'Online Earning WhatsApp Groups: How to Find Legit Ones (2026)',
        'desc': 'Online earning WhatsApp groups can be goldmines or scams. Learn how to spot legit freelancing, trading, and reselling groups in 2026 — and the red flags to avoid.',
        'keywords': 'online earning whatsapp groups, freelancing whatsapp group, earn money whatsapp group, trading whatsapp group, reselling whatsapp group, #onlineearning, #freelancing, #earnmoneyonline',
        'hashtags': '#onlineearning #freelancing #earnmoneyonline #whatsappgroups #makemoneyonline',
        'paras': [
            'Thousands of people join <strong>online earning WhatsApp groups</strong> every day hoping for freelance gigs, trading signals, or reselling opportunities. Some groups genuinely deliver. Many are traps. Here is how to tell them apart.',
            '<strong>Legit earning groups share:</strong> real job postings with clear pay terms, portfolio reviews, skill tutorials, and member success stories with proof. Admins answer questions publicly instead of pushing you to DM.',
            '<strong>Red flags — leave immediately if you see these:</strong> anyone asking for an <strong>\u201cregistration fee\u201d or \u201cactivation charge\u201d</strong> before you can earn; promises of <strong>guaranteed daily profits</strong> from trading; \u201cdouble your money\u201d schemes; admins who only talk in DMs and delete questions.',
            'The safest earning paths discussed in good groups: <strong>freelancing</strong> (writing, design, video editing, SEO), <strong>reselling</strong> (buy wholesale, sell via WhatsApp catalogs), <strong>content creation</strong>, and <strong>skill-based services</strong>. Anything promising money for zero skill is almost certainly a scam.',
            '<strong>Protect yourself:</strong> never pay to join an earning group, never share bank or wallet credentials, and always insist on <strong>advance payment terms</strong> (50% upfront is the freelance standard) before starting client work.',
            'Start with vetted communities in our <a href="../category/online-earning.html">Online Earning</a> and <a href="../category/jobs.html">Jobs</a> collections — every listing reviewed, every link checked.',
        ],
    },
    {
        'slug': 'whatsapp-group-link-expired-fix',
        'title': 'WhatsApp Group Link Expired? Here\u2019s How to Fix It (2026)',
        'desc': 'WhatsApp group link expired or revoked? Learn why invite links stop working and 5 ways to get back into the group in 2026.',
        'keywords': 'whatsapp group link expired, whatsapp invite link revoked, whatsapp link not working, fix whatsapp group link, #whatsappgroups, #whatsapptips',
        'hashtags': '#whatsappgroups #whatsapptips #whatsappgrouplink #fixwhatsapp',
        'paras': [
            'You tap a WhatsApp invite link and see <strong>\u201cThis invite link is invalid\u201d or \u201cexpired.\u201d</strong> Frustrating — but it happens for specific reasons, and most of them have fixes.',
            '<strong>Why links die:</strong> (1) The admin hit <strong>\u201cReset link\u201d</strong> — old links stop working instantly. (2) The <strong>group was deleted</strong>. (3) The group hit <strong>1,024 members</strong> — WhatsApp\u2019s hard cap — and rejects everyone new. (4) You were <strong>removed and blocked</strong> from rejoining. (5) The link was simply typed wrong.',
            '<strong>Fix 1: Get the fresh link.</strong> Ask any current member or the admin for the new invite link. <strong>Fix 2: Check an updated directory</strong> — listings that re-verify links will have the current one.',
            '<strong>Fix 3: If the group is full</strong>, ask an admin to add you directly (admins can add beyond the link flow in some cases) or join a <strong>sister group</strong> — big communities often run Group 2, Group 3, and so on.',
            '<strong>Fix 4: If you were removed</strong>, contact an admin privately and politely ask what happened. <strong>Fix 5: Clear app cache</strong> and retry — rarely, a stale cache shows an error for a working link.',
            'Admins: reset links sparingly, and <strong>update your directory listings</strong> the same day you reset — otherwise hundreds of people hit a dead page.',
            'Browse <a href="../index.html">freshly verified groups</a> where dead links are flagged and removed automatically.',
        ],
    },
]

def blog_article_html(post):
    slug = post['slug']
    kw = post['keywords']
    hashtags = post['hashtags']
    paras = '\n'.join(f'<p>{p}</p>' for p in post['paras'])
    article_json = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": post['title'],
        "description": post['desc'],
        "inLanguage": "en",
        "author": {"@type": "Organization", "name": SITE_NAME},
        "publisher": {"@type": "Organization", "name": SITE_NAME}}, ensure_ascii=False)
    extra = (f'<meta name="keywords" content="{esc(kw)}">\n'
             + f'<meta property="og:type" content="article">\n'
             + f'<meta name="twitter:card" content="summary">\n'
             + f'<meta name="twitter:title" content="{esc(post["title"])}">\n'
             + f'<meta name="twitter:description" content="{esc(post["desc"])}">\n'
             + f'<script type="application/ld+json">{article_json}</script>\n')
    h = header(post['title'] + ' | ' + SITE_NAME, post['desc'], f'blog/{slug}.html', extra_head=extra)
    h += f"""<div class="container"><div class="section" style="max-width:780px">
<div class="crumb"><a href="../index.html">Home</a> / <a href="../blog.html">Guides</a> / {esc(post['title'][:40])}...</div>
<h1>{esc(post['title'])}</h1>
<p class="sub">{esc(post['desc'])}</p>
<div class="article-body">{paras}</div>
<p class="hashtags" style="color:#1a73e8;font-size:14px;margin-top:20px;font-weight:bold">{esc(hashtags)}</p>
<div class="share-row" style="margin-top:18px">
<a href="https://wa.me/?text={esc(post['title'])}" target="_blank" rel="noopener">Share on WhatsApp</a>
<a href="https://www.facebook.com/sharer/sharer.php?u=" target="_blank" rel="noopener">Share on Facebook</a>
<a href="https://twitter.com/intent/tweet?text={esc(post['title'])}" target="_blank" rel="noopener">Share on X</a>
</div>
</div></div>"""
    h += FOOTER.format(name=SITE_NAME, prefix='../')
    return h

def main():
    with open(f'{BASE}/groups.json') as f:
        groups = json.load(f)
    print(f"Loaded {len(groups)} groups")

    # assign slugs + normalize
    for i, g in enumerate(groups):
        g['gid'] = i
        if not g.get('slug'):
            g['slug'] = slugify(g['name'], i)
        # clean description of source mentions
        if g.get('description'):
            g['description'] = re.sub(r'\s+on Groupizo\.?', '', g['description'], flags=re.I)

    cat_counts = Counter(g['category'] for g in groups if g.get('category'))
    print("Categories:", dict(cat_counts.most_common(12)))

    # ---- index.html ----
    # NOTE: group data is loaded client-side from groups.json (fetch) so the
    # homepage stays small. Do NOT inline the full dataset here.

    cat_cards = '\n'.join(
        f'<a class="catcard" href="category/{cat_slug(c)}.html"><span class="ico">{icon}</span><span class="nm">{esc(c)}</span><span class="ct">{cat_counts.get(c,0)} groups</span></a>'
        for c, icon in CATEGORIES if cat_counts.get(c, 0) > 0
    )

    index = header(f'{SITE_NAME} — WhatsApp Group Links Directory ({len(groups)}+ Groups)',
                   f'Browse {len(groups)}+ active WhatsApp group invite links across education, jobs, earning, entertainment and more. Search, filter by category, and join instantly.', 'index.html',
                   extra_head=f'<meta name="keywords" content="{esc(BASE_KEYWORDS + ", pakistan whatsapp groups, india whatsapp groups, girls whatsapp groups, study whatsapp groups, jobs whatsapp groups, earning whatsapp groups, islamic whatsapp groups, entertainment whatsapp groups, gaming whatsapp groups, news whatsapp groups")}">\n'
                   + '<script type="application/ld+json">{"@context":"https://schema.org","@type":"WebSite","name":"WhatsGroupLinks","alternateName":"WhatsApp Group Links Directory","url":"' + SITE_URL + '/","description":"Directory of active WhatsApp group invite links","potentialAction":{"@type":"SearchAction","target":"' + SITE_URL + '/index.html?q={search_term_string}","query-input":"required name=search_term_string"}}</script>\n')
    index += f"""
<div class="hero"><div class="container">
<h1>Find & Join Active WhatsApp Groups</h1>
<p>Browse {len(groups)}+ hand-reviewed WhatsApp group links — education, jobs, online earning, entertainment, Islamic, gaming and more. Search below and tap any group to join instantly.</p>
<div class="searchbar"><input id="search-input" type="text" placeholder="Search groups... (e.g. UPSC, jobs, earning)"><button onclick="document.getElementById('search-input').dispatchEvent(new Event('input'))">Search</button></div>
</div></div>
<div class="container">
<div class="section"><h2>Browse by Category</h2><p class="sub">Pick a topic and explore every group listed under it.</p>
<div class="catgrid">{cat_cards}</div></div>
<div class="section"><h2>Latest Groups</h2><p class="sub" id="result-count"></p>
<div style="margin-bottom:16px"><select id="cat-filter" style="padding:10px 16px;border-radius:8px;border:1px solid #ddd;font-size:15px"><option value="">All categories</option>
{''.join(f'<option value="{esc(c)}">{esc(c)}</option>' for c in sorted(cat_counts))}</select></div>
<div class="groupgrid" id="group-grid"></div>
<button class="loadmore" id="load-more">Load More Groups</button></div>
<div class="section"><div class="faq"><h2>Frequently Asked Questions</h2>
<details><summary>How do I join a WhatsApp group from this site?</summary><p>Find a group you like, open its page, and tap the green "Join on WhatsApp" button. WhatsApp will open directly at the group's join screen. No account or sign-up on this site is needed.</p></details>
<details><summary>Are the group invite links checked?</summary><p>Yes. Every submitted group is reviewed before publishing — we verify the invite link opens, the name and category make sense, and the submission looks genuine. Inactive links are flagged and removed.</p></details>
<details><summary>Why does a link say it is expired or revoked?</summary><p>WhatsApp lets group admins reset their invite link at any time, which deactivates the old one. Groups also stop accepting members at 1,024 participants. If you spot a dead link, please report it on the group page.</p></details>
<details><summary>How do I add my own WhatsApp group?</summary><p>Go to the Submit page, paste your WhatsApp invite link, choose a category and country, and send it in. Listings are reviewed and usually go live within 24 hours. It is completely free.</p></details>
<details><summary>Is this directory free to use?</summary><p>Yes — browsing, searching, joining, and submitting groups are all free. There is no account, no paid plan, and no catch.</p></details>
<details><summary>Do you read messages inside the groups?</summary><p>No. We only check the invite link, name, image, and description provided at submission time. What happens inside a group is between you and that community.</p></details>
</div></div>
</div>
<div id="grid-loading" style="text-align:center;padding:30px;color:#888">Loading groups…</div>
"""
    index += FOOTER.format(name=SITE_NAME, prefix='')
    open(f'{BASE}/index.html', 'w').write(index)
    print("index.html written")

    # ---- categories.html ----
    cats_page = header('All Categories — ' + SITE_NAME, 'Browse WhatsApp groups by category.', 'categories.html')
    cats_page += f'<div class="container"><div class="section"><div class="crumb"><a href="index.html">Home</a> / Categories</div><h2>All Categories</h2><p class="sub">{len(groups)} groups across {len([c for c in cat_counts if cat_counts[c]>0])} categories.</p><div class="catgrid">{cat_cards}</div></div></div>'
    cats_page += FOOTER.format(name=SITE_NAME, prefix='')
    open(f'{BASE}/categories.html', 'w').write(cats_page)

    # ---- category pages (paginated, 60 per page) ----
    os.makedirs(f'{BASE}/category', exist_ok=True)
    PER_PAGE = 60
    all_cat_urls = []
    for c, icon in CATEGORIES:
        clist = [g for g in groups if g.get('category') == c]
        if not clist:
            continue
        cs = cat_slug(c)
        total = len(clist)
        npages = (total + PER_PAGE - 1) // PER_PAGE
        kw = cat_keywords(c)
        hashtags = ' '.join('#' + w for w in re.sub(r'[^a-z0-9 &]+', '', c.lower()).split() if w) + ' #whatsappgrouplink #whatsappgroups #joingroups'
        for pgnum in range(1, npages + 1):
            start = (pgnum - 1) * PER_PAGE
            pg_groups = clist[start:start + PER_PAGE]
            fname = f'{cs}.html' if pgnum == 1 else f'{cs}-page{pgnum}.html'
            all_cat_urls.append(f'category/{fname}')
            items = []
            for pos, g in enumerate(pg_groups, start + 1):
                items.append({"@type": "ListItem", "position": pos,
                              "url": f'{SITE_URL}/groups/{g["slug"]}.html',
                              "name": g['name']})
            itemlist_json = json.dumps({
                "@context": "https://schema.org", "@type": "ItemList",
                "name": f"{c} WhatsApp Group Links (Page {pgnum})",
                "description": f"Active {c} WhatsApp group invite links — page {pgnum} of {npages}",
                "numberOfItems": total,
                "itemListElement": items}, ensure_ascii=False)
            seo_extra = ''
            if pgnum > 1:
                prevf = f'{cs}.html' if pgnum == 2 else f'{cs}-page{pgnum - 1}.html'
                seo_extra += f'<link rel="prev" href="{SITE_URL}/category/{prevf}">\n'
            if pgnum < npages:
                seo_extra += f'<link rel="next" href="{SITE_URL}/category/{cs}-page{pgnum + 1}.html">\n'
            extra = (seo_extra
                     + f'<meta name="keywords" content="{esc(kw)}">\n'
                     + f'<meta name="twitter:card" content="summary">\n'
                     + f'<meta name="twitter:title" content="{esc(c)} WhatsApp Group Link 2026 — Join {total} Active Groups">\n'
                     + f'<meta name="twitter:description" content="{esc(f"Join {total} active {c} WhatsApp groups. Browse the full list and tap any group to join instantly.")}">\n'
                     + f'<script type="application/ld+json">{itemlist_json}</script>\n')
            if pgnum == 1:
                pgtitle = f'{c} WhatsApp Group Link 2026 — Join {total} Active Groups | ' + SITE_NAME
            else:
                pgtitle = f'{c} WhatsApp Groups — Page {pgnum} of {npages} | ' + SITE_NAME
            p = header(pgtitle,
                       f'Join {total} active {c} WhatsApp groups. Browse the full list and tap any group to join instantly. Updated 2026.', f'category/{fname}',
                       extra_head=extra)
            cards = '\n'.join(
                f'<div class="gcard"><a href="../groups/{g["slug"]}.html"><img class="gimg" loading="lazy" src="{esc(g.get("image","../assets/default-group.png"))}" alt="{esc(g["name"])}"></a><div class="gbody"><span class="gcat">{esc(c)}</span><h3><a href="../groups/{g["slug"]}.html">{esc(g["name"])}</a></h3><a class="joinbtn" href="../groups/{g["slug"]}.html">View & Join</a></div></div>'
                for g in pg_groups
            )
            pgnav = pagination_html(cs, pgnum, npages) if npages > 1 else ''
            if npages > 1:
                showing = f'Showing {start + 1}–{start + len(pg_groups)} of {total} active groups. Tap any card to view details and join.'
            else:
                showing = f'{total} active groups. Tap any card to view details and join.'
            p += f'<div class="container"><div class="section"><div class="crumb"><a href="../index.html">Home</a> / <a href="../categories.html">Categories</a> / {esc(c)}</div><h2>{icon} {esc(c)} WhatsApp Groups</h2><p class="sub">{showing}</p>{pgnav}<div class="groupgrid">{cards}</div>{pgnav}<p class="hashtags" style="color:#888;font-size:13px;margin-top:18px">{esc(hashtags)}</p></div></div>'
            p += FOOTER.format(name=SITE_NAME, prefix='../')
            open(f'{BASE}/category/{fname}', 'w').write(p)
    print(f"category pages written ({len(all_cat_urls)} paginated pages)")

    # ---- individual group pages ----
    os.makedirs(f'{BASE}/groups', exist_ok=True)
    for g in groups:
        name = esc(g['name'])
        cat = esc(g.get('category') or 'General')
        desc = esc((g.get('description') or f'Join {g["name"]}, an active WhatsApp group. Tap the button below to join instantly.')[:400])
        img = esc(g.get('image') or '../assets/default-group.png')
        invite = esc(g.get('invite') or '#')
        country = esc(g.get('country') or '')
        gcat = g.get('category') or 'General'
        og_json = json.dumps({
            "@context": "https://schema.org", "@type": "WebPage",
            "name": f'{g["name"]} WhatsApp Group — Join Link',
            "description": (g.get('description') or '')[:160],
            "inLanguage": "en",
            "isPartOf": {"@type": "WebSite", "name": SITE_NAME}}, ensure_ascii=False)
        g_extra = (f'<meta property="og:url" content="{SITE_URL}/groups/{g["slug"]}.html">\n'
                   + f'<meta property="og:type" content="article">\n'
                   + f'<meta property="og:image" content="{img}">\n'
                   + f'<meta name="twitter:card" content="summary_large_image">\n'
                   + f'<meta name="twitter:title" content="{name} WhatsApp Group — Join Link">\n'
                   + f'<meta name="twitter:description" content="{desc[:160]}">\n'
                   + f'<meta name="twitter:image" content="{img}">\n'
                   + f'<meta name="keywords" content="{esc(cat_keywords(gcat))}">\n'
                   + f'<script type="application/ld+json">{og_json}</script>\n')
        pg = header(f'{g["name"]} WhatsApp Group Link 2026 — Join Now | ' + SITE_NAME,
                    (g.get('description') or '')[:160], f'groups/{g["slug"]}.html',
                    extra_head=g_extra)
        pg += f"""<div class="container"><div class="gdetail">
<div class="crumb"><a href="../index.html">Home</a> / <a href="../category/{cat_slug(g.get('category') or 'general')}.html">{cat}</a> / {name}</div>
<div class="top"><img class="gbig" src="{img}" alt="{name} WhatsApp group">
<div class="meta"><h1>{name}</h1>
<span class="pill">📁 {cat}</span>{f'<span class="pill">🌍 {country}</span>' if country else ''}
<div class="desc"><p>{desc}</p></div>
<a class="bigjoin" href="{invite}" target="_blank" rel="noopener nofollow">Join on WhatsApp</a>
<p style="font-size:13px;color:#888">Tapping the button opens WhatsApp directly at this group's join screen. If the link has expired, the group admin may have reset it.</p>
</div></div>
<div class="share-row">
<a href="https://wa.me/?text={esc(g['name'])}%20WhatsApp%20group" target="_blank" rel="noopener">Share on WhatsApp</a>
<a href="https://www.facebook.com/sharer/sharer.php?u=" target="_blank" rel="noopener">Share on Facebook</a>
<a href="https://twitter.com/intent/tweet?text={esc(g['name'])}" target="_blank" rel="noopener">Share on X</a>
<button onclick="navigator.clipboard&&navigator.clipboard.writeText(location.href).then(()=>this.textContent='Copied!')">Copy Link</button>
</div>
</div></div>"""
        pg += FOOTER.format(name=SITE_NAME, prefix='../')
        open(f'{BASE}/groups/{g["slug"]}.html', 'w').write(pg)
    print(f"{len(groups)} group pages written")

    # ---- static pages ----
    about = header('About Us — ' + SITE_NAME, 'Learn about our WhatsApp groups directory.', 'about.html')
    about += """<div class="container"><div class="section" style="max-width:760px"><div class="crumb"><a href="index.html">Home</a> / About</div>
<h2>About Us</h2>
<p>We started this directory after getting tired of clicking WhatsApp invite links that led nowhere — dead pages, expired invites, groups at full capacity. The directories we found were not maintaining their listings.</p>
<p>So we built a directory with a simple promise: <strong>every group is reviewed before it goes live</strong>. We check that the invite link actually opens, that the name and category make sense, and that the submission looks genuine. After publishing, inactive links are flagged and removed.</p>
<p>We only look at what the submitter provides — name, image, description. We never enter groups or read any messages. What goes on inside a community is between its members.</p>
<p>Our mission is to make it effortless to find your people on WhatsApp — study partners, job alerts, hobby communities, local groups — whatever you are looking for.</p>
</div></div>""" + FOOTER.format(name=SITE_NAME, prefix='')
    open(f'{BASE}/about.html', 'w').write(about)

    contact = header('Contact Us — ' + SITE_NAME, 'Get in touch with the directory team.', 'contact.html')
    contact += """<div class="container"><div class="form-card"><div class="crumb"><a href="index.html">Home</a> / Contact</div>
<h2>Contact Us</h2><p class="sub">Questions, broken links, or takedown requests — send us a message and we will get back to you.</p>
<form onsubmit="event.preventDefault();this.innerHTML='<p>Thank you! Your message has been received.</p>'">
<label>Your name</label><input required>
<label>Your email</label><input type="email" required>
<label>Subject</label><select><option>General question</option><option>Report a broken link</option><option>Remove my group</option><option>Advertising</option><option>Other</option></select>
<label>Message</label><textarea required></textarea>
<button type="submit">Send Message</button></form></div></div>""" + FOOTER.format(name=SITE_NAME, prefix='')
    open(f'{BASE}/contact.html', 'w').write(contact)

    privacy = header('Privacy Policy — ' + SITE_NAME, 'How we handle your data.', 'privacy.html')
    privacy += """<div class="container"><div class="section" style="max-width:760px"><div class="crumb"><a href="index.html">Home</a> / Privacy Policy</div>
<h2>Privacy Policy</h2><p><em>Last updated: October 2026</em></p>
<h3>1. Information we collect</h3><p>We collect minimal information: when you submit a group, we store the group name, invite link, category, country, and description you provide. When you use the contact form, we receive your name, email, and message. We do not require accounts and do not track you across the web.</p>
<h3>2. How we use it</h3><p>Submitted group data is used solely to display the listing in the directory. Contact messages are used only to respond to your inquiry.</p>
<h3>3. Cookies</h3><p>We use only strictly necessary technical cookies (if any). We do not use advertising or cross-site tracking cookies ourselves. Third-party advertising partners (such as Google AdSense, when enabled) may use cookies to serve personalized ads; you can opt out via your browser settings or Google's ad settings.</p>
<h3>4. Data sharing</h3><p>We do not sell your personal information. Group listings you submit are public by design. We may disclose information if required by law.</p>
<h3>5. Your rights (GDPR/CCPA)</h3><p>You may request access, correction, or deletion of your personal data, including removal of a group you submitted, by contacting us. We respond within 30 days.</p>
<h3>6. Children</h3><p>This directory is not directed at children under 13, and we do not knowingly collect their data.</p>
<h3>7. Changes</h3><p>We may update this policy; the latest version is always posted on this page.</p>
</div></div>""" + FOOTER.format(name=SITE_NAME, prefix='')
    open(f'{BASE}/privacy.html', 'w').write(privacy)

    terms = header('Terms of Service — ' + SITE_NAME, 'Rules for using the directory.', 'terms.html')
    terms += """<div class="container"><div class="section" style="max-width:760px"><div class="crumb"><a href="index.html">Home</a> / Terms</div>
<h2>Terms of Service</h2><p><em>Last updated: October 2026</em></p>
<h3>1. The service</h3><p>We operate a directory of user-submitted WhatsApp group invite links. Listings are provided "as is"; we review submissions but cannot guarantee every link stays active.</p>
<h3>2. Submitting groups</h3><p>By submitting a group you confirm you are authorized to share its invite link and that the listing is accurate and lawful. We may edit, recategorize, or remove any listing at our discretion. Spam, adult content, illegal activity, and misleading listings are prohibited.</p>
<h3>3. Joining groups</h3><p>Groups are run by their own admins, not by us. We are not responsible for anything that happens inside a WhatsApp group. Exercise normal caution: never share passwords, bank details, or one-time codes.</p>
<h3>4. Acceptable use</h3><p>Do not scrape the site aggressively, attempt to disrupt it, or submit bulk spam listings.</p>
<h3>5. Intellectual property</h3><p>Group names, images, and descriptions belong to their respective owners. Our site design and original text are ours.</p>
<h3>6. Limitation of liability</h3><p>To the maximum extent permitted by law, we are not liable for any loss arising from use of the directory or of any listed group.</p>
</div></div>""" + FOOTER.format(name=SITE_NAME, prefix='')
    open(f'{BASE}/terms.html', 'w').write(terms)

    submit = header('Submit Your WhatsApp Group Link 2026 — ' + SITE_NAME, 'Add your WhatsApp group to the directory for free. Only active groups with working invite links are listed.', 'submit.html',
                      extra_head='<meta name="keywords" content="submit whatsapp group, add whatsapp group link, list my whatsapp group, #whatsappgroups">\n')
    submit += """<div class="container"><div class="form-card"><div class="crumb"><a href="index.html">Home</a> / Submit Group</div>
<h2>Submit Your Group</h2><p class="sub">Free forever. Every link is checked — only active groups with working invite links are listed. Dead or expired links are automatically removed.</p>
<form id="submit-form">
<label>Group name *</label><input id="f-name" required maxlength="80">
<label>WhatsApp invite link *</label><input id="f-link" required placeholder="https://chat.whatsapp.com/..." pattern="https://chat.whatsapp.com/.+">
<div id="dup-warning" style="display:none;color:#d32f2f;font-size:14px;margin:-8px 0 12px;font-weight:bold"></div>
<div id="adult-warning" style="display:none;color:#d32f2f;font-size:14px;margin:-8px 0 12px;font-weight:bold"></div>
<label>Category *</label><select id="f-cat" required><option value="">Select...</option>""" + ''.join(f'<option>{esc(c)}</option>' for c, _ in CATEGORIES) + """</select>
<label>Country</label><input id="f-country" placeholder="e.g. Pakistan">
<label>Short description</label><textarea id="f-desc" maxlength="300" placeholder="What is this group about? (max 300 characters)"></textarea>
<button type="submit">Submit Group</button></form>
<script>
(function(){
  var existingCodes = {};
  fetch('groups.json').then(function(r){return r.json();}).then(function(groups){
    groups.forEach(function(g){
      var code = (g.invite||'').trim().split('/').pop().split('?')[0];
      if(code) existingCodes[code] = g.name;
    });
  }).catch(function(){});
  var linkInput = document.getElementById('f-link');
  var warn = document.getElementById('dup-warning');
  var nameInput = document.getElementById('f-name');
  var descInput = document.getElementById('f-desc');
  var adultWarn = document.getElementById('adult-warning');
  var ADULT_RE = /\\b(porn|pornography|xxx|sex|sexy|nudes?|naked|escort|playboy|girls?|call[\\s-]?girls?|desi[\\s-]?girls?|hot[\\s-]?girls?|whatsapp[\\s-]?girls?|night[\\s-]?girls?|bhabhi|aunty|mms|leak(?:ed|s)?[\\s-]?videos?|viral[\\s-]?videos?|bedroom[\\s-]?videos?|blue[\\s-]?films?|adult[\\s-]?videos?|sex[\\s-]?(videos?|chat)|sexy[\\s-]?videos?|porn[\\s-]?videos?|xxx[\\s-]?videos?|hot[\\s-]?videos?|video[\\s-]?call[\\s-]?girls?|girls?[\\s-]?numbers?|massage[\\s-]?girls?)\\b|18\\+/i;
  function containsAdult(){
    var t = ((nameInput.value||'') + ' ' + (descInput.value||'')).toLowerCase();
    if(/adult\\s+(education|quran|class|course|learning)/i.test(t)) return false;
    return ADULT_RE.test(t);
  }
  function showAdultError(){
    adultWarn.style.display = 'block';
    adultWarn.textContent = 'Blocked: adult / pornographic content is not allowed on WhatsGroupLinks. This submission has been rejected.';
  }
  function hideAdultError(){ adultWarn.style.display = 'none'; adultWarn.textContent = ''; }
  nameInput.addEventListener('input', function(){ containsAdult() ? showAdultError() : hideAdultError(); });
  descInput.addEventListener('input', function(){ containsAdult() ? showAdultError() : hideAdultError(); });
  linkInput.addEventListener('input', function(){
    var code = linkInput.value.trim().split('/').pop().split('?')[0];
    if(code && existingCodes[code]){
      warn.style.display = 'block';
      warn.textContent = '\\u26A0\\uFE0F This group link is already listed as "' + existingCodes[code] + '". Duplicate links are not accepted.';
    } else {
      warn.style.display = 'none';
      warn.textContent = '';
    }
  });
  document.getElementById('submit-form').addEventListener('submit', function(e){
    e.preventDefault();
    if(containsAdult()){ showAdultError(); nameInput.focus(); return; }
    hideAdultError();
    var code = linkInput.value.trim().split('/').pop().split('?')[0];
    if(code && existingCodes[code]){
      warn.style.display = 'block';
      warn.textContent = '\\u26A0\\uFE0F This group is already in our directory. Each link can only be added once.';
      linkInput.focus();
      return;
    }
    this.innerHTML = '<p>Thank you! Your group has been received and is now in the review queue.</p>';
  });
})();
</script>
<p style="font-size:13px;color:#888;margin-top:14px">By submitting you agree to our <a href="terms.html">Terms of Service</a>. No spam, adult, or illegal content.</p>
</div></div>""" + FOOTER.format(name=SITE_NAME, prefix='')
    open(f'{BASE}/submit.html', 'w').write(submit)

    # ---- blog/guides section ----
    os.makedirs(f'{BASE}/blog', exist_ok=True)
    for post in BLOG_POSTS:
        open(f'{BASE}/blog/{post["slug"]}.html', 'w').write(blog_article_html(post))
    print(f"{len(BLOG_POSTS)} blog articles written")

    blog_cards = '\n'.join(
        f'<div class="gcard"><div class="gbody"><span class="gcat">Guide</span><h3><a href="blog/{p["slug"]}.html">{esc(p["title"])}</a></h3><p class="gdesc">{esc(p["desc"][:140])}</p><a class="joinbtn" href="blog/{p["slug"]}.html">Read Guide</a></div></div>'
        for p in BLOG_POSTS
    )
    blog_idx = header('WhatsApp Guides & Tips 2026 — ' + SITE_NAME,
                      'Step-by-step guides: how to join WhatsApp groups, best study groups, group rules for admins, earning groups safety, and fixing expired links.',
                      'blog.html',
                      extra_head='<meta name="keywords" content="whatsapp guides, how to join whatsapp group, whatsapp tips 2026, #whatsappgroups, #whatsapptips">\n')
    blog_idx += f'<div class="container"><div class="section"><div class="crumb"><a href="index.html">Home</a> / Guides</div><h2>📖 WhatsApp Guides & Tips</h2><p class="sub">Practical guides to finding, joining, and managing WhatsApp groups.</p><div class="groupgrid">{blog_cards}</div></div></div>'
    blog_idx += FOOTER.format(name=SITE_NAME, prefix='')
    open(f'{BASE}/blog.html', 'w').write(blog_idx)
    print("blog.html written")

    # sitemap.xml (as index) + split sitemaps — Google caps 50,000 URLs per file
    # and requires ABSOLUTE <loc> values.
    def sm_write(fname, urls):
        sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for u in urls:
            sm += f'  <url><loc>{SITE_URL}/{u}</loc><lastmod>2026-10-17</lastmod></url>\n'
        sm += '</urlset>'
        open(f'{BASE}/{fname}', 'w').write(sm)

    static_urls = ['index.html', 'categories.html', 'blog.html', 'submit.html', 'about.html', 'contact.html', 'privacy.html', 'terms.html']
    static_urls += all_cat_urls  # all paginated category pages
    static_urls += [f'blog/{p["slug"]}.html' for p in BLOG_POSTS]
    group_urls = [f'groups/{g["slug"]}.html' for g in groups]
    sm_write('sitemap-main.xml', static_urls)
    sm_write('sitemap-groups-1.xml', group_urls[:40000])
    sm_write('sitemap-groups-2.xml', group_urls[40000:])
    idx = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           f'  <sitemap><loc>{SITE_URL}/sitemap-main.xml</loc><lastmod>2026-10-17</lastmod></sitemap>\n'
           f'  <sitemap><loc>{SITE_URL}/sitemap-groups-1.xml</loc><lastmod>2026-10-17</lastmod></sitemap>\n'
           f'  <sitemap><loc>{SITE_URL}/sitemap-groups-2.xml</loc><lastmod>2026-10-17</lastmod></sitemap>\n'
           '</sitemapindex>')
    open(f'{BASE}/sitemap.xml', 'w').write(idx)

    # robots.txt
    open(f'{BASE}/robots.txt', 'w').write(
        f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n')

    # .nojekyll — serve 61k static files directly, skip Jekyll processing
    open(f'{BASE}/.nojekyll', 'w').write('')

    print("Static pages + sitemaps written")

if __name__ == '__main__':
    main()
