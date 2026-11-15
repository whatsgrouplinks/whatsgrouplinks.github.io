#!/usr/bin/env python3
"""team02 — linkado grupo sitemap indices 6000-8499 (wave_20261114).
Fetches grupo pages, extracts invite codes, dedupes vs union + in-team,
verifies live via ONE shared requests.Session on chat.whatsapp.com,
screens live og:title, banks candidates. Checkpoints after each chunk.
"""
import json, re, time, html, unicodedata, os, sys, signal
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

class VerifyTimeout(Exception):
    pass

def _alarm_handler(signum, frame):
    raise VerifyTimeout()

signal.signal(signal.SIGALRM, _alarm_handler)
ATTEMPT_LOG = None  # set in main()

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261114'
SITEMAP = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261110/linkado_sitemap.xml'
UNION = '/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json'
START, END = 6000, 8500  # END exclusive
CHUNK = 250
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'}

CANON = ["Education","Entertainment","Sports","Funny","Community & Social","Finance","Buy Sell",
         "Islamic","Health","News","Jobs","Technology","Gaming","Business","Cooking","Crypto",
         "Poetry","Real Estate","Travel","Scholarship","Freelance","Earning"]

DIRCAT = {
 'educacao':'Education','entretenimento':'Entertainment','esportes':'Sports','humor':'Funny',
 'comunidade':'Community & Social','amizade':'Community & Social','namoro':'Community & Social',
 'dinheiro':'Finance','compras e vendas':'Buy Sell','compras':'Buy Sell','vendas':'Buy Sell',
 'religiao':'Community & Social','saude':'Health','noticias':'News','empregos':'Jobs',
 'tecnologia':'Technology','jogos':'Gaming','negocios':'Business','culinaria':'Cooking',
 'criptomoedas':'Crypto','poesia':'Poetry','imoveis':'Real Estate','viagem':'Travel',
 'bolsas de estudo':'Scholarship','freelance':'Freelance','ganhar dinheiro':'Earning',
 'moda e beleza':'Buy Sell','musica':'Entertainment','futebol':'Sports','filmes e series':'Entertainment',
 'esporte':'Sports','financas':'Finance','investimentos':'Finance','marketing':'Business',
 'livros':'Education','idiomas':'Education','cursos':'Education','carros':'Buy Sell',
 'animais':'Community & Social','familia':'Community & Social','politica':'News',
}

def norm(s):
    s = unicodedata.normalize('NFKD', s or '')
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return s.lower()

def fold(s):
    """ASCII-fold stylized unicode (mathematical bold etc.) then lowercase."""
    s = unicodedata.normalize('NFKD', s or '')
    out = []
    for c in s:
        if unicodedata.combining(c):
            continue
        try:
            out.append(c.encode('ascii').decode('ascii'))
        except UnicodeEncodeError:
            out.append(c)
    return ''.join(out).lower()

# ---------- screening on live og:title ----------
BET_CTX = ['aviator','tiger','tigrinho','bet','banca','plataforma','vip','green','cassino','casino',
           'slots','slot','aposta','palpite','lucro','saque','recarga','bonus','cadastro','pagante',
           'fortune','roleta','blackjack','spaceman','mines','bicho','cambista']

