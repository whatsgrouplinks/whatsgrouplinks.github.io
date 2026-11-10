import json

# --- verified: none ---
verified = []

# --- pending: transport-only (3) ---
pending = [
 {"name":"WhatsApp Group Girl","category":"Community & Social","country":"PK",
  "description":"A WhatsApp group for girls in Pakistan to chat and make new friends.",
  "invite":"https://chat.whatsapp.com/KzwO6LVoaS8DT0LBwqu16S",
  "code":"KzwO6LVoaS8DT0LBwqu16S",
  "reason":"Transport failure on 2nd verification attempt: curl rc 28 timeout, partial 16KB body, no og:title captured (after 1 completed HTTP 200 with empty og:title). Not confirmed dead; retry later."},
 {"name":"College Girls","category":"Community & Social","country":"PK",
  "description":"A friendship group for college girls in Pakistan to chat and share college life.",
  "invite":"https://chat.whatsapp.com/Fp53YAbEUa78T4zAZcCjRZ",
  "code":"Fp53YAbEUa78T4zAZcCjRZ",
  "reason":"Transport failure on 2nd verification attempt: curl rc 28 timeout, HTTP 000, 0 bytes (after 1 completed HTTP 200 with empty og:title). Not confirmed dead; retry later."},
 {"name":"Punjab Group girls","category":"Community & Social","country":"PK",
  "description":"A girls friendship group for members from Punjab, Pakistan.",
  "invite":"https://chat.whatsapp.com/KR7gWco4iCw3aRB8JtcI70",
  "code":"KR7gWco4iCw3aRB8JtcI70",
  "reason":"Transport failure on 2nd verification attempt: curl rc 28 timeout, HTTP 000, 0 bytes (after 1 completed HTTP 200 with empty og:title). Not confirmed dead; retry later."},
]

# --- leads: listing pages discovered ---
leads = [
 {"url":"https://walink.pk/","note":"Homepage; 111 group entries, 103 unique codes; clean sections already fully known, fresh codes almost all adult."},
 {"url":"https://walink.pk/category/whatsapp-group-links/","note":"Category archive; 0 group entries parsed (post links only)."},
 {"url":"https://walink.pk/whatsapp-group-link-pakistan/","note":"Listing page; 11 entries, mostly girls-section overlap with homepage."},
 {"url":"https://walink.pk/girls-whatsapp-group/","note":"Listing page; 12 entries, girls sections."},
 {"url":"https://walink.pk/desi-girl-whatsapp-group/","note":"Listing page; 17 entries, desi-girl sections (adult-heavy)."},
 {"url":"https://walink.pk/pakistan-viral-video-whatsapp-group/","note":"Listing page; 9 entries, viral-video (leak) section."},
 {"url":"https://walink.pk/whatsapp-group-xxiv-girl/","note":"Listing page; 11 entries, XXIV girls section (adult-heavy)."},
 {"url":"https://walink.pk/1000-members-whatsapp-group-link/","note":"Listing page; 11 entries, 1000-members girls section."},
 {"url":"https://walink.pk/81-whatsapp-group-link/","note":"Listing page; 11 entries, '81' girls section (adult, 18+)."},
 {"url":"https://walink.pk/porn-whatsapp-group/","note":"ADULT-ONLY section — NOT fetched, do not mine for clean groups."},
 {"url":"https://walink.pk/sexy-whatsapp-group/","note":"ADULT-ONLY section — NOT fetched, do not mine for clean groups."},
 {"url":"https://walink.pk/xxx-whatsapp-group/","note":"ADULT-ONLY section — NOT fetched, do not mine for clean groups."},
]

