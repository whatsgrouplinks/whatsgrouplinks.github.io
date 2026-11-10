#!/usr/bin/env python3
"""Team 03, wave 20261110, leads slice 3 (184 listing URLs).
Own implementation: fetch listing pages, extract invite codes + metadata,
dedupe vs union(.existing_codes.json, groups.json invite codes), verify
fresh codes against chat.whatsapp.com with curl (max 3 parallel, >=0.6s
gap between check starts, 15s timeout). LIVE = HTTP 200 + non-empty og:title.
Writes team03-leads-slice3*.json + summary in this wave dir only.
"""
import json, re, subprocess, sys, time, html, threading
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

BASE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110"
SITE = "/home/hatch/workspace/whatsapp-groups-site"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
ALLOWED_CATS = ["Entertainment","Jobs","Education","Islamic","Sports","Community & Social",
                "Finance","Funny","Buy Sell","Health","News","Gaming","Technology","Business"]

def fetch(url, timeout=20, tries=2):
    for a in range(tries):
        try:
            r = subprocess.run(["curl","-s","-L","-A",UA,"--max-time",str(timeout),url],
                               capture_output=True, timeout=timeout+10)
            if r.returncode == 0 and r.stdout:
                return r.stdout.decode("utf-8", errors="replace")
        except Exception:
            pass
        time.sleep(1)
    return None

def clean(s):
    return re.sub(r"\s+", " ", html.unescape(s or "")).strip()

def meta(h, prop):
    for pat in (r'<meta[^>]*(?:property|name)=["\']'+re.escape(prop)+r'["\'][^>]*content=["\']([^"\']*)["\']',
                r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*(?:property|name)=["\']'+re.escape(prop)+r'["\']'):
        m = re.search(pat, h, re.I)
        if m:
            return clean(m.group(1))
    return ""

CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_\-]{10,})")
def code_in(h):
    if not h:
        return None
    m = CODE_RE.search(h)
    if not m:
        return None
    c = m.group(1)
    return c[:22] if len(c) > 22 else c

def norm_code(raw):
    if not raw:
        return None
    c = re.split(r"[?#]", raw.strip())[0].rstrip("/")
    return c or None

