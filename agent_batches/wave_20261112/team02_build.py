import json, re, time, sys, os, html, subprocess, unicodedata
from concurrent.futures import ThreadPoolExecutor

WAVE="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112/"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
CATMAP={
 "Amizade":"Friendship","Namoro":"Friendship","Trabalho":"Jobs","Vagas":"Jobs","Empregos":"Jobs",
 "Tecnologia":"Technology","Games":"Gaming","RPG":"Gaming","Free Fire":"Gaming",
 "Comprar e venda":"Buy Sell","Vendas":"Buy Sell","Compras":"Buy Sell",
 "Esportes":"Sports","Futebol":"Sports","Educação":"Education","Estudos":"Education",
 "Musica":"Entertainment","Música":"Entertainment","Figurinhas":"Entertainment","Filmes":"Entertainment",
 "Séries":"Entertainment","Animes":"Entertainment","Entretenimento":"Entertainment","Humor":"Funny",
 "Links":"Community & Social","Status":"Community & Social","Moda e beleza":"Community & Social",
 "LGBT":"Community & Social","Família":"Community & Social","Religião":"Community & Social",
 "Animais":"Community & Social","Política":"News","Notícias":"News",
 "Saúde":"Health","Negócios":"Business","Ganhar Dinheiro":"Online Earning","Dinheiro":"Online Earning",
 "Criptomoedas":"Crypto","Culinária":"Cooking","Poesia":"Poetry","Viagem":"Travel",
 "Bolsas de Estudo":"Scholarship","Freelance":"Freelance","Imóveis":"Real Estate",
 "Finanças":"Finance","Islam":"Islamic","Islã":"Islamic",
}
def clean_name(n):
    n=html.unescape(n or "")
    n=re.sub(r"<3", " ", n)
    out=[]
    for ch in n:
        if unicodedata.category(ch).startswith("So") or unicodedata.category(ch)=="Sk":
            out.append(" ")
        elif ch in "❤💕": out.append(" ")
        else: out.append(ch)
    n="".join(out)
    n=re.sub(r"[^\w\s&'’().,!?/-]", " ", n, flags=re.UNICODE)
    n=re.sub(r"\s+", " ", n).strip(" -.,/")
    return n[:120]
def _norm(t):
    t=html.unescape(t or "")
    t=unicodedata.normalize("NFKD", t)
    t="".join(c for c in t if not unicodedata.combining(c))
    return t.lower()
# prohibition clauses: remove spans that forbid porn/xxx/sex before screening
PROHIB_CLAUSES=[
 r"(proibid[oa]s?|nao\s+(e\s+)?permitid[oa]|nao\s+pode|nao\s+postar|nao\s+enviar|nao\s+mandar)[^,.;!?\n]{0,80}?(porn|putaria|xxx|sexo|hentai|imagens?\s+improprias)",
 r"sem\s+[^,.;!?\n]{0,40}?(porn|putaria|xxx|sexo|hentai)",
 r"(nada|nem|zero)\s+de\s+(porn|putaria|xxx|sexo)",
 r"menos\s+(porn|putaria|xxx|sexo)",
 r"[\U0001F6AB\u274C\u26D4]\s*(porn|putaria|xxx|sexo|links?\s+de\s+grupo)?",
 r"🚫[^,.;!?\n]{0,30}?(porn|putaria|xxx)?",
]
BLOCK_PATTERNS=[
 (r"\bxxx\b","hard porn xxx"),(r"porn", "hard porn"),(r"putaria","hard porn"),
 (r"novinh","sexualised minors-adjacent"),(r"loli","lolicon/minors sexual content"),
 (r"vazad[oa]","leaked porn content"),(r"conteudo adulto","adult content"),
 (r"\bnudes?\b","nudes"),(r"pelad[oa]","nude content"),(r"safad[oa]","sexual content"),
 (r"sexo\s+explicito","explicit sex"),
 (r"b-?love","crypto-airdrop scam B-Love"),(r"forsage","crypto-airdrop scam Forsage"),
 (r"sheyi","crypto-airdrop scam SHEYI"),(r"holiverse","crypto-airdrop scam HOLIVERSE"),
 (r"meta[\s-]?whale","crypto-airdrop scam meta-whale"),(r"\bairdrop\b","crypto airdrop"),
 (r"apost[ao]s?","betting scam"),(r"cassino","betting scam"),(r"casino","betting scam"),
 (r"tigrinho","betting scam"),(r"aviator","betting scam"),(r"bet365","betting scam"),
 (r"blazer\.com","betting scam"),
]
PHONE_RE=re.compile(r"(\+?\d[\d\s().-]{7,}\d)")
EMAIL_RE=re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
def screen(name, desc):
    scan=_norm(f"{name} {desc}")
    for pat in PROHIB_CLAUSES:
        scan=re.sub(pat, " ", scan, flags=re.I)
    for pat, reason in BLOCK_PATTERNS:
        if re.search(pat, scan, re.I):
            return reason
    raw=f"{name} {desc}"
    if EMAIL_RE.search(raw): return "personal info: email in text"
    m = PHONE_RE.search(name)
    if m and len(re.sub(r"\D","",m.group(1)))>=9: return "personal info: phone-like digits in name"
    return None
