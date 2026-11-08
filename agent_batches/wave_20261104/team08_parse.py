#!/usr/bin/env python3
"""Parse browser.open category-page text (stdin) -> cards: outlink_idx, name, desc_pt.
Usage: python3 team08_parse.py <slug> <cat_pt_name> < <pagetext>
Prints TSV: idx \t name \t desc_pt \t [code if URL entry present]"""
import sys, re, html

slug = sys.argv[1]
catpt = sys.argv[2]
text = sys.stdin.read()
text = html.unescape(text)

entries = re.findall(r']*)】', text)
cards = {}
for idx, body in entries:
idx = int(idx)
if '/grupo/' in body and 'ongrupos.com/grupo/' in body:
m = re.search(r'ongrupos\.com/grupo/([A-Za-z0-9]{20,24})', body)
if m:
cards.setdefault(idx, {})['code'] = m.group(1)
if 'Imagem do grupo' in body:
b = body
# strip leading category breadcrumb + 'Imagem do grupo'
p = b.find('Imagem do grupo')
rest = b[p + len('Imagem do grupo'):].strip()
name, desc = rest, ''
# doubled-name detection: "NAME NAME DESC"
found = False
for k in range(4, min(120, len(rest) // 2 + 1)):
if rest[k] == ' ' and rest[:k] == rest[k+1:k+1+k]:
name, desc = rest[:k].strip(), rest[k+1+k:].strip()
found = True
break
if not found:
# fallback: name = up to first 80 chars? use whole as name, desc empty
name, desc = rest[:120], rest[120:]
cards.setdefault(idx, {})['name'] = re.sub(r'\s+', ' ', name).strip()
cards[idx]['desc'] = re.sub(r'\s+', ' ', desc).strip()

for idx in sorted(cards):
c = cards[idx]
if 'name' not in c: continue
print(f"{idx}\t{c.get('code','')}\t{c['name']}\t{c.get('desc','')}")
