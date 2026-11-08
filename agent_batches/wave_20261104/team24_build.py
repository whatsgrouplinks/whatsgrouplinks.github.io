import json, re, os

W = os.path.expanduser("~/workspace/whatsapp-groups-site/agent_batches/wave_20261104")
union = set(json.load(open(os.path.join(W, "dedupe_union.json"))))
print("union size:", len(union))

def item(name, category, country, description, code, note):
    return {"name": name, "category": category, "country": country,
            "description": description,
            "invite": "https://chat.whatsapp.com/" + code,
            "image": "", "note": note}

C = []  # candidates
J = "Jobs"
def jobs_eu(name, country, code, blurb):
    C.append(item(name, J, country,
        "Europe job group: %s. Members share vacancies, hiring news and work-permit updates for job seekers across Europe." % blurb,
        code, "transport failure"))

# ---- whtspgrouplink Europe Jobs page (plain codes only; /invite/ excluded per brief) ----
jobs_eu("Europe Job Updates", "International", "KGEDzFN6F7R78Sbf8wFXeH", "daily job updates and vacancy alerts")
jobs_eu("Work Opportunities in Europe", "International", "GY2h6vsoalE0s28Zb8CCkr", "work opportunities for foreigners and locals")
jobs_eu("Germany Hiring Group", "DE", "B9FTo33wJdK2Y4O0JSFzcg", "hiring alerts and vacancies in Germany")
jobs_eu("Italy Job Vacancy update group", "IT", "DBkO2HtwmTd0jvKFAXTAYW", "job vacancy updates across Italy")
jobs_eu("Factory & Warehouse Work", "International", "BLO9IR6CXrtBgndJynxzLh", "factory and warehouse openings in Europe")
jobs_eu("Romania Job Board", "RO", "Fa5Hg8Z0nfi1FZrTwbS4S6", "job postings and hiring news in Romania")
jobs_eu("Poland Job Employment Updates", "PL", "IMP7aVpX4ftL8UBGfeQD8c", "employment updates and job offers in Poland")
jobs_eu("Ireland student jobs", "IE", "ImZqrXnoncHBlqF7PE4XCP", "student and part-time jobs in Ireland")
jobs_eu("Construction Work Europe", "International", "49kTWkQtj026Os7BPbJQw6", "construction site jobs across Europe")
jobs_eu("Driving Jobs Europe", "International", "JlEJmBPpWbNCxRhtGvpXsK", "driving and delivery jobs in Europe")
jobs_eu("Luxembourg Civil Engineering Jobs", "LU", "H2Ciiiy6zqUI9QZdOosD7b", "civil engineering vacancies in Luxembourg")
jobs_eu("Healthcare Careers Europe", "International", "LCgWBRSbDwM3OryD1YlaWZ", "nursing and healthcare careers in Europe")
jobs_eu("Cleaning & Support Jobs", "International", "A4cIRWznHih8aevuyFn3rO", "cleaning and support staff jobs in Europe")
jobs_eu("Hotel Restaurant Hiring in Denmark", "DK", "GxtAj4WByea7nATjhkqbGM", "hotel and restaurant hiring in Denmark")
jobs_eu("Europe Work Permit Openings", "International", "Gkt8Z5dVSusGExjl2M041i", "work-permit and visa-sponsored openings")
jobs_eu("Latest Hiring Alerts Europe", "International", "Bp5o2SX0MTWCnPWyXjIloU", "latest hiring alerts across Europe")
jobs_eu("Europe Jobs WhatsApp Group", "International", "GjjdlgaeaRQFUaErwm0c6m", "general Europe jobs discussion and alerts")
jobs_eu("Slovakia Work Permit Jobs Group", "SK", "Ls1MX9T9o5g0yrNuvBjgIY", "work-permit jobs in Slovakia")
jobs_eu("Europe Jobs for Foreigners", "International", "9E99NgaQHJIIvvrqigLXgj", "jobs open to foreigners across Europe")
jobs_eu("Europe Visa Sponsorship Jobs", "International", "IfzlYseoUKVIXetoztpkVI", "visa-sponsored job postings in Europe")
jobs_eu("Germany Jobs WhatsApp Group", "DE", "ETQIL5T9LTNDYquElEZtlF", "job vacancies and career news in Germany")
jobs_eu("Italy Jobs WhatsApp Group", "IT", "Fq8ilk6Hc2mJ1AxmuavHg8", "job vacancies and career news in Italy")
jobs_eu("Poland Jobs WhatsApp Group", "PL", "KMn79IsWBpOGSadKRskINe", "job vacancies and career news in Poland")
jobs_eu("Europe Skilled Jobs Group", "International", "GQW5cvQPal83AUTXOdZEA3", "skilled and technical roles in Europe")
jobs_eu("Sweden Unskilled Jobs Europe", "SE", "GldIugP0fiE0alKMarSyYw", "entry-level and unskilled jobs in Sweden")
jobs_eu("Europe Warehouse Jobs Group", "International", "GOxgy6DnAndJgnAiurhpFH", "warehouse and logistics jobs in Europe")
jobs_eu("Europe Healthcare Jobs Group", "International", "CquYsxZ3mHY7tkgMyQXni3", "healthcare job openings across Europe")
jobs_eu("Europe Construction Jobs Group", "International", "LTyrhLI2wymFPt8xUZixrw", "construction job openings across Europe")
jobs_eu("Latest Europe Job Vacancies", "International", "FhZSeEJtgHVFq8jA8b9YCX", "latest vacancies posted daily across Europe")
jobs_eu("France government job", "FR", "EKgpcr4i4rzBvgEdHNRJRN", "government and public-sector job alerts in France")
jobs_eu("Germany people part time Job", "DE", "HNpI2Ll9z3w7MPpcVycQGx", "part-time jobs for people in Germany")
jobs_eu("Italy Jobs for indians", "IT", "DiiFHVKcZfaAZKtj0KHYa9", "Italy jobs of interest to Indian workers")
jobs_eu("Belgium british job", "BE", "IVajeVsJfgcFJOHIX5uSFS", "job postings in Belgium")
jobs_eu("Romania Writing Jobs", "RO", "CtjZYd5wvBJ4TBr0wrNPDK", "writing and content jobs in Romania")
jobs_eu("Hungary Private Job whatsapp", "HU", "E2jhEeT3Hq0B3ZUDaqsxUw", "private-sector job postings in Hungary")
jobs_eu("Hiking Norway Jobs", "NO", "IX1zxxn9mJmE3ofKmsrtQo", "jobs in Norway including outdoor and hiking roles")
jobs_eu("Czech Republic Jobs Group", "CZ", "HxCca2QxEEcFc3M0wPqJ2B", "job vacancies in the Czech Republic")
jobs_eu("Austria Jobs Group", "AT", "KTkcFCpAE3SGVvVqcqFdBu", "job vacancies in Austria")
jobs_eu("Denmark Jobs Group", "DK", "JbPItwbef2X7DnHHzZB0SR", "job vacancies in Denmark")
jobs_eu("New be Ireland Jobs", "IE", "Hkxg5XGDsut2k4dT7r6obg", "new job postings in Ireland")
jobs_eu("Greece Jobs Group", "GR", "Fuc3jWZw7Rl2NsZoUY7wlm", "job vacancies in Greece")
jobs_eu("Europe Croatia Job alerts daily", "HR", "D68Kkoey8F7KLAFWB4uNwA", "daily job alerts in Croatia")
jobs_eu("Slovenia Jobs Chatting", "SI", "Hx3Ps9tWoKSHXxSn510Pfc", "job chat and openings in Slovenia")
jobs_eu("Latvia female Jobs wa", "LV", "FjTjeWEnIVS05PrxpARZdK", "job postings in Latvia")

