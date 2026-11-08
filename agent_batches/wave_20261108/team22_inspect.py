import json, re
raw = json.load(open("/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/team22_raw.json"))
for label in ["77links-earning","newgrouplinks-crypto"]:
    h = raw[label]["html"]
    code = "BR6AhxrdYrQLcRSF0K4urg" if label=="77links-earning" else "DZs2rQmbQ3BKJgIXtR6vms"
    i = h.find(code)
    print("="*30, label)
    print(h[max(0,i-3000):i+200])
    print()
