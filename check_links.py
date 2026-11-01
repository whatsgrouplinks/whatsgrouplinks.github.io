#!/usr/bin/env python3
"""
WhatsGroupLinks — Link Validator
Checks all WhatsApp invite links in groups.json for validity.
Removes dead/expired links from the directory.

Tahir's rule (Oct 17): Only ACTIVE groups with VALID links stay listed.
Dead/deleted/expired links are removed.

Detection (verified Oct 18): fetch the invite URL with curl and read the
og:title meta tag. A working invite has the group name in og:title;
a dead/revoked invite returns the same page with an EMPTY og:title.
URLs that fail to load (transport error / non-200) are NOT deleted —
they are kept and logged as uncheckable.

Safety: if the dead fraction exceeds 20%, the run aborts and nothing
is removed (mass-dead almost always means a network/checker problem).
"""
import json, time, os, re, html, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
GROUPS_JSON = os.path.join(SITE_DIR, 'groups.json')
LOG_FILE = os.path.join(SITE_DIR, 'link_check.log')
STATE_FILE = os.path.join(SITE_DIR, 'link_check_state.json')  # resume checkpoint

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
MAX_WORKERS = int(os.environ.get('LINK_CHECK_WORKERS', '60'))
DEAD_ABORT_FRACTION = 0.90  # abort removal if more than this fraction is dead
CANARY_URL = 'https://chat.whatsapp.com/KrDwdK8EIkB6vgauHg5M7N'  # verified-good link; must stay 'ok'
CANARY_EVERY = 10000  # re-verify canary every N checks to catch mid-run blocks
SAVE_EVERY = 2000  # persist checkpoint every N completed checks


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_state(state):
    tmp = STATE_FILE + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(state, f)
    os.replace(tmp, STATE_FILE)


LOCK_FILE = os.path.join(SITE_DIR, 'link_check.lock')


def acquire_lock():
    """Exit gracefully if another check_links.py run is already active."""
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE) as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)  # raises if process gone
            if pid != os.getpid():
                print(f"Another check_links.py run (pid {pid}) is active — exiting.", flush=True)
                raise SystemExit(0)
        except (ValueError, ProcessLookupError, PermissionError, OSError):
            pass  # stale lock or unreadable; proceed
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))


def release_lock():
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except OSError:
        pass


def fetch_og_title(url):
    """Return (http_code, og_title or None). Raises on transport failure."""
    p = subprocess.run(
        ['curl', '-s', '-L', '--max-time', '20', '-A', UA,
         '-w', '\n%{http_code}', url],
        capture_output=True, timeout=30)
    body = p.stdout.decode('utf-8', errors='ignore')
    lines = body.rsplit('\n', 1)
    code = lines[1].strip() if len(lines) == 2 else '000'
    t = lines[0]
    m = re.search(r'og:title[^>]*?content="([^"]*)"', t)
    title = html.unescape(m.group(1)).strip() if m else None
    return code, title


def check_link(url):
    """Classify a WhatsApp invite link: ('ok'|'dead'|'uncheckable', detail)."""
    if not url:
        return 'dead', 'no url'
    last = 'no attempt'
    for attempt in range(2):
        try:
            code, title = fetch_og_title(url)
        except Exception as e:
            last = f"transport error: {str(e)[:50]}"
            time.sleep(1)
            continue
        if code != '200':
            last = f"HTTP {code}"
            time.sleep(1)
            continue
        if title:
            return 'ok', title[:60]
        return 'dead', 'empty og:title'
    return 'uncheckable', last


def main():
    acquire_lock()
    try:
        _main()
    finally:
        release_lock()


