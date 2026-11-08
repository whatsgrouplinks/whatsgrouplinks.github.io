import json, re
raw = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team22_raw.json"))
checks = [
 ("grouplink-com-in-1800","BCCIm1cdDbvK4meBs28szr"),
 ("grouplink-com-in-1800","Bte0626nuW6FT5USahHEiq"),
 ("grouplink-com-in-1800","CindfGo478i2qz49wyN4vB"),
 ("grouplink-com-in-1800","GysPbrwOiWwKl6VBUo7Dv1"),
 ("whatstele-stock","Ge1yF51cHAMEU2ayEw2JRR"),
 ("coinweb-signals","ETvrOZzIGzC7Yb5UQUSKt2"),
 ("coinweb-signals","ElCwvJf7ZYh9RLba4FAfza"),
 ("coinweb-signals","HDXdN6CBXEkCGldXqtfEa7"),
]
for label, code in checks:
    h = raw[label]["html"]
    i = h.find(code)
    seg = h[max(0,i-700):i+80]
    seg = re.sub(r'<[^>]+>', '|', seg)
    seg = re.sub(r'\|+', ' | ', seg)
    seg = re.sub(r'\s+', ' ', seg)
    print(f"--- {label} {code}\n{seg}\n")
