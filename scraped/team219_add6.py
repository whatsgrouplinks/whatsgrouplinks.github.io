#!/usr/bin/env python3
"""TEAM 219 add-on batch 6: full technoearning.in page harvest."""
import json, os, pickle, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPED = os.path.join(BASE, 'scraped')
OUT = os.path.join(SCRAPED, 'team219-friendship.json')
PKL = os.path.join(SCRAPED, '_seen_all_codes.pkl')

seen = pickle.load(open(PKL, 'rb'))
existing = json.load(open(OUT, encoding='utf-8'))
have = set(seen) | {e['invite'].rsplit('/', 1)[-1] for e in existing}

LABELED = [
("Girls WhatsApp Group", "G2HsvRw87moIudiSFm2sDj", "Girls friendship group"),
("Kerala WhatsApp Group", "Eq3ZttErdKe94IYLUnPvem", "Kerala community social group"),
("Indian WhatsApp Group", "Jtcz6zhyI9lF77NbaPsvk2", "Indian community social group"),
("USA WhatsApp Group", "BRZk6Oe3DxcEY7SM4hvXWf", "USA community social group"),
("full Masti", "BBpT3JVRz4i5a8FPKg1mUN", "Fun and friendship group"),
("Uttrakhand WhatsApp Group Link", "ExGCSzFeW7t9j1yEuyxVpx", "Uttarakhand community social group"),
("Australia WhatsApp Group", "Cm9AU949j2lHNmb9AAld0b", "Australia community social group"),
("Indian WhatsApp group links3", "L5enUGXf3e87cad1ccspSL", "Indian community social group"),
("Indian WhatsApp group links 4", "DOvqrbP84AdDdfflQcns5P", "Indian community social group"),
("Dosti Group", "GovWgIP969ZEIQoadyS0mq", "Dosti friendship group"),
("WhatsApp group girls", "FlfVDsKhztKGoIPTaxaWoT", "Girls friendship group"),
("Punjabi girl WhatsApp group link", "KnJGkrhYMrwBGQX4JHutGi", "Punjabi girls friendship group"),
("WhatsApp group girls", "1wEQNMG9oytGtGMPuiiT0W", "Girls friendship group"),
("WhatsApp group girls", "HZLM2oRHmob1IJKk1fV4yE", "Girls friendship group"),
("WhatsApp group girls", "Bv5UUyUskYXEdz1URSgiDx", "Girls friendship group"),
("WhatsApp group girls", "IHd1gnD9Jzf1Kw9cI0LR6p", "Girls friendship group"),
("friendship WhatsApp group", "GkEmISGYa4c3JiIaqojm4V", "Friendship WhatsApp group"),
("WhatsApp group girls", "CxP4iq3Rev5JdJJLGwen5j", "Girls friendship group"),
("WhatsApp group girls", "BYzVNQCGyvvBBIm4DzvHL2", "Girls friendship group"),
("Punjabi girl WhatsApp group link", "F4SegnKYnHeAUBUp7ftokQ", "Punjabi girls friendship group"),
("Brazil WhatsApp Group", "DwWhlyYo19SL5kDwuQiBaS", "Brazil community social group"),
("WhatsApp group girls", "Jptchc7pcwJ0oEqaqeQWU5", "Girls friendship group"),
("Punjabi girl WhatsApp group link", "FvzVZUstBKiF9CscQXzvbc", "Punjabi girls friendship group"),
("girl WhatsApp group join", "IBXFtxLHtT20r70rNA0vy9", "Girls friendship group"),
("WhatsApp group girls", "HP9i9hnVGmM8NzJkEpzr7R", "Girls friendship group"),
("Punjabi girl WhatsApp group link", "Jf95AJDtBlWK63tcWwIvxh", "Punjabi girls friendship group"),
("Punjabi girl WhatsApp group link", "LCqjGTXMTgI5GyeWCjoSuA", "Punjabi girls friendship group"),
("Punjabi girl WhatsApp group link", "KnnX2WxWZxi80CxlUuyq4N", "Punjabi girls friendship group"),
("girl WhatsApp group join", "EBujfRbIIbHIk4X2CboAD2", "Girls friendship group"),
("Love Story", "KJ5x4ugSQZXJjWC7lPVbiC", "Love story social group"),
("Love Story", "BzCTUSz3ooO4ivMZUJcqSu", "Love story social group"),
("girl's WhatsApp group name", "HpKlN67A6XOLjBL3RwpMaT", "Girls friendship group"),
("girl's WhatsApp group name", "Jf8mlnaTstL6Eq6tdtAx0b", "Girls friendship group"),
("girl's WhatsApp group name", "EWF8eVJ2Dgz0zA9qGFxWb1", "Girls friendship group"),
("girl's WhatsApp group name", "GVKr23E0zoCI2kYX8oO9KA", "Girls friendship group"),
("girl's WhatsApp group name", "EYANZIh9R5v9OF9qWpXXyK", "Girls friendship group"),
("girl's WhatsApp group name", "CYkTQQNydbCIlSnBbpW6Eq", "Girls friendship group"),
("girl WhatsApp group join", "CW63y8rJq3VFE8ZC7rpDgq", "Girls friendship group"),
("girl WhatsApp group join", "LKC4kKhoXh90Uk5wNZme4R", "Girls friendship group"),
("Punjabi girl WhatsApp group link", "DqK3GAHrY1gHQdo5D5XpAo", "Punjabi girls friendship group"),
("girl's WhatsApp group name", "G1o5KWdgjgh1FxTzpdfOYf", "Girls friendship group"),
("girl WhatsApp group join", "IyMQb8PsC8OKwg3g7RpHzb", "Girls friendship group"),
("girl's WhatsApp group name", "0QRoE4vRosnKsBrUD6aui5", "Girls friendship group"),
("friendship WhatsApp group", "KGCfX3YIdNRAqYO2lNcLLI", "Friendship WhatsApp group"),
("friendship WhatsApp group", "I3DMfjMaFlI63tt4noHzsz", "Friendship WhatsApp group"),
("friendship WhatsApp group", "Do1XNzIHgL69LVjVbNF3R6", "Friendship WhatsApp group"),
("friendship WhatsApp group", "HQVXE3Y67yj0oQjXqxrDCc", "Friendship WhatsApp group"),
("friendship WhatsApp group", "LsVyztVFYIi8f5htIknj1p", "Friendship WhatsApp group"),
("friendship WhatsApp group", "KtvcQLPwMMnG7vdbjaGyjK", "Friendship WhatsApp group"),
("friendship WhatsApp group", "JzWxLlUr9djGMh7twNK6FQ", "Friendship WhatsApp group"),
("Indian WhatsApp group links 1", "L44xni2qmHGJOHrfBeAdDs", "Indian community social group"),
("Indian WhatsApp group links 2", "Bn9MT07C7cl5qzub0HrjWf", "Indian community social group"),
("whatsappgroupjoinlink", "CPldieVbY8OHEWTVYNWEf", "Social group"),
("whatsappgroupjoinlink", "G246k52gfgJJK86KX5T7pv", "Social group"),
("whatsappgroupjoinlink", "BDZd2y6G5JJAJcKXSnxcPd", "Social group"),
("whatsappgroupjoinlink", "EA2hZujSCxHG1FKyDmnYFM", "Social group"),
("whatsappgroupjoinlink", "EpSiveiwhqqDeLgA2CqsLv", "Social group"),
("whatsappgroupjoinlink", "HIOhke4bRniDbLKCD5zQGv", "Social group"),
("whatsappgroupjoinlink", "Cdi7GFMkMqu8YJvV3ZWRxr", "Social group"),
("whatsappgroupjoinlink", "BufKn94ImTe3DOpBxJJZ6k", "Social group"),
("whatsappgroupjoinlink", "K3Twi1WFQB4CUqibVzuVdh", "Social group"),
("Punjabi girl WhatsApp group link", "JUXcHB5kPv40QTdMr8t3hR", "Punjabi girls friendship group"),
("Punjabi girl WhatsApp group link", "Gg1wpE9Y7hLF02y6SoAJjd", "Punjabi girls friendship group"),
("Punjabi girl WhatsApp group link", "FG3gqv6ux1GK0OHMPg3XnI", "Punjabi girls friendship group"),
]

