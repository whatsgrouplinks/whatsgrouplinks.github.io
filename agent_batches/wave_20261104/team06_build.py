import json, os, re, time

BASE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261104")
v = json.load(open(os.path.join(BASE, "_t06_verify5.json")))
cands = json.load(open(os.path.join(BASE, "_t06_candidates.json")))
union = set(json.load(open(os.path.join(BASE, "_team06_dedupe_set.json"))))

def wretry(path, obj, tries=15):
    data = json.dumps(obj, ensure_ascii=False, indent=1)
    for a in range(tries):
        try:
            with open(path, "w") as f:
                f.write(data); f.flush(); os.fsync(f.fileno())
            back = json.load(open(path))
            assert len(back) == len(obj), (path, len(back), len(obj))
            print(path, "OK len", len(back), flush=True)
            return
        except Exception as e:
            print(path, "attempt", a, "FAIL", type(e).__name__, flush=True)
            time.sleep(3)
    raise RuntimeError("write failed: " + path)

# ---- content-rule drops ----
def drop_reason(code, name, title):
    n = (name + " " + title).lower()
    # scam / HYIP / ponzi
    for sig in ["forsage", "mmm global", "mavro", "double_money", "double money", "mt20.io", "mt20"]:
        if sig in n: return "scam-hyip"
    if "gmail" in n and "buyer" in n: return "scam-account-buying"
    if "edollor" in n and "invest" in n: return "scam-hyip"
    if re.search(r"\b\d{7,}\b", n): return "personal-info-phone"
    if "hashish" in n or "crystal" in n and "contact" in n: return "illegal-drugs"
    if "3 patt" in n or "teen patti" in n: return "gambling"
    if re.fullmatch(r"\s*хуйня\s*", title.lower()): return "porn-vulgar"
    if "hafiz siddiq teach" == title.lower(): return "personal-name-title"
    if "by areef malik" in title.lower(): return "personal-name-branded"
    return None

