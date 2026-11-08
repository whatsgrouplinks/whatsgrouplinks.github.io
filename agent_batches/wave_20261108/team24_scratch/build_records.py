# Build final team24 records from verified inputs. Run after all harvest/verify jobs finish.
import json, re, html, sys
ADULT_EMOJI=set(['🥵','🍆','🍑','🔞','💦','👅','👄','💋'])
ADULT_WORDS=['hentai','porno','porn','xxx','onlyfans','puta','sexo','swinger','escort','call girl','call-girl',
 'tetas','culo','pene','verga','cachondo','nudes','desnudo','desnuda','pack ','packs','hot ','caliente']
SCAM_WORDS=['bitfinex','payPal loader','paypal loader','counterfeit','fake money','dinheiro falso','money mule']
CATS=['Education','Jobs','Entertainment','Islamic','News','Sports','Technology','Health','Business','Gaming',
 'Friendship','Community & Social','Online Earning','Crypto','Cooking','Poetry','Travel','Scholarship',
 'Freelance','Real Estate','Buy & Sell','Finance','Funny']
def map_cat(raw, name=''):
    r=(raw or '').strip().lower()
    m={'amistad':'Friendship','amizade':'Friendship','amor':'Friendship','romance':'Friendship','namoro':'Friendship',
     'casais':'Friendship','empleo':'Jobs','empregos':'Jobs','trabalho':'Jobs','vagas':'Jobs','trabajos':'Jobs',
     'educacion':'Education','educação':'Education','educacao':'Education','estudos':'Education','estudio':'Education',
     'estudos-e-tarefas':'Education','cursos':'Education','concursos':'Education',
     'deportes':'Sports','esportes':'Sports','futebol':'Sports','fútbol':'Sports','futbol':'Sports',
     'musica':'Entertainment','música':'Entertainment','peliculas':'Entertainment','películas':'Entertainment',
     'series':'Entertainment','cine':'Entertainment','filmes':'Entertainment','anime':'Entertainment',
     'juegos':'Gaming','games':'Gaming','gaming':'Gaming','free fire':'Gaming','minecraft':'Gaming','roblox':'Gaming',
     'memes':'Funny','humor':'Funny','figurinhas':'Funny','stickers':'Funny',
     'noticias':'News','news':'News','tecnologia':'Technology','technology':'Technology','programacao':'Technology',
     'programación':'Technology','salud':'Health','fitness':'Health','saude':'Health',
     'cocina':'Cooking','recetas':'Cooking','poesia':'Poetry','poesía':'Poetry',
     'viajes':'Travel','viagens':'Travel','negocios':'Business','emprendimiento':'Business','empreendedorismo':'Business',
     'ventas':'Buy & Sell','vendas':'Buy & Sell','ofertas':'Buy & Sell','cupones':'Buy & Sell',
     'compra':'Buy & Sell','compra-venta':'Buy & Sell','criptomonedas':'Crypto','cripto':'Crypto',
     'religion':'Community & Social','religiao':'Community & Social','religión':'Community & Social',
     'islamic':'Islamic','islam':'Islamic','general':'Community & Social','chat':'Community & Social',
     'mundial':'Community & Social','diversion':'Entertainment','diversão':'Entertainment','rol':'Entertainment',
     'destacados':'Community & Social','cultura':'Community & Social','culture':'Community & Social',
     'recreation':'Community & Social','entrepreneurship':'Business','sports':'Sports',
     'health and wellness':'Health','spiritual':'Community & Social','affinity':'Community & Social',
     'expats':'Community & Social','dancing':'Entertainment','beer':'Community & Social',
     'services':'Business','finance':'Finance','finanzas':'Finance','dinheiro':'Finance'}
    if r in m: return m[r]
    for k,v in m.items():
        if k and k in r: return v
    return 'Community & Social'
NEG_RE=re.compile(r'\b(sem|proibido|prohibido|n\u00e3o|nao|no\u00e3|not|never|sin|prohibida|prohibidos)\b[^.;,]{0,40}\b(nudes|porn|xxx|sexo|hentai|onlyfans|desnudo|desnuda|pack|packs)\b')
def blocked(name, desc, ogtitle=''):
    t=((name or '')+' '+(ogtitle or '')).lower()
    if any(e in (name or '')+(ogtitle or '') for e in ADULT_EMOJI): return 'adult-emoji'
    if any(w in t for w in ADULT_WORDS): return 'adult-word'
    if any(w in t for w in SCAM_WORDS): return 'scam'
    d=NEG_RE.sub('', (desc or '').lower())
    if any(w in d for w in ADULT_WORDS): return 'adult-word-desc'
    if any(w in d for w in SCAM_WORDS): return 'scam'
    return None
def clean_name(n):
    n=html.unescape((n or '').strip())
    n=re.sub(r'\s+',' ',n)
    return n[:120]
def desc_for(name, cat, country):
    cname={'BR':'Brazil','CO':'Colombia','MX':'Mexico','ES':'Spain','AR':'Argentina','CU':'Cuba',
     'US':'United States','DO':'Dominican Republic','International':'around the world'}.get(country,'')
    place=f' in {cname}' if cname and cname!='around the world' else ''
    return f'Join {name}, a WhatsApp group listed under {cat}{place}. Connect with members, share updates and take part in the conversation.'
