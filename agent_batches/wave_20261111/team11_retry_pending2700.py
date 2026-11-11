#!/usr/bin/env python3
"""TEAM 11 wave 20261111 — one retry pass over the 25 transport-failure pendings."""
import json, re, time, html, subprocess
from concurrent.futures import ThreadPoolExecutor

WD = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
ADULT = ["🔞", "🥵", "porn", "xxx", "sexo explícito", "sexo explicito",
         "putaria", "conteúdo adulto", "conteudo adulto", "nudes", "novinhas",
         "gostosas", "safada", "tesão", "tesao", "erótico", "erotico",
         "onlyfans", "pack de", "vazados", "vazadas", "amadores quentes",
         "sex chat", "acompanhantes", "garotas de programa", "sexo grátis",
         "sexo gratis", "xereca", "boquete", "siririca"]
SCAM = ["b-love", "blove", "b love", "forsage", "shey", "holiverse", "meta-whale",
        "meta whale", "airdrop", "paypal loader", "bitfinex",
        "counterfeit currency", "crypto-doubling", "carding",
        "dinheiro fácil", "dinheiro facil", "dobrar seu dinheiro",
        "lucro garantido", "investimento garantido", "ganhe dinheiro rápido",
        "ganhe dinheiro rapido", "multiplicar bitcoin", "multiplicar seu dinheiro",
        "falsificar", "clonar cartão", "clonar cartao", "roubar", "hackear whatsapp",
        "sinais vip", "banca garantida", "aposta garantida", "ganhar na loteria"]
NEG = ["proibido", "proibida", "proibidos", "proibidas", "sem ", "não ", "nao ",
       "nunca", "zero ", "nenhum", "nenhuma"]

def strip_negated(text):
    parts = re.split(r'(?<=[.!;])\s+', text)
    return " ".join(p for p in parts
                    if not (any(n in p.lower() for n in NEG) and any(a in p.lower() for a in ADULT)))

def fetch(url, timeout=25):
    try:
        r = subprocess.run(["curl", "-s", "-L", "-A", UA, "--max-time", str(timeout),
                            "-w", "\n%{http_code}", url],
                           capture_output=True, text=True, timeout=timeout + 10)
        body, _, code = r.stdout.rpartition("\n")
        st = int(code) if code.strip().isdigit() else None
        return (st, body) if st else (None, "")
    except Exception:
        return None, ""

def clean_desc(d):
    d = re.sub(r'^Grupo de WhatsApp [^,]+, na categoria [^\.]+\.\s*', '', d, flags=re.I)
    d = re.sub(r'linkado\.app|Linkado', '', d, flags=re.I)
    d = re.sub(r'https?://\S+|www\.\S+', '', d)
    d = re.sub(r'[\w.+-]+@[\w-]+\.[\w.]+', '', d)
    d = re.sub(r'\+?\d[\d\s().-]{7,}\d', '', d)
    return re.sub(r'\s+', ' ', d).strip()

def main():
    cands = {c["code"]: c for c in json.load(open(f"{WD}/team11_candidates2700.json"))["cands"]}
    pending = json.load(open(f"{WD}/team11-linkado-2700-pending.json"))
    verified = json.load(open(f"{WD}/team11-linkado-2700.json"))
    summary = json.load(open(f"{WD}/team11-linkado-2700-summary.json"))
    print(f"retrying {len(pending)} pendings", flush=True)

    def verify(p):
        c = cands[p["invite"].split("/")[-1]]
        time.sleep(0.6)
        for attempt in range(2):
            st, h = fetch(f"https://chat.whatsapp.com/{c['code']}")
            if st is None:
                if attempt == 0:
                    time.sleep(4)
                    continue
                return (c, "pending", "transport failure (no HTTP status) after retry pass")
            if st == 200:
                m = re.search(r'property="og:title"\s+content="([^"]*)"', h or "")
                og = html.unescape(m.group(1)).strip() if m else ""
                if og:
                    return (c, "live", og)
                if attempt == 0:
                    time.sleep(4)
                    continue
                return (c, "dead", "HTTP 200 but empty og:title after 2 spaced tries (retry pass)")
            return (c, "dead", f"HTTP {st} (retry pass)")
        return (c, "pending", "transport failure")

    results = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        for res in ex.map(verify, pending):
            results.append(res)
            print(res[0]["code"], res[1], res[2][:60], flush=True)

    new_pending, new_dead = [], 0
    for c, s, info in results:
        if s == "live":
            low = (c["title"] + " " + info).lower()
            if any(a in strip_negated(low) for a in ADULT):
                summary["exclusions"].append({"code": c["code"], "reason": "adult signals in WhatsApp og:title (retry pass): " + info[:100]})
                new_dead += 1
                continue
            if any(a in low for a in SCAM):
                summary["exclusions"].append({"code": c["code"], "reason": "scam signals in WhatsApp og:title (retry pass): " + info[:100]})
                new_dead += 1
                continue
            og = info.strip()
            name = c["name"] if (og.endswith("...") or og.endswith("…") or "�" in og or len(og) < 3) else re.sub(r'\s+', ' ', og).strip()[:120]
            d = clean_desc(c["desc"])
            if not d or len(d) < 15:
                d = f"A WhatsApp group for {name}. Join to chat, share updates and connect with members."
            if len(d) > 240:
                d = d[:237].rsplit(" ", 1)[0] + "..."
            verified.append({"name": name or "WhatsApp Group", "category": c["category"],
                             "country": "BR", "description": d,
                             "invite": f"https://chat.whatsapp.com/{c['code']}"})
        elif s == "pending":
            new_pending.append({"name": c["name"], "category": c["category"], "country": "BR",
                                "description": clean_desc(c["desc"])[:200],
                                "invite": f"https://chat.whatsapp.com/{c['code']}",
                                "reason": info})
        else:
            new_dead += 1

    summary["verified"] = len(verified)
    summary["pending"] = len(new_pending)
    summary["dead"] = summary["dead"] + new_dead
    summary["notes"] += (f" Retry pass on the 25 transport-failure pendings: "
                         f"{len(verified) - 57} went live, {new_dead} dead, {len(new_pending)} still pending.")
    json.dump(verified, open(f"{WD}/team11-linkado-2700.json", "w"), ensure_ascii=False, indent=1)
    json.dump(new_pending, open(f"{WD}/team11-linkado-2700-pending.json", "w"), ensure_ascii=False, indent=1)
    json.dump(summary, open(f"{WD}/team11-linkado-2700-summary.json", "w"), ensure_ascii=False, indent=1)
    # append retry outcomes to verify checkpoint
    with open(f"{WD}/team11_verify2700.ckpt.jsonl", "a") as f:
        for c, s, info in results:
            f.write(json.dumps({"code": c["code"], "status": s, "info": info, "retry_pass": True}, ensure_ascii=False) + "\n")
    print(f"RETRY DONE: verified now {len(verified)}, pending {len(new_pending)}, new dead {new_dead}", flush=True)

if __name__ == "__main__":
    main()
