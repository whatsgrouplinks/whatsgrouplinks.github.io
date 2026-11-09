import subprocess, os
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
urls = {
 "hubrecipes_news": "https://hubrecipes.com/active-news-whatsapp-group-links/",
 "groupor_news": "https://www.groupor.link/group/category/news-magazines-politics",
 "hubrecipes_pk": "https://hubrecipes.com/active-pakistani-whatsapp-group-links/",
}
for name, url in urls.items():
    out = f"team23_raw/{name}.html"
    if os.path.exists(out) and os.path.getsize(out) > 5000:
        print(name, "cached", os.path.getsize(out)); continue
    subprocess.run(["curl","-sL","--max-time","60","-A",UA,url,"-o",out], capture_output=True)
    print(name, os.path.getsize(out) if os.path.exists(out) else "MISSING")
