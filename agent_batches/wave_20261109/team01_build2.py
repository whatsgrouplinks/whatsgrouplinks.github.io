#!/usr/bin/env python3
"""Team 01 v2 - assemble screened candidates from verified-live codes.
Manual review decisions (from linkado full descriptions + og:titles):
- DROP: dark-web/adult (BLwt...), resenha masculina 18+ (BT5l...), ganhe-dinheiro
  scam (BoN4...), no-sigilo 18+ (CDjq...), Prudence/hookup (FFWb...), boate 18+
  (FLZc...), CHUDAI/novinhos (HdkO...), flerte & curticao hookup (H0OQ...),
  amizade colorida FWB (HHgz...).
- KEEP: 23 groups below with hand-written English descriptions translated from
  each group's own published description.
"""
import json, os

WAVE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261109")

verify = []
for f in ["team01_verify.json", "team01_verify_shard0.json", "team01_verify_shard1.json",
          "team01_verify_shard2.json", "team01_verify_new0.json", "team01_verify_new1.json",
          "team01_verify_new2.json"]:
    p = os.path.join(WAVE, f)
    if os.path.exists(p):
        verify.extend(json.load(open(p)))
live = {r["code"]: r for r in verify if r["status"] == "live"}
print("live codes:", len(live))

DROP = {
    "BLwtFQt47paJqiQcZDN44W": "adult dark-web group, 18+ marked",
    "BT5lEoVolBhIgEd3H4gkjU": "adult men's chat, 18+ marked",
    "BoN4z5TkZPs9hdP9GqfiXM": "free-money scam pitch (register energy account, earn money)",
    "CDjqbJ54fThH9cAP5QrQs6": "secret 18+ hookup group",
    "FFWbQN9KnqnG2giN0k8MI6": "condom-brand hookup invite, 18+ marked",
    "FLZckue0Pq09Klt0zLIJQb": "18+ nightclub group",
    "HdkOweOdMT651roRg5iari": "explicit sexual content, 'novinhos' (young lads)",
    "H0OQ4GOOpiZ707nShR3Gk4": "flirting / hookup group (Flerte & Curticao)",
    "HHgzRYwXBQZ6skjjsWWCHR": "friends-with-benefits group (Amizade Colorida)",
}