# --- exclusions: 47 name/section-screen + 4 og:title-screen ---
NAME_EXC = {
 "Ky3CLUcinA4COQPF2FarW5":"name has kiss/lips emojis (Unlimited Members) — sexual signal",
 "BZq3FwPhj8pJRLWYj6Xzqp":"ambiguous '1000+ girls Members' listing on adult-heavy page — dropped on doubt",
 "KX3QzWH41roF4rDjmfJSy5":"name has kiss emojis (New Added Members) — sexual signal",
 "Ih6mBGvvajRClnPGBxxFuJ":"name has kiss/lips emojis (Pakistani Group Members) — sexual signal",
 "Gc1GEWvSVpFAaHUImaE9Ef":"section '18+ Sexy 81 WhatsApp Group Link'; 'viral videos' leak context",
 "L4x3nVbYXBC4R0jXauC0ny":"section '18+ Sexy 81 WhatsApp Group Link'",
 "E2DApzLs3yhIGFJCRMwrA5":"name contains 'Sexy'; section '18+ Sexy 81'",
 "JrXVKSGMbro2RWqj0r2Nvg":"leetspeak 'L0vely V3dio Call Girl'; section '18+ Sexy 81'",
 "DgmRGVE2JtfK5w9UIUAb5O":"name contains 'sexy' (Pakistani 81 desi sexy)",
 "GzNSmeFrq7e8aTsgCvj5rJ":"'leak videos' in name",
 "CggcOXweBr6D4DI2lfiYKz":"'Video Call Service' in desi-girl section — escort-service signal; dropped on doubt",
 "BdPMgvTHNn1Cj6EaAgAyPx":"name contains 'xxx' (Desi xxx video Link)",
 "LTFj6RIsNq4Im1FtdCxtcp":"name contains 'sexy' (Desi sexy girl)",
 "Ksye8DAjJGH10tsB5BWgeI":"'X Videos' — porn brand",
 "Km75ZNi08mZITpf4o8kPOw":"name has sexual emojis (water drops, bikini)",
 "HX8hBrNjTyb6D4CCdFfv0d":"name 'Smexy Vibes' — 'smexy' = sexy",
 "GYcWdzp0sKDDpXT7oBQ8o1":"name contains '18+' (18+ Girls Group)",
 "GdLaqY8l1k8BDS8eteV9fv":"name has kiss emojis (Desi Girls); dropped on doubt on adult-heavy source",
 "DBrKSi4LKgI62owtUqZqUQ":"'Sex chat' in name",
 "EJHuj5gvBHU3mKqhdZzyDY":"'only hot' in name; XXX section",
 "KBhPfTaXF4CAtRIPg9lcLh":"'xxx Group' in name",
 "GiPLeWbDwTEFCs1oX48Or1":"'Hot Girls Video' in name; Porn section",
 "H7Atc1QzkOy6VbDa2qHuaf":"name has hot-face emoji; Porn section",
 "LBaC2LeKFlxHxAMcX8BPOu":"'porn Group' in name",
 "JaB83j9kNZkBrJCDYpd6T1":"'Mall' is adult slang on this site (leaked-girls content)",
 "HmnTN5fQxEj0kCaiN0YSDb":"'Xxx chat with friends' in name",
 "JxVukoFEJf0KLcGls8gbPR":"name has kiss/lips emojis (Chill Video)",
 "Gk7J4ZTcpQMGk1Bmpv4Syy":"'sexy Groups' in name",
 "Jllsm6Lf8k8DjsOd8equa0":"name has kiss emojis (Single Girls Hub); dropped on doubt",
 "FIjlyks2AzKGCFoAyUsYMm":"'Pakistani Mall' — adult slang on this site",
 "FcOohzwlqYLArQVEJA4THs":"profanity/sexual name 'Fuck Single Girl'",
 "DHOPWAnOHrPKtFWsaudwKR":"'Single Girl Number' — sharing girls' phone numbers (personal info)",
 "CRysh2wOgDS6RqO0nN9lZq":"'School Family' in School Girls section — school-age targeting; dropped on doubt",
 "DgrtACZ7BDY4OWbFIleFUd":"'Dark Videos' — leaked/dark content signal",
 "K6HDRJdbZcW7Fl4ktL56xN":"explicit sexual name (milf, hot-face/kiss/tongue emojis)",
 "KFbdlkrDMo7GDIS3ThKEZG":"obfuscated 'RAPE_VIDEO' — non-consensual sexual content",
 "HapLr2GK26SILjgg3My77N":"'high school thots' — sexual slang plus school-age targeting",
 "FnQT3RRUpvuFQSnWJj424S":"'Hot girls free'; Rawalpindi Night Girl section",
 "D8c33p5nwODLSH8G5JUZud":"'Famous Girl Leak Data Available' — leaked content",
 "DPuHMhR9DAKFEivcGqckMu":"'New adult content' in name",
 "EFnjDr29JbiFZFUkJn7UAV":"'Free Video 18-' in name",
 "GpzUg0asCwQ49RjPbw4G67":"explicit 'DASI GRIL VIDEO' in Private section",
 "JJZV4XnsMzuHoSK8JtawpM":"'Sexy Girls Night' in name",
 "DuLSCwCcFDH3oczAT5xeZ8":"'Viral video group' in Private section — viral = leak context here; dropped on doubt",
 "Gnmsn5z0RvfEOmbuHu8zKn":"'MaaL' — adult slang on this site",
 "IGINFypyo4018T4WQx5wf4":"'Viral content' in Girls section — viral = leak context here; dropped on doubt",
 "LIHzjLrUR6xGYMUghErcZs":"'MiX data video group' — leaked data/videos signal",
}
OG_EXC = {
 "BQPSgynhRtL46JgW8bXnGQ":"LIVE but og:title 'Freedom Sexy group' — adult signal 'sexy'",
 "I4jvFgDg4j24YVVKWUfaVD":"LIVE but og:title 'HERA MANDI KI RANDIA' + hot-face emoji — explicit adult/prostitution reference",
 "HXhsIL7LkdKCNBl3pQSQeo":"LIVE but og:title 'No name' — placeholder name; live group does not match listing 'Silent Love' poetry group, identity unverifiable",
 "ChQ53L6gyJJChMeQDsTTcO":"LIVE but og:title 'Girls Leaked Videos' — leaked/adult content",
}
exclusions=[{"code":c,"reason":r} for c,r in NAME_EXC.items()]+[{"code":c,"reason":r} for c,r in OG_EXC.items()]
assert len(NAME_EXC)==47, len(NAME_EXC)
assert len(exclusions)==51, len(exclusions)