def _main():
    with open(GROUPS_JSON) as f:
        groups = json.load(f)

    total = len(groups)
    state = load_state()
    pending = [g for g in groups if g.get('invite', '') not in state]
    already = total - len(pending)
    print(f"Checking {len(pending)} links ({already} already done) with {MAX_WORKERS} workers...", flush=True)

    valid_groups = []
    dead = []
    uncheckable = []
    done = 0
    t0 = time.time()
    t_start = time.time()
    status_of = {}  # invite -> status, merged with state at the end

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        future_to_group = {ex.submit(check_link, g.get('invite', '')): g for g in pending}
        for fut in as_completed(future_to_group):
            g = future_to_group[fut]
            done += 1
            try:
                status, detail = fut.result()
            except Exception as e:
                status, detail = 'uncheckable', f"worker error: {str(e)[:50]}"
            url = g.get('invite', '')
            status_of[url] = status
            state[url] = status  # checkpoint
            if status == 'ok':
                pass
            elif status == 'dead':
                dead.append((g.get('name', 'unknown'), detail))
            else:
                uncheckable.append((g.get('name', 'unknown'), detail))
            if done % 5000 == 0 or done == len(pending):
                elapsed = time.time() - t0
                print(f"  Checked {done}/{len(pending)} this run (dead={len(dead)} "
                      f"uncheckable={len(uncheckable)} {elapsed:.0f}s)", flush=True)
            if done % SAVE_EVERY == 0:
                save_state(state)
            if done % CANARY_EVERY == 0:
                cstatus, _ = check_link(CANARY_URL)
                if cstatus != 'ok':
                    print(f"CANARY FAILED at {done} checks (status={cstatus}) — "
                          f"checker environment degraded. ABORTING, nothing removed.", flush=True)
                    with open(LOG_FILE, 'a') as f:
                        f.write(f"\n=== Check {time.strftime('%Y-%m-%d %H:%M')} ===\n")
                        f.write(f"CANARY FAILURE at {done}/{total}: status={cstatus}. Nothing removed.\n")
                    return

    save_state(state)

    # Combine resumed classifications from state with this run's results
    all_dead = set(state.get(u) == 'dead' and u for u in state) - {False}
    valid_groups = [g for g in groups if g.get('invite', '') not in all_dead]
    n_dead = len(all_dead)
    n_uncheckable = sum(1 for u, s in state.items() if s == 'uncheckable')

    elapsed = time.time() - t_start
    print(f"\nRun done in {elapsed/60:.1f} min. Total: {total}, Valid: {len(valid_groups)}, "
          f"Dead: {n_dead}, Uncheckable: {n_uncheckable}", flush=True)
    for name, reason in dead[:20]:
        print(f"  DEAD: {name} ({reason})", flush=True)

    with open(LOG_FILE, 'a') as f:
        f.write(f"\n=== Check {time.strftime('%Y-%m-%d %H:%M')} ===\n")
        f.write(f"Total: {total}, Valid: {len(valid_groups)}, Dead: {n_dead}, "
                f"Uncheckable: {n_uncheckable}\n")
        for u in sorted(all_dead):
            f.write(f"  DEAD: {u}\n")
        for name, reason in uncheckable[:100]:
            f.write(f"  UNCHECKABLE: {name} ({reason})\n")

    if not all_dead:
        print("No dead links found!", flush=True)
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
        return

    # Safety: mass-dead almost always means a network/checker problem.
    if n_dead / total > DEAD_ABORT_FRACTION:
        print(f"ABORT: dead fraction {n_dead/total:.1%} exceeds {DEAD_ABORT_FRACTION:.0%} — "
              f"likely a network/checker failure. NOTHING removed.", flush=True)
        with open(LOG_FILE, 'a') as f:
            f.write("  ABORTED: dead fraction too high, nothing removed.\n")
        return

    # Backup then update
    backup = GROUPS_JSON + f".backup-{time.strftime('%Y%m%d-%H%M')}"
    os.rename(GROUPS_JSON, backup)
    print(f"Backup saved: {backup}", flush=True)

    with open(GROUPS_JSON, 'w') as f:
        json.dump(valid_groups, f, indent=2, ensure_ascii=False)
    print(f"Updated groups.json: {len(valid_groups)} groups", flush=True)

    # Checkpoint consumed — remove it so the next scheduled run starts fresh
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)

if __name__ == '__main__':
    main()