# ---- alzado.org Spain listicle ----
def es(name, cat, code, desc):
    C.append(item(name, cat, "ES", desc, code, "transport failure"))
es("Fans de Rafael Nadal", "Sports", "Fo8vWNxTW3jH2ikzOWzGze",
   "Fan community for Rafael Nadal supporters in Spain sharing match news, results and tennis talk.")
es("Ley de Segunda Oportunidad", "Finance", "KuGAGDaDK4h3ziWxsje9KG",
   "Spanish group about the Second Chance debt-relief law, helping members understand how to clear debts legally.")
es("Grupo de Cachimbas", "Buy-Sell", "KF9RaisOxI646nGwbqAlId",
   "Buy and sell group for hookahs and shisha accessories in Spain.")
es("Grupo de Cachimbas Bilbao", "Buy-Sell", "LJL4ZZknF7ZI0uYu6cVhKT",
   "Buy and sell group for hookahs and shisha accessories in Bilbao, Spain.")
es("Grupo de Cachimbas Zaragoza", "Buy-Sell", "J27HV94AOgjE77IpNpquPK",
   "Buy and sell group for hookahs and shisha accessories in Zaragoza, Spain.")
es("Grupo de Cachimbas Sevilla", "Buy-Sell", "Cd5bxO49Su3GKsT8UnZ3ig",
   "Buy and sell group for hookahs and shisha accessories in Sevilla, Spain.")
