import json, re, html, unicodedata
W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/"
names = json.load(open(W+"team22_fresh_names.json"))
verify = json.load(open(W+"team22_verify_raw.json"))
retry = json.load(open(W+"team22_retry_raw.json")) if __import__("os").path.exists(W+"team22_retry_raw.json") else []
extra = json.load(open(W+"team22_extra_verify.json")) if __import__("os").path.exists(W+"team22_extra_verify.json") else []

# listing names (cleaned) per code
LIST_NAME = {}
for code, v in names.items():
    ctx = v["name_ctx"]
    # 77links: "NAME: description" -> NAME
    if v["source"] == "77links-earning":
        nm = ctx.split(":")[0]
    else:
        nm = re.sub(r'\s*[–-]\s*(Join|Link)\s*$', '', ctx).strip()
    # strip leading emoji/symbols/punct
    nm = re.sub(r'^[\W_]+', '', nm)
    nm = re.sub(r'\s+', ' ', nm).strip()
    LIST_NAME[code] = nm
LIST_NAME["CindfGo478i2qz49wyN4vB"] = "Real Online Earning No Scam"
LIST_NAME["HDXdN6CBXEkCGldXqtfEa7"] = "Binance Big Signals"
LIST_NAME["Ge1yF51cHAMEU2ayEw2JRR"] = "Best Buy"
LIST_NAME["FGCjBbFnDm655h3aBIhpF9"] = "Investors Alliance"
LIST_NAME["DZs2rQmbQ3BKJgIXtR6vms"] = "The Golden Insiders"
# extra singles
LIST_NAME["IGhtsGtrH3n3k5TS0Tn2PQ"] = "Market Makers Method"
LIST_NAME["EkeiobkWygVIVJP9DmrB58"] = "Forex Trading Free Signals Group"

CAT = {
 "DZs2rQmbQ3BKJgIXtR6vms": "Crypto",
 "BCCIm1cdDbvK4meBs28szr": "Crypto",
 "Bte0626nuW6FT5USahHEiq": "Crypto",
 "CindfGo478i2qz49wyN4vB": "Online Earning",
 "GysPbrwOiWwKl6VBUo7Dv1": "Finance",
 "Ge1yF51cHAMEU2ayEw2JRR": "Finance",
 "ETvrOZzIGzC7Yb5UQUSKt2": "Crypto",
 "ElCwvJf7ZYh9RLba4FAfza": "Crypto",
 "HDXdN6CBXEkCGldXqtfEa7": "Crypto",
 "FGCjBbFnDm655h3aBIhpF9": "Finance",
 "GqlxZvws9rpAsnYU80NpXC": "Finance",
 "Ck0RDMrmvzxInWvuDQhNPT": "Crypto",
 "BcoHLF6PNplFc4FcPR0tAD": "Crypto",
 "HpUaQS0mGwDLnRMqOeMUsd": "Crypto",
 "Hftij0Rle5xFM6cL50ZroN": "Freelance",
 "IGhtsGtrH3n3k5TS0Tn2PQ": "Finance",
 "EkeiobkWygVIVJP9DmrB58": "Finance",
}
COUNTRY = {
 "DQ7C9UtpZaPKuDASHrponN": "PK", "DdYCZULjuRkG6zBaz3zJ4x": "PK",
 "E9CQetNpiqA92Yg5uBTxvt": "PK", "J0s6XD3iM8tHnRWyRlFasR": "PK",
 "GhH296psnSzFo5KyOtU8jQ": "PK", "L7MNRquboz38tgZG5qXG7j": "PK",
 "L8lS7DjrCr9627LLIInvsl": "PK", "H4bmcZ8TJvy3n8CAWAGfrf": "PK",
 "I1oNbYPzG4bHgMZD7prhuy": "PK",
 "ETHNO7O5wenCYLkx4N691T": "IN", "JpwF54YsnCY8H60gsZ4pBm": "IN",
 "JmZHaWEZ8llAEV4AWfkmn6": "IN", "Ge1yF51cHAMEU2ayEw2JRR": "IN",
}

def live_title(code):
    for src in (verify, retry, extra):
        for r in src:
            if r["code"] == code and r["status"] == 200 and r["title"] and r["title"] not in ("WhatsApp Group", "Join this group on WhatsApp"):
                return html.unescape(r["title"]).strip()
    return ""

verified, pending = [], []
allres = {r["code"]: r for r in verify}
for r in retry: allres.setdefault(r["code"], r)
for r in extra: allres[r["code"]] = r

for code, r in allres.items():
    t = live_title(code)
    if t:
        cat = CAT.get(code, "Online Earning")
        country = COUNTRY.get(code, "International")
        name = t
        # og:title sometimes has different name than listing; prefer og:title (real group name)
        desc = f"Join {name}, a WhatsApp group listed under {cat}. Connect with members to discuss {cat.lower()} topics, share updates and learn together."
        verified.append({"name": name, "category": cat, "country": country, "description": desc,
                         "invite": f"https://chat.whatsapp.com/{code}", "image": ""})
    elif r["status"] == 0:
        # transport error only -> pending
        cat = CAT.get(code, "Online Earning")
        country = COUNTRY.get(code, "International")
        name = LIST_NAME.get(code, "Online Earning Group")
        desc = f"Join {name}, a WhatsApp group listed under {cat}. Connect with members to discuss {cat.lower()} topics, share updates and learn together."
        pending.append({"name": name, "category": cat, "country": country, "description": desc,
                        "invite": f"https://chat.whatsapp.com/{code}", "image": "", "reason": "transport"})

verified.sort(key=lambda x: x["invite"])
pending.sort(key=lambda x: x["invite"])
json.dump(verified, open(W+"team22-listicles-crypto-earning.json","w"), indent=1, ensure_ascii=False)
json.dump(pending, open(W+"team22-listicles-crypto-earning-pending.json","w"), indent=1, ensure_ascii=False)
print("verified:", len(verified))
for v in verified: print(" ", v["name"], "|", v["category"], "|", v["country"], "|", v["invite"])
print("pending:", len(pending))
for v in pending: print(" ", v["name"], "|", v["invite"])
