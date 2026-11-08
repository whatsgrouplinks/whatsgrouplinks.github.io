#!/usr/bin/env python3
"""Coordinator validation for wave 20261105.
Validates every canonical team file, computes cross-team dedupe overlaps,
pending/leads totals, and writes manifest.txt + wave_20261105_summary.md.
"""
import json, os, re, sys
from collections import Counter, defaultdict

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261105"
UNION_F = os.path.join(WAVE, "dedupe_union.json")

VERIFIED = {
 "01": "team01-groups1-pool-a.json", "02": "team02-groups1-pool-b.json",
 "03": "team03-igrupos.json", "04": "team04-ongrupos.json",
 "05": "team05-gjl-linkado.json", "06": "team06-arabic.json",
 "07": "team07-appgrouplink.json", "08": "team08-groupchatconnect.json",
 "09": "team09-groupsinvite.json", "10": "team10-small-pending.json",
 "11": "team11-groupssor.json", "12": "team12-grupbul.json",
 "13": "team13-whatshub.json", "14": "team14-latam.json",
 "15": "team15-linkado.json", "16": "team16-groupjoin.json",
 "17": "team17-whatsappkanali.json", "18": "team18-visadb.json",
 "19": "team19-meetup-nextdoor.json", "20": "team20-ireland-uni.json",
 "21": "team21-groupda.json", "22": "team22-groupsinvite-link.json",
 "23": "team23-portugal.json", "24": "team24-ongrupos-slices.json",
 "25": "team25-igrupos-ongrupos-new.json", "26": "team26-new-dirs-a.json",
 "27": "team27-new-dirs-b.json", "28": "team28-listicles-a.json",
 "29": "team29-listicles-b.json", "30": "team30-appgrouplink-new.json",
 "31": "team31-groupchatconnect.json", "32": "team32-gjl-tags.json",
 "33": "team33-leads-bank-a.json", "34": "team34-leads-bank-b.json",
 "35": "team35-new-tags.json", "36": "team36-recovery.json",
}
SLICE = {
 "01": "groups1 pool A (codes[0:5892])", "02": "groups1 pool B (codes[5892:])",
 "03": "igrupos pending", "04": "ongrupos pending",
 "05": "gjl-newtags+linkado pending", "06": "Arabic pending",
 "07": "appgrouplink pending", "08": "groupchatconnect pending",
 "09": "groupsinvite recovery", "10": "small pending bundle",
 "11": "groupssor API re-poll", "12": "grupbul.com categories",
 "13": "whatshub.es", "14": "LatAm directories",
 "15": "linkado.app resume", "16": "groupjoin.link tags",
 "17": "whatsappkanali.com", "18": "visadb.io EU",
 "19": "Meetup/Nextdoor", "20": "Ireland + universityapplicants",
 "21": "groupda retry + groupda.pk API", "22": "groupsinvite.link retry",
 "23": "Portugal directories", "24": "ongrupos slices",
 "25": "igrupos+ongrupos new since Nov 4", "26": "new directories set A",
 "27": "new directories set B", "28": "listicles set A (study/jobs/sports)",
 "29": "listicles set B (movies/regional)", "30": "appgrouplink new since Nov 4",
 "31": "groupchatconnect leads-only", "32": "gjl tag candidates (team13 leads)",
 "33": "leads bank part A", "34": "leads bank part B",
 "35": "igrupos+ongrupos new tags", "36": "pending-file recovery + empty audit",
}
FIELDS = {"name", "category", "country", "description", "invite", "image"}

def code_of_invite(inv):
    if not isinstance(inv, str):
        return None
    m = re.match(r"^https?://chat\.whatsapp\.com/(?:invite/)?([A-Za-z0-9_-]+)\s*$", inv.strip())
    return m.group(1) if m else None

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

union = set(load_json(UNION_F))
print(f"union entries: {len(union)}")