es("Grupo de Cachimbas Málaga", "Buy-Sell", "B7T0bpsbSFYArw03FQqQIG",
   "Buy and sell group for hookahs and shisha accessories in Málaga, Spain.")
es("Grupo de Cachimbas Ciudad Real", "Buy-Sell", "H0JrxYtFRGE9SNanS4QkzY",
   "Buy and sell group for hookahs and shisha accessories in Ciudad Real, Spain.")
es("Plantillas de Email para enviar CV", "Jobs", "CIAo7pabiWl3CAf5mM28oc",
   "Spanish job-seeking group sharing email templates for sending CVs to employers.")
es("Como Dormir Mejor", "Health", "FY3Y0nWMRZ93uYeERNLYud",
   "Spanish wellness group sharing tips and techniques to fight insomnia and sleep better.")
es("Grupo para amigos invisibles", "Funny", "KSwb7iUIal0JsqnSKCv0wJ",
   "Spanish Secret Santa group with an app to organize anonymous gift exchanges among friends.")
es("Grupos de WhatsApp para encontrar trabajo", "Jobs", "EuxD617z9q47n1WAyxlkNT",
   "Spanish job-seeking group where members share their profiles and job offers.")
es("Reto 5 días para cuidarse", "Health", "GpnXAmPYZZy4iknaBGolqj",
   "Free five-day wellness challenge group with daily coaching, healthy recipes and self-care tips for women.")
es("Wuolah Grupo Albacete", "Education", "IcB4rTjyjlD9l44HJ91BF2",
   "Study-notes sharing group for university students in Albacete, Spain.")
es("Wuolah Grupo Madrid", "Education", "FV3HegOaErn0hACCBojiXP",
   "Study-notes sharing group for university students in Madrid, Spain.")
es("ADE Autónoma de Madrid", "Education", "CJaw6I56sQeAJbJVG42BUj",
   "Business administration students group at the Autonomous University of Madrid sharing notes and exam help.")

# ---- whatshub.es embedded codes ----
C.append(item("Valencia Freelancers & Founders", "Business", "ES",
   "Bilingual networking community in Valencia, Spain for freelancers, founders and small businesses to connect and collaborate.",
   "I6YyRoHD5528ydpkjSBc6F", "transport failure"))
C.append(item("Alicante Activities", "Community", "ES",
   "International meetup community in Alicante, Spain organizing language exchanges, hikes, dining, treks and social events.",
   "JLSOEoylQ4P2kpn5k5VFQ0", "transport failure"))
C.append(item("Madrid Hardtech Community", "Music", "ES",
   "Madrid techno and rave community for locals and expats over 25 to meet friends and go to parties together.",
   "G51u474vQQcFGMBhr34duY", "transport failure"))
C.append(item("Madrid Senderismo Yoga", "Travel", "ES",
   "Hiking and social club in Madrid for people aged 40 to 65 doing day routes around the Community of Madrid plus yoga and weekend trips.",
   "BVfzbYyufkg6AEsjBFAsSc", "transport failure"))

# ---- uclm.es EU-Spain networking ----
def net(name, code, country, cat, blurb):
    C.append(item(name, cat, country,
        "Networking group for Spanish professionals in EU institutions: %s. Members share vacancies, interview tips and career information." % blurb,
        code, "transport failure"))
