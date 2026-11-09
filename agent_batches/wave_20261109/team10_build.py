import json, re, html, unicodedata

WAVE = '/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261109/'

CAT_PT = {
    'amizade': 'Friendship', 'dinheiro': 'Finance', 'namoro': 'Friendship',
    'carros': 'Community & Social', 'links': 'Community & Social',
    'lgbt': 'Community & Social', 'figurinhas': 'Funny', 'status': 'Entertainment',
    'comprar e venda': 'Buy Sell', 'trabalho': 'Jobs', 'games': 'Gaming',
    'musica': 'Entertainment', 'religiao': 'Community & Social',
    'esportes': 'Sports', 'series': 'Entertainment', 'moda e beleza': 'Community & Social',
    'tecnologia': 'Technology', 'cidades': 'Community & Social',
    'educacao': 'Education', 'politica': 'News', 'saude': 'Health',
    'filmes': 'Entertainment', 'noticias': 'News', 'esporte': 'Sports',
    'humor': 'Funny', 'memes': 'Funny', 'futebol': 'Sports',
    'cursos': 'Education', 'empregos': 'Jobs', 'vagas': 'Jobs',
    'vendas': 'Buy Sell', 'ofertas': 'Buy Sell', 'promocoes': 'Buy Sell',
    'gospel': 'Community & Social', 'cristao': 'Community & Social',
    'anime': 'Entertainment', 'desenhos': 'Entertainment', 'livros': 'Education',
    'ingles': 'Education', 'concursos': 'Education', 'financas': 'Finance',
    'investimentos': 'Finance', 'criptomoedas': 'Finance', 'bitcoin': 'Finance',
    'free fire': 'Gaming', 'roblox': 'Gaming', 'minecraft': 'Gaming',
    'bible': 'Community & Social', 'oracao': 'Community & Social',
}
ALLOWED = {"Gaming", "Education", "Online Earning", "Community & Social", "Business",
           "Friendship", "Finance", "Buy Sell", "Islamic", "Entertainment", "Jobs",
           "Technology", "Funny", "Sports", "Health", "News"}

# --- screening ---
PORN = ['porn', 'xxx', 'xvideo', 'sexo', 'sex ', 'sexo ', 'sexo,', 'putaria',
        'putaria', 'escort', 'acompanhante', 'cam girl', 'camgirl', 'cangirl',
        'sexy', 'sexie', 'hentai', 'onlyfans', 'novinhas', 'vazados', 'vazada',
        'nudes', 'nude ', 'pelada', 'peladas', 'taradas', 'tarado', 'gostosas',
        'gostosa', 'safada', 'safado', 'safadas', 'punheta', 'boquete', 'tesao',
        'tesão', 'foder', 'sexvideo', 'porno', 'pornô', 'erotic', 'erótico',
        'hookup', 'transar', 'sex chat', 'sexo gratis', 'videos porno',
        'garotas de programa', 'acompanhantes', 'massagem erotica']
SCAM = ['b-love', 'b love', 'blove', 'forsage', 'sheyi', 'airdrop',
        'ganhe dinheiro', 'ganhar dinheiro', 'dinheiro gratis', 'dinheiro grátis',
        'renda extra', 'lucro garantido', 'ganhe renda', 'investimento garantido',
        'dobrar dinheiro', 'multiplique seu dinheiro', 'dinheiro facil',
        'dinheiro fácil', 'saque imediato', 'saque pix', 'pix gratis',
        'free money', 'earn $', 'earn money fast', 'get rich quick',
        'double your money', 'guaranteed profit', 'investimento', 'investir',
        'aplicativo pagando', 'app pagando', 'apps pagando', 'app que paga',
        'kwai gold', 'tigrinho', 'jogo do tigre', 'fortune tiger',
        'plataforma pagando', 'plataforma nova pagando', 'sacar dinheiro']
# 'fox club invest', 'invest' handled via SCAM 'investimento'/'investir'; add:
SCAM += ['fox club', 'club invest',
         'sinais vip', 'sinais de trade', 'trade vip', 'robô de trade',
         'robo de trade']
BETTING_KEEP = ['aposta', 'apostas', 'bet', 'palpite', 'palpites', 'brasileirão',
                'futebol', 'efootball', 'cassino', 'cassino online']