results = {}
code_to_teams = defaultdict(set)
file_sum = 0
issues = []
for tn in sorted(VERIFIED):
    fn = VERIFIED[tn]
    path = os.path.join(WAVE, fn)
    entry = {"file": fn, "slice": SLICE[tn], "exists": os.path.exists(path),
             "size": os.path.getsize(path) if os.path.exists(path) else 0}
    if not entry["exists"]:
        entry.update(count=None, valid_json=False, schema_ok=False, dupes_in_file=0,
                     in_union=0, bad_invite=0)
        issues.append(f"team{tn}: MISSING verified file {fn}")
        results[tn] = entry
        continue
    try:
        data = load_json(path)
        entry["valid_json"] = True
    except Exception as e:
        entry.update(count=None, valid_json=False, schema_ok=False, dupes_in_file=0,
                     in_union=0, bad_invite=0)
        issues.append(f"team{tn}: INVALID JSON in {fn}: {e}")
        results[tn] = entry
        continue
    if not isinstance(data, list):
        entry.update(count=None, valid_json=True, schema_ok=False, dupes_in_file=0,
                     in_union=0, bad_invite=0)
        issues.append(f"team{tn}: {fn} is not a JSON array")
        results[tn] = entry
        continue
    entry["count"] = len(data)
    file_sum += len(data)
    codes = []
    schema_ok = True
    bad_invite = 0
    for i, rec in enumerate(data):
        if not isinstance(rec, dict) or set(rec.keys()) != FIELDS:
            schema_ok = False
            if i < 3:
                issues.append(f"team{tn}: schema violation at index {i}: keys={sorted(rec.keys()) if isinstance(rec, dict) else type(rec)}")
            continue
        c = code_of_invite(rec.get("invite", ""))
        if c is None:
            bad_invite += 1
            if bad_invite <= 3:
                issues.append(f"team{tn}: bad invite at index {i}: {rec.get('invite')!r}")
        else:
            codes.append(c)
            code_to_teams[c].add(tn)
        # first-item schema detail
        if i == 0:
            entry["first"] = {k: (str(v)[:60]) for k, v in rec.items()}
    entry["schema_ok"] = schema_ok
    entry["bad_invite"] = bad_invite
    cnt = Counter(codes)
    entry["dupes_in_file"] = sum(v - 1 for v in cnt.values() if v > 1)
    entry["in_union"] = sum(1 for c in set(codes) if c in union)
    if entry["dupes_in_file"]:
        issues.append(f"team{tn}: {entry['dupes_in_file']} duplicate codes inside {fn}")
    if entry["in_union"]:
        issues.append(f"team{tn}: {entry['in_union']} verified codes already in union")
    results[tn] = entry

# cross-team overlaps (verified)
overlaps = {}
for c, teams in code_to_teams.items():
    if len(teams) > 1:
        key = tuple(sorted(teams))
        overlaps.setdefault(key, []).append(c)
unique_verified = len(code_to_teams)
overlap_pairs = sorted(((k, len(v)) for k, v in overlaps.items()), key=lambda x: -x[1])
overlap_total_extra = file_sum - unique_verified

# pending + leads
pending = {}
leads = {}
pending_codes = defaultdict(set)
for tn in sorted(VERIFIED):
    pf = os.path.join(WAVE, f"team{tn}-unverified-pending.json")
    lf_candidates = [os.path.join(WAVE, f"team{tn}-leads.json"),
                     os.path.join(WAVE, f"team{tn}-groupchatconnect-leads.json")]
    pcount = None
    if os.path.exists(pf):
        try:
            pd = load_json(pf)
            pcount = len(pd) if isinstance(pd, list) else None
            if isinstance(pd, list):
                for r in pd:
                    if isinstance(r, dict):
                        c = r.get("code") or code_of_invite(r.get("invite", "")) or None
                        if c:
                            pending_codes[c].add(tn)
        except Exception as e:
            issues.append(f"team{tn}: pending file invalid JSON: {e}")
    else:
        issues.append(f"team{tn}: MISSING pending file team{tn}-unverified-pending.json")
    lcount = None
    for lf in lf_candidates:
        if os.path.exists(lf):
            try:
                ld = load_json(lf)
                lcount = len(ld) if isinstance(ld, list) else None
            except Exception as e:
                issues.append(f"team{tn}: leads file invalid JSON: {e}")
            break
    if lcount is None:
        issues.append(f"team{tn}: MISSING leads file")
    pending[tn] = pcount
    leads[tn] = lcount

pending_total = sum(v for v in pending.values() if v is not None)
leads_total = sum(v for v in leads.values() if v is not None)
pending_unique = len(pending_codes)
# verified codes also appearing in some pending file
ver_in_pending = sum(1 for c in code_to_teams if c in pending_codes)

