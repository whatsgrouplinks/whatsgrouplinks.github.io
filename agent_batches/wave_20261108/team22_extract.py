import json, re, html
raw = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team22_raw.json"))
union = set(json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/dedupe_union.json")))
print("union", len(union))
pat = re.compile(r'chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{20,24})')
pat2 = re.compile(r'whatsapp\.com/invite/([A-Za-z0-9]{20,24})')
for label, d in raw.items():
    h = d["html"]
    codes = pat.findall(h) + pat2.findall(h)
    uniq = sorted(set(codes))
    fresh = [c for c in uniq if c not in union]
    print(f"{label}: total_occ={len(codes)} uniq={len(uniq)} fresh_vs_union={len(fresh)}")
    # also count internal join links
    print("   internal /join or href count chat:", h.count("chat.whatsapp.com"))
