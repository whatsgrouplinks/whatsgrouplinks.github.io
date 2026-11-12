#!/usr/bin/env python3
"""TEAM 01 wave 20261112 — deep-fetch unresolved groupsinvite slugs + linkado ids.
Reads sub lists + done lists from wave_20261111 progress (never modifies it).
Writes ONLY wave_20261112 files:
  team01-deep-candidates.json  {code: rec} resolved candidates
  team01-deep-progress.json    {gi_done, linkado_done, failed, nocode, exclusions}
  team01-deep-progress.jsonl   checkpoint log
Resolves: groupsinvite slug -> https://groupsinvite.link/group/rules/<slug>/
          linkado id -> https://linkado.app/grupo/<id>
6 workers (different hosts from chat.whatsapp.com; the sequential rule applies
only to chat.whatsapp.com). Failed fetches are NOT marked done (retried on
resume); pages with no invite code ARE marked done (stale slug/id).
Dedupes against .existing_codes.json + merged + verified + stream-verified.
Screens banked names (porn/scam tokens, negated-prohibition aware).
Usage: team01_deep.py [gi|linkado|all] [cap]
"""
import json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from team01_mine import (fetch, clean_name, infer_category, infer_country,
                         make_desc, screen_text, load_json, save_json)
from concurrent.futures import ThreadPoolExecutor

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
SRC = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261111"
SRC_PROG = os.path.join(SRC, "team01-leads-slice1-progress.json")
SRC_PROG_RESCUE = os.path.join(SRC, "team01-rescue-progress.json")
EXISTING_FILE = "/home/hatch/workspace/whatsapp-groups-site/.existing_codes.json"
CAND_FILE = os.path.join(WAVE, "team01-deep-candidates.json")
PROG_FILE = os.path.join(WAVE, "team01-deep-progress.json")
PROG_JSONL = os.path.join(WAVE, "team01-deep-progress.jsonl")

def log_progress(msg):
    with open(PROG_JSONL, "a") as f:
        f.write(json.dumps({"t": time.strftime("%H:%M:%S"), "msg": msg}) + "\n")

