import json
leads = [
 {"url": "https://www.groupjoin.link/recent-groups", "note": "NEEDS-BROWSER-LEG: JS-gated; text fetch shows only first 3 groups. Paginate for newest submissions.", "source": "groupjoin.link"},
 {"url": "https://www.groupjoin.link/group-search?category=32", "note": "NEEDS-BROWSER-LEG: JS-gated search page; check newest submissions per category.", "source": "groupjoin.link"},
 {"url": "https://www.groupjoin.link/tag/G?safeSearch=blur", "note": "NEEDS-BROWSER-LEG: tag page, JS-gated; 59,362 results listed.", "source": "groupjoin.link"},
 {"url": "https://www.groupjoin.link/popular-groups", "note": "NEEDS-BROWSER-LEG: JS-gated listing page from sitemap-main.", "source": "groupjoin.link"},
 {"url": "https://www.groupjoin.link/whatsapp-groups", "note": "NEEDS-BROWSER-LEG: JS-gated directory page from sitemap-main.", "source": "groupjoin.link"},
 {"url": "https://whatsgroupslinkspk.com/all-groups/", "note": "Paginated index of 53 category posts (page/2/ ...); homepage already mined, but deeper pages may hold unharvested codes.", "source": "whatsgroupslinkspk.com"},
 {"url": "https://whatsgroupslinkspk.com/all-groups/page/2/", "note": "All-groups index page 2.", "source": "whatsgroupslinkspk.com"},
]
json.dump(leads, open('team16-leads.json','w'), indent=1, ensure_ascii=False)
print('leads:', len(leads))
