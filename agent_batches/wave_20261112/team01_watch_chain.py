#!/usr/bin/env python3
"""TEAM 01 wave 20261112 — chain watcher: waits for the merged-pass stream
verifier to exit, then verifies the deep candidates, then runs finalize2.
Launched once; survives as a background process. All stages checkpoint to
disk, so a VM reboot loses little — re-launch this script to resume the chain.
Usage: team01_watch_chain.py <verifier_pid>
"""
import os, sys, time, subprocess, json

WAVE = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261112"
LOG = os.path.join(WAVE, "team01-chain.log")

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def pid_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True

def main():
    pid = int(sys.argv[1])
    log(f"chain: waiting for verifier pid {pid}")
    while pid_alive(pid):
        time.sleep(60)
    log(f"chain: verifier pid {pid} exited; starting deep-candidates verify")
    r = subprocess.run([sys.executable, os.path.join(WAVE, "team01_verify_stream.py"),
                        os.path.join(WAVE, "team01-deep-candidates.json")],
                       cwd=WAVE, stdout=open(os.path.join(WAVE, "team01-stream-deep12.log"), "w"),
                       stderr=subprocess.STDOUT)
    log(f"chain: deep verify exit={r.returncode}")
    r2 = subprocess.run([sys.executable, os.path.join(WAVE, "team01_finalize2.py")],
                        cwd=WAVE, stdout=open(os.path.join(WAVE, "team01-finalize2.log"), "w"),
                        stderr=subprocess.STDOUT)
    log(f"chain: finalize2 exit={r2.returncode}")
    with open(os.path.join(WAVE, "team01-chain-DONE.json"), "w") as f:
        json.dump({"done": True, "verify_exit": r.returncode, "finalize2_exit": r2.returncode,
                   "t": time.strftime("%Y-%m-%d %H:%M:%S")}, f)
    log("chain: DONE")

if __name__ == "__main__":
    main()
