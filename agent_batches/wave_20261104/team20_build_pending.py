import json

P = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261104/"

NOTE = ("transport failure — og:title verification unreachable this run "
        "(egress-proxy timeouts on all hosts; chat.whatsapp.com returns 403 via fetch service). "
        "Resume: curl invite URL with Chrome UA, include only if og:title non-empty; re-dedupe vs union.")

pending = [
 # --- Nepal (snippet-harvested, 22-char codes) ---
 {"name":"Digital Pathshala","category":"Education","country":"NP",
  "description":"Nepal's affordable online IT learning platform community sharing class updates, Google Meet links and study resources for students.",
  "invite":"https://chat.whatsapp.com/BufShnZESAB5kbVh9BJmbF","image":"","note":NOTE},
 {"name":"Digital Pathshala Community","category":"Education","country":"NP",
  "description":"Learning support community for Nepali online IT students with course updates, class links and study help.",
  "invite":"https://chat.whatsapp.com/JEOjeSsRlAeKZykFdL6r8O","image":"","note":NOTE},
 # --- Sri Lanka (snippet-harvested, 22-char codes) ---
 {"name":"SSC International Chess Academy","category":"Sports","country":"LK",
  "description":"Sri Lanka chess event updates and registration information from the Matara-based international chess academy.",
  "invite":"https://chat.whatsapp.com/L45MoGL59pgDnn8js9vQGt","image":"","note":NOTE},
 {"name":"Mayor Chess Club","category":"Sports","country":"LK",
  "description":"Colombo chess club group for players with tournament news, meetups and game discussion.",
  "invite":"https://chat.whatsapp.com/DVJniTbpMNmIWL3h8dNxul","image":"","note":NOTE},
 {"name":"Mayor Chess Club Chat","category":"Sports","country":"LK",
  "description":"Community chat for Mayor Chess Club members in Sri Lanka to discuss games and club events.",
  "invite":"https://chat.whatsapp.com/D3I1qb7qW81IVXP6XJUUNt","image":"","note":NOTE},
 {"name":"Diploma in Environmental Management","category":"Education","country":"LK",
  "description":"Rajarata University of Sri Lanka diploma programme group covering lectures, field classes and assignments.",
  "invite":"https://chat.whatsapp.com/DpP8S0yEaDjLdlH9WEcTP9","image":"","note":NOTE},
 {"name":"OUSL BSc IT Aptitude Test Prep","category":"Education","country":"LK",
  "description":"Aptitude test guidance, Zoom class updates and study materials for Open University of Sri Lanka BSc IT applicants.",
  "invite":"https://chat.whatsapp.com/ButmH0acT3d6UQNdp3nki8","image":"","note":NOTE},
 {"name":"BotSoc OUSL Community","category":"Education","country":"LK",
  "description":"Botanical Society of the Open University of Sri Lanka community with activities, announcements and opportunities.",
  "invite":"https://chat.whatsapp.com/H3OUyLDAZtV4fLZstRVvDV","image":"","note":NOTE},
 {"name":"A/L Geography 2026 Batch","category":"Education","country":"LK",
  "description":"Advanced Level Geography revision fast-track class group for Sri Lankan students in Sinhala medium.",
  "invite":"https://chat.whatsapp.com/I0Lqi05I9PfLUQryGQz4f7","image":"","note":NOTE},
 {"name":"A/L Classes 2027 Batch","category":"Education","country":"LK",
  "description":"Advanced Level theory class group for Sri Lankan students with schedules and study updates.",
  "invite":"https://chat.whatsapp.com/IXN2oAFlanB3yAcHGVvAGQ","image":"","note":NOTE},
 # --- Bangladesh (snippet-harvested) ---
 {"name":"PSSM Bangladesh Bengali Meditation","category":"Community","country":"BD",
  "description":"Free Bengali meditation group run by the PSSM Bangladesh spiritual organization, open to all backgrounds.",
  "invite":"https://chat.whatsapp.com/GdMdEFHIY5RAseR8CQrKXy","image":"","note":NOTE},
]

json.dump(pending, open(P+"team20-unverified-pending.json","w"), ensure_ascii=False, indent=1)
print("pending items:", len(pending))