print(f"verified file-sum: {file_sum}")
print(f"verified unique codes: {unique_verified}")
print(f"cross-team overlap extra copies: {overlap_total_extra}")
print(f"pending total: {pending_total} (unique codes {pending_unique})")
print(f"leads total: {leads_total}")
print(f"verified codes also in some pending file: {ver_in_pending}")
for k, n in overlap_pairs:
    print(f"overlap {'+'.join(k)}: {n} codes")
print("ISSUES:")
for i in issues:
    print(" -", i)

# manifest
with open(os.path.join(WAVE, "manifest.txt"), "w", encoding="utf-8") as f:
    f.write("WAVE 20261105 MANIFEST\n")
    f.write("======================\n")
    f.write(f"Verified file-sum (sum of per-team counts): {file_sum}\n")
    f.write(f"Verified unique codes (after cross-team dedupe): {unique_verified}\n")
    f.write(f"Cross-team duplicate copies removed by dedupe: {overlap_total_extra}\n")
    f.write(f"Pending file-sum: {pending_total} (unique pending codes: {pending_unique})\n")
    f.write(f"Leads file-sum: {leads_total}\n")
    f.write(f"Verified codes also present in some pending file: {ver_in_pending}\n\n")
    f.write("Per-team verified files:\n")
    for tn in sorted(VERIFIED):
        r = results[tn]
        f.write(f"  team{tn} {r['file']}: count={r.get('count')} valid_json={r.get('valid_json')} "
                f"schema_ok={r.get('schema_ok')} size={r['size']} dupes_in_file={r.get('dupes_in_file')} "
                f"in_union={r.get('in_union')} bad_invite={r.get('bad_invite')} | slice: {r['slice']}\n")
    f.write("\nPer-team pending / leads:\n")
    for tn in sorted(VERIFIED):
        f.write(f"  team{tn}: pending={pending[tn]} leads={leads[tn]}\n")
    f.write("\nCross-team verified-code overlaps (team pairs -> shared codes):\n")
    if overlap_pairs:
        for k, n in overlap_pairs:
            f.write(f"  {' + '.join(k)}: {n}\n")
    else:
        f.write("  none\n")
    f.write("\nValidation issues:\n")
    if issues:
        for i in issues:
            f.write(f"  - {i}\n")
    else:
        f.write("  none\n")

# summary md (data section; narrative flags appended by coordinator in the file after)
summary = []
summary.append("# Wave 20261105 — coordinator summary")
summary.append("")
summary.append("**Wave:** 20261105 | **Current groups.json total (start of wave):** 50,109 | **Dedupe union:** 85,731 codes")
summary.append("")
summary.append("## Headline numbers (validated from files, not from team claims)")
summary.append("")
summary.append(f"- **Verified file-sum:** {file_sum}")
summary.append(f"- **Verified unique codes (after cross-team dedupe):** {unique_verified}")
summary.append(f"- **Cross-team duplicate copies:** {overlap_total_extra}")
summary.append(f"- **Pending file-sum:** {pending_total} (unique pending codes: {pending_unique})")
summary.append(f"- **Leads file-sum:** {leads_total}")
summary.append(f"- **Verified codes also present in some pending file:** {ver_in_pending} (parent: keep one copy each; pending copies are stale duplicates)")
summary.append("")
summary.append("## Per-team table (verified / pending / leads)")
summary.append("")
summary.append("| Team | Slice | Verified | Pending | Leads |")
summary.append("|---|---|---|---|---|")
for tn in sorted(VERIFIED):
    r = results[tn]
    summary.append(f"| team{tn} | {r['slice']} | {r.get('count')} | {pending[tn]} | {leads[tn]} |")
summary.append("")
summary.append("## Cross-team verified-code overlaps")
summary.append("")
if overlap_pairs:
    for k, n in overlap_pairs:
        summary.append(f"- **{' + '.join('team'+t for t in k)}:** {n} shared codes")
else:
    summary.append("- None.")
summary.append("")
summary.append("## Validation issues")
summary.append("")
if issues:
    for i in issues:
        summary.append(f"- {i}")
else:
    summary.append("- None — all 36 verified files parse, match the 6-field schema, and contain no in-file dupes, no union codes, and no bad invites.")
summary.append("")
with open(os.path.join(WAVE, "wave_20261105_summary.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(summary) + "\n")
print("wrote manifest.txt + wave_20261105_summary.md (data sections)")