def run(kind, cap):
    prog = load_json(PROG_FILE, {})
    if not prog:
        # seed from wave_20261111 progress files (main + rescue)
        p1 = load_json(SRC_PROG, {})
        p2 = load_json(SRC_PROG_RESCUE, {})
        prog = {
            "gi_done": sorted(set(p1.get("deep_gi_done", [])) | set(p2.get("deep_gi_done", []))),
            "linkado_done": sorted(set(p1.get("deep_linkado_done", [])) | set(p2.get("deep_linkado_done", []))),
            "gi_todo": sorted(set(p1.get("sub_groupsinvite", [])) | set(p2.get("sub_groupsinvite", []))),
            "linkado_todo": sorted(set(p1.get("sub_linkado", [])) | set(p2.get("sub_linkado", []))),
            "failed": [], "nocode": [], "exclusions": [],
        }
        save_json(PROG_FILE, prog)
    cands = load_json(CAND_FILE, {})
    existing = set(load_json(EXISTING_FILE, []))
    # skip codes already known (merged unverified + verified + stream-verified)
    known = set()
    for path in [os.path.join(WAVE, "team01-merged-candidates.json"),
                 os.path.join(WAVE, "team01-leads-slice1.json"),
                 os.path.join(WAVE, "team01-stream-verified.json")]:
        d = load_json(path, {} if "merged" in path else [])
        if isinstance(d, dict):
            known |= set(d.keys())
        else:
            known |= {v["invite"].split("/")[-1] for v in d}
    if kind in ("gi", "all"):
        done = set(prog["gi_done"])
        items = [s for s in prog["gi_todo"] if s not in done][:cap]
        print(f"DEEP gi: {len(items)} to resolve (todo {len(prog['gi_todo'])}, done {len(done)})", flush=True)
        def work(slug):
            try:
                t = fetch(f"https://groupsinvite.link/group/rules/{slug}/")
            except Exception as e:
                return (slug, None, False)
            m = re.search(r"https://chat\.whatsapp\.com/([A-Za-z0-9]{10,30})", t)
            if not m:
                return (slug, None, True)
            code = m.group(1)
            title = re.search(r"<title>(.*?)</title>", t, re.S | re.I)
            title = title.group(1) if title else ""
            import html as _html
            title = _html.unescape(re.sub(r"<[^>]+>", "", title)).strip()
            name = clean_name(re.sub(r"\s+WhatsApp Group Rules.*$", "", title, flags=re.I))
            return (slug, (code, name), True)
        n = 0
        with ThreadPoolExecutor(max_workers=6) as ex:
            for slug, res, ok in ex.map(work, items):
                if ok:
                    done.add(slug)
                else:
                    prog["failed"].append({"kind": "gi", "item": slug})
                if res:
                    code, name = res
                    if code in existing or code in known or code in cands or not name:
                        pass
                    else:
                        r = screen_text(name)
                        if r:
                            prog["exclusions"].append({"code": code, "reason": r + " (deep gi name)"})
                        else:
                            cat = infer_category(name)
                            cc = infer_country(name)
                            cands[code] = {"name": name, "category": cat, "country": cc,
                                           "description": make_desc(name, cat, cc),
                                           "invite": f"https://chat.whatsapp.com/{code}",
                                           "source": f"https://groupsinvite.link/group/rules/{slug}/"}
                elif ok:
                    prog["nocode"].append({"kind": "gi", "item": slug})
                n += 1
                if n % 100 == 0:
                    prog["gi_done"] = sorted(done)
                    save_json(CAND_FILE, cands); save_json(PROG_FILE, prog)
                    print(f"  gi {n}/{len(items)}: candidates={len(cands)}", flush=True)
        prog["gi_done"] = sorted(done)
        save_json(CAND_FILE, cands); save_json(PROG_FILE, prog)
        log_progress(f"gi done: candidates={len(cands)} done={len(done)}")
        print(f"DEEP gi DONE: candidates={len(cands)} done={len(done)}", flush=True)
    if kind in ("linkado", "all"):
        done = set(prog["linkado_done"])
        items = [g for g in prog["linkado_todo"] if g not in done][:cap]
        print(f"DEEP linkado: {len(items)} to resolve (todo {len(prog['linkado_todo'])}, done {len(done)})", flush=True)
        def work(gid):
            try:
                t = fetch(f"https://linkado.app/grupo/{gid}")
            except Exception:
                return (gid, None, False)
            m = re.search(r"https://chat\.whatsapp\.com/([A-Za-z0-9]{10,30})", t)
            if not m:
                return (gid, None, True)
            code = m.group(1)
            title = re.search(r"<title>(.*?)</title>", t, re.S | re.I)
            title = title.group(1) if title else ""
            import html as _html
            title = _html.unescape(re.sub(r"<[^>]+>", "", title)).strip()
            name = clean_name(re.sub(r"\s*-\s*[A-Za-zÀ-ÿ ]+$", "", title))
            return (gid, (code, name), True)
        n = 0
        with ThreadPoolExecutor(max_workers=6) as ex:
            for gid, res, ok in ex.map(work, items):
                if ok:
                    done.add(gid)
                else:
                    prog["failed"].append({"kind": "linkado", "item": gid})
                if res:
                    code, name = res
                    if code in existing or code in known or code in cands or not name:
                        pass
                    else:
                        r = screen_text(name)
                        if r:
                            prog["exclusions"].append({"code": code, "reason": r + " (deep linkado name)"})
                        else:
                            cat = infer_category(name + " linkado")
                            cc = infer_country(name)
                            cands[code] = {"name": name, "category": cat, "country": cc,
                                           "description": make_desc(name, cat, cc),
                                           "invite": f"https://chat.whatsapp.com/{code}",
                                           "source": f"https://linkado.app/grupo/{gid}"}
                elif ok:
                    prog["nocode"].append({"kind": "linkado", "item": gid})
                n += 1
                if n % 100 == 0:
                    prog["linkado_done"] = sorted(done)
                    save_json(CAND_FILE, cands); save_json(PROG_FILE, prog)
                    print(f"  linkado {n}/{len(items)}: candidates={len(cands)}", flush=True)
        prog["linkado_done"] = sorted(done)
        save_json(CAND_FILE, cands); save_json(PROG_FILE, prog)
        log_progress(f"linkado done: candidates={len(cands)} done={len(done)}")
        print(f"DEEP linkado DONE: candidates={len(cands)} done={len(done)}", flush=True)

if __name__ == "__main__":
    kind = sys.argv[1] if len(sys.argv) > 1 else "all"
    cap = int(sys.argv[2]) if len(sys.argv) > 2 else 100000
    run(kind, cap)
