import json, os
W = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")
cands = json.load(open(f"{W}/team05-candidates.json"))
ver = json.load(open(f"{W}/team05-verify.json"))

DESC = {
 "News": "Join this {n} WhatsApp group for the latest news updates and headlines shared daily with members.",
 "Jobs": "Join this {n} WhatsApp group for daily job updates, new vacancies and employment opportunities shared with members.",
 "Finance": "Join this {n} WhatsApp group to discuss finance, investments and market updates with fellow members.",
 "Buy Sell": "Join this {n} WhatsApp group to buy, sell and trade with members and find the best deals.",
 "Online Earning": "Join this {n} WhatsApp group to learn online earning ideas and share ways to earn money online.",
 "Technology": "Join this {n} WhatsApp group for technology updates, tips and services shared with members.",
 "Community & Social": "Join this {n} WhatsApp group to connect with members, share updates and chat with the community.",
}
# (code -> (category, country, name_override))
FIX = {
 "Ep5WZm4GMsU1T9Hhui4u7f": ("Buy Sell", "KE", None),
 "LKrinN0RQBe6ivFweWBPDT": ("Finance", "IN", None),
 "DUqvcXwvbVZHqRYnSVtq6N": ("Jobs", "IN", None),
 "Dgc4vbNqAkBIiG9Ex4k3RC": ("Jobs", "IN", None),
 "GNzlxImcvOnHbnVCm2TXJy": ("Online Earning", "IN", None),
 "Fy32ZXBYlgm54jdp0kRqVW": ("Community & Social", "IN", None),
 "H3gLZcjlcZaD6NEAGXC1cC": ("Jobs", "AU", None),
 "IpYZtwi1xzb0AvZ7lhZ5gn": ("Technology", "IN", None),
 "CtlGpaOz8zgEXL7jzi9anl": ("Jobs", "AE", "Page Immigration Cruise Jobs & Overseas Employment"),
}
for c in cands:
    code = c["invite"].rsplit("/", 1)[-1]
    if code in FIX:
        cat, country, name = FIX[code]
        c["category"] = cat; c["country"] = country
        if name: c["name"] = name
    # restore full verified og:title as name where it was truncated mid-word (except the one renamed above)
    if code not in FIX or FIX[code][2] is None:
        full = ver.get(code, {}).get("title", "").strip()
        if full and (len(c["name"]) < len(full)):
            c["name"] = full
    n = c["name"]
    c["description"] = DESC.get(c["category"], DESC["Community & Social"]).format(n=n)
json.dump(cands, open(f"{W}/team05-candidates.json", "w"), indent=1, ensure_ascii=False)
for c in cands:
    print(c["category"], c["country"], "|", c["name"][:70], "|", c["description"][:90])
print("total:", len(cands))
