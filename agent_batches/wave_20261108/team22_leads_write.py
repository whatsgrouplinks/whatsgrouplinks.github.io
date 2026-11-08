import json
W = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/"
leads = [
 {"url": "https://groupsgyani.org/whatsapp-group-links", "source": "groupsgyani"},
 {"url": "https://blockpool.io/blog/best-crypto-whatsapp-groups.html", "source": "blockpool"},
 {"url": "https://www.directionsmag.com/crypto/best-crypto-whatsapp-groups", "source": "directionsmag"},
 {"url": "https://www.forexgdp.com/forex-signals/whatsapp-group-links/", "source": "forexgdp"},
 {"url": "https://grupbul.com/group/915743", "source": "grupbul"},
 {"url": "https://grupbul.com/group/479310", "source": "grupbul"},
 {"url": "https://grupbul.com/group/742466", "source": "grupbul"},
 {"url": "https://grupbul.com/group/358957", "source": "grupbul"},
 {"url": "https://www.grouplinksforyou.com/search/label/Forex%20Trading?&max-results=5", "source": "grouplinksforyou"},
]
json.dump(leads, open(W+"team22-listicles-crypto-earning-leads.json","w"), indent=1)
print("leads:", len(leads))