COUNTRY_SLUG = {
 "nigeria":"NG","pakistan":"PK","india":"IN","united-states":"US","usa":"US","canada":"CA",
 "germany":"DE","russia":"RU","romania":"RO","rwanda":"RW","kenya":"KE","ghana":"GH",
 "bangladesh":"BD","indonesia":"ID","malaysia":"MY","philippines":"PH","brazil":"BR",
 "united-kingdom":"GB","uk":"GB","australia":"AU","south-africa":"ZA","egypt":"EG",
 "saudi-arabia":"SA","uae":"AE","turkey":"TR","france":"FR","italy":"IT","spain":"ES",
 "netherlands":"NL","poland":"PL","ukraine":"UA","nepal":"NP","sri-lanka":"LK","myanmar":"MM",
 "thailand":"TH","vietnam":"VN","japan":"JP","china":"CN","korea":"KR","south-korea":"KR",
 "mexico":"MX","colombia":"CO","argentina":"AR","peru":"PE","chile":"CL","venezuela":"VE",
 "morocco":"MA","algeria":"DZ","tunisia":"TN","ethiopia":"ET","uganda":"UG","tanzania":"TZ",
 "zambia":"ZM","zimbabwe":"ZW","cameroon":"CM","senegal":"SN","ivory-coast":"CI","mali":"ML",
 "burkina-faso":"BF","niger":"NE","chad":"TD","sudan":"SD","somalia":"SO","yemen":"YE",
 "iraq":"IQ","iran":"IR","afghanistan":"AF","jordan":"JO","lebanon":"LB","syria":"SY",
 "palestine":"PS","israel":"IL","kuwait":"KW","qatar":"QA","bahrain":"BH","oman":"OM",
 "georgia":"GE","azerbaijan":"AZ","kazakhstan":"KZ","uzbekistan":"UZ","kyrgyzstan":"KG",
 "tajikistan":"TJ","turkmenistan":"TM","mongolia":"MN","taiwan":"TW","hong-kong":"HK",
 "singapore":"SG","cambodia":"KH","laos":"LA","brunei":"BN","fiji":"FJ","new-zealand":"NZ",
 "ireland":"IE","portugal":"PT","greece":"GR","belgium":"BE","switzerland":"CH","austria":"AT",
 "sweden":"SE","norway":"NO","denmark":"DK","finland":"FI","czech-republic":"CZ","hungary":"HU",
 "croatia":"HR","serbia":"RS","bulgaria":"BG","lithuania":"LT","latvia":"LV","estonia":"EE",
 "belarus":"BY","moldova":"MD","albania":"AL","bosnia-herzegovina":"BA","north-macedonia":"MK",
 "montenegro":"ME","iceland":"IS","luxembourg":"LU","malta":"MT","cyprus":"CY",
 "sierra-leone":"SL","liberia":"LR","togo":"TG","benin":"BJ","gabon":"GA","congo":"CG",
 "democratic-republic-of-congo":"CD","angola":"AO","mozambique":"MZ","madagascar":"MG",
 "mauritius":"MU","botswana":"BW","namibia":"NA","lesotho":"LS","eswatini":"SZ","malawi":"MW",
 "burundi":"BI","eritrea":"ER","djibouti":"DJ","mauritania":"MR","libya":"LY","jamaica":"JM",
 "trinidad-and-tobago":"TT","barbados":"BB","guyana":"GY","suriname":"SR","bolivia":"BO",
 "ecuador":"EC","paraguay":"PY","uruguay":"UY","costa-rica":"CR","panama":"PA","guatemala":"GT",
 "honduras":"HN","el-salvador":"SV","nicaragua":"NI","cuba":"CU","dominican-republic":"DO",
 "haiti":"HT","bahamas":"BS","belize":"BZ",
}
AR_COUNTRY = {"مصر":"EG","السعودية":"SA","اليمن":"YE","فلسطين":"PS","المغرب":"MA","الجزائر":"DZ",
 "العراق":"IQ","سوريا":"SY","لبنان":"LB","تركيا":"TR","الهند":"IN","باكستان":"PK",
 "بنغلاديش":"BD","إندونيسيا":"ID","ماليزيا":"MY","نيجيريا":"NG","كينيا":"KE","أمريكا":"US",
 "الولايات المتحدة":"US","الإمارات":"AE","قطر":"QA","الكويت":"KW","البحرين":"BH","ليبيا":"LY",
 "تونس":"TN","السودان":"SD","الأردن":"JO","عمان":"OM","غانا":"GH","البرازيل":"BR",
 "فرنسا":"FR","ألمانيا":"DE","إيطاليا":"IT","إسبانيا":"ES","بريطانيا":"GB","كندا":"CA",
 "أستراليا":"AU","روسيا":"RU","أوكرانيا":"UA","الصين":"CN","اليابان":"JP","كوريا":"KR",
 "تايلاند":"TH","فيتنام":"VN","الفلبين":"PH","نيبال":"NP","إثيوبيا":"ET","الصومال":"SO",
 "موريتانيا":"MR","تشاد":"TD","النيجر":"NE","مالي":"ML","السنغال":"SN","الكاميرون":"CM",
 "زامبيا":"ZM","زيمبابوي":"ZW","موزمبيق":"MZ","أنغولا":"AO","كولومبيا":"CO","الأرجنتين":"AR",
 "المكسيك":"MX","البرتغال":"PT","هولندا":"NL","بلجيكا":"BE","سويسرا":"CH","النمسا":"AT",
 "السويد":"SE","النرويج":"NO","الدنمارك":"DK","فنلندا":"FI","اليونان":"GR","بولندا":"PL",
 "رومانيا":"RO","المجر":"HU","صربيا":"RS","كرواتيا":"HR"}