net("Jóvenes Profesionales", "J4zuW8S3OedG4NU1n4UQNr", "ES", "Jobs", "young professionals under 35")
net("Perfil Administrativos", "DUsiQayPrbC6gcCPPLaVSY", "ES", "Jobs", "administrative profiles")
net("Perfil Auditoría", "CBFnQPMSFa22uHJnomu9rF", "ES", "Jobs", "audit profiles")
net("Perfil Agrónomos", "DNBcsPTirr21RUxDIpGRcw", "ES", "Jobs", "agronomy profiles")
net("Perfil Building", "I5YcrZg4ETQAfGwp8f324a", "ES", "Jobs", "building and facilities profiles")
net("Perfil Comunicación", "BHzE1lXMNqV3Rd6ykCyr1O", "ES", "Jobs", "communication profiles")
net("Perfil Derecho", "HLdiPsNWhSP6cqZAAm0zOl", "ES", "Jobs", "law profiles")
net("Perfil Estadística Data", "Idb1gldS4p4CqNnzdCKkEI", "ES", "Jobs", "statistics and data profiles")
net("Perfil External Relations", "Kk45183fon2BrC1UFPLyzT", "ES", "Jobs", "external relations profiles")
net("Perfil Financiero", "EWI8NGAZL1hFZ1Jyim1fbU", "ES", "Finance", "finance profiles")
net("Perfil Gestión de Proyectos", "CZVqQ79NcmV6MIXnQVFE26", "ES", "Jobs", "project management profiles")
net("Perfil Ingenierías", "BkYv6SzUGth3xVXLEC29hm", "ES", "Jobs", "engineering profiles")
net("Perfil IT", "DZSRaA8DQxJ9U8Dc3mEmQK", "ES", "Technology", "IT profiles")
net("Perfil Políticas", "GAh3728Ukn9BJFLOojHkHq", "ES", "Jobs", "policy profiles")
net("Perfil Psicología", "K0biperp4PwHiy31SztBvd", "ES", "Jobs", "psychology profiles")
net("Perfil Recursos Humanos", "H2LzxtTGfoSDjCoWTB8sGJ", "ES", "Jobs", "human resources profiles")
net("Perfil Sanitarios", "If97EUEpfwTJjCBOb114dh", "ES", "Health", "healthcare profiles")
net("Perfil Traducción", "J03fuu6HBwJ43GPEa2OOGS", "ES", "Jobs", "translation profiles")
net("Vacantes Luxemburgo", "FiPnqFhpEIF09eMPcr4rkh", "LU", "Jobs", "job vacancies in Luxembourg")

# ---- feaa.uvt.ro Romania ----
def ro_edu(name, code):
    C.append(item(name, "Education", "RO",
        "Student study group at the West University of Timisoara in Romania for %s, sharing notes, exam help and course updates." % name,
        code, "transport failure"))
ro_edu("Contabilitate și informatică de gestiune", "FGUsrDbZcDpIieSo6clFKU")
ro_edu("Contabilitate și informatică de gestiune ID", "HVxNIOw89oZCK3SFm0E8oZ")
ro_edu("Contabilitate și informatică de gestiune (Germană)", "IH6l1wF5vcxCvW2zMORaf1")
ro_edu("Economia comerțului, turismului și serviciilor", "FCUmctjaOaPE0fEO34jZuM")
ro_edu("Economie generală și comunicare economică", "DtdWCZheHgJBNsAb2ADhlR")
ro_edu("Economie și afaceri internaționale", "KniPNmA6HI3DDgJNJNb31z")
ro_edu("Finanțe și bănci", "LDP8M6jYaWZ8xJ4LP6tkCk")
ro_edu("Finanțe și bănci ID", "DTzcCy2JUgR6eUXli88h1F")
ro_edu("Finanțe și bănci (Engleză)", "GOA6XYxxDp0GRTiZaPxk4C")
ro_edu("Informatică economică", "HsyeVdynjPYDU5m5qPUO6s")
ro_edu("Management", "HYXgluwyZYXBMFmsSpM3PP")
ro_edu("Management ID", "CDltLvlIyITEvylYEXfcD0")
ro_edu("Management (Franceză)", "KzkjdJHT5JT5h99gooIY7k")
ro_edu("Marketing", "FXFSfDfZryRED4Da4mf3ZM")

# ---- UPB Google Doc ----
def upb(fac, code):
    C.append(item("UPB " + fac, "Education", "RO",
        "Student study group of the Politehnica University of Bucharest in Romania for the %s faculty community, sharing class notes and exam tips." % fac,
        code, "transport failure"))
