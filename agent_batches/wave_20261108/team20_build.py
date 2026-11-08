import json, re

D = "/home/hatch/workspace/whatsapp-groups-site/agent_batches/wave_20261108/"
ver = json.load(open(D + "team20_verified.json"))
live = {x["code"]: x for x in ver if x["status"] == "live"}

# (code, category, country, description-topic)
KEEP = [
 ("JOZAGIiBPpR87JG1YhZplQ", "Education", "PK", "O Level Chemistry (Chem 5070) tutoring, study notes and exam help"),
 ("JGl8PCZGRvO7Xp3lvanrdn", "Education", "PK", "teachers across Pakistan sharing teaching resources, updates and guidance"),
 ("CHaxA4bKeDSAtPJxfQpc5v", "Education", "PK", "Pakistan Air Force test preparation, guidance and motivation for aspirants"),
 ("GfSvZlp6Eh56condB2NqM4", "Education", "IN", "maths preparation for competitive exams with practice questions and tricks"),
 ("CEMzPrKXdj9CWYkzgbxOGb", "Education", "IN", "reasoning preparation for competitive exams with practice questions and tips"),
 ("3rdfwN9J6mGCj4DcafsU41", "Education", "IN", "agriculture exam preparation, notes and discussion for aspirants"),
 ("IbCe3G6AqoBLy7e5Q1tXtC", "Education", "IN", "study notes for all government exams, current affairs and exam updates"),
 ("IbWWezxuT8q4Iry5CbU9cD", "Education", "IN", "general studies preparation for competitive exams with notes and quizzes"),
 ("3Z8a9gNljY1Fo6A2ge5tmQ", "Education", "IN", "ICAR agriculture entrance exam preparation, notes and guidance"),
 ("KL4qzUFUxhD3lVX90w4lqS", "Education", "IN", "English preparation for competitive exams with practice material and tips"),
 ("E4IX8dUViBYAwVTU0L0gZ9", "Education", "International", "DevOps and AWS learning, tutorials and discussion for IT learners"),
 ("BdgU9Z6BgWj8PvwIIUVrvI", "Education", "IN", "current exam updates, notifications and preparation discussion"),
 ("BnvrMXsAorGJtFntessIaw", "Jobs", "IN", "government job alerts, vacancies and exam notifications"),
 ("HbiDQdHSHfR17661T2oHXs", "Online Earning", "International", "online earning ideas, tips and discussion for members"),
 ("Fv3lCYLIhpfHn0hzd73YSr", "Online Earning", "International", "online earning in dollars, tips and opportunities shared by members"),
 ("L6vTZzYQeARL1oiqbHaxFP", "Education", "International", "IT courses and internship offers for students and freshers"),
 ("FZDLLee6BA4CT3WhT1CQR8", "Online Earning", "International", "earn money online, tips and opportunities shared by members"),
 ("EnyeREwpivBLPxv3VOqIdw", "Education", "CA", "pharmacy students sharing study resources, exam preparation and updates"),
 ("LQZoftVxndC8Lmv9ThePCQ", "Scholarship", "International", "scholarship updates, application guides and funding opportunities for students"),
 ("H59esmUSSMbKCPYn1ii5Md", "Education", "DE", "international exchange students and buddies at Ludwigsburg University, winter 2026/2027"),
]
ADULT = set("🥵🍆🍑🔞💦👅👄💋")
union = set(json.load(open(D + "dedupe_union.json")))
out, seen = [], set()
for code, cat, country, topic in KEEP:
    assert code in live, code
    assert code not in union, code
    assert code not in seen, code
    seen.add(code)
    name = live[code]["og_title"].strip()
    assert not (set(name) & ADULT), name
    assert len(code) == 22, code
    desc = f"Join {name}, a WhatsApp group listed under {cat}. {topic[0].upper() + topic[1:]}."
    out.append({"name": name, "category": cat, "country": country,
                "description": desc, "invite": f"https://chat.whatsapp.com/{code}", "image": ""})

def w(path, data):
    for i in range(5):
        try:
            json.dump(data, open(path, "w"), ensure_ascii=False, indent=1)
            print("wrote", path, len(data)); return
        except Exception as e:
            print("write retry", i, e)
    raise SystemExit("write failed " + path)

w(D + "team20-listicles-study-jobs.json", out)
w(D + "team20-listicles-study-jobs-pending.json", [])

