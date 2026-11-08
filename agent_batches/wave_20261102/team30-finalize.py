#!/usr/bin/env python3
"""Team30 finalizer: clean names, keyword-classify categories, write original
English descriptions, emit team30-mexico-ca.json (schema-exact)."""
import json, re, os, html as ihtml, unicodedata as _u

BASE = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261102")

COUNTRY_NAME = {"MX": "Mexico", "GT": "Guatemala", "CR": "Costa Rica",
                "SV": "El Salvador", "HN": "Honduras", "NI": "Nicaragua",
                "PA": "Panama"}

PORN_RE = re.compile(
    r'\b(porn|pornhub|xxx|nude|nudist|sex\s?video|escort|call\s?girl|'
    r'fuck|dick|pussy|boobs?|tits|anal|horny|porno|'
    r'sexo\s?(gratis|duro|expl[ií]cito)|chicas\s?(calientes|sexys))\b', re.I)
EMOJI_RE = re.compile('[\U0001F975\U0001F346\U0001F351\U0001F51E\U0001F4A6\U0001F445\U0001F444\U0001F48B]')

BAD_NAME = re.compile(
    r'^(whatsapp group invite|join( this)? group|invitation|invitaci[oó]n|'
    r'enlaces?|solo enlaces.*|links?|grupo(s)? de whatsapp|whatsapp)$', re.I)

def ascii_fold(text):
    n = _u.normalize("NFKD", text)
    return "".join(c for c in n if not _u.combining(c)).lower()

# hard-drop: fraud/hate/sexual-18+/drug content and out-of-slice misfiles
DROP_RE = re.compile(
    r'(h+hacker|hackers?\s*(service|servicio)|servicios?\s*hhacker|'
    r'fetiche|fetish|bdsm|swinger|'
    r'anabolic|anabolico|esteroides?|steroids?|'
    r'\bmaricon|trabas?\b.*estafador|'
    r'alcal[aá] de henares|torrej[oó]n|henares)',
    re.I)

RULES = [  # (category, ascii keywords)
    ("Music", ["musica","music","rap","freestyle","reggaeton","rock","k-pop","kpop","banda","corridos","dj","spotify","trap","metal","cumbia","salsa","bachata","vallenato","mariachi","hip hop","lofi","edm","techno","house music","swiftie","taylor","cantante","concierto","banda "]),
    ("Gaming", ["gaming","gamer","free fire","freefire","pubg","fortnite","minecraft","call of duty","fifa","ea fc","xbox","playstation","ps4","ps5","nintendo","roblox","brawl stars","clash royale","valorant","videojuegos","gta","zelda","among us","warzone","apex","league of legends","steam","gamers","witcher","genshin","helldivers","pokemon","tcg","impact ","warriors","reclutamiento","clan"]),
    ("Sports", ["futbol","soccer","deportes","sport","apuestas","liga mx","champions","boxeo","mma","lucha libre","beisbol","nfl","ciclismo","running","atletismo","tenis","deport","pickleball","padel","gym "]),
    ("Girls", ["chicas","amor y","citas","ligar","solteros","solteras","noviazgo","pareja","dating","coqueteo","flirt","olvida a tu ex","corazones rotos"]),
    ("Friendship", ["amistad","amigos","amigas","conocer gente","conocer amigos","socializar","platicar","charlar","conversar","friends","amistades","hacer amigos","nuevas amistades","panitas","sala de estar","quedada","quedadas","compas","parceros","nuevos amigos","buen rollo","buena onda"]),
    ("Jobs", ["empleo","empleos","trabajo","trabajos","vacantes","job","bolsa de trabajo","ofertas laborales","contrataci","busco trabajo","ofrezco trabajo"]),
    ("Education", ["estudio","estudiar","tarea","tareas","homework","escuela","colegio","universidad","examen","ingles","english","idiomas","cursos","aprendizaje","estudiantes","tutor","clases","maestros","profesores","curso","matematica","olimpiada","olimpica","fisica","quimica","biologia","historia","geografia","lectura","leer","libros"]),
    ("News", ["noticias","news","noticiero","prensa","periodismo","ultima hora","ultimas noticias","informativo"]),
    ("Crypto", ["cripto","crypto","bitcoin","trading","forex","binance","ethereum","altcoin","shiba","doge"]),
    ("Finance", ["dinero","finanzas","inversion","prestamo","credito","ahorro","banco","sueldo","salario"]),
    ("Business", ["negocios","negocio","emprendimiento","emprendedores","emprendedoras","marketing","networking","pyme","startup","empresa"]),
    ("Buy-Sell", ["venta","ventas","vendo","compro","compra","comprar","vender","marketplace","clasificados","remates","ofertas","tianguis","bazar","subasta","articulos","se vende","se compra"]),
    ("Technology", ["tecnologia","tech","programacion","developers","software","inteligencia artificial","gadgets","smartphones","android","iphone","informatica","linux","windows","ciberseguridad","programador","informatico"]),
    ("Health", ["salud","fitness","gym","gimnasio","dieta","nutricion","medicina","doctores","bienestar","ejercicio","saludable","yoga","pilates"]),
    ("Travel", ["viajes","viajar","turismo","viajeros","mochileros","vuelos","hoteles","aviones","playas","moteras","motos","bikers","ruta","road trip","senderismo","camping"]),
    ("Movies", ["peliculas","cine","series","netflix","pelis","doramas","anime","kdrama","marvel","disney","pelicula","cinefilos","terror","suspenso","kawaiis","kawaii","dragon ball","naruto","one piece"]),
    ("Entertainment", ["entretenimiento","farandula","chismes","espectaculos","stickers","famosos","celebridades","filtro","filtros","amino","sala amino","grupo de acceso","fichas","rol ","roleplay","otakus","geek","cosplay","streamers","twitch"]),
    ("Food", ["comida","recetas","cocina","restaurantes","tacos","gastronomia","chef","reposteria","cocinar","foodies","antojos","asado","parrilla","postres"]),
    ("Pets", ["mascotas","perros","gatos","animales","pets","perritos","gatitos","veterinaria","perro","gato"]),
    ("Funny", ["humor","memes","chistes","risa","jajas","funny","comedia","risas","diversion","jajaja"]),
    ("Regional", ["venezolan","colombianos","peruanos","argentinos","mexicanos en","dominicanos","comunidad "]),
]