def screen(title):
    """Return (drop_reason or None, flag or None)."""
    t = fold(title)
    # strip negated-prohibition spans: 'proibido porn', 'sem apostas', etc.
    banned_words = r'(porn|xxx|sexo|aposta|apostas|cassino|casino|tigrinho|sinais|plataforma|plataformas)'
    t2 = re.sub(r'\b(proibido|proibida|proibidos|sem|nao|não|zero|banido|banida)\b[^,.;]{0,40}?\b' + banned_words, ' ', t)
    w = lambda pat: re.search(r'\b' + pat + r'\b', t2)
    # hard porn / xxx
    for pat in [r'porn', r'xxx', r'xvideos', r'onlyfans', r'redtube', r'putaria', r'novinha',
                r'safad[oa]', r'conteudo adulto', r'sexo explicito', r'sexo oral', r'video porno',
                r'gostosa', r'peitos', r'buceta', r'caralho']:
        if w(pat):
            return f"hard porn/xxx marker '{pat}'", None
    if 'sexo' in t2.split() and any(x in t2 for x in ['🔞','18+','quente','explicito','videos','fotos']):
        return "adult sexual content (sexo + explicit/18+ context)", None
    if '🔞' in title and any(x in t2 for x in ['safad','gostosa','sexo','putaria','encontro','quente']):
        return "adult sexual content (18+ + sexual context)", None
    # casino / betting
    if '🎰' in title:
        return "casino/slots (slot machine emoji)", None
    for pat in [r'tigrinho', r'fortune tiger', r'cassino', r'casino', r'apostas?', r'bet365',
                r'palpites?', r'cambista', r'jogo do bicho', r'roleta', r'blackjack',
                r'aviator', r'spaceman', r'plataformas? pagantes?', r'pg slots?', r'pg metodos?',
                r'metodo.*slots?', r'slots?', r'\bbets?\b', r'betting', r'\bodds?\b']:
        if w(pat) or re.search(pat, t2):
            return f"casino/betting marker '{pat}'", None
    if w(r'fortune') and any(x in t2 for x in ['tiger', 'slot', 'tigrinho']):
        return "casino/betting marker 'fortune + tiger/slots'", None
    if w(r'sinais') and any(x in t2 for x in BET_CTX):
        return "betting signals (sinais + betting context)", None
    if w(r'plataformas?') and any(x in t2 for x in ['bonus','cadastro','recarga','saque','lucro','pagante','pagando','paga','vip','cassino','casino','link','lancamento','divulgacao']):
        return "casino/signal platform promo (plataforma + bonus/cadastro/link/lancamento/pagando)", None
    if w(r'banca') and any(x in t2 for x in ['aposta','bet','sinais','green','vip']):
        return "betting (banca + betting context)", None
    if w(r'bonus') and any(x in t2 for x in ['cadastro','recarga','plataforma','cassino','casino','aposta','saque']):
        return "casino signup-bonus promo", None
    if w(r'poker') and any(x in t2 for x in ['dinheiro','aposta','cassino','casino','vip','lucro']):
        return "betting (poker + money context)", None
    # crypto-airdrop / binary / free-money scams
    for pat in [r'airdrop', r'opcoes binarias', r'binary options?', r'lucro garantido',
                r'retorno garantido', r'dinheiro gratis', r'free money', r'renda garantida',
                r'fique rico', r'dobrar.*dinheiro', r'multiplicar.*dinheiro', r'ganhe.*sem investir']:
        if re.search(pat, t2):
            return f"scam marker '{pat}'", None
    # flags (keep, but note)
    if w(r'sinais'):
        return None, "standalone 'sinais' — kept, watch for betting context"
    if w(r'banca'):
        return None, "standalone 'banca' — kept (may be exam board)"
    if '🔞' in title or '18+' in title:
        return None, "18+ age gate on non-porn group — kept"
    return None, None

KW_CAT = [
 (r'\b(curso|aula|estudo|estudos|enem|vestibular|faculdade|escola|aprender|ingles|concurso)\b','Education'),
 (r'\b(futebol|fut|flamengo|corinthians|palmeiras|vasco|esporte|treino|academia|musculacao)\b','Sports'),
 (r'\b(venda|vendas|comprar|compra|promocao|promocoes|achadinhos|oferta|ofertas|loja|brech[oó]|bazar|imoveis|aluguel)\b','Buy Sell'),
 (r'\b(emprego|empregos|vaga|vagas|trabalho|contratando)\b','Jobs'),
 (r'\b(receita|receitas|culinaria|cozinha|bolo|doces)\b','Cooking'),
 (r'\b(viagem|viagens|turismo|passagem)\b','Travel'),
 (r'\b(bitcoin|cripto|criptomoeda|ethereum|trading)\b','Crypto'),
 (r'\b(noticia|noticias|jornal)\b','News'),
 (r'\b(saude|fitness|emagrecer|dieta)\b','Health'),
 (r'\b(freelancer|freela)\b','Freelance'),
 (r'\b(bolsa|bolsas|scholarship)\b','Scholarship'),
 (r'\b(renda extra|ganhar dinheiro|ganhar renda)\b','Earning'),
 (r'\b(memes|humor|engracado|risada)\b','Funny'),
 (r'\b(filme|filmes|serie|series|musica|anime|desenho)\b','Entertainment'),
 (r'\b(jogo|jogos|gamer|free fire|minecraft|roblox)\b','Gaming'),
 (r'\b(amizade|amigos|conversar|bate-papo|namoro|solteiros)\b','Community & Social'),
 (r'\b(islam|islamico|musulmano|alcorao|mesquita)\b','Islamic'),
 (r'\b(poesia|poema|poemas)\b','Poetry'),
]