CAT_OVERRIDES = {
    "Ea8YVP4d5ZoFvXoylh5niy": "Finance",   # Future Dreams 2
    "IlgAY7RsdH77vB7cPHbEHO": "Finance",   # New & old trusted Earning site
    "K6RTvp4Jt60IDnaz1DFURw": "Finance",   # Online work
    "J7nVn3rDDAJ4BGfzR9vd52": "Finance",   # UAE1.ae
    "LlPl4UMSnSyBpzU0hm66Xl": "Business",  # Online earning group
    "LCOqGn8DVF97jnK39cTpvJ": "Crypto",    # Real134
    "CALbZbTEZgVK49SufavdDC": "Crypto",    # Market Capsule
    "B68ChOAk07GLuF3eNJtfRT": "Finance",   # SOCIAL MONEY MAKERS
    "GOH2srKBZwZD8SqbgF667b": "Finance",   # Earn and fun
    "FVqve86VOJcChEjkc00awp": "Crypto",    # Crypto Family
    "D1hoC4E3ZC73wwGyjSXlLn": "Gaming",    # LUDO PLAY & EARN
    "JJP94cTEVgU6O1bA9yaALA": "Finance",   # LOOTS FACTORY
    "LIujgkzbSZrGyJdYLyuyuT": "Buy-Sell",  # ONLINE SHOPPING DEALS
    "Ej6r8gARp9HD9veNsQvdKm": "Crypto",    # CRYPTO VETERANS GROUP
    "Im6s2yrfxxBA7ccORMKNLk": "Sports",    # Dream 11 Winnerz
    "EardTtbnUk9J5gKOomF87n": "Finance",   # Easiest Online Work
    "LDBP4GEdSFcAZo8wbvzSat": "Finance",   # UAE1.ae
    "JHAmEepUB939uSJS3ygtMu": "Finance",   # Pakistan zindabad
    "CsAOr4fjKKx4sXan0KhEof": "Finance",   # Loot earn and Enjoy
    "BQAqXPCP6xH1tCoIFiUSFB": "Finance",   # Ads views online earning
    "D54KjnMeNxC1Rr1iolRE2b": "Business",  # Urdu: start business with 75 rupees
    "F2YsV4xEohdFtvRHWS9mbs": "Finance",   # Online Loot and Earn Money
    "Fsc8eKpXUex1uYVWgZ1yTi": "Technology",# SmmGreata.com
    "IaRMU3pmqiLEEv0kaGOKj2": "Finance",   # Bonus Moment 09
    "FFWwQ3IKC5iAGzKRHO9g9h": "Crypto",    # 1 million downloads App (bitcoin earnings app)
    "KpXmuNo0Vmm9qHqKBwHCck": "Jobs",      # Part time wrk
    "I8pOJhIsxEzBtizAF2yh0k": "Crypto",    # USDT earning
    "BfZh6OYYO8kDV8kvmWxSGc": "Finance",   # Earn from Social Media
    "KlXBFdmro7uL7M8lJNH5aP": "Finance",   # Online patym money
    "DBAi1WFh8J6LqC36Vea3qx": "Finance",   # Network marketing
    "CvbBMQiCE0DLWwF78uJlvZ": "Finance",   # Dailyincomez Special
    "G2CnGp02sAN9qUPuXbYKK6": "Jobs",      # Online earning apps (job & course)
    "FfNakjGIZFyBLNl9fWs00O": "Finance",   # Let's earn
    "L7MoZ6UFQskBvACoYZyjlh": "Finance",   # World ads
    "CqYFVUyJYpi4xr3aw59v74": "Finance",   # Earn with Digital business
    "LEjOlqIkNOFJJSv219zrJR": "Finance",   # Ragp members
    "DywO0WkTZcg1mvBH0WZGN3": "Finance",   # Earning Group
    "KrtoTP5N0KALVlrfDwvndE": "Finance",   # Online Earning
    "H8KSn7eeaEfBy3POpzDqcI": "Finance",   # only erning loot
    "HwEbIU7FYeU9dZWUvVMLRY": "Finance",   # KYC compliance
    "LXoHAksW8MBFeXLJJpVfxg": "Jobs",      # Work from home
    "JVObDYpqFkx38z0qKuY81J": "Finance",   # Fast Earning Website
    "FZJXoBWwl5p1O1tOzzhNZT": "Finance",   # Online Earning with Proof
    "CG3vHCheJ6u4a2NMMlysDj": "Finance",   # Get money in 10mins
    "CpYO0GYfqkDGa4HgVtW2bH": "Finance",   # forex trading
    "LdZsbLWbGph2mDSD31MY7l": "Business",  # Bussines opporunity
    "IfZsTD5w03SJV9N1CK4bYj": "Finance",   # Invest and Earn
    "CRfpr0ZV2h2HvYEebp7qrG": "Finance",   # Online Earning Free
    "CS36M6wtMpsIT6OBqp31Ux": "Finance",   # Earn Daily with us
    "IlULCnQOEiQGPTm1aJds5i": "Finance",   # Earn money online
    "KmegkMQhOec0usDOpqbGbo": "Crypto",    # Earn Bitcoin ETH 100%
    "DoCTg3ktj1A4wMW1g8Gy2y": "Finance",   # ZONE
    "Ktz1GfngrVsCmdjIjMcPAf": "Finance",   # Online Earning
    "G6aAMkR95n8Jhul7Ipzb0W": "Finance",   # 100% without free earning
    "Ffc5qnaswiD0yXwhibablH": "Finance",   # ADX Loading
    "HGEZlvztyfg0OWC73WKQkc": "Finance",   # Online Earn money
    "D3wmgAqpbu6LZiU5cQDHvo": "Finance",   # Make Money Online
    "GCSw3sT8IkaCch91qJaoG6": "Finance",   # Trading & Digital Funds
    "DXZu5EdmoDT0L5mgKfTwPn": "Crypto",    # Online Earning Airdrops Free
    "GR2GgaoOg8THyisp2200Ue": "Finance",   # online earning without investment
    "Dej3R6PA7NCDLw2g7n4R2k": "Finance",   # ONLINE (Paytm Earning)
    "DpZVb7t0iceKN0u9qmxFRK": "Finance",   # Help each other succeed
    "H1km0vqkJKvHm0ny95fDPV": "Finance",   # PKR PLATFORM UPDATE
    "La88QYUAERFGfPiGyCtMtq": "Finance",   # Forex Trading Earnings
    "JZeHg0mTrMFKg1FjMiO1yC": "Technology",# ONLINE EARNING 2 (SMM)
    "CcWKAESGfeK1z3Ootql7bO": "Buy-Sell",  # DealsForAll.in
    "HWp2Mt2LobJ2geDaF7DipS": "Entertainment", # Hago
    "L2LqxUOWuLcBOaUklwEYHP": "Finance",   # Genuine Group
    "KCGPWuz5UIsFLEkFI3lQXZ": "Finance",   # Real Earning Pk
    "ESeZOp7Axie0Gxb21zcQiE": "Finance",   # MFX PRO TRADING
    "IOG77HHSdlMH9Rl8s9Ufir": "Finance",   # QORNEX Launching
    "Ewn9YyOgdrj7QfS04EXx9d": "Crypto",    # ETHEREUM EARNERS
    "LOAeJY4wBlU8YMZrXeAkYw": "Finance",   # Paytm Earning
    "HN0tmoRWkw26zL72LflmhU": "Finance",   # R100 Olivia
    "GWYGBw07ZUrFirdcD1bxsa": "Crypto",    # Free Bitcoin Earnings App
    "BsCMjX8uYXT8S23GhptdFO": "Finance",   # Online Hunter
    "KHmh3yHqj2oBoTCWmAhwA8": "Finance",   # Binomo Binnry trading
    "I2DWRRjiEWC7QVs977HaUi": "Finance",   # Online earning No Investm
    "EMcEj5rNk6pHXEuwPzvdP0": "Finance",   # How to earn daily 2k-3k
    "Hlg0TrRhtZ82SPP5cnyNth": "Technology",# Online earning apps (photo editing)
    "IrilBX8VpnV0xpzAdYnC22": "Finance",   # RICH GOLD
    "DbzHs5vilWnDih5BmuHAiZ": "Gaming",    # Online working (best earning game)
    "Hnw3l8aYt8O07i6Tuk6xdt": "Finance",   # Online Sailing Purchasing
}