def classify(text):
    t = ascii_fold(text)
    for cat, kws in RULES:
        for k in kws:
            if k in t:
                return cat
    return "Other"

DESC = {
    "Music": [
        "A {c} music WhatsApp community where fans share songs, playlists and concert plans. Talk about favorite artists, new releases and local gigs with fellow music lovers.",
        "Music fans in {c} chat daily in this lively WhatsApp group. Share tracks, discover new artists and discuss concerts, genres and playlists together.",
    ],
    "Gaming": [
        "A {c} gaming WhatsApp group for players to team up, share tips and talk strategy. Find squad mates, discuss updates and enjoy daily gaming chat.",
        "Gamers from {c} gather here on WhatsApp to share gameplay, news and tricks. Join the conversation, find teammates and stay current on your favorite games.",
    ],
    "Sports": [
        "A {c} sports WhatsApp community for fans to follow matches, share results and debate the game. Daily football and sports talk with fellow supporters.",
        "Sports lovers in {c} chat here on WhatsApp about matches, teams and tournaments. Share predictions, highlights and live-match reactions with the group.",
    ],
    "Girls": [
        "A friendly {c} WhatsApp community for meeting new people and making connections. Members chat, share interests and enjoy relaxed, respectful conversation.",
        "Singles and social members in {c} use this WhatsApp group to meet new friends and potential partners. Friendly daily chat in a welcoming atmosphere.",
    ],
    "Friendship": [
        "A warm {c} WhatsApp community for meeting new friends and good conversation. Members share daily life, plans and laughs in a relaxed, friendly space.",
        "Make new friends in {c} through this active WhatsApp group. Chat about everyday topics, share experiences and build real connections with locals.",
    ],
    "Jobs": [
        "A {c} jobs WhatsApp group sharing vacancies, career tips and work opportunities. Members post openings and help each other find employment.",
        "Job seekers in {c} connect here on WhatsApp to share openings and hiring leads. Get alerts about new vacancies and practical job-hunting advice.",
    ],
    "Education": [
        "A {c} study WhatsApp group where students share notes, homework help and exam tips. Learn together with motivated classmates and clear explanations.",
        "Students in {c} use this WhatsApp group to study together, solve doubts and share learning resources. Friendly support for classes and exams.",
    ],
    "News": [
        "A {c} news WhatsApp group keeping members updated on current events and headlines. Share and discuss the day's most important stories.",
        "Stay informed with this {c} news community on WhatsApp. Members share breaking stories, updates and thoughtful discussion of local and world events.",
    ],
    "Crypto": [
        "A {c} crypto WhatsApp group for discussing markets, coins and trading ideas. Share analysis, news and strategies with fellow crypto enthusiasts.",
        "Crypto followers in {c} chat here on WhatsApp about prices, projects and market trends. Exchange insights and stay updated on the digital asset world.",
    ],
    "Finance": [
        "A {c} finance WhatsApp community sharing money tips, savings ideas and investment talk. Learn practical ways to manage and grow your money.",
        "Members in {c} discuss personal finance on WhatsApp, from budgeting to investments. Share advice and learn smarter money habits together.",
    ],
    "Business": [
        "A {c} business WhatsApp group connecting entrepreneurs and professionals. Share opportunities, marketing ideas and networking with driven members.",
        "Entrepreneurs in {c} gather on WhatsApp to exchange business ideas and growth tips. Network, collaborate and learn from fellow founders.",
    ],
    "Buy-Sell": [
        "A {c} buy-and-sell WhatsApp group for posting items, deals and classifieds. Members trade products locally with quick, friendly negotiation.",
        "Shoppers and sellers in {c} use this WhatsApp group to list products and find bargains. Browse offers, post your items and buy or sell with ease.",
    ],
    "Technology": [
        "A {c} tech WhatsApp community for discussing gadgets, apps, software and digital trends. Share tips and solve tech questions with fellow enthusiasts.",
        "Tech lovers in {c} chat on WhatsApp about the latest devices, programming and internet culture. Get help, share news and explore new tools together.",
    ],
    "Health": [
        "A {c} health and fitness WhatsApp group sharing workout routines, nutrition tips and motivation. Support each other toward a healthier lifestyle.",
        "Members in {c} discuss wellness on WhatsApp, from exercise plans to healthy eating. Find daily motivation and practical health advice in this group.",
    ],
    "Travel": [
        "A {c} travel WhatsApp community for sharing trip ideas, itineraries and travel tips. Plan adventures and discover new destinations with fellow travelers.",
        "Travel fans in {c} chat on WhatsApp about destinations, cheap flights and hidden gems. Exchange experiences and plan your next trip together.",
    ],
    "Movies": [
        "A {c} movies and series WhatsApp group for film lovers. Discuss premieres, share recommendations and chat about favorite shows and sagas.",
        "Cinephiles in {c} gather on WhatsApp to talk films, series and streaming picks. Share reviews, trailers and must-watch lists with the community.",
    ],
    "Entertainment": [
        "A {c} entertainment WhatsApp group for fun daily content, trending topics and celebrity buzz. Chat, share and enjoy light-hearted conversation.",
        "Members in {c} share entertainment news and viral moments on WhatsApp. A relaxed group for daily fun, stickers and lively group chat.",
    ],
    "Food": [
        "A {c} food WhatsApp group where members share recipes, cooking tips and restaurant finds. Swap dishes and discover new flavors together.",
        "Food lovers in {c} chat on WhatsApp about recipes, local eateries and homemade dishes. Share photos, tips and tasty ideas every day.",
    ],
    "Pets": [
        "A {c} pets WhatsApp community for animal lovers. Share photos, care tips and stories about dogs, cats and other beloved companions.",
        "Pet owners in {c} connect on WhatsApp to exchange advice and adorable pet moments. A friendly space for everyone who loves animals.",
    ],
    "Funny": [
        "A {c} humor WhatsApp group full of memes, jokes and funny content. Share laughs daily with members who love a good joke.",
        "Laugh every day in this {c} funny WhatsApp community. Members post memes, comedy clips and jokes to keep the good vibes going.",
    ],
    "Other": [
        "An active WhatsApp community in {c} for friendly daily conversation. Members chat about everyday topics and share experiences together.",
        "A welcoming WhatsApp group for people in {c} to connect and chat. Join the discussion, share your thoughts and meet new friends.",
    ],
    "Regional": [
        "A {c} regional WhatsApp community bringing locals and neighbors together. Share local news, events and everyday conversation with people nearby.",
        "Neighbors in {c} connect here on WhatsApp to chat about local life, events and community topics. A friendly space for regional conversation.",
    ],
}