AR_CAT = {"رياضة":"Sports","دين":"Islamic","أعمال":"Business","تعليم":"Education",
 "ترفيه":"Entertainment","صحة":"Health","أخبار":"News","تقنية":"Technology",
 "زواج":"Community & Social","حب":"Community & Social","أخرى":"Community & Social",
 "مال":"Finance","تجارة":"Business","ألعاب":"Gaming","وظائف":"Jobs","عمل":"Jobs",
 "فن":"Entertainment","موسيقى":"Entertainment"}

def infer_category(blob):
    b = (blob or "").lower()
    if re.search(r"quran|islam|muslim|allah|ramadan|deen|hijab|madrasa|namaz|dua\b", b): return "Islamic"
    if re.search(r"\bjob|jobs|career|hiring|vacancy|vacancies|naukri|recruit", b): return "Jobs"
    if re.search(r"study|exam|school|class|learn|course|student|ielts|css|pms|university|college|teacher", b): return "Education"
    if re.search(r"gaming|game|games|pubg|free fire|mlbb|mobile legends|gamer", b): return "Gaming"
    if re.search(r"coding|python|developer|software|programmer|programming|android|tech\b|technology|computer", b): return "Technology"
    if re.search(r"business|entrepreneur|startup|company", b): return "Business"
    if re.search(r"earn|earning|money|forex|trading|bitcoin|crypto|invest", b): return "Finance"
    if re.search(r"buy|sell|shop|store|market|jual|beli|akun|top ?up|rekber|price|sale", b): return "Buy Sell"
    if re.search(r"football|cricket|sport|fitness|gym|workout", b): return "Sports"
    if re.search(r"health|doctor|medical|hospital|diet|weight", b): return "Health"
    if re.search(r"\bnews|breaking|headline|update", b): return "News"
    if re.search(r"movie|music|song|drama|entertainment|video|film|serial", b): return "Entertainment"
    if re.search(r"funny|joke|meme|comedy|fun\b", b): return "Funny"
    return "Community & Social"

# ---- listing processors ----
def process_gi(item):
    url = item["url"]; slug = url.rstrip("/").split("/")[-1]
    rec = {"listing_url": url, "source": "groupsinvite.link", "slug": slug}
    h = fetch(url)
    if not h:
        rec["error"] = "detail fetch failed"; return [rec], []
    t = re.search(r"<title>(.*?)</title>", h, re.S)
    name = clean(t.group(1)) if t else ""
    name = re.sub(r"\s*WhatsApp Group Invite Link.*$", "", name)
    name = re.sub(r"\s*\|\s*GroupsInvite\s*$", "", name)
    rec["name"] = name
    desc = meta(h, "og:description") or meta(h, "description")
    fd = re.search(r'data-full-description="([^"]*)"', h)
    if fd and len(fd.group(1)) > len(desc):
        desc = clean(fd.group(1))
    rec["desc"] = desc
    rec["tags"] = [clean(x) for x in re.findall(r'class="tag-pill"[^>]*>([^<]+)</a>', h)][:6]
    cm = re.search(r'https://groupsinvite\.link/group/country/([^"/]+)/', h)
    rec["country_hint"] = COUNTRY_SLUG.get(cm.group(1), "International") if cm else "International"
    leads = []
    for s in sorted(set(re.findall(r"https://groupsinvite\.link/group/link/([a-z0-9]+)/", h))):
        u = f"https://groupsinvite.link/group/link/{s}/"
        if u != url:
            leads.append({"url": u, "source": "groupsinvite.link related group"})
    rules = fetch(f"https://groupsinvite.link/group/rules/{slug}/")
    if rules:
        rec["code"] = code_in(rules)
    if not rec.get("code"):
        rec["error"] = rec.get("error", "") + "; no code on rules page"
    return [rec], leads