UNLABELED = """FZUmFQ4s6aMDyvy4EWZovP CtVM1cllIxK30hQOxfNsSP CNx1S3caQGzCTZ8iOY265x L7y2DysdpWC1UGSXMzCd9B
KBBzb176bVd2gub8TYOij9 I12VZ0YnIax9K0pm1MRE3c JuAMWLUTBae1b3WlEKxcPY Gn6vBA918sS5yvfbnwxHqQ
FFLGG0u0Af86geJ4PH89kE Er40kJvImat4DQ7nSM54fu JqFSGqGUKBdEhTt9Y8EUEi Lc1NXgzeGe41XLLbZeLCHQ
F7jalLtt3zHH3jMJuwvjLx HnO787aQNbCGcetUHSWr9M Cc9FrjOXmzECe2b0ozMGGW E1Q8yF6J4nMDDFgyhqZLwd
BYuXhVDdKRpG88jbNIvogK IIS1J4w4V9S1QQckkrny5W KKaQaKcMc1lBfvMA5q3kAk F2vuwcyQO4iDxlKspJizdp
EChtmmurJId3ZqxBc32vWj Idc4JxFcQBc0AkaSJOAl19 FPdbjsBkCeA8tLJN592xsI CFl3vVhfItx356A8fcIef3
BpLUrVO6RW251gdAC5ittd JjFgSt51FM7040crRyK5im COdEoHdnpRrLfAaM4TWcve Eb7qr4CJANp9zejnB0k463
GWFZys1Ck4v6KHHoyn3frE EHs1VuBugwt0zln6206Zqy 96GAB69ZwJoKaQOU3CGRWj FtXCQSTfsvc9BfchJ9eE18
Lh6dp7FOXKMKnjq7cbIyKc GueWWxAP35sCCpj1V7fuB5 DvfOOy6sNHnJPC1UycWgN2 CcK1OaluZRLEpLWiYYARk9
B8uTKdpcVUoITqjTCNLIqz GyW4hJVHaIUKoVxfJcqK7X Drk0XMHXEERA9hoXhlWj7t Kdy2LgBfQrqIHMzOAOIBS5
F28mHc8q1liB2IGJupq7Xj LpCkEMmttTj3V18LV9fO49 LZVprZBRvXV10K07fHa91g KddmkvaEY526wk6lkBPJmJ
FEJiRe5rr7WKS3dAedATJf FgZtCPoJmB84SokOV9worr Enb9IYugkaeKWwWDmzJC4r I7eOaPYiuYY8308p4fzjjU
INBH6pbn6d2L1hKK0shni7 FTTAkkGciJO91G2ZTTkRs8 IohLTCwZIPX0UzVKjJ6P9z C2OenJc3iPaIds9enzITkC
GPzB4KOxKz64jUVEQjVxee JDkb5gGKqDr1eDKYDRrKkG GjN0K9Hn0qGDqA3IBjMS65 ERTNWPqaueA3f5zMRYEzcO
JK5Cdkz9dyz4sSloy7iMsy LxUSPgVTauQ7NWKyaiZuJ9 I9WVPkx2fXM3oaPQaXxXdG DnmFzQ0Ew0fAIUyTo1Z3lq
KWFJYMnUmzJ6Hat5umkaQi BoD2RDIMBzcLdo3sbdpVDZ L6lfGZq5wEKBNPXwIhobUU K0rb8ADzhRg1fAmsxzJbwB
JcL120XObM82m8qcXqtVuM Bljv5kRvsnH8orcHG4EjAa GDYjSjmOQTVGLlFN4EZktY BbNGPNWWufF6gZvK2KDEEG
BL3ehLCvy9lE25P8IJ3Uj6 EkWdFdUoype8r9noL0be6w IVfnzZunVZwBNlP35wEGe7 JwzlRhPKdfY6LHnvnZYLri
Iq9MoRGceKuL8EC2rYJTAY JwhYmae73LJItntvVhwapN EUbeYNZI1Hy3UtJqQoUMig DjtUQM2plrw9KUJjZwJfGl
7QkNeBoQjWQGYB5KnTq6cI LBhCFwyy9nn7yqHdWSIR8r Kz4lUhDE9YWIntWtDWGfwW DcMoZIlPChwF2wNLfA2366
JDgQQa9OEeK4VjMVaUVLHD EaQVeACrT6n8Hc5iLTNl4W CZOvvt0gAz59a5PnBFyGyk HzdOcMvY7mW6EleeXwhPCY
HtvOnjS7ugzFB4a98uNwEN J1YvBwvjq8r7Ef0Q7jCuJN CvfI2Cxs6uQGDmq8ss3wRz H3ffkNKegNtCngIjNznZYL
BVvqfveSoyeJXVfHUnV6AB GladNNKc0RIKLYAKu8vMai KyD7B66GrtkIUn7JscQtXB Cj1ORUE4pysFo6kkAkfSDe
JjYQVGxrAvdGDiuoFScITO GCbSBTsG09s325qzSPEP6U LuU3LO4qZtiI2ecxppcmyE JnB5TbASOy91iOyBlGyBFa
Bik6IcSu5ynBpOiXrmsWEi LqxKKoxo3QsJs9jM7G4aK7 BOn9iHlDwhnGmFo0qKQZXW IOkdXIDaXNNKK3Iu6htkbd
J4fhJ5p3N6QDvrmkeQIwXc FrVqH6VaUKMGGDt9bUHIF1 HA7bQCU9U3PBpzkNScf0eR GgkkKLlh4onFx5c0bv2oh0
CeJX7Qrfn4cE1JEZ2McZO9 LNGcr5JfNmkB4Ienw1F6rj DQoiefGzmcS7Zf2i7Gd3NR DMn9LfvX6uY9Nb73zZfJPY
H5ZFtjQiIBj07HKfXkOMHL Dj79RVVaZwe8SQWRUBZgG5 FuAf54QOyCpEb0gzbrlIh0 Jxh2c7JlgoLEzCXxJXXKAF
JMX9GYwJxx64D6yxwpIWx9 Di5GwIrd7t3IFr7FaCz7CH DkoIjpJ8gNQIwvIJbCyZgb J9orChGsXFBFv3xNZBHb5Q
BtE7efEKsv82qff6aYpj01 FKKLvE2xMm90XEWsrsSZHy Dg4Tl21Mzh35RVSsJs9a8q BLgDyPgwrxwGBWd89t2xVe
Gqratpa1OmK9je3Lgja2Hl GVU4Zhhmrtp2tfG4IBXcr9 JGYb14MDwGK6eL4B6J5v2t CGGItRidENZEoXgfYIMtwE
KS7DHzI2G2QLJUIsKAYOiE DDvSwyfNuIaLDZL35qNwTg ECiEWwtm4VQLieAaU6XwUO Hn3lnna2koHBDrb5fCsTiA
GQixkSjFX7ZAsBRHzSKagJ L0AloQoqMiH9fWxmCfDNdF JDubQABbXu3BSkZrlY3XXb GGBij4g83Qb0WMuYpRi4xr
DtBixfqCgFOBT8rnF90JwP FcLQfPLpIvs36j3VHdYXMU I9wmPl7E1qYHDNSwhzAYey D4W5ByldEsqFs7HT2WMboy
Clnh5yuY9ZE64aPl0BONt3 CYQywO6gobO7gBiBnUIDqs G9rFNUfe97JBp0ZpGWsLC9 LpXgk3c7AXFH9tMYYMzMC9
LyBHQfbwzGQJrTPjaDPAUN FHKjYWGhrwF3ZZdxI31k8n EQh4Xv5TYKv0CFcEfjDBFt LOeY0kXF5jVITz22AUiBNJ
DOrsqBPaEiZ5DJPI1fdXIM 2ZjDSrOnhXa1jqVHsF5atB 6pO80ObUHqK6XM6Zrxh6qv 1HQ8piAEq009QZ7xv9Y5Vz
JZHhk9vU7cJ77PxpjKn4WY KLc727MvcHw864evK0sm4a IQk25OKHlFELuHQx20NxcZ BpWBdnrGmX8Ju8ayP4UJXS
Fr7aUMAmelO9pymGTLPHvG J5GoggWOP3z56zoAE2QQmR DSP0QAD7vtu33Dggsm0Wc3 ERPBj3WNw1s0vu4Vum1iT8
FFiikAGe80M75A6nhCRrtd Gvr1WTlUHyq3mQqdLOKPBp Ces93oZBfDx9QTAYp9Eldq LsRKclsbY5cAd1bL84Oo2g
GqddXpC8eEOIqDznG1LrsN JGdOCBilX057Is6bhtaH2i Fko2XfKkoWu7DCeMEaFL2S ISfZpfbv80jJsBSW1pW98i
JpT5Pkn6RBv4P4pTTp6Tzg DGuW2Za8TOu9wE15lhZcfN DmvBptWnbvR7yEba6DIs6o HXESqR2fkGZKkGPKoUpDeB
LmNvXRZuizaCf6Pf3MKx6R BmU4AMpI148JsuAouXpTpm DN5NF23DB0G07rGAS5TYNw Fq6aFRnuc1d4NmiGqKlxqP
Jkb9JUCmNJQ8iw7XaQmKOo E1oVJIuxuITDj60KGXDR6N GtEDuhpugRqBJQlhidBtCE Dtf6Qk908ks3OBqVUSPpQA""".split()

PORN = re.compile(r'(?i)\b(porn|pornhub|xxx|sexy|nudes?\b|escorts?|call\s*girls?|adult\s*(video|chat|dating)|hentai|onlyfans|cam\s*girls?|paid\s*girl|hotel\s*girl|girl\s*(photo|number|phone))\b')
added = skipped_seen = 0
n = 0
for name, code, desc in LABELED:
    code = code.strip()
    if code in have or PORN.search(name + ' ' + desc):
        if code in have: skipped_seen += 1
        continue
    have.add(code)
    existing.append({"name": name, "invite": f"https://chat.whatsapp.com/{code}", "desc": desc, "cat": "Friendship"})
    added += 1
for code in UNLABELED:
    code = code.strip()
    if code in have or PORN.search(code):
        if code in have: skipped_seen += 1
        continue
    n += 1
    have.add(code)
    existing.append({"name": f"Interesting WhatsApp Group {n}", "invite": f"https://chat.whatsapp.com/{code}", "desc": "Social group", "cat": "Friendship"})
    added += 1

json.dump(existing, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"added={added} skipped_seen={skipped_seen} total={len(existing)}")