dead_codes=["JmcRrXGFgyiHqndAn7VHsW","G62CUkZciTfF6buEqvQMQR","GFTVdCpaXA53GD2E5zUWMv",
 "E8EHpwkECDL64vs0fN0R0Q","BfHXQMIhIYj0AT5SY4lL5p","KK5hCAezfhvCeoPIWPtFws",
 "IEVw3U2h2nk7b6Zl5oM3Fu","FmYjiEhElyY6X2bC5Vfix5","IeZiqR3jpEE7N160llnfET",
 "GFTTUzali7E6Ec1SBMh0mi","ChMoC5eTdOkDdLeyPjiIE0","IKv4AvhauPx1RkzQOwWXQ6"]
assert len(dead_codes)==12

json.dump(verified, open('team22-walink.json','w'), ensure_ascii=False, indent=2)
json.dump(pending, open('team22-walink-pending.json','w'), ensure_ascii=False, indent=2)
json.dump(leads, open('team22-walink-leads.json','w'), ensure_ascii=False, indent=2)
summary={
 "team":22,
 "slice":"walink.pk",
 "sources":["https://walink.pk/","https://walink.pk/category/whatsapp-group-links/",
  "https://walink.pk/whatsapp-group-link-pakistan/","https://walink.pk/girls-whatsapp-group/",
  "https://walink.pk/desi-girl-whatsapp-group/","https://walink.pk/pakistan-viral-video-whatsapp-group/",
  "https://walink.pk/whatsapp-group-xxiv-girl/","https://walink.pk/1000-members-whatsapp-group-link/",
  "https://walink.pk/81-whatsapp-group-link/"],
 "verified":0,
 "pending":3,
 "leads":12,
 "dead":12,
 "exclusions":exclusions,
 "resume":"SOURCE EXHAUSTED for clean groups — do not reassign walink.pk for clean mining. 131 unique codes found across homepage + 9 sub-pages; 65 already in the 108,364-code union; of the 66 fresh, 47 dropped on adult name/section screen and 19 verified — 12 dead (HTTP 200, empty og:title on 2 spaced attempts), 3 transport-pending (curl timeouts on 2nd attempt), 4 live but ALL excluded on og:title screen (adult/placeholder). 0 verified-clean. Clean sections (Drama, Poetry, Islamic, Study, Earning, Funny, Shopping, Movies) are fully already-known; only adult sections yield fresh codes.",
 "notes":("Fetch: direct curl to walink.pk times out (slow ~1.1MB homepage behind Cloudflare); Python urllib with 60s timeout works. "
  "Dedupe: .existing_codes.json (108,364) already contains all 72,742 groups.json invite codes, so union = 108,364. "
  "Verification control: 2 known-live groups.json codes returned non-empty og:title with the same browser UA, validating the live criterion; dead invites return HTTP 200 with empty og:title. "
  "WhatsApp throttled this VM IP mid-run (empty curl responses after ~10 requests, cleared after a 60s pause) and again on retry round 2 (3x curl rc 28 timeouts) — the 3 pending codes each have 1 completed empty-og:title attempt plus 1 transport failure. "
  "3 whatsapp.com/channel links seen on homepage were dropped (channels, not groups). Porn/sexy/xxx sub-pages deliberately not fetched (adult-only sections). "
  "No scam codes (B-Love/Forsage/etc.) surfaced among fresh candidates. Dead codes (12): "+", ".join(dead_codes)+".")
}
json.dump(summary, open('team22-walink-summary.json','w'), ensure_ascii=False, indent=2)
print("verified",len(verified),"pending",len(pending),"leads",len(leads),"dead",len(dead_codes),"exclusions",len(exclusions))