def wa_check(code):
    # returns (live_bool, og_title, transport_fail_bool)
    for attempt in (1,2):
        try:
            p=subprocess.run(["curl","-s","-A",UA,"--max-time","45",
                              f"https://chat.whatsapp.com/{code}"],
                             capture_output=True, timeout=55)
            h=p.stdout.decode('utf-8','ignore')
            if p.returncode!=0 or not h:
                time.sleep(5); continue
            m=re.search(r'property="og:title"\s+content="([^"]*)"', h)
            og=(m.group(1).strip() if m else "")
            if og: return True, og, False
            time.sleep(5)
        except Exception:
            time.sleep(5); continue
    # after retries: if we never got a page at all -> transport fail handled by caller via flag
    return False, "", False
def wa_check_traced(code):
    got_page=False
    for attempt in (1,2):
        try:
            p=subprocess.run(["curl","-s","-A",UA,"--max-time","45",
                              f"https://chat.whatsapp.com/{code}"],
                             capture_output=True, timeout=55)
            h=p.stdout.decode('utf-8','ignore')
            if p.returncode==0 and h:
                got_page=True
                m=re.search(r'property="og:title"\s+content="([^"]*)"', h)
                og=(m.group(1).strip() if m else "")
                if og: return ("live", og)
                time.sleep(5)
            else:
                time.sleep(5)
        except Exception:
            time.sleep(5)
    return ("pending" if not got_page else "dead", "")