DESC = {
    "Finance": [
        "A Pakistani online-earning community where members swap tips on apps, websites and daily income ideas to make money from home.",
        "WhatsApp group for online earners in Pakistan and India sharing trusted earning apps, task sites and payment-proof screenshots.",
        "Community focused on earning money online through freelancing tasks, referral programs and legit income apps.",
        "Members discuss work-from-home earning methods, new apps and payout experiences across Pakistan and India.",
        "An earning tips group where people share the latest online income apps, offers and daily loot deals.",
    ],
    "Crypto": [
        "Cryptocurrency WhatsApp group for traders and beginners tracking Bitcoin, Ethereum and USDT price moves and market news.",
        "Crypto trading community sharing signals, coin updates and market analysis for Pakistani and Indian crypto enthusiasts.",
        "A WhatsApp chat for crypto investors discussing Bitcoin, altcoins and airdrop opportunities with daily market updates.",
        "Members follow crypto earning strategies, mining sites and exchange news in this active cryptocurrency group.",
    ],
    "Gaming": [
        "Play-and-earn gaming group where members join Ludo matches and other games to win real cash rewards.",
        "Gaming chat for players competing in earning games and sharing tips to boost winnings.",
    ],
    "Sports": [
        "Fantasy sports group for Dream11 fans sharing team predictions, player picks and contest tips.",
    ],
    "Buy-Sell": [
        "Shopping deals group sharing online discounts, promo codes and bargain finds for buyers in Pakistan and India.",
    ],
    "Technology": [
        "Tech services group covering SMM panels, social media growth tools and digital marketing tips.",
        "A digital services community discussing photo editing, online tools and social media work.",
    ],
    "Jobs": [
        "Work-opportunity group posting part-time, remote and work-from-home openings for job seekers in Pakistan.",
        "Freelancer community sharing gigs, client leads and online work opportunities.",
    ],
    "Business": [
        "Small-business WhatsApp group for entrepreneurs discussing low-cost business ideas and online selling.",
        "Business opportunity chat where members explore online ventures and investment-free earning plans.",
    ],
    "Entertainment": [
        "Fun social group around the Hago gaming app with casual chat and play-along sessions.",
    ],
}

COUNTRY = {"earning": "PK", "dubai": "AE", "crypto": "International"}

items, seen, porn_drop, scam_drop = [], set(), 0, 0
di = {k: 0 for k in DESC}
for code in sorted(v.keys()):
    r = v[code]
    if r["status"] != "live": continue
    if code in seen or code in union: continue
    name = (cands[code]["name"] or "").strip()
    title = r["title"].strip()
    real_name = title if title else name
    reason = drop_reason(code, name, title)
    if reason == "porn-vulgar":
        porn_drop += 1; continue
    if reason:
        scam_drop += 1; continue
    if not real_name: continue
    # never a URL / source boilerplate as name
    if "http" in real_name or "grouplinksforyou" in real_name.lower():
        scam_drop += 1; continue
    cat = CAT_OVERRIDES.get(code, "Finance")
    page = cands[code]["page"]
    country = COUNTRY.get(page, "International")
    pool = DESC.get(cat, DESC["Finance"])
    desc = pool[di[cat] % len(pool)]; di[cat] += 1
    seen.add(code)
    items.append({
        "name": real_name,
        "category": cat,
        "country": country,
        "description": desc,
        "invite": "https://chat.whatsapp.com/" + code,
        "image": "",
    })

wretry(os.path.join(BASE, "team06-grouplinksforyou.json"), items)
wretry(os.path.join(BASE, "team06-unverified-pending.json"), [])
leads = [
    {"domain": "grouplinksforyou.com",
     "url": "https://www.grouplinksforyou.com/ (category archive / Business & Finance pages)",
     "why": "Team06 scraped only the Cryptocurrency, Online Earning and Dubai pages of grouplinksforyou.com. The site publishes other money-vein pages (Business, Forex, Trading listsicles) not yet scraped; the crypto page's 44 fresh codes ALL died during this wave (0/44 live), so re-crawl that page next wave. 77 /invite/ channel codes and telegram-button groups were skipped per brief (channels excluded); name-only items were not banked."},
]
wretry(os.path.join(BASE, "team06-leads.json"), leads)
print("VERIFIED:", len(items), "PORN_DROP:", porn_drop, "SCAM_DROP:", scam_drop, flush=True)
