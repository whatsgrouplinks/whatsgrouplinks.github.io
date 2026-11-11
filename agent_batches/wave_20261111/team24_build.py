"""Build Team 24 wave-20261111 output files from checkpoints."""
import json, os

W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/"
INV = "https://chat.whatsapp.com/"

verified = [
    {"name": "4 Abroad Jobs", "category": "Jobs", "country": "",
     "description": "A group sharing abroad job opportunities.",
     "invite": INV + "H9LTbkC34L5989l4xuHTb5"},
    {"name": "International Manpower Solutions", "category": "Jobs", "country": "",
     "description": "A group sharing international manpower and job opportunities.",
     "invite": INV + "FzF8gpujVhXCTeXTe50y6P"},
    {"name": "Abroad Jobs 3", "category": "Jobs", "country": "",
     "description": "A group sharing abroad job opportunities.",
     "invite": INV + "F1cw4R2sf8KLj9rxNQhgrQ"},
    {"name": "Target UPSC", "category": "Education", "country": "IN",
     "description": "A study group for UPSC exam preparation and discussion.",
     "invite": INV + "9cr4ESYIFog7Sk6sWaLO0C"},
]

pending = [
    {"name": "PK 100 NEWS ENGLISH WORLD", "category": "News", "country": "PK",
     "description": "A news group sharing English world news updates.",
     "invite": INV + "Ic6RiVSQY3R5mMwoEmQ1H5",
     "reason": "transport failure: curl to chat.whatsapp.com returned no HTTP status after 3 spaced attempts on two separate runs (WhatsApp throttling)"},
    {"name": "USA Income", "category": "Online Earning", "country": "US",
     "description": "A group sharing income-earning opportunities in the USA.",
     "invite": INV + "1LppAANrAKl3EJolsce16A",
     "reason": "transport failure: curl to chat.whatsapp.com returned no HTTP status after 3 spaced attempts on two separate runs (WhatsApp throttling)"},
    {"name": "Foreigner Jobs in Belize", "category": "Jobs", "country": "BZ",
     "description": "A group sharing job opportunities for foreigners in Belize.",
     "invite": INV + "KFxh1zRuPpjJAqM4H8rObO",
     "reason": "transport failure: curl to chat.whatsapp.com returned no HTTP status after 3 spaced attempts on two separate runs (WhatsApp throttling)"},
    {"name": "USA Private company Jobs", "category": "Jobs", "country": "US",
     "description": "A group sharing private company job openings in the USA.",
     "invite": INV + "IZ5QYRAro8q1altcqb6Z7A",
     "reason": "transport failure: curl to chat.whatsapp.com returned no HTTP status after 3 spaced attempts on two separate runs (WhatsApp throttling)"},
    {"name": "Jobs Everyone", "category": "Jobs", "country": "US",
     "description": "A group sharing job openings for everyone.",
     "invite": INV + "K0B9kbf8MiACd71xrrcGvU",
     "reason": "transport failure: curl to chat.whatsapp.com returned no HTTP status after 3 spaced attempts on two separate runs (WhatsApp throttling)"},
    {"name": "Equity", "category": "Finance", "country": "",
     "description": "An equity markets group sharing news and discussion.",
     "invite": INV + "EeI2EVMcoHE4qBHKttflHA",
     "reason": "transport failure: curl to chat.whatsapp.com returned no HTTP status after 3 spaced attempts on three separate runs (Nov-10 pending + two Nov-11 retries; WhatsApp throttling)"},
    {"name": "ONE MISSION@IAS", "category": "Education", "country": "IN",
     "description": "A study group for IAS aspirants sharing preparation material and motivation.",
     "invite": INV + "H4pSJdaTGpyAm6Lsyqkvp6",
     "reason": "transport failure: curl to chat.whatsapp.com returned no HTTP status after 3 spaced attempts on two separate runs (Nov-10 pending + Nov-11 retry; WhatsApp throttling)"},
]

