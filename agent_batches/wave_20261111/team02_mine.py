import json, re, time, sys, os, html, unicodedata
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

WAVE="/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111/"
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
CATMAP={
 "Trabalho":"Jobs","Educação":"Education","Educacao":"Education","Entretenimento":"Entertainment",
 "Religião":"Community & Social","Religiao":"Community & Social","Islam":"Islamic","Islã":"Islamic",
 "Notícias":"News","Noticias":"News","Esportes":"Sports","Tecnologia":"Technology","Saúde":"Health","Saude":"Health",
 "Negócios":"Business","Negocios":"Business","Jogos":"Gaming","Amizade":"Friendship","Comunidade":"Community & Social",
 "Ganhar Dinheiro":"Online Earning","Dinheiro":"Online Earning","Criptomoedas":"Crypto","Culinária":"Cooking","Culinaria":"Cooking",
 "Poesia":"Poetry","Viagem":"Travel","Bolsas de Estudo":"Scholarship","Freelance":"Freelance","Imóveis":"Real Estate","Imoveis":"Real Estate",
 "Compra e Venda":"Buy Sell","Finanças":"Finance","Financas":"Finance","Humor":"Funny","Filmes":"Entertainment","Música":"Entertainment","Musica":"Entertainment",
 "Futebol":"Sports","Namoro":"Friendship","Família":"Community & Social","Familia":"Community & Social",
}
def fetch(url, timeout=30):
    req=urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode('utf-8','ignore')
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, ""

def extract(page_html, url):
    # title
    m=re.search(r'<title>(.*?)</title>', page_html, re.S|re.I)
    title=html.unescape(m.group(1)).strip() if m else ""
    name=title
    cat_raw=""
    if name.startswith("Grupo de WhatsApp "):
        name=name[len("Grupo de WhatsApp "):]
    if " - " in name:
        name, cat_raw = name.rsplit(" - ",1)
    name=name.strip()
    d=re.search(r'property="og:description"\s+content="([^"]*)"', page_html)
    desc=html.unescape(d.group(1)).strip() if d else ""
    # also unescape \" sequences in embedded JSON variant
    desc=desc.replace('\\"','"')
    codes=re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{10,})', page_html)
    codes=list(dict.fromkeys(codes))
    return {"url":url,"name":name,"cat_raw":cat_raw,"desc":desc,"codes":codes,"title":title}

if __name__=="__main__":
    urls=json.load(open(WAVE+"leads_slice2.json"))
    start=int(sys.argv[1]) if len(sys.argv)>1 else 0
    end=int(sys.argv[2]) if len(sys.argv)>2 else len(urls)
    out_file=WAVE+"team02-extracted.jsonl"
    done=set()
    if os.path.exists(out_file):
        with open(out_file) as f:
            for line in f:
                try: done.add(json.loads(line)["url"])
                except: pass
    batch=urls[start:end]
    todo=[u for u in batch if u not in done]
    print(f"total slice {len(urls)} range {start}-{end} todo {len(todo)} already {len(done)}", flush=True)
    def work(u):
        st, h = fetch(u)
        time.sleep(0.6)
        if st!=200 or not h:
            return {"url":u,"error":f"http{st}"}
        return extract(h,u)
    t0=time.time()
    with open(out_file,"a") as f, ThreadPoolExecutor(max_workers=6) as ex:
        for i,rec in enumerate(ex.map(work, todo)):
            f.write(json.dumps(rec, ensure_ascii=False)+"\n"); f.flush()
            if (i+1)%100==0:
                print(f"{i+1}/{len(todo)} elapsed {time.time()-t0:.0f}s", flush=True)
    print(f"DONE elapsed {time.time()-t0:.0f}s", flush=True)
