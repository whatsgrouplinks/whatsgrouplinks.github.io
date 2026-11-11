#!/usr/bin/env python3
"""Team27 wave 20261111: extract chat.whatsapp.com codes from fetched HTML/PDF-text
files with surrounding name context, dedupe vs .existing_codes.json, screen content."""
import json, re, os, html, sys

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
RAW = os.path.join(WAVE, "team27_raw")
UNION = json.load(open("/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"))
if isinstance(UNION, dict):
    UNION = set(UNION.keys())
else:
    UNION = set(UNION)
print("union size:", len(UNION), file=sys.stderr)

CODE_RE = re.compile(r"chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9]{22})")

# per-file manual category/country defaults (filled in by operator per source)
FILE_META = {
    "www_thelastsurvivors_org_grup_wa_youtubers_": ("Entertainment", "ID"),
    "www_thelastsurvivors_org_grup_wa_ff_": ("Gaming", "ID"),
    "www_agunghostkey_com_2023_07_99_link_grup_wa_cari_pacar_html": ("Friendship", "ID"),
    "virenial_com_teknologi_vr_21585_grup_ff_wa_2024": ("Gaming", "ID"),
    "alatekno_com_grup_wa_random_": ("Community & Social", "ID"),
    "tutorial1001_com_link_grup_wa_cari_jodoh_indonesia_": ("Friendship", "ID"),
    "aussiesin_com_": ("Travel", ""),
    "grouplink_com_in_1800_new_whatsapp_group_link_": ("Community & Social", ""),
    "joinnchat_com_philippines_girl_whatsapp_group_link_": ("Friendship", "PH"),
    "helloworldawaits_com_digital_nomad_travel_trusted_travel_whatsapp_channel_": ("Travel", ""),
    "meetup_kl": ("Community & Social", "MY"),
    "meetup_klfriends": ("Friendship", "MY"),
    "meetup_manila": ("Community & Social", "PH"),
    "fkph": ("Education", "ID"),
    "apium": ("Education", "MY"),
    "usm": ("Education", "MY"),
}

def strip_tags(t):
    t = re.sub(r"<script.*?</script>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    t = re.sub(r"\s+", " ", t)
    return t

def guess_name(text, pos):
    # take up to 120 chars before the code, strip junk, use last plausible phrase
    before = text[max(0, pos - 160):pos]
    before = re.sub(r"(https?://\S+|chat\.whatsapp\.com\S*)", " ", before)
    before = before.strip(" |:;,-–—•\t\n")
    # last sentence-ish chunk
    parts = re.split(r"[|\n]", before)
    cand = parts[-1].strip()
    cand = re.sub(r"^(Join|Link|Join Now|Join Group|Gabung|Masuk|Klik|Click)\s*:?\s*", "", cand, flags=re.I)
    cand = cand.strip()
    if len(cand) > 60:
        cand = cand[-60:].strip()
    return cand

out = {}  # code -> {name, category, country, source}
for fname in sorted(os.listdir(RAW)):
    if fname.endswith(".html"):
        key = fname[:-5]
        raw = open(os.path.join(RAW, fname), encoding="utf-8", errors="ignore").read()
        text = strip_tags(raw)
    elif fname.endswith(".txt") and fname[:-4] in FILE_META:
        key = fname[:-4]
        text = open(os.path.join(RAW, fname), encoding="utf-8", errors="ignore").read()
        text = re.sub(r"\s+", " ", text)
    else:
        continue
    cat, ctry = FILE_META.get(key, ("Community & Social", ""))
    path = os.path.join(RAW, fname)
    for m in CODE_RE.finditer(text):
        code = m.group(1)
        name = guess_name(text, m.start())
        if code not in out:
            out[code] = {"name": name, "category": cat, "country": ctry,
                         "invite": "https://chat.whatsapp.com/" + code,
                         "source": fname}
        elif not out[code]["name"] and name:
            out[code]["name"] = name

fresh = {c: v for c, v in out.items() if c not in UNION}
print(f"total unique codes extracted: {len(out)}; fresh vs union: {len(fresh)}; in-union: {len(out)-len(fresh)}", file=sys.stderr)
json.dump(fresh, open(os.path.join(WAVE, "team27_pool.json"), "w"), ensure_ascii=False, indent=1)
for c, v in sorted(fresh.items()):
    print(c, "|", v["category"], "|", v["country"], "|", v["name"][:70], "|", v["source"])
