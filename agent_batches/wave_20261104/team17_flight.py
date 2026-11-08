"""team17: parse TanStack flight-data ($R[N]={...}) records from category HTML."""
import re, html as htmlmod

REC_START = re.compile(r'\$R\[(\d+)\]=\{')

FIELD_RES = {
    "id": re.compile(r'(?:^|[,{])id:"((?:[^"\\]|\\.)*)"'),
    "name": re.compile(r'(?:^|[,{])name:"((?:[^"\\]|\\.)*)"'),
    "description": re.compile(r'(?:^|[,{])description:"((?:[^"\\]|\\.)*)"'),
    "category": re.compile(r'(?:^|[,{])category:"((?:[^"\\]|\\.)*)"'),
    "country": re.compile(r'(?:^|[,{])country:"((?:[^"\\]|\\.)*)"'),
    "language": re.compile(r'(?:^|[,{])language:"((?:[^"\\]|\\.)*)"'),
    "link": re.compile(r'(?:^|[,{])link:"((?:[^"\\]|\\.)*)"'),
    "image": re.compile(r'(?:^|[,{])image:"((?:[^"\\]|\\.)*)"'),
}
CODE_RE = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
INVITE_RE = re.compile(r'chat\.whatsapp\.com/invite/')

def unesc(s):
    # JS string escapes: \" \\ \n \uXXXX
    try:
        return s.encode("utf-8").decode("unicode_escape").encode("latin1").decode("utf-8", "replace")
    except Exception:
        return s.replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\")

def extract_records(html_text):
    """Yield dicts for each $R[N]={...} record containing a link field."""
    out = []
    for m in REC_START.finditer(html_text):
        i = m.end()  # position after '{'
        depth = 1
        instr = False
        esc = False
        j = i
        n = len(html_text)
        while j < n and depth > 0:
            c = html_text[j]
            if instr:
                if esc:
                    esc = False
                elif c == '\\':
                    esc = True
                elif c == '"':
                    instr = False
            else:
                if c == '"':
                    instr = True
                elif c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
            j += 1
        body = html_text[i:j - 1]
        if 'link:"' not in body and "link:'" not in body:
            continue
        rec = {}
        for k, rx in FIELD_RES.items():
            fm = rx.search(body)
            if fm:
                rec[k] = unesc(fm.group(1))
        if rec.get("link"):
            out.append(rec)
    return out

def records_to_candidates(recs):
    cands = []
    for r in recs:
        link = r.get("link", "")
        cm = CODE_RE.search(link)
        if not cm:
            continue
        if INVITE_RE.search(link):
            continue  # channel
        code = cm.group(1)
        cands.append({
            "name": htmlmod.unescape(r.get("name", "")).strip(),
            "description": htmlmod.unescape(r.get("description", "")).strip(),
            "category_badge": r.get("category", ""),
            "country_badge": r.get("country", ""),
            "code": code,
            "image": r.get("image", ""),
            "rec_id": r.get("id", ""),
        })
    return cands

if __name__ == "__main__":
    t = open("team17_cat_jobs-career.html", encoding="utf-8", errors="replace").read()
    recs = extract_records(t)
    print("records with link:", len(recs))
    cands = records_to_candidates(recs)
    print("candidates:", len(cands), "unique codes:", len(set(c["code"] for c in cands)))
    for c in cands[:5]:
        print(c["code"], "|", c["name"][:50], "|", c["country_badge"])
