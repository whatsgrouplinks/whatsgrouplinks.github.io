import requests, re, json
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
s = requests.Session()
def get(url, timeout=90):
    try:
        r = s.get(url, headers=UA, timeout=timeout)
        return r.status_code, r.content
    except Exception as e:
        return None, f"ERR {e}".encode()

# UCLM PDF
st, c = get("https://www.uclm.es/-/media/Files/C01-Centros/CEE/Recomendaciones/GRUPOS-Networking-Espanoles-UE_230324_082900.ashx?la=es")
print("UCLM status", st, "bytes", len(c))
open("team24-uclm.pdf","wb").write(c if isinstance(c, bytes) else b"")
# Rotary PDF
st, c = get("https://rotary2202.es/es/file/6942698c0b35a/download")
print("Rotary status", st, "bytes", len(c))
open("team24-rotary.pdf","wb").write(c if isinstance(c, bytes) else b"")
# meetup page
st, c = get("https://www.meetup.com/deplanespormadrid/")
print("meetup status", st, "bytes", len(c))
open("team24-meetup.html","wb").write(c if isinstance(c, bytes) else b"")
# elyex
st, c = get("https://elyex.com/grupos-de-whatsapp-ecuador-link-unirse-colegios-amistad-ligar-5/")
print("elyex status", st, "bytes", len(c))
open("team24-elyex.html","wb").write(c if isinstance(c, bytes) else b"")
# whts.club sitemap
st, c = get("https://whts.club/news_pages.xml")
print("whts sitemap status", st, "bytes", len(c))
open("team24-whts-sitemap.xml","wb").write(c if isinstance(c, bytes) else b"")