def process_ong(item):
    url = item["url"]; code = url.rstrip("/").split("/")[-1]
    rec = {"listing_url": url, "source": "ongrupos.com", "code": norm_code(code), "country_hint": "BR"}
    h = fetch(url)
    if not h:
        rec["error"] = "detail fetch failed"; return [rec], []
    tm = re.search(r"<title>(.*?)</title>", h, re.S)
    name = clean(tm.group(1)) if tm else ""
    name = re.sub(r"^Grupo WhatsApp - ", "", name)
    rec["name"] = meta(h, "og:title") or name
    rec["desc"] = meta(h, "description")
    leads = []
    for c in sorted(set(re.findall(r"https://ongrupos\.com/grupo/([A-Za-z0-9]+)", h))):
        u = f"https://ongrupos.com/grupo/{c}"
        if u != url:
            leads.append({"url": u, "source": "ongrupos group detail"})
    return [rec], leads

def gcc_recover(n):
    """go.php?id=N -> join.php?id=N (301 to groupsor join token) -> groupsor rules -> code."""
    try:
        r = subprocess.run(["curl","-s","-A",UA,"--max-time","20","-D","-","-o","/dev/null",
                            f"https://groupchatconnect.info/join.php?id={n}"],
                           capture_output=True, timeout=30)
        hdrs = r.stdout.decode("utf-8", errors="replace")
        m = re.search(r"groupsor\.link/group/join/([A-Za-z0-9]+)", hdrs)
        if not m:
            return None, "join.php did not redirect to groupsor"
        token = m.group(1)
        rules = fetch(f"https://groupsor.link/group/rules/{token}/")
        c = code_in(rules)
        return c, (None if c else "no code on groupsor rules page")
    except Exception as e:
        return None, f"recover error: {e}"

def process_gcc(item):
    url = item["url"]
    rec = {"listing_url": url, "source": "groupchatconnect.info"}
    is_channel = "/channel/" in url
    h = fetch(url, timeout=25)
    if not h:
        rec["error"] = "detail fetch failed"; return [rec], []
    m = re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S)
    name = clean(re.sub(r"<[^>]+>", "", m.group(1))) if m else (meta(h, "og:title") or "")
    name = re.sub(r"\s*على دردشة جماعية.*$", "", name).strip()
    rec["name"] = name
    rec["desc"] = meta(h, "description") or meta(h, "og:description")
    if is_channel:
        rec["error"] = "channel-only page (no group invite)"
        rec["channel_only"] = True
    else:
        tok = re.search(r'href="/go/([A-Za-z0-9]+)"', h)
        if tok:
            rec["code"] = norm_code(tok.group(1))
        else:
            gp = re.search(r'href="/go\.php\?id=(\d+)"', h)
            if gp:
                c, err = gcc_recover(gp.group(1))
                if c:
                    rec["code"] = c; rec["recovered_via"] = "go.php->join.php->groupsor"
                else:
                    rec["error"] = f"go.php recovery failed: {err}"
            else:
                # direct groupsor join link?
                gj = re.search(r"groupsor\.link/group/join/([A-Za-z0-9]+)", h)
                if gj:
                    rules = fetch(f"https://groupsor.link/group/rules/{gj.group(1)}/")
                    rec["code"] = code_in(rules)
                    if not rec.get("code"):
                        rec["error"] = "no code on groupsor rules page"
                else:
                    rec["error"] = "no /go/ token found"
    leads = []
    for n in sorted(set(re.findall(r'href="/groupe/(\d+)"', h))):
        u = f"https://groupchatconnect.info/groupe/{n}"
        if u != url:
            leads.append({"url": u, "source": "groupchatconnect.info groupe"})
    for n in sorted(set(re.findall(r'href="/channel/(\d+)"', h))):
        u = f"https://groupchatconnect.info/channel/{n}"
        if u != url:
            leads.append({"url": u, "source": "groupchatconnect.info channel", "note": "channel-only page"})
    return [rec], leads