# code -> (name [og:title], category, description)
KEEP = {
    "BFcuNjMw34T6nYVbwpGDL6": ("ᵇᵘᶻ ᶠⁱᵍᵘʳⁱⁿʰᵃˢ 👀", "Entertainment",
        "A sticker-sharing group for finding the perfect figurinha to spice up your chats."),
    "Cb14GCrwgdWEsiH59Ug4GN": ("Governador Celso Ramos/SC", "Community & Social",
        "A community group for residents of Governador Celso Ramos, Santa Catarina, focused on local development and well-being."),
    "CfBkVo6wlQVJGATsZiDuUf": ("ACHADINHOS DA ELIZA TUDO SOBRE SKINCARE 🩵🩵", "Buy Sell",
        "Skincare finds and recommendations from Eliza, with the best skincare tips and deals shared daily."),
    "DTVVPyhqv5G3jk73VlACST": ("⫷𝕸𝖆𝖓𝖎𝖈ô𝖒𝖎𝖔 ⫸", "Friendship",
        "A light-hearted chat group for meeting new people and talking about anything and everything."),
    "EJ4rhiXquQsLA5tAO5jYV5": ("Dica, Gostei e Comprei - SHOPEE", "Buy Sell",
        "Shopee deals group sharing discount coupons and product finds from Shopee."),
    "ENOtXQU6PPs6IJg1K8mPFA": ("👨\u200d❤️\u200d💋\u200d👨❤️ALÉM DOS HORIZONTES ❤️👩\u200d❤️\u200d👨", "Friendship",
        "A friendship group for good conversation, hanging out and having fun together."),
    "EkMVAm5oICO6nnTSnUHU2V": ("Atualizações Fs Play 🎬", "Entertainment",
        "Updates on movies, series and live channels from Fs Play, all entertainment in one place."),
    "F1cliKK3K2H4eCIaM8lvV6": ("👑 Rei da Promoção & Ofertas ⚡", "Buy Sell",
        "A Shopee deals group sharing sales, offers and discount finds for smart shoppers."),
    "FWVQCB51bd5L4LjtgWj3mv": ("Achei, Amei, Comprei! 😍🛍️🥰", "Buy Sell",
        "Promotions and finds from Shopee and Mercado Livre shared with the group."),
    "FxeebhbgRlOCVcVjTIeTik": ("⚽ Bolão Chutômetro ✅", "Sports",
        "A football betting pool group with easy predictions, a daily ranking and prizes for the best guessers."),
    "G6L2P41O16V3dswTrwZmLz": ("CUIDADO E BELEZA PESSOAL 💋💞", "Health",
        "A personal care and beauty group sharing tips on looking after yourself."),
    "HECinkAnjTBBsNdyJV3MUp": ("† SUBMUNDO 24 HORAS† 🖤✨", "Friendship",
        "A very lively 24-hour friendship group for chatting, gossip and making new friends like family."),
    "Hr02P966lXYJyCYm1qJyvQ": ("🥷 Elite da Resenha👑", "Friendship",
        "A chat group for hanging out and meeting new people — introduce yourself when you join."),
    "I5P1Xe7oYo09hwYQADXsJV": ("ACHADINHOS VEM NOVIDADES 🤩🥳", "Buy Sell",
        "A deals group for finding quality products at good prices, with new finds posted regularly."),
    "IFoHLtGzxCMKvY97huz7WZ": ("Grupo", "Friendship",
        "A friendship group for meeting new people and making friends."),
    "JXYaRhGiBp40czheYkrNc1": (">DEVIS/GEMERS<", "Gaming",
        "A gamers group to play and have fun together — introduce yourself with your name, age and city when you join."),
    "JeBfXDibWsqDsFMATE8UZB": ("Grupo figurinhas", "Entertainment",
        "A sticker group for sharing figurinhas and chatting."),
    "Juo6JJo7FWY2Jxi95QXAOL": ("Jogar conversa fora😝", "Friendship",
        "A casual chat group — come to play, come to make friends, prejudice not welcome."),
    "JyYbX3ZXjmYFnbKdApmz4W": ("🔥 𝔅𝔬𝔫𝔡𝔢 𝔡𝔞𝔰 𝔩𝔢𝔫𝔡𝔞𝔰🔥", "Friendship",
        "A friendship chat group — say hello and introduce yourself when you join."),
    "KhnoeUED0omBR01cN01eyu": ("Grupo de figurinhas", "Entertainment",
        "A sticker group for sharing figurinhas and hanging out."),
    "KjQgv5NXY0x9hLtiC1Gbjd": ("VITRINE KIDS", "Buy Sell",
        "Deals on kids' items from Shopee and Mercado Livre — clothes, shoes, diapers and more."),
    "L98xMkARl5FDZgWH6CUFc1": ("Amizades", "Friendship",
        "A new group for LGBT people to make friends, meet new people and chat."),
    "LORBUZYHt4e4D4yqMp4A5J": ("🛍️ promoçãos roupas femininas da shopee 💋", "Buy Sell",
        "Women's clothing deals and promotions from Shopee and Shein — grab your look before it is gone."),
}

candidates, screened_out = [], []
for code, r in sorted(live.items()):
    if code in DROP:
        screened_out.append({"code": code, "name": (r.get("title") or ""),
                             "reason": DROP[code]})
        continue
    if code not in KEEP:
        screened_out.append({"code": code, "name": (r.get("title") or ""),
                             "reason": "live but not in reviewed keep list — held for manual review"})
        continue
    name, cat, desc = KEEP[code]
    # sanity: og:title should match the kept name (modulo unicode normalisation)
    assert r.get("title"), f"no og:title for {code}"
    candidates.append({"name": name, "category": cat, "country": "BR",
                       "description": desc,
                       "invite": f"https://chat.whatsapp.com/{code}"})

# safety: no source names/links, no phone numbers in output
import re
for c in candidates:
    blob = c["name"] + " " + c["description"]
    assert "linkado" not in blob.lower() and "whatsappkanali" not in blob.lower(), c
    assert not re.search(r"\+\d[\d\s\-()]{9,}", blob), c
    assert c["category"] in ["Gaming", "Education", "Online Earning", "Community & Social",
                             "Business", "Friendship", "Finance", "Buy Sell", "Islamic",
                             "Entertainment", "Jobs", "Technology", "Funny", "Sports",
                             "Health", "News"], c

json.dump(candidates, open(os.path.join(WAVE, "team01-candidates.json"), "w"), indent=1, ensure_ascii=False)
json.dump(screened_out, open(os.path.join(WAVE, "team01_screened_out.json"), "w"), indent=1, ensure_ascii=False)
print("candidates:", len(candidates), "| screened out:", len(screened_out))
for c in candidates:
    print(" KEEP", c["name"][:60], "|", c["category"])
for s in screened_out:
    print(" DROP", s["code"], "|", s["reason"])