def clean_name(name, fallback):
    n = ihtml.unescape(name or "").strip()
    n = re.sub(r'\s+', ' ', n)
    if len(n) < 3 or BAD_NAME.match(n) or re.fullmatch(r'[^\w\s]{1,6}', n):
        n = ihtml.unescape(fallback or "").strip()
        n = re.sub(r'\s+', ' ', n)
    # strip control chars
    n = "".join(ch for ch in n if _u.category(ch)[0] != "C")
    return n

def main():
    d = json.load(open(os.path.join(BASE, "team30-progress.json")))
    verified = d["verified"]
    pending = d["pending"]
    porn = d.get("porn_drops", 0)

    out, seen_codes = [], set()
    dropped = 0
    for i, x in enumerate(verified):
        meta = x.get("_meta", {})
        name = clean_name(x["name"], meta.get("title", ""))
        code = x["invite"].split("/")[-1]
        if code in seen_codes:
            dropped += 1; continue
        if not name or len(name) < 3 or BAD_NAME.match(name):
            dropped += 1; continue
        if PORN_RE.search(name) or EMOJI_RE.search(name):
            porn += 1; dropped += 1; continue
        if DROP_RE.search(name):
            dropped += 1; continue
        cat = classify(name + " " + meta.get("desc", "") + " " + meta.get("tag", ""))
        ctry = x["country"]
        cname = COUNTRY_NAME.get(ctry, ctry)
        tmpl = DESC[cat][i % 2]
        desc = tmpl.format(c=cname)
        if PORN_RE.search(desc):
            desc = DESC["Other"][i % 2].format(c=cname)
        seen_codes.add(code)
        out.append({
            "name": name,
            "category": cat,
            "country": ctry,
            "description": desc,
            "invite": x["invite"],
            "image": "",
        })

    json.dump(out, open(os.path.join(BASE, "team30-mexico-ca.json"), "w"), ensure_ascii=False, indent=1)
    if pending:
        json.dump(pending, open(os.path.join(BASE, "team30-unverified-pending.json"), "w"), ensure_ascii=False, indent=1)
    print(f"final verified={len(out)} dropped={dropped} porn_total={porn} pending={len(pending)}")
    # validate
    cats = {}
    for x in out: cats[x["category"]] = cats.get(x["category"], 0) + 1
    print(cats)

if __name__ == "__main__":
    main()