def process_gj(item):
    url = item["url"]
    body = fetch(url)
    if not body:
        return [{"listing_url": url, "source": "groupjoin.link API", "error": "api fetch failed"}], []
    try:
        data = json.loads(body).get("data", [])
    except Exception as e:
        return [{"listing_url": url, "source": "groupjoin.link API", "error": f"json parse: {e}"}], []
    recs = []
    for d in data:
        link = d.get("link") or ""
        m = re.search(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_\-]{10,})", link)
        recs.append({
            "listing_url": url, "source": "groupjoin.link API",
            "code": m.group(1) if m else None,
            "name": clean(str(d.get("group_title") or "")),
            "desc": clean(str(d.get("group_desc") or "")),
            "country_hint": ((d.get("country") or {}).get("iso2") or "International"),
            "category_hint": (d.get("category") or {}).get("category_name") or "",
            "nsfw": d.get("nsfw"),
            "tags": d.get("tags") or [],
        })
    return recs, []

def main_extract():
    leads = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/leads_slice_03.json"))
    existing = set(json.load(open(f"{SITE}/.existing_codes.json")))
    groups = json.load(open(f"{SITE}/groups.json"))
    gcodes = set()
    for r in groups:
        m = re.search(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_\-]+)", r.get("invite", ""))
        if m:
            gcodes.add(m.group(1))
    union = existing | gcodes
    print(f"slice={len(leads)} existing={len(existing)} groups_codes={len(gcodes)} union={len(union)}", flush=True)
    json.dump({"existing": len(existing), "groups_codes": len(gcodes), "union": len(union)},
              open(f"{BASE}/team03-dedupe.json", "w"), indent=1)

    def work(item):
        src = item.get("source", "")
        try:
            if "groupsinvite" in src: return process_gi(item)
            if "ongrupos" in src: return process_ong(item)
            if "groupchatconnect" in src: return process_gcc(item)
            if "team04" in src: return process_gj(item)
            return [{"listing_url": item["url"], "source": src, "error": "unknown source type"}], []
        except Exception as e:
            return [{"listing_url": item["url"], "source": src, "error": f"exception: {e}"}], []

    all_recs, all_leads = [], []
    with ThreadPoolExecutor(max_workers=6) as ex:
        for i, (recs, lds) in enumerate(ex.map(work, leads)):
            all_recs.extend(recs); all_leads.extend(lds)
            if (i + 1) % 25 == 0:
                print(f"... {i+1}/{len(leads)} recs={len(all_recs)}", flush=True)
    json.dump(all_recs, open(f"{BASE}/team03-raw.json", "w"), ensure_ascii=False, indent=1)
    slice_urls = {x["url"] for x in leads}
    new_leads, seen_l = [], set()
    for l in all_leads:
        if l["url"] not in slice_urls and l["url"] not in seen_l:
            seen_l.add(l["url"]); new_leads.append(l)
    json.dump(new_leads, open(f"{BASE}/team03-discovered-leads.json", "w"), ensure_ascii=False, indent=1)
    # fresh unique codes
    seen, fresh = set(), []
    dup = nocode = 0
    for r in all_recs:
        c = norm_code(r.get("code")); r["code"] = c
        if not c:
            nocode += 1; continue
        if c in union or c in seen:
            dup += 1; continue
        seen.add(c); fresh.append(r)
    json.dump(fresh, open(f"{BASE}/team03-fresh.json", "w"), ensure_ascii=False, indent=1)
    print(f"records={len(all_recs)} dup_codes={dup} no_code_records={nocode} fresh_unique={len(fresh)} discovered_leads={len(new_leads)}", flush=True)
    for r in all_recs:
        if r.get("error"):
            print(" ERR:", r.get("listing_url"), "|", r.get("error"), flush=True)
    return fresh, new_leads, all_recs

if __name__ == "__main__":
    main_extract()