def categorize(title, dircat):
    t = norm(title)
    for pat, cat in KW_CAT:
        if re.search(pat, t):
            return cat
    return dircat or 'Community & Social'

def describe(name, cat):
    return f"Join {name}, an active WhatsApp group for {cat.lower()}. Connect with members, share updates and join the conversation."

def main():
    global ATTEMPT_LOG
    ATTEMPT_LOG = open(os.path.join(WAVE, 'team02-attempts.log'), 'a', buffering=1)
    xml = open(SITEMAP, encoding='utf-8').read()
    urls = re.findall(r'<loc>([^<]+)</loc>', xml)
    grupo = [u for u in urls if '/grupo/' in u]
    assert len(grupo) == 19731, len(grupo)
    slice_urls = grupo[START:END]
    union = set(json.load(open(UNION)))
    print(f"slice {START}-{END-1}: {len(slice_urls)} URLs; union {len(union)}", flush=True)

    # resume from state if present
    state_path = os.path.join(WAVE, 'team02-state.json')
    if os.path.exists(state_path):
        st = json.load(open(state_path))
        done = set(st['done_offsets'])
        candidates = json.load(open(os.path.join(WAVE, 'team02-candidates.json')))
        pending = json.load(open(os.path.join(WAVE, 'team02-pending.json')))
        excluded = st['excluded']
        counts = st['counts']
        seen = set(st['seen_codes'])
        print(f"resumed: {len(done)} offsets done, {len(candidates)} candidates", flush=True)
    else:
        done, candidates, pending, excluded = set(), [], [], []
        counts = {'raw':0,'dupes':0,'dead':0,'excluded_n':0,'pending_n':0,'no_invite':0,'fetch_fail':0}
        seen = set()

    fetch_sess = requests.Session()
    fetch_sess.headers.update(UA)
    verify_sess = requests.Session()
    verify_sess.headers.update(UA)

    def fetch_page(url):
        for att in range(2):
            try:
                r = fetch_sess.get(url, timeout=25)
                if r.status_code == 200 and r.text:
                    return r.text
                if r.status_code in (429, 500, 502, 503):
                    time.sleep(5)
                    continue
                return None
            except Exception:
                time.sleep(3)
        return None

    def extract(text):
        if not text:
            return None, None
        m = re.findall(r'chat\.whatsapp\.com/([A-Za-z0-9_-]{15,30})', text)
        code = m[0] if m else None
        t = re.search(r'<title>([^<]+)</title>', text)
        dircat = None
        if t:
            title = html.unescape(t.group(1))
            parts = title.split(' - ')
            if len(parts) >= 2:
                dircat = DIRCAT.get(norm(parts[-1]).strip())
        return code, dircat

    def og_title(text):
        if not text:
            return ''
        m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]*content=["\']([^"\']*)', text)
        if not m:
            m = re.search(r'<meta[^>]+content=["\']([^"\']*)["\'][^>]*property=["\']og:title["\']', text)
        return html.unescape(m.group(1)).strip() if m else ''

    def verify_once(code):
        """Single attempt, hard-bounded to 75s by SIGALRM (spec timeout is
        60-90s; the alarm only cuts pathological dribble-hangs that the
        per-recv read timeout cannot). Returns (status, title_or_reason):
        live/empty/pending."""
        t0 = time.time()
        try:
            signal.setitimer(signal.ITIMER_REAL, 75)
            try:
                r = verify_sess.get(f'https://chat.whatsapp.com/{code}', timeout=60)
                if r.status_code == 429:
                    # do NOT sleep+retry here: defer to the end-of-chunk
                    # cool-down sweep so one 429 doesn't cost 10s per code
                    return 'rate_limited', ''
                title = og_title(r.text)
                return ('live', title) if title else ('empty', '')
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
        except VerifyTimeout:
            return 'pending', 'verify wall-time 75s (hung read)'
        except Exception as e:
            try:
                signal.setitimer(signal.ITIMER_REAL, 75)
                try:
                    r = verify_sess.get(f'https://chat.whatsapp.com/{code}', timeout=60)
                    if r.status_code == 429:
                        return 'rate_limited', ''
                    title = og_title(r.text)
                    return ('live', title) if title else ('empty', '')
                finally:
                    signal.setitimer(signal.ITIMER_REAL, 0)
            except VerifyTimeout:
                return 'pending', 'verify wall-time 75s (hung read)'
            except Exception as e2:
                return 'pending', f'{type(e2).__name__}: {e2}'
        finally:
            try:
                ATTEMPT_LOG.write(f"{time.strftime('%H:%M:%S')} {code} {time.time()-t0:.1f}s\n")
                ATTEMPT_LOG.flush()
            except Exception:
                pass

    offsets = [i for i in range(len(slice_urls)) if i not in done]
    for ci in range(0, len(offsets), CHUNK):
        chunk_offsets = offsets[ci:ci+CHUNK]
        chunk_urls = [(o, slice_urls[o]) for o in chunk_offsets]
        # Phase A: fetch grupo pages concurrently
        raw = {}  # offset -> (code, dircat)
        with ThreadPoolExecutor(max_workers=6) as ex:
            futs = {ex.submit(fetch_page, u): o for o, u in chunk_urls}
            for fut in as_completed(futs):
                o = futs[fut]
                try:
                    text = fut.result()
                except Exception:
                    text = None
                if text is None:
                    counts['fetch_fail'] += 1
                    done.add(o)
                    continue
                code, dircat = extract(text)
                if not code:
                    counts['no_invite'] += 1
                    done.add(o)
                    continue
                raw[o] = (code, dircat)
                counts['raw'] += 1
        # Phase B: dedupe + verify sequentially on ONE session.
        # First pass: single attempt per code. Empty-og:title codes are
        # re-tried in two spaced passes at end of chunk (same retry count,
        # but the spacing is between passes, not a per-code sleep).
        empties = []  # (offset, code, dircat)
        ratelimited = []  # (offset, code, dircat) — HTTP 429, retried after cool-down
        n_to_verify = 0
        for o in sorted(raw):
            code, dircat = raw[o]
            done.add(o)
            if code in union or code in seen:
                counts['dupes'] += 1
                continue
            seen.add(code)
            n_to_verify += 1
            if n_to_verify % 50 == 0:
                print(f"  chunk progress: {n_to_verify} verify attempts", flush=True)
            status, info = verify_once(code)
            if status == 'pending':
                counts['pending_n'] += 1
                pending.append({'code': code, 'reason': info or 'transport/429 failure',
                                'listing': slice_urls[o]})
            elif status == 'rate_limited':
                ratelimited.append((o, code, dircat))
            elif status == 'empty':
                empties.append((o, code, dircat))
            else:
                title = info
                reason, flag = screen(title)
                if reason:
                    counts['excluded_n'] += 1
                    excluded.append({'code': code, 'reason': reason, 'title': title})
                else:
                    cat = categorize(title, dircat)
                    candidates.append({'name': title, 'category': cat, 'country': 'BR',
                                       'description': describe(title, cat),
                                       'invite': f'https://chat.whatsapp.com/{code}'})
                    if flag:
                        excluded.append({'code': code, 'reason': f"KEPT-FLAG: {flag}", 'title': title})
        # Cool-down sweep: retry 429-deferred codes once after 60s.
        if ratelimited:
            print(f"  cool-down: {len(ratelimited)} rate-limited, sleeping 60s", flush=True)
            time.sleep(60)
            for o, code, dircat in ratelimited:
                status, info = verify_once(code)
                if status == 'live':
                    title = info
                    reason, flag = screen(title)
                    if reason:
                        counts['excluded_n'] += 1
                        excluded.append({'code': code, 'reason': reason, 'title': title})
                    else:
                        cat = categorize(title, dircat)
                        candidates.append({'name': title, 'category': cat, 'country': 'BR',
                                           'description': describe(title, cat),
                                           'invite': f'https://chat.whatsapp.com/{code}'})
                        if flag:
                            excluded.append({'code': code, 'reason': f"KEPT-FLAG: {flag}", 'title': title})
                elif status == 'pending' or status == 'rate_limited':
                    counts['pending_n'] += 1
                    pending.append({'code': code, 'reason': info or 'HTTP 429',
                                    'listing': slice_urls[o]})
                else:
                    empties.append((o, code, dircat))
        # Spaced retry passes over empties (2 retries before dead)
        for pass_no, pause in ((1, 5), (2, 10)):
            if not empties:
                break
            time.sleep(pause)
            still = []
            for o, code, dircat in empties:
                status, info = verify_once(code)
                if status == 'live':
                    title = info
                    reason, flag = screen(title)
                    if reason:
                        counts['excluded_n'] += 1
                        excluded.append({'code': code, 'reason': reason, 'title': title})
                    else:
                        cat = categorize(title, dircat)
                        candidates.append({'name': title, 'category': cat, 'country': 'BR',
                                           'description': describe(title, cat),
                                           'invite': f'https://chat.whatsapp.com/{code}'})
                        if flag:
                            excluded.append({'code': code, 'reason': f"KEPT-FLAG: {flag}", 'title': title})
                elif status == 'pending' or status == 'rate_limited':
                    counts['pending_n'] += 1
                    pending.append({'code': code, 'reason': info or 'HTTP 429',
                                    'listing': slice_urls[o]})
                else:
                    still.append((o, code, dircat))
            empties = still
            print(f"  retry pass {pass_no}: {len(empties)} still empty", flush=True)
        counts['dead'] += len(empties)
        # checkpoint
        json.dump(candidates, open(os.path.join(WAVE, 'team02-candidates.json'), 'w'), ensure_ascii=False, indent=1)
        json.dump(pending, open(os.path.join(WAVE, 'team02-pending.json'), 'w'), ensure_ascii=False, indent=1)
        leads = [{'index': START + o, 'url': slice_urls[o]} for o in range(len(slice_urls)) if o not in done]
        json.dump(leads, open(os.path.join(WAVE, 'team02-leads.json'), 'w'), ensure_ascii=False, indent=1)
        st = {'done_offsets': sorted(done), 'seen_codes': sorted(seen),
              'excluded': excluded, 'counts': counts,
              'slice': f'{START}-{END-1}', 'last_chunk_offsets': chunk_offsets}
        json.dump(st, open(state_path, 'w'), ensure_ascii=False, indent=1)
        print(f"chunk done: processed {len(done)}/{len(slice_urls)} | candidates {len(candidates)} "
              f"| raw {counts['raw']} dupes {counts['dupes']} dead {counts['dead']} "
              f"excluded {counts['excluded_n']} pending {counts['pending_n']} "
              f"no_invite {counts['no_invite']} fetch_fail {counts['fetch_fail']}", flush=True)

    # final re-screen of ALL banked candidates with the current screen
    # (covers any chunk banked before a screen fix)
    kept = []
    for c in candidates:
        code = c['invite'].split('/')[-1]
        reason, flag = screen(c['name'])
        if reason:
            counts['excluded_n'] += 1
            excluded.append({'code': code, 'reason': reason + ' (post-hoc re-screen)', 'title': c['name']})
        else:
            kept.append(c)
    candidates = kept
    json.dump(candidates, open(os.path.join(WAVE, 'team02-candidates.json'), 'w'), ensure_ascii=False, indent=1)
    # final summary
    leads = [{'index': START + o, 'url': slice_urls[o]} for o in range(len(slice_urls)) if o not in done]
    summary = {
        'team': 'team02',
        'slice': f"linkado.app grupo sitemap indices {START}-{END-1} (grupo-only, 0-based; {END-START} URLs; first={slice_urls[0]} last={slice_urls[-1]})",
        'sources': ['linkado.app grupo pages (sitemap copy wave_20261110/linkado_sitemap.xml, 19731 grupo URLs; index mapping confirmed vs team05 last idx5999 and team34 first idx8500)'],
        'controls': {
            'live': "KrDwdK8EIkB6vgauHg5M7N -> og:title 'JAY - PHP & Python Full Stack Developer' (LIVE, as expected)",
            'fabricated': "ZzZzZzZzZzZzZzZzZzZzZzZz -> empty og:title (dead, as expected)"},
        'raw': counts['raw'], 'verified': len(candidates), 'dupes': counts['dupes'],
        'dead': counts['dead'], 'excluded': [e for e in excluded if not e['reason'].startswith('KEPT-FLAG')],
        'kept_flags': [e for e in excluded if e['reason'].startswith('KEPT-FLAG')],
        'pending': len(pending), 'leads': len(leads),
        'listings_attempted': len(done), 'listings_no_invite': counts['no_invite'],
        'listings_fetch_fail': counts['fetch_fail'],
        'resume_point': f"done_offsets={len(done)}/{len(slice_urls)}; unmined indices banked in team02-leads.json",
    }
    json.dump(summary, open(os.path.join(WAVE, 'team02-summary.json'), 'w'), ensure_ascii=False, indent=1)
    print('FINAL:', json.dumps({k: summary[k] for k in ('raw','verified','dupes','dead','pending','leads')}), flush=True)

if __name__ == '__main__':
    main()
