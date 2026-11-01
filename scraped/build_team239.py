#!/usr/bin/env python3
"""team239-latam: Latin America (Mexico, Argentina, Colombia, Peru, Chile) WhatsApp groups.
Builds ~/workspace/whatsapp-groups-site/scraped/team239-latam.json
Dedupes by code and against the site's existing _seen_all_codes.pkl.
Skips adult-only content.
"""
import json, pickle, os

BASE = os.path.expanduser("~/workspace/whatsapp-groups-site/scraped")
OUT = os.path.join(BASE, "team239-latam.json")

# (code, name, desc, cat, country)
E = [
# ---------- MEXICO ----------
("F0EFr8Xk0KM0wBMTiErY0s","BTS México","Fans de BTS en México: noticias, eventos y comunidad ARMY.","Entertainment","Mexico"),
("EKG1dkhACQYIPTKf7pyypO","U2 México Fans","Fans de U2 en México planeando los conciertos del tour 2027 en CDMX.","Entertainment","Mexico"),
("Fz5hjqDADojDg1OMXV9slH","WIN GROUP MX","Comunidad mexicana WIN GROUP: amistad, convivencia y buen rollo.","Community & Social","Mexico"),
("K6L9HXQyPE2FQCgFcUElWB","UNAM Movilidad Nacional 2026-2","Estudiantes UNAM: movilidad nacional semestre 2026-2, dudas y apoyo.","Education","Mexico"),
("DmdVck7KSgE5WWMUFEjobQ","UNAM Proyectos PITAAE 2026","Estudiantes UNAM coordinando proyectos PITAAE 2026.","Education","Mexico"),
("LmzDCrYgFJP4p238831Pto","Amistades FIFAS","Comunidad de fútbol femenil en México: hacer amistades y jugar.","Sports","Mexico"),
("JyudpFCppw1FOOohXg8PH5","AMPJD Dudas Diplomado","Dudas y apuntes del diplomado de psicología criminal AMPJD, México.","Education","Mexico"),
("GvPrw8FKNjJ31qqbDpiMoA","Grupo SM México Educadores","Educadores mexicanos compartiendo materiales y experiencias.","Education","Mexico"),
("LJ678HnWQ4wJAxvWnfTLUs","Que Viva Lavi Camping","Campamentos, viajes y convivencia para solteros en México.","Travel & Tourism","Mexico"),
("FU4yyO00LV59DRaHDQQoJN","Mensajes Reina de la Paz","Mensajes espirituales y devocionales de la Reina de la Paz, México.","Community & Social","Mexico"),
("EdjLPOUO0rHL08iodsEG9C","Cetmar No. 9 Ciudad Madero","Estudiantes del CETMAR No. 9 de Ciudad Madero, México.","Education","Mexico"),
("Dq7pbEG5avaJZZ2V40V2Pt","Games Army México","Comunidad gamer Games Army: promos, juegos y torneos en México.","Entertainment","Mexico"),
("IHXrQBde5cOGP7qPLPI25c","Finanzas y Café México","Comunidad de finanzas personales y café en México.","Community & Social","Mexico"),
("IdMqBVGRUUC0FM8eTRDJDX","Reporte Ciudadano Irapuato","Reportes ciudadanos y noticias de Irapuato, Guanajuato México.","News","Mexico"),
("GXU0hreJAUd0a0klXDNsiL","Curso Ingreso UNAM Facultad de Ciencias","Grupo de preparación para el examen de admisión a la UNAM, Facultad de Ciencias.","Education","Mexico"),
("K03liSsM7om0pXnyIRXOcZ","Fan Project K-pop CDMX","Grupo de fan project K-pop en Ciudad de México: actividades y eventos.","Entertainment","Mexico"),
("LmzOQ7sNzadEc7IamADiMb","Quintana Roo Hoy","Noticias de Quintana Roo, México.","News","Mexico"),
("Cb66vao83Aq9faApIndqWy","Escuela de Misterios MAAT","Comunidad espiritual y de estudio esotérico en Ciudad de México.","Community & Social","Mexico"),
("HLHKWIvqUEx4bDIpvyO9Lx","Alquimia del Ser CDMX","Encuentro espiritual mensual para mujeres en CDMX, México.","Community & Social","Mexico"),
("JvmK1oleGE7FuGotsYOGjh","Meditación por la Paz México","Meditación semanal en línea por la paz mundial, comunidad CDMX México.","Community & Social","Mexico"),
("KTFEFpEHIjf9kkvRoad0Ml","Seminario Bautista de México","Comunidad académica del Seminario Bautista de México, CDMX.","Education","Mexico"),
("EZgwofyA5mYAk9go2XE8Y0","Alboro Tours Viajeros","Grupo de viajeros de Alboro Tours Guadalajara: destinos y promociones.","Travel & Tourism","Mexico"),
("BoSjn0qQeYaCTpDbWfM5Q7","Mujeres de Oración México","Comunidad de mujeres de oración e intercesión cristiana.","Community & Social","Mexico"),
("LoikQDXkY9HF4r1LodFIBl","AlSer Kam Constelaciones","Grupo de constelaciones familiares y autoconocimiento, Ciudad de México.","Community & Social","Mexico"),
("L0uMATEfpffC8pNGnHiI9Z","Red de Mujeres Holísticas","Red internacional de mujeres holísticas: sanación y rituales.","Community & Social","Mexico"),
("CYdcqFu9DsxL1A5qbIOkZE","Amigos de Granja Cocotla","Comunidad de amigas de la granja agroecológica Cocotla, Texcoco.","Community & Social","Mexico"),
("I8f8s6Riv3ULFJFo7hM7oQ","Atención Psicológica Estudiantes","Comunidad de apoyo en atención psicológica para estudiantes universitarios.","Education","Mexico"),
# ---------- ARGENTINA ----------
("L10m2aD7fF4A4O2h5JqP4J","BTS Argentina","Fans de BTS en Argentina: noticias, eventos y comunidad ARMY.","Entertainment","Argentina"),
("FLnsL4neidoFWuYdiG91YF","U2 Argentina Fans","Fans de U2 en Argentina planeando los conciertos del tour 2027 en Buenos Aires.","Entertainment","Argentina"),
("Eswk7CAeTUsD9hYGDMtbnR","BoatOat Argentina Fanbase","Fanbase argentina de BoatOat: memes, noticias y comunidad.","Entertainment","Argentina"),
("JmBlWo4A24b3a6pgxmCC5k","Belleza Baires Estudio","Cursos de belleza y estética en Buenos Aires, Argentina.","Education","Argentina"),
("ITiTwgyE0bUDzaBErCBlSy","Ferrocarril Urquiza Comunidad","Comunidad vecinal y aficionada al Ferrocarril Urquiza, Argentina.","Community & Social","Argentina"),
("C1eDlhYIQ5t6EEO8QDwhqh","Canotaje Argentina","Aficionados al canotaje y remo en Argentina.","Sports","Argentina"),
("F7AL4pe0Dg10hihF01fnOw","Habla al Mundo Consagración","Comunidad cristiana Habla al Mundo: oración y consagración, Argentina.","Community & Social","Argentina"),
("CxrWUOpPvfZBMIZF47q6EH","Ser y Hacer Malargüe","Noticias y comunidad de Malargüe, Mendoza, Argentina.","News","Argentina"),
("HtBckzLubhR57FuvLfq3ZX","Ser y Hacer Malargüe 2","Noticias y comunidad de Malargüe, Mendoza, Argentina.","News","Argentina"),
("5iVeUlPjJQW7k3yFpqqY4V","InfoBrandsen Comunidad","Noticias y avisos comunitarios de Brandsen, Buenos Aires.","News","Argentina"),
("L6wzuSrC0d92DnyK8mSDfQ","InfoBrandsen Comunidad 2","Noticias y avisos comunitarios de Brandsen, Buenos Aires.","News","Argentina"),
("CTo03UdomC18l7tb3iyqIH","El Camino del Closer 2026","Formación de ventas El Camino del Closer 2026, Argentina.","Education","Argentina"),
("KO483HnQJlhClLuUtUjTkd","Unión Malvinizadora Argentina","Comunidad malvinizadora: memoria y soberanía de las Islas Malvinas.","Community & Social","Argentina"),
("DthrXI1qdtQ3470FMnqcYT","Ballet El Pyaguazu Folklore","Ballet folclórico El Pyaguazu: ensayos, eventos y cultura, Argentina.","Entertainment","Argentina"),
("KiReds1iiwYCB97TyCrWSb","Conciencia Cósmica","Comunidad de espiritualidad y conciencia cósmica en Argentina.","Community & Social","Argentina"),
("CHBaL6ByV2FHEMzKmUwTPQ","Villa María Ya","Noticias y comunidad de Villa María, Córdoba, Argentina.","News","Argentina"),
("CJM5f4sa2V0D4fTlGugRzB","Ahora Mendoza OK","Noticias de Mendoza y Argentina, comunidad Ahora Mendoza.","News","Argentina"),
("J3pO6v8v5qJJ7w96BxxerR","Sociología de la Educación UNSA","Estudiantes de sociología de la educación, Universidad Nacional de Salta.","Education","Argentina"),
("DZMMJuS7vZ9F0XEKNYbe9R","UNSL San Luis Asignatura","Estudiantes UNSL San Luis: clases, exámenes y coordinación de la asignatura.","Education","Argentina"),
("Lq8WiUffNW4HdVOaGfhRLQ","UNSJ LATEA Ingeniería","Visita guiada y comunidad del laboratorio LATEA, UNSJ San Juan.","Education","Argentina"),
("HQIEbWLtwer5AvmGpzh0hw","Trabajadoras del Hogar en Acción","Comunidad de empleadas del hogar en lucha por derechos laborales y obra social, Argentina.","Community & Social","Argentina"),
("KQQiDvA8BLBCMG8cKhGBAn","Santuario de Schoenstatt Belgrano","Comunidad de oración del Santuario de Schoenstatt, Belgrano Buenos Aires.","Community & Social","Argentina"),
("JXuUvIkBR8VKyanyUgFKWa","Practical Philosophy Club BA","Club de filosofía práctica en Buenos Aires: conversaciones profundas y comunidad.","Community & Social","Argentina"),
("GLy0DUbfEjEDPZx8iWlY6n","UNRN Colectivos y Comunidad","Comunidad de estudiantes UNRN Río Negro: recorridos de colectivos e información.","Education","Argentina"),
("Ekz5joyWRonG3jshZMdkCj","Radio Club Argentino Iniciación","Grupo del curso de iniciación a la radioafición, Buenos Aires.","Education","Argentina"),
("FOWgKFDMirQ5D1hISOskyx","Comunidad Amoras","Comunidad de mujeres: afirmaciones, meditaciones y encuentros.","Community & Social","Argentina"),
("ImcGy2Zb7bTJVdbhFqErhj","Amigos del Animal Jujuy","ONG de rescate y protección animal de Jujuy, Argentina.","Community & Social","Argentina"),
("EGTtMwuUBmL6AuC57MvUMD","Viajero Hostel Buenos Aires","Comunidad de viajeros del Viajero Hostel en Buenos Aires.","Travel & Tourism","Argentina"),
# ---------- CHILE ----------
("Yf00438sH8gG23f69fV5d3","BTS Chile","Fans de BTS en Chile: noticias, eventos y comunidad ARMY.","Entertainment","Chile"),
("IkdRGNbI5AD49zTarYyY8H","Red Gentil Chile","Comunidad Red Gentil: apoyo mutuo y amistad en Chile.","Community & Social","Chile"),
("Er7Ioza7aTnDvwuynyH75i","Tomato Republic Chile","Comunidad gamer Tomato Republic Chile: juegos y torneos.","Entertainment","Chile"),
("LQFrC3sLNr08qJl1yvYI6d","Tomato Republic Vanguard","Comunidad Cardfight Vanguard en Chile: torneos y duelos.","Entertainment","Chile"),
("IPQJ5ZUyJJP53eHad5Pefp","Tomato Republic One Piece","Comunidad One Piece en Chile: noticias, cartas y eventos.","Entertainment","Chile"),
("Lib39S11DqmCp1IRICoaZ0","Tomato Republic Hololive","Comunidad Hololive en Chile: vtubers, eventos y convivencia.","Entertainment","Chile"),
("FVzQxrtoVMhAlgm6gwlwNUA","Abundancia Cuántica Chile","Comunidad de desarrollo personal y abundancia cuántica en Chile.","Community & Social","Chile"),
("JgwBAu3hkqK4ekSVrzCU7X","Mega Te Ayuda","Comunidad solidaria Mega Te Ayuda en Chile.","Community & Social","Chile"),
("H0nei76DazOJOe0qvaxwoZ","Mega Te Ayuda 2","Comunidad solidaria Mega Te Ayuda en Chile.","Community & Social","Chile"),
("Lc70SHZcx27IyoPPT9LEBU","Mega Te Ayuda 3","Comunidad solidaria Mega Te Ayuda en Chile.","Community & Social","Chile"),
("FrCsJgtO9LbKYKk0inPhK6","Mega Te Ayuda 4","Comunidad solidaria Mega Te Ayuda en Chile.","Community & Social","Chile"),
("IsdJXs6NvuYHxTBQVSk7t8","Mega Te Ayuda 5","Comunidad solidaria Mega Te Ayuda en Chile.","Community & Social","Chile"),
("DmHPaeJmXMhKvN69BOHqLX","Mega Te Ayuda 6","Comunidad solidaria Mega Te Ayuda en Chile.","Community & Social","Chile"),
("H0ibxRfqlbT3lQNGLzFt3o","Analistas del Tablero","Comunidad de básquet chileno: análisis y debate.","Sports","Chile"),
("FQlgWvo9HlqKXvU2FJy69p","Academia Las Condes","Grupo general de alumnos y profesores de arte y cultura, Las Condes Chile.","Education","Chile"),
# ---------- COLOMBIA ----------
("948l75A21uS81uW9J1R5I4","BTS Colombia","Fans de BTS en Colombia: noticias, eventos y comunidad ARMY.","Entertainment","Colombia"),
("KQj28e8EqNM2oEMSyhxX7P","Que Viva Lavi Colombia","Viajes y camping para solteros en Colombia.","Travel & Tourism","Colombia"),
("IVr1EXqGANYJjxBkqTafuA","ITF Senior Colombia","Tenis senior ITF Colombia: torneos y comunidad de jugadores.","Sports","Colombia"),
("DOxVzvGiGzaIE8JVaA5mHu","Perritos Engativá Bogotá","Ayuda y adopción de perritos en Engativá, Bogotá.","Community & Social","Colombia"),
("G52CrcHCsqY6gYRT8QmNKy","MTA Cundinamarca","Agroclima y comunidad agrícola en Cundinamarca, Colombia.","Community & Social","Colombia"),
("Ktx0jzc7gTEAhkoQ1zxtCZ","UNAL Medellín Posgrados","Aspirantes a posgrados UNAL Medellín: dudas y preparación.","Education","Colombia"),
("JCfSH24ahV7EIDcphjnk56","Bomberos Del Mundo Colombia","Comunidad Bomberos Del Mundo en Colombia.","Community & Social","Colombia"),
("EYAEJJ41eag043hpPKgPN9","Parque Biblioteca Tomás Carrasquilla","Comunidad del Parque Biblioteca Tomás Carrasquilla, Medellín.","Education","Colombia"),
("LcAgJwpcIecGD9PNfFnVta","Travelemprendedores","Comunidad de viajeros emprendedores en Colombia.","Travel & Tourism","Colombia"),
("FpI1d5d3aMaC2PqNwzVMYt","Club de Inglés Unicauca","Club de conversación en inglés, Universidad del Cauca, Popayán.","Education","Colombia"),
("L30p3WYWFBlHtBkwgd0QjY","CENESIS Universidad del Valle","Centro de Estudios de Ingeniería de Sistemas, Universidad del Valle Cali.","Education","Colombia"),
("JVoC7xM9NIz6K6T5oQrX4j","Rescate La Monita Colombia","Comunidad de rescate y ayuda para perritas en Colombia.","Community & Social","Colombia"),
("Hg12z5iF8gW2Tzp6xoGBiT","Nueva Colonia Turbo Comunidad","Comunidad de Nueva Colonia, Turbo Colombia: noticias y ayuda mutua.","Community & Social","Colombia"),
("HYRHUkwPG4f7KB","Biblioteca Fernando Gómez Martínez","Comunidad de la Biblioteca Fernando Gómez Martínez, Robledo Medellín.","Education","Colombia"),
("IoqBYKqdYXz2qymYEzsaoo","Medellín Hike Club","Club de senderismo en Medellín: caminatas, cascadas y nuevas amistades.","Travel & Tourism","Colombia"),
("HPtI8QwUWPgCCXGZuNcufh","Parroquia Dolores La América","Comunidad parroquial de Nuestra Señora de los Dolores, La América Medellín.","Community & Social","Colombia"),
("DNkuZAsAyXE2rkGlM0dTGg","Memorias del Tablón Bogotá Azul","Comunidad de hinchas de Millonarios FC Bogotá: recuerdos e información.","Sports","Colombia"),
("LNVYT5j6umc0fDsvsD9yBN","Colegio de la Presentación Medellín","Grupo institucional de padres de familia del Colegio de la Presentación, Medellín.","Education","Colombia"),
("I5MV5O3XtiUIoeCzYKKP0p","Nubia Rescata y Protege","Comunidad de rescate y protección animal en Colombia.","Community & Social","Colombia"),
# ---------- PERU ----------
("42R38S8B5G8sH5f9F3g3I5","BTS Peru","Fans de BTS en Perú: noticias, eventos y comunidad ARMY.","Entertainment","Peru"),
("JqmNCBhUSPi4CDSLlvqsB0","CODE 2025 Emprendedores UNI","Comunidad de emprendimiento del evento CODE 2025 en la UNI, Lima.","Education","Peru"),
("JGRl8SkRFyiDP84S5qeXOT","TEC UNI Reincorporados","Grupo de apoyo para estudiantes UNI en riesgo académico y reincorporados.","Education","Peru"),
("G6HChq85CfqEOIyPuHEVnj","Noticias Trujillo","Noticias y reportes ciudadanos de Trujillo, Perú.","News","Peru"),
("KUAdtitahfLDyCGVpoX0UV","Sonora Estéreo 98.4 FM","Comunidad de oyentes de Sonora Estéreo, emisora de la Escuela de Tecnologías de Antioquia.","Entertainment","Colombia"),
("JRngg1nAKMF1dMFdA2itXZ","Vitrina Vintage Perú","Coleccionistas de vintage en Perú: compra, venta y comunidad.","Community & Social","Peru"),
("FyQZOEoB1gt4NPCZZKsRo3","Cámara Perú-Rusia Padres","Padres de familia de la Cámara Perú-Rusia: coordinación escolar.","Education","Peru"),
("JdReAlHvgBZJrGv5eAV5NO","Jóvenes Ileños Ilo","Voluntarios jóvenes de Ilo: actividades y ayuda comunitaria, Perú.","Community & Social","Peru"),
("HnkwqGKYAATKdaMgS6Tyj3","Sentimiento Sikuris UNAP","Conjunto de sikuris de Ingeniería Civil, UNAP Puno, Perú.","Entertainment","Peru"),
("Kutl7ePYwh6H5VOqeyBba1","RUA UNSA Becas","Becas y oportunidades para estudiantes UNSA Arequipa, Perú.","Education","Peru"),
("DNcozaRW5AJGw34eGh1LsS","IPAE Perú Salud","Curso de salud IPAE Perú: estudiantes y profesionales.","Education","Peru"),
("HbxVBBbG6cs7qoXKMJTQqu","EDU CREA Chosica","Comunidad educativa EDU CREA en Chosica, Perú.","Education","Peru"),
("GPwBFNbjRL6J5NIHQ5xY26","EDU CREA Maestros","Maestros de la comunidad educativa EDU CREA, Perú.","Education","Peru"),
("IyQGhwxHFbXEst9TULnZqj","WL Academy Cajamarca","Academia WL en Cajamarca: clases y comunidad estudiantil.","Education","Peru"),
("LlYIK5ba1ZhGuoNLMednrp","Academia San Ignacio Sicuani","Academia preuniversitaria San Ignacio de Loyola, Sicuani Perú.","Education","Peru"),
("JFrKo9V83xIDXHfnIpYRdm","Ciencias Forenses Perú","Estudiantes de ciencias forenses CEPESFORCRI, Perú.","Education","Peru"),
("HZ1D5cVSWs97mqsiai2i2K","ISSI Medicina Natural","Comunidad ISSI de medicina natural en Perú.","Education","Peru"),
("GpwhtglhmkuFbxR0mnvxqU","Capacitaciones JC Huacho","Centro de capacitaciones JC en Huacho, Perú.","Education","Peru"),
("JtxgZOcn5QuLAmmFwnjPuV","Miss Kary Docentes Chiclayo","Comunidad de docentes y auxiliares de educación, Chiclayo Perú.","Education","Peru"),
("HhL22l7Di0G1SPoX8SPXk7","FitnessClub Perú Mami Fitness","Grupo de mujeres Mami Fitness: bienestar y pérdida de peso saludable, Nuevo Chimbote Perú.","Community & Social","Peru"),
("LKFJl2NjW7mApZbdBXuzW6","IPAE Perú Humanización del Cuidado","Curso gratuito de humanización del cuidado en salud, IPAE Perú.","Education","Peru"),
("JbsGQpXk1xG1fddNrj3ysJ","Danzas Folclóricas Pacora","Grupo de danzas folclóricas costa, sierra y selva, Pacora Perú.","Entertainment","Peru"),
("LmervIZ7OaUKhYigPuS0KW","Ayuda Perrito Mustafa","Comunidad de ayuda para el rescate del perrito Mustafa, Perú.","Community & Social","Peru"),
("IzKrBT9uVIXGBo8mhlRThG","Evidencia.pe Noticias","Noticias de Arequipa y el sur del Perú.","News","Peru"),
("Gnx4yp4CtlG9yQTYmFh0oR","Café Deportivo Podcast","Podcast de fútbol peruano: análisis y debate de la selección y la liga.","Sports","Peru"),
("B76Dnl4u011FSeizI55HHu","Ferroviarios del Altiplano","Grupo de la pandilla puneña de carnavales de Puno: ensayos y actividades.","Entertainment","Peru"),
("JeBkSPIvcS8Cdr2TukiTzH","Misión Académica Medellín Inspira","Misión académica de arquitectura de la Universidad Continental a Medellín.","Education","Peru"),
("ERAHtYzzsNu5Ux8VTfeIi1","CESCDAC Simulados EsSalud","Simulacros de examen para postulantes a EsSalud, CESCDAC Facultad de Medicina UNT Trujillo.","Education","Peru"),
("CcmNSMb3N4TB0oNqTWHZWZ","THEMIS Seminarios PUCP","Seminarios de derecho THEMIS en la PUCP, Lima: eventos y preventas.","Education","Peru"),
("CxUOsBkkzQqKDZbsjuSapO","PROA Voluntariado Perú","Voluntariado social PROA en el Perú: Refugio de Sonrisas y programas.","Community & Social","Peru"),
("ENBNLXTtpk1I5yQaOAiA8g","APEMH UCSUR Endocrinología","Curso de introducción a la fisiología endocrina, APEMH UCSUR Lima.","Education","Peru"),
("ELOir8A374t7VuYhPfESdr","Tuna Femenina Continental Arequipa","Tuna femenina novata de la Universidad Continental, Arequipa: música y viajes.","Entertainment","Peru"),
("LLWjBwbQEAQBITpwUzAWw2","CF Sociales UNMSM Danza","Elenco de danza folclórica del Centro Federado de Sociales, UNMSM Perú.","Entertainment","Peru"),
("CURWPFa5DcK4rTCzQybX9Y","Comunidad Yhor Velásquez Pasco","Comunidad de seguidores de Yhor Velásquez en Pasco, Perú.","Community & Social","Peru"),
("BbJaVB92FYS2TboMzU7ILj","Edición Especial Perú","Comunidad del programa Edición Especial: noticias del Perú.","News","Peru"),
]

ADULT = ("porn","xxx","nude","escort","call-girl","sexy","adult","nopor")
out = []
seen = set()
for row in E:
    code, name, desc, cat, country = row
    if code.lower() in seen:
        continue
    seen.add(code.lower())
    t = (name+" "+desc).lower()
    if any(k in t for k in ADULT):
        continue
    out.append({"name": name,
                "invite": "https://chat.whatsapp.com/"+code,
                "description": desc,
                "category": cat,
                "country": country,
                "image": ""})

# dedupe against site's existing seen-set
try:
    with open(os.path.join(BASE,"_seen_all_codes.pkl"),"rb") as f:
        seen_all = pickle.load(f)
    print("seen-set size:", len(seen_all))
    before = len(out)
    out = [e for e in out if e["invite"].rstrip("/").split("/")[-1] not in seen_all]
    print("dropped (already on site):", before-len(out))
except Exception as ex:
    print("seen-set check skipped:", ex)

with open(OUT,"w",encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("saved:", len(out), "->", OUT)