leads = [
 ("https://grouplink.com.in/scholarship-whatsapp-group-links/", "grouplink-scholarship"),
 ("https://grouplink.com.in/ielts-whatsapp-group-links/", "grouplink-ielts"),
 ("https://grouplink.com.in/neet-whatsapp-group-links/", "grouplink-neet"),
 ("https://grouplink.com.in/freelancer-whatsapp-group-links/", "grouplink-freelancer"),
 ("https://grouplink.com.in/education-whatsapp-group-links/", "grouplink-education"),
 ("https://grouplink.com.in/top-500-jobs-whatsapp-groups-for-career-success/", "grouplink-top500jobs"),
 ("https://grouplink.com.in/2500-online-earning-whatsapp-groups-links/", "grouplink-online-earning"),
 ("https://grouplink.com.in/1000-join-active-placement-whatsapp-group-links-for-job-updates/", "grouplink-placement"),
 ("https://grouplink.com.in/all-exams-whatsapp-group-links-boost-success-with-ease-now/", "grouplink-all-exams"),
 ("https://grouplink.com.in/join-active-bank-exam-whatsapp-group-links-for-preparations/", "grouplink-bank-exam"),
 ("https://grouplink.com.in/study-material-whatsapp-group-links-for-quick-access/", "grouplink-study-material"),
 ("https://grouplink.com.in/female-job-whatsapp-group-links/", "grouplink-female-job"),
 ("https://grouplink.com.in/3200-indian-job-whatsapp-group-links/", "grouplink-3200-jobs"),
 ("https://grouplink.com.in/data-entry-whatsapp-group-links-skills-and-career/", "grouplink-data-entry"),
 ("https://grouplink.com.in/gulf-jobs-whatsapp-group-links-for-bright-careers/", "grouplink-gulf-jobs"),
 ("https://grouplink.com.in/europe-jobs-whatsapp-group-links/", "grouplink-europe-jobs"),
 ("https://grouplink.com.in/bank-jobs-whatsapp-group-links/", "grouplink-bank-jobs"),
 ("https://grouplink.com.in/private-job-whatsapp-group-links/", "grouplink-private-job"),
 ("https://grouplink.com.in/12th-class-student-whatsapp-group-links/", "grouplink-12th-class"),
 ("https://grouplink.com.in/join-latest-english-grammar-whatsapp-group-links/", "grouplink-english-grammar"),
 ("https://grouplink.com.in/powerful-python-whatsapp-group-links-for-learning/", "grouplink-python"),
 ("https://grouplink.com.in/sarkari-result-whatsapp-group-links/", "grouplink-sarkari-result"),
 ("https://grouplink.com.in/kota-university-whatsapp-group-links-for-students/", "grouplink-kota"),
 ("https://grouplink.com.in/all-india-study-whatsapp-group-links/", "grouplink-study"),
 ("http://grouplink.com.in/3000-indian-govt-jobs-whatsapp-group-links-group-link/", "grouplink-govtjobs"),
 ("https://whatstele.com/whatsapp/group-links/pakistani/", "whatstele-pk"),
 ("https://www.grouplinksforyou.com/search/label/Fiverr%20Whatsapp%20Group%20Links", "grouplinksforyou-fiverr"),
 ("https://joingram.in/online-earning-whatsapp-group-links/", "joingram-earning"),
 ("https://whatinfotech.com/1000-active-whatsapp-online-earning-groups-2026-free-join-links-for-make-money-online-ideas/", "whatinfotech-earning"),
 ("https://whgroups.link/pakistan-jobs-whatsapp-group-links/", "whgroups-pkjobs"),
 ("https://newgrouplinks.pk/jobs-whatsapp-group-links/", "newgrouplinks-jobs"),
 ("https://ccsupsc.com/join-upsc-jpsc-bpsc-whatsapp-group/", "ccsupsc-upsc"),
 ("https://hubrecipes.com/active-english-learning-whatsapp-group-links/", "hubrecipes-english"),
 ("https://groupsinvite.link/education/study/english-learning/", "groupsinvite-english"),
 ("https://wahublink.com/online-earning-whatsapp-group-links/", "wahublink-earning"),
 ("https://englishan.com/english-whatsapp-group-link-2021/", "englishan"),
 ("https://opendoorpathways.com/opportunity/all-funded-submit-applications-for-the-waaw-foundation-scholarship-2026-for-african-women-in-stem-undergraduate-scholarship/", "opendoorpathways-waaw"),
 ("http://cv-templates-for.blogspot.com/2026/10/complete-scholarship-application-guides.html", "cv-templates-scholarship"),
]
w(D + "team20-listicles-study-jobs-leads.json", [{"url": u, "source": s} for u, s in leads])
from collections import Counter
print(Counter(g["category"] for g in out))
print(Counter(g["country"] for g in out))