PROHIBIT_RE = re.compile(
    r'[^.!?\n]*(?:proibido|não é permitido|nao e permitido|não compartilhe|'
    r'nao compartilhe|não envie|nao envie|não poste|proibida|proibidas|'
    r'não é permitida|nao permitido|sem pornografia|sem conteúdo adulto|'
    r'conteúdo inapropriado|conteudo inapropriado|não compartilhem)[^.!?\n]*[.!?\n]?',
    re.I)

def strip_prohibitions(text):
    return PROHIBIT_RE.sub(' ', text)

def screen(name, title, desc):
    """Return drop reason or None."""
    raw = f'{name} {title} {desc}'
    clean = strip_prohibitions(raw)
    low = clean.lower()
    for w in PORN:
        if w in low:
            return 'porn/adult: ' + w
    for w in SCAM:
        if w in low:
            return 'scam/money-pitch: ' + w
    return None

def clean_name(og, page_title):
    """Prefer the real WhatsApp group name (og:title); fall back to linkado title."""
    name = (og or '').strip()
    if not name or len(name) < 2:
        t = page_title or ''
        t = re.sub(r'^Grupo de WhatsApp\s*', '', t, flags=re.I).strip()
        t = re.sub(r'\s*-\s*[^-]+$', '', t).strip()
        name = t
    name = html.unescape(name)
    name = re.sub(r'\s+', ' ', name).strip()
    # drop trailing ' | Grupo de ofertas' style suffixes from og titles
    name = re.sub(r'\s*\|\s*Grupo de .*?$', '', name).strip()
    return name[:120]

def linkado_category(page_title, desc):
    m = re.search(r'-\s*([^-]+?)\s*$', page_title or '')
    pt = m.group(1).strip().lower() if m else ''
    if pt in CAT_PT:
        return CAT_PT[pt]
    m2 = re.search(r'na categoria\s+([^.,]+)', desc or '', re.I)
    if m2 and m2.group(1).strip().lower() in CAT_PT:
        return CAT_PT[m2.group(1).strip().lower()]
    return None

def guess_category(name, title, desc, linkado_cat):
    text = f'{name} {title} {desc}'.lower()
    if linkado_cat:
        return linkado_cat
    if any(k in text for k in ['free fire', 'roblox', 'minecraft', 'pubg', 'gta',
                               'jogo', 'jogos', 'game', 'gamer', 'guilda', 'clan']):
        return 'Gaming'
    if any(k in text for k in ['curso', 'cursos', 'estudo', 'estudos', 'escola',
                               'aprender', 'aula', 'concurso', 'vestibular', 'enem',
                               'ingles', 'inglês']):
        return 'Education'
    if any(k in text for k in ['emprego', 'empregos', 'vaga', 'vagas', 'trabalho',
                               'recrutamento']):
        return 'Jobs'
    if any(k in text for k in ['venda', 'vendas', 'oferta', 'ofertas', 'promoção',
                               'promocao', 'comprar', 'shopee', 'mercado livre',
                               'achadinho', 'achadinhos']):
        return 'Buy Sell'
    if any(k in text for k in ['futebol', 'esporte', 'esportes', 'brasileirão',
                               'palmeiras', 'flamengo', 'corinthians']):
        return 'Sports'
    if any(k in text for k in ['amizade', 'amigos', 'amizades', 'conhecer pessoas',
                               'fazer amigos', 'namoro', 'relacionamento']):
        return 'Friendship'
    if any(k in text for k in ['musica', 'música', 'serie', 'série', 'filme',
                               'filmes', 'novela', 'status']):
        return 'Entertainment'
    if any(k in text for k in ['dinheiro', 'finanças', 'financas', 'renda']):
        return 'Finance'
    return 'Community & Social'

