#!/usr/bin/env python3
"""TEAM 01 — repair junk linkado names ('Entrar no Grupo') from grupo page titles.
For every candidate whose name is exactly 'Entrar no Grupo' (or empty) and whose
source is a linkado.app/grupo/<id> page, fetch the grupo page <title>
('Grupo de WhatsApp <NAME> - <CategoryPT>'), derive the real name + category,
and rewrite name/category/description in place in each candidate file.
"""
import json, re, html, os, sys
import requests
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
JUNK = {"Entrar no Grupo", "Join", "Join Group", "Join Now", "Entrar", ""}

CAT_PT = {"trabalho": "Jobs", "amizade": "Friendship", "namoro": "Friendship",
    "dinheiro": "Online Earning", "games": "Gaming", "jogos": "Gaming",
    "esportes": "Sports", "futebol": "Sports", "filmes": "Entertainment",
    "series": "Entertainment", "musica": "Entertainment", "música": "Entertainment",
    "memes": "Funny", "humor": "Funny", "tecnologia": "Technology",
    "educação": "Education", "educacao": "Education", "estudos": "Education",
    "notícias": "News", "noticias": "News", "saúde": "Health", "saude": "Health",
    "negócios": "Business", "negocios": "Business", "culinária": "Cooking",
    "culinaria": "Cooking", "receitas": "Cooking", "poesia": "Poetry",
    "viagem": "Travel", "turismo": "Travel", "criptomoedas": "Crypto",
    "finanças": "Finance", "financas": "Finance", "vendas": "Buy Sell",
    "compras": "Buy Sell", "religião": "Islamic", "religiao": "Islamic",
    "igreja": "Islamic", "evangelho": "Islamic", "bíblia": "Islamic"}

def clean_name(n):
    n = html.unescape(n or "")
    n = re.sub(r"<[^>]+>", "", n)
    n = re.sub(r"\s+", " ", n).strip(" -|—–·•\t:\"'“”")
    n = re.sub(r"^Grupo de WhatsApp\s+", "", n, flags=re.I)
    n = re.sub(r"\s*\|\s*(Linkado|GroupsInvite|Groupizo)$", "", n, flags=re.I)
    return n[:120].strip()

def fetch_title(gid):
    try:
        r = requests.get(f"https://linkado.app/grupo/{gid}", headers=UA, timeout=25)
        if r.status_code != 200:
            return None
        m = re.search(r"<title>(.*?)</title>", r.text, re.S | re.I)
        return html.unescape(m.group(1)).strip() if m else None
    except Exception:
        return None

def repair_file(path):
    try:
        d = json.load(open(path))
    except Exception as e:
        print(path, "ERR", e); return 0
    todo = []
    for code, rec in d.items():
        if rec.get("name", "").strip() in JUNK:
            m = re.search(r"linkado\.app/grupo/([0-9a-f]+)", rec.get("source", ""))
            if m:
                todo.append((code, m.group(1)))
    print(f"{os.path.basename(path)}: {len(todo)} junk names to repair", flush=True)
    fixed = 0
    def work(item):
        code, gid = item
        title = fetch_title(gid)
        if not title:
            return (code, None)
        # title: 'Grupo de WhatsApp <NAME> - <CAT>' (cat may contain ' & ')
        base = re.sub(r"\s*-\s*([A-Za-zÀ-ÿ &]+)$", "", title)
        catpt = ""
        cm = re.search(r"\s*-\s*([A-Za-zÀ-ÿ &]+)$", title)
        if cm: catpt = cm.group(1).strip().lower()
        name = clean_name(base)
        cat = CAT_PT.get(catpt, "Community & Social")
        if not name or name in JUNK:
            return (code, None)
        return (code, (name, cat))
    with ThreadPoolExecutor(max_workers=6) as ex:
        for code, res in ex.map(work, todo):
            if res:
                name, cat = res
                rec = d[code]
                rec["name"] = name
                rec["category"] = cat
                rec["description"] = f"Join {name}, an active WhatsApp group for {cat.lower()}. Connect with members, share updates and stay in touch."
                fixed += 1
    if fixed:
        tmp = path + ".tmp"
        json.dump(d, open(tmp, "w"), ensure_ascii=False)
        os.replace(tmp, path)
    print(f"{os.path.basename(path)}: fixed {fixed}/{len(todo)}", flush=True)
    return fixed

if __name__ == "__main__":
    total = 0
    for f in ["team01-leads-slice1-candidates.json", "team01-rescue-candidates.json",
              "team01-remine-candidates.json", "team01-remine0-candidates.json"]:
        total += repair_file(os.path.join(WAVE, f))
    print(f"REPAIR DONE: {total} names fixed")