if __name__=="__main__":
    existing=set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json")))
    slice_urls=json.load(open(WAVE+"leads_slice2.json"))
    recs=[]
    if os.path.exists(WAVE+"team02-extracted.jsonl"):
        with open(WAVE+"team02-extracted.jsonl") as f:
            for line in f:
                try: recs.append(json.loads(line))
                except: pass
    ok=[r for r in recs if 'error' not in r]
    mined_urls={r["url"] for r in ok}
    fetch_fail_urls=[r["url"] for r in recs if 'error' in r]
    # candidates: dedupe within slice (first wins), dedupe vs existing
    seen=set(); cands=[]; dup_existing=0; dup_within=0; no_code=0; exclusions=[]
    for r in ok:
        codes=r.get("codes") or []
        if not codes: no_code+=1; continue
        for code in codes:
            if code in existing: dup_existing+=1; continue
            if code in seen: dup_within+=1; continue
            seen.add(code)
            name=clean_name(r.get("name",""))
            if not name:
                exclusions.append({"code":code,"reason":"empty name after cleaning"}); continue
            cat=CATMAP.get((r.get("cat_raw") or "").strip(), "Community & Social")
            desc_src=r.get("desc") or ""
            reason=screen(name, desc_src)
            if reason:
                exclusions.append({"code":code,"reason":reason}); continue
            desc=f"Join the '{name}' WhatsApp group for {cat} — chat with members, share updates and connect."
            cands.append({"name":name,"category":cat,"country":"BR","description":desc[:200],
                          "invite":f"https://chat.whatsapp.com/{code}","_code":code})
    print(f"extracted {len(recs)} ok {len(ok)} fetch_fail {len(fetch_fail_urls)} no_code {no_code}", flush=True)
    print(f"cands {len(cands)} dup_existing {dup_existing} dup_within {dup_within} exclusions {len(exclusions)}", flush=True)
    _lim=int(sys.argv[1]) if len(sys.argv)>1 else None
    if _lim: cands=cands[:_lim]
    _lim=int(sys.argv[1]) if len(sys.argv)>1 else None
    if _lim: cands=cands[:_lim]
    # incremental verify state
    STATE_FILE=WAVE+"team02-verify-state.json"
    state={}
    if os.path.exists(STATE_FILE):
        try: state=json.load(open(STATE_FILE))
        except: state={}
    def save_state():
        json.dump(state, open(STATE_FILE,"w"), ensure_ascii=False)
    verified=[]; pending=[]; dead=0
    # reuse prior verdicts; pending codes get re-checked
    to_check=[]
    for c in cands:
        st=state.get(c["_code"])
        if st and st.get("status")=="live":
            cc=dict(c); cc.pop("_code"); verified.append(cc)
        elif st and st.get("status")=="dead":
            dead+=1
        else:
            to_check.append(c)
    print(f"reuse live {len(verified)} dead {dead} to_check {len(to_check)}", flush=True)
    # verify slow, 6 workers, >=0.5s delay per worker between requests
    def work(c):
        st, og = wa_check_traced(c["_code"])
        time.sleep(0.6)
        return c, st, og
    t0=time.time(); n=0
    with ThreadPoolExecutor(max_workers=6) as ex:
        for c, st, og in ex.map(work, to_check):
            n+=1
            state[c["_code"]]={"status":st, "og":og}
            if st=="live":
                cc=dict(c); cc.pop("_code"); verified.append(cc)
            elif st=="pending":
                cc=dict(c); cc.pop("_code"); cc["reason"]="transport failure: no WhatsApp page after retries"
                pending.append(cc)
            else:
                dead+=1
            if n%50==0:
                save_state()
                print(f"verified {n}/{len(to_check)} live {len(verified)} pending {len(pending)} dead {dead} elapsed {time.time()-t0:.0f}s", flush=True)
    save_state()
    for v in verified: v.pop("_og_title", None)
    # outputs for this snapshot
    json.dump([{k:v for k,v in x.items()} for x in verified], open(WAVE+"team02-leads-slice2.json","w"), ensure_ascii=False, indent=1)
    json.dump(pending, open(WAVE+"team02-leads-slice2-pending.json","w"), ensure_ascii=False, indent=1)
    remaining=[u for u in slice_urls if u not in mined_urls]
    json.dump(remaining, open(WAVE+"team02-leads-slice2-leads.json","w"), ensure_ascii=False, indent=1)
    summary={"team":"02","slice":"leads_slice2","sources":["linkado.app grupo pages"],
      "verified":len(verified),"pending":len(pending),"leads":len(remaining),"dead":dead,
      "dup_existing":dup_existing,"dup_within":dup_within,"no_code_listings":no_code,
      "fetch_fail_listings":len(fetch_fail_urls),
      "exclusions":exclusions,
      "resume":f"mined {len(mined_urls)}/{len(slice_urls)} listing pages; next unmined listing index in leads_slice2.json = first URL in team02-leads-slice2-leads.json; extraction checkpoint team02-extracted.jsonl",
      "notes":"WhatsApp live-check diagnostic: curl returned HTTP 200 + EMPTY og:title for every code tested, including 3 provably-bogus control codes (AAAAAAAAAAAAAAAAAAAAAA etc.), desktop/mobile/facebookexternalhit UAs and full browser headers. The og:title rule therefore cannot discriminate live vs dead from this VM; empty-og codes were counted DEAD per the deterministic task rule and none banked as live. Recommend parent re-check banked candidates via a live-browser route before any deploy. Miner still running in background (team02_mine2.py, 12 workers) when this snapshot was built."}
    json.dump(summary, open(WAVE+"team02-leads-slice2-summary.json","w"), ensure_ascii=False, indent=1)
    print(f"BUILD DONE verified {len(verified)} pending {len(pending)} leads {len(remaining)} dead {dead} elapsed {time.time()-t0:.0f}s", flush=True)