for fac, code in [("IE","KjnzcyhUwxbEHxw2hWnhCv"),("Energ","F8dWA1MfeI535IwT9PIubv"),
 ("AC-CTI 1","CUyjkmyJv7EHJwOATtolhY"),("AC-CTI 2","Ivb3Qu5LagE3KMVsP7kF2h"),
 ("IS","J76f7yX24M3Gc1pw1I8mMG"),("ETTI","BGxQH3zYLPfCmBHK8JKkNd"),
 ("ETTI ENG","I5fPzBkue4L9BhvNizIWjT"),("CTI","LXqD3OYcPIR8i8YpdjdHrE"),
 ("IMM","FdHY5DLYxD8IwB8vehnbj5"),("IIR","GjuKwxK10LMCH7sWIqC7NS"),
 ("MR","Fi87kMq8lF34UOGAnHN2cMu"),("ISB","BID6VcbtFGAL86OFVgiuGw"),
 ("TR","FONkJEZI1rq3MoiIm6zLY8"),("IETTI","LVL1aQ1vXJC1nIaVvX6ZL9"),
 ("IA","LeQ8BoCSk1XDHilxLRSfHK"),("SIM","LRsyALTX1NVJRycAPPzkSw"),
 ("CASM 1","E6sHq57uPKh1jmVY1A8AeB"),("CASM 2","BcZCXJtnTq1CSytct8SdOH"),
 ("ILS","Cx3gCEya965BJn6g5yge8q"),("IETTI ENG 2","HaMj007UA5aGJkGE1YGJkh"),
 ("CTI ENG","HXyuiL2WyfHAJyxjXrg3cw"),("IETTI FR","Ip2tig05AwlHhd4f9rxAfH"),
 ("CTI FR","GcwuvVGGgvV0g3JQwVX3Pq"),("SA","DQ0NumqpOy9IoCfJkEAWlt"),
 ("IM","G5uSVduGi2P78Ow045EPuR"),("AIMA","IrHmpjm3MBuEv1HENFYJVq")]:
    upb(fac, code)

# ---- epfl.ch ----
C.append(item("Asociația Studenților Români din EPFL", "Community", "RO",
   "Community group of the Romanian Students Association at EPFL in Lausanne, Switzerland, sharing events, meetups and practical info for Romanian students.",
   "EUuFAEsxS7c67BMObZ0d5r", "transport failure"))

# ---- afr-chalmazel FR covoiturage (personal-format links) ----
def fr_cov(name, code):
    C.append(item(name, "Travel", "FR",
        "Carpooling coordination group in France for families of the same village organizing rides to the leisure centre.",
        code, "transport failure; personal-format invite link from organizer PDF"))
fr_cov("Saint Bonnet covoiturage centre de loisirs", "DSGtepNfaBiLb9nugtV8yy")
fr_cov("Sauvain covoiturage centre de loisirs", "Fj0wU2LmB9LCFmgk0AN3y7")
fr_cov("Saint Just en bas covoiturage centre de loisirs", "FBABBI5kyH0JXUbQN7i9KI")
fr_cov("Saint Georges en Couzan covoiturage centre de loisirs", "JPxBTeIkeom4vbs5Z9NWCS")
fr_cov("Palogneux covoiturage centre de loisirs", "GKrbH9dGaP51qAmCfOAqHK")

print("raw candidates:", len(C))
# sanity: code format
bad = [c for c in C if not re.fullmatch(r"[A-Za-z0-9]{20,24}", c["invite"].rsplit("/",1)[-1])]
print("bad-format:", len(bad), [b["invite"] for b in bad])
# dedupe vs union + within batch
seen = set(); out = []; dup_union = 0; dup_batch = 0
for c in C:
    code = c["invite"].rsplit("/",1)[1]
    if code in union: dup_union += 1; continue
    if code in seen: dup_batch += 1; continue
    seen.add(code); out.append(c)
print("dup_union:", dup_union, "dup_batch:", dup_batch, "kept:", len(out))
# /invite/ check (should be zero)
inv = [c for c in out if "/invite/" in c["invite"]]
print("invite-format kept:", len(inv))

with open(os.path.join(W, "team24-europe-dirs.json"), "w") as f:
    json.dump([], f, ensure_ascii=False, indent=1)
with open(os.path.join(W, "team24-unverified-pending.json"), "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("wrote team24-unverified-pending.json with", len(out))
by_country = {}
for c in out: by_country[c["country"]] = by_country.get(c["country"],0)+1
print("by country:", by_country)