def build_description(name, cat, page_desc, og):
    """1-2 English sentences, no source name/link, no phone numbers."""
    d = (page_desc or '').strip()
    # strip the boilerplate prefix 'Grupo de WhatsApp X, na categoria Y.'
    d = re.sub(r'^Grupo de WhatsApp[^.]*,\s*na categoria\s+[^.]+\.\s*', '', d, flags=re.I)
    d = re.sub(r'^Grupo de WhatsApp[^.]*\.\s*', '', d, flags=re.I)
    d = strip_prohibitions(d)
    d = html.unescape(d)
    d = re.sub(r'https?://\S+|chat\.whatsapp\.com/\S+', ' ', d)
    d = re.sub(r'\+?\d[\d\s().-]{7,}\d', ' ', d)  # phone numbers
    d = re.sub(r'\s+', ' ', d).strip()
    # take first 1-2 sentences, cap length
    sents = re.split(r'(?<=[.!?])\s+', d)
    sents = [s for s in sents if len(s) > 3]
    core = ' '.join(sents[:2])[:280].strip()
    if core and not core.endswith(('.', '!', '?')):
        core += '.'
    cat_word = {'Friendship': 'make new friends and chat',
                'Gaming': 'games and gaming chat',
                'Education': 'learning and study resources',
                'Jobs': 'job opportunities and career talk',
                'Buy Sell': 'buying, selling and deals',
                'Sports': 'sports talk and fans',
                'Entertainment': 'entertainment and fun',
                'Technology': 'technology talk',
                'Funny': 'funny content and laughs',
                'Finance': 'money and finance talk',
                'Health': 'health and wellness',
                'News': 'news and updates',
                'Business': 'business talk',
                'Online Earning': 'online earning ideas',
                'Community & Social': 'community chat',
                'Islamic': 'Islamic discussion'}.get(cat, 'community chat')
    if core:
        # translate-ish: keep original PT if it reads as a description, else generic
        desc = (f'Join {name}, a WhatsApp group for {cat_word}. {core}'
                if len(core) > 15 else
                f'Join {name}, a WhatsApp group for {cat_word}.')
    else:
        desc = f'Join {name}, a WhatsApp group for {cat_word}.'
    desc = re.sub(r'\s+', ' ', desc).strip()
    return desc[:500]

def main():
    verify = json.load(open(WAVE + 'team10_verify.json'))
    live = {c: r for c, r in verify.items() if r['status'] == 'live'}
    dead = {c: r for c, r in verify.items() if r['status'] == 'dead'}
    pending = {c: r for c, r in verify.items() if r['status'] == 'pending'}
    print('live:', len(live), 'dead:', len(dead), 'pending:', len(pending))

    candidates, dropped = [], []
    seen_codes = set()
    for code, r in sorted(live.items()):
        if code in seen_codes:
            continue
        seen_codes.add(code)
        name = clean_name(r.get('og_title', ''), r.get('page_title', ''))
        reason = screen(name, r.get('og_title', ''), r.get('page_desc', ''))
        if reason:
            dropped.append({'code': code, 'name': name, 'reason': reason,
                            'og_title': r.get('og_title', ''),
                            'page_title': r.get('page_title', '')})
            continue
        if not name or len(name) < 2:
            dropped.append({'code': code, 'name': name, 'reason': 'no usable name',
                            'og_title': r.get('og_title', ''),
                            'page_title': r.get('page_title', '')})
            continue
        if re.search(r'\d[\d\s().-]{7,}\d', name):
            dropped.append({'code': code, 'name': name, 'reason': 'phone-like name',
                            'og_title': r.get('og_title', ''),
                            'page_title': r.get('page_title', '')})
            continue
        lcat = linkado_category(r.get('page_title', ''), r.get('page_desc', ''))
        cat = guess_category(name, r.get('page_title', ''), r.get('page_desc', ''), lcat)
        if cat not in ALLOWED:
            cat = 'Community & Social'
        desc = build_description(name, cat, r.get('page_desc', ''), r.get('og_title', ''))
        candidates.append({'name': name, 'category': cat, 'country': 'BR',
                           'description': desc,
                           'invite': 'https://chat.whatsapp.com/' + code})

    # dedupe candidates by invite code (already unique) and by name+category
    seen = set()
    uniq = []
    for c in candidates:
        k = c['invite']
        if k in seen:
            continue
        seen.add(k)
        uniq.append(c)

    json.dump(uniq, open(WAVE + 'team10-candidates.json', 'w'), ensure_ascii=False, indent=1)
    json.dump([{'code': c, 'invite': 'https://chat.whatsapp.com/' + c,
                'name': r.get('og_title', ''), 'page_title': r.get('page_title', ''),
                'note': 'transport-failed during verification; recheck later'}
               for c, r in sorted(pending.items())],
              open(WAVE + 'team10-pending.json', 'w'), ensure_ascii=False, indent=1)
    json.dump(dropped, open(WAVE + 'team10-dropped.json', 'w'), ensure_ascii=False, indent=1)
    print('candidates:', len(uniq), 'dropped:', len(dropped))
    from collections import Counter
    print(Counter(c['category'] for c in uniq))
    print('drop reasons:', Counter(d['reason'].split(':')[0] for d in dropped))

if __name__ == '__main__':
    main()