dead = ["FN9zH2RN31032Ycv9y4eKR", "Hjeck49eZsu3k3QmY0If7I", "EBzKkFCvi01EOFMxtDpreV",
        "IGa2WwYKdD67tt4fnZjwww", "G6iuCsQLpPw4O9kRMopMWZ", "CZMuehOdUJ20N7hNer7gfx",
        "DRLjaHdHh5w2c03ZUtIo0v", "FE7l37sw0maGMUrs0GOC7F", "I54Yz1nZhOpKplkNAtSlhR",
        "Lg1sP8KFLxrAlPXuK0HA6D", "EIxv6OAwg3q4WSJYVFCj5l", "HUi8nMf06ju4Pizmek3Xps",
        "JqSCbwY486HLP1EB8cxKke"]

# leads: Nov-10 leads entries whose page was NOT successfully mined this run
leads_in = json.load(open(W + "team24-leads-in.json"))
mined = set(json.load(open(W + "team24_mined.json")))
leads = []
failed_fetch = []
for i, entry in enumerate(leads_in):
    url = entry["url"] if isinstance(entry, dict) else entry
    slug = url.rstrip("/").split("/")[-1] + ".html"
    if slug not in mined:
        leads.append(url)
        if i < 120:
            failed_fetch.append(url)
print("leads remaining:", len(leads), "of which failed-fetch (idx<120):", len(failed_fetch))
for u in failed_fetch:
    print("  failed-fetch:", u)

mined_urls = []
for fn in sorted(mined):
    mined_urls.append("https://whtspgrouplink.com/" + fn[:-5] + "/")

json.dump(verified, open(W + "team24-whtspgrouplink.json", "w"), indent=1, ensure_ascii=False)
json.dump(pending, open(W + "team24-whtspgrouplink-pending.json", "w"), indent=1, ensure_ascii=False)
json.dump(leads, open(W + "team24-whtspgrouplink-leads.json", "w"), indent=1, ensure_ascii=False)

summary = {
    "team": 24,
    "slice": "whtspgrouplink.com",
    "sources": mined_urls,
    "verified": len(verified),
    "pending": len(pending),
    "leads": len(leads),
    "dead": len(dead),
    "exclusions": [],
    "resume": ("Re-check the 7 pending codes first (5 fresh + Equity + ONE MISSION@IAS; all transport-only, "
               "WhatsApp curl throttling). Then mine the 357 unmined post-sitemap listing pages in "
               "team24-whtspgrouplink-leads.json (indices 120-472 of the Nov-10 leads + 4 failed-fetch pages: "
               "brunei, vdm, spoken-english, welding-jobs — retry those 4 first)."),
    "notes": ("Mined 116 of 120 attempted listing pages (60 batch 1 + 56 batch 2; 4 fetch timeouts: brunei, "
              "vdm, spoken-english, welding-jobs). Extracted 2,288 unique invite codes from the 116 pages; "
              "only 10 fresh vs the 108,992-code union (site is heavily already-covered). Nov-10 pending "
              "re-check: 4 live, 7 dead, 3 transport. Fresh-code verification: 5 dead, 5 transport; "
              "pending-transport retry: 1 dead (Swing Trading), 2 still transport. WhatsApp curl throttled "
              "hard most of the day (HTTP 000 on most attempts); verdicts only flipped to 200/empty-og or "
              "live on spaced retries, so the 7 transport codes are likely partly live. Extractor fix this "
              "run: the first pass missed the /invite/ URL format (316 codes) and table-row listings — "
              "re-extraction with <li> and <td> name patterns recovered them. One glued artifact code "
              "(HUi8nMf06ju4Pizmek3Xpsht = 22-char code + 'ht' of a duplicated https:// in a malformed href) "
              "was dropped and replaced by the genuine 22-char code HUi8nMf06ju4Pizmek3Xps (USA Remote Work "
              "Job), which verified DEAD. No live item triggered adult/scam screens. Country for '4 Abroad "
              "Jobs' left '' (og:title gives no country; Nov-10 SG label came from the directory name). "
              "Runtime restarted mid-run during the retry pass; verifier resumed cleanly from its checkpoint "
              "file (2 codes) with no duplicate checks.")
}
json.dump(summary, open(W + "team24-whtspgrouplink-summary.json", "w"), indent=1, ensure_ascii=False)
print("verified:", len(verified), "pending:", len(pending), "leads:", len(leads), "dead:", len(dead))
print("OUTPUTS WRITTEN")
