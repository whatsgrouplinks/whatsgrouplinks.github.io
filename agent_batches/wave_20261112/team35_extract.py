import json, re, html
from pathlib import Path
RAW = Path("team35_raw")
CODE_RE = re.compile(r"chat\.whatsapp\.com/([A-Za-z0-9]{15,30})")
out = []

# --- 1. whatsgroupjoinlinks homepage: h3 sections, li items ---
w = (RAW/"whatsgroupjoinlinks_home.html").read_text()
# split by h3 headings
parts = re.split(r"<h3[^>]*>(.*?)</h3>", w)
# parts[0] preamble, then heading, body, heading, body...
for i in range(1, len(parts), 2):
    heading = re.sub(r"<[^>]+>", "", parts[i]).strip()
    body = parts[i+1] if i+1 < len(parts) else ""
    for li in re.findall(r"<li[^>]*>(.*?)</li>", body, re.S):
        m = CODE_RE.search(li)
        if not m: continue
        pre = li[:m.start()]
        pre = pre[:pre.rfind("<a")] if "<a" in pre else pre
        name = re.sub(r"<[^>]+>", "", pre).strip(" \t\n\r-–—:;|")
        name = html.unescape(name).strip()
        out.append({"code": m.group(1), "name": name, "section": heading, "source": "whatsgroupjoinlinks.com homepage"})

# --- 2. groupslink.pk pages: name paragraph -> following code ---
def glpk_extract(fname, section, source):
    h = (RAW/fname).read_text()
    # find all name paragraphs and all codes with positions, pair each code to nearest preceding name para
    paras = [(m.start(), html.unescape(re.sub(r"<[^>]+>","",m.group(1))).strip()) for m in re.finditer(r'<p class="has-text-align-center wp-block-paragraph">([^<]+)</p>', h)]
    for m in CODE_RE.finditer(h):
        code = m.group(1)
        # nearest preceding paragraph
        name = ""
        for pos, txt in reversed(paras):
            if pos < m.start():
                name = txt; break
        out.append({"code": code, "name": name, "section": section, "source": source})

glpk_extract("groupslink_pk_home.html", "homepage", "groupslink.pk homepage")
for fname, section, src in [
 ("glpk_desi_girl.html","Desi Girl","groupslink.pk/desi-girl-whatsapp-group-links/"),
 ("glpk_funny.html","Funny","groupslink.pk/funny-whatsapp-group-link/"),
 ("glpk_pak_groups.html","Pakistani Groups","groupslink.pk/whatsapp-groups-links-pakistan/"),
 ("glpk_join.html","Join Group","groupslink.pk/join-group-whatsapp/"),
 ("glpk_joinlink.html","Join Link","groupslink.pk/whatsapp-group-join-link/"),
 ("glpk_18comm.html","Community","groupslink.pk/18-community-groups/"),
 ("glpk_private.html","Private","groupslink.pk/private-whatsapp-group-link/"),
 ("glpk_viral1.html","Viral Video","groupslink.pk/grup-wa-viral-video-links/"),
 ("glpk_viral2.html","Viral Video","groupslink.pk/pakistan-viral-video-whatsapp-group-link-join/"),
]:
    glpk_extract(fname, section, src)

# dedupe by code, keep first
seen = {}
for r in out:
    seen.setdefault(r["code"], r)
pool = list(seen.values())
print("raw rows:", len(out), "unique codes:", len(pool))
with open("team35_extracted.jsonl","w") as f:
    for r in pool:
        f.write(json.dumps(r, ensure_ascii=False)+"\n")
# union dedupe
union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
fresh = [r for r in pool if r["code"] not in union]
print("fresh vs union:", len(fresh), "already in union:", len(pool)-len(fresh))
with open("team35_fresh.jsonl","w") as f:
    for r in fresh:
        f.write(json.dumps(r, ensure_ascii=False)+"\n")
# show name quality
print("sample fresh:", fresh[:5])
print("empty-name fresh:", sum(1 for r in fresh if not r["name"]))
