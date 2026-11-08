"""Kill running team13 worker processes by matching argv, excluding self/ancestors."""
import subprocess, os, signal, sys

targets = sys.argv[1:]
out = subprocess.run(["ps", "-eo", "pid,args"], capture_output=True, text=True).stdout
me = os.getpid()
killed = []
for line in out.splitlines():
    parts = line.strip().split(None, 1)
    if len(parts) < 2:
        continue
    try:
        pid = int(parts[0])
    except ValueError:
        continue
    cmd = parts[1]
    if pid == me or pid == os.getppid():
        continue
    if "python3" in cmd and any(t in cmd for t in targets):
        try:
            os.kill(pid, signal.SIGTERM)
            killed.append((pid, cmd[:100]))
        except ProcessLookupError:
            pass
print("killed:", killed)
