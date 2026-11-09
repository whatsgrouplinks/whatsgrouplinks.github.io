import json
leads = [
 ("https://tglinkhub.com/all-group-links/", "tglinkhub hub listing page"),
 ("https://tglinkhub.com/aunty-whatsapp/", "tglinkhub aunty whatsapp listing"),
 ("https://tglinkhub.com/bhabhi-whatsapp/", "tglinkhub bhabhi whatsapp listing"),
 ("https://tglinkhub.com/education-group/", "tglinkhub education whatsapp listing"),
 ("https://tglinkhub.com/entertainment-whatsapp/", "tglinkhub entertainment whatsapp listing"),
 ("https://tglinkhub.com/girl-groups/", "tglinkhub girl groups listing"),
 ("https://tglinkhub.com/indian-whatsapp/", "tglinkhub indian whatsapp listing"),
 ("https://tglinkhub.com/pakistani-girl-whatsapp/", "tglinkhub pakistani girl whatsapp listing"),
 ("https://tglinkhub.com/pakistani-whatsapp/", "tglinkhub pakistani whatsapp listing"),
 ("https://tglinkhub.com/women-whatsapp-group-link/", "tglinkhub women whatsapp listing"),
 ("https://tglinkhub.com/whatsapp/", "tglinkhub whatsapp hub"),
 ("https://tglinkhub.com/football-whatsapp/", "tglinkhub football whatsapp listing (search result)"),
 ("https://tglinkhub.com/tamil-girls-whatsapp/", "tglinkhub tamil girls whatsapp listing (search result)"),
 ("https://tglinkhub.com/pakistani-drama-whatsapp/", "tglinkhub pakistani drama whatsapp listing (search result)"),
 ("https://tglinkhub.com/delhi-whatsapp/", "tglinkhub delhi whatsapp listing (search result)"),
 ("https://tglinkhub.com/movies-whatsapp/", "tglinkhub movies whatsapp listing (search result)"),
 ("https://tglinkhub.com/category/girls/", "tglinkhub category archive: girls"),
 ("https://tglinkhub.com/category/jobs/", "tglinkhub category archive: jobs"),
 ("https://tglinkhub.com/category/education/", "tglinkhub category archive: education"),
 ("https://tglinkhub.com/category/entertainment/", "tglinkhub category archive: entertainment"),
 ("https://tglinkhub.com/category/news/", "tglinkhub category archive: news"),
 ("https://tglinkhub.com/category/sports/", "tglinkhub category archive: sports"),
 ("https://tglinkhub.com/category/country/", "tglinkhub category archive: country"),
 ("https://tglinkhub.com/category/mix-groups/", "tglinkhub category archive: mix groups"),
 ("https://tglinkhub.com/category/aunty/", "tglinkhub category archive: aunty"),
]
out = [{"url": u, "source": "team12-tglinkhub", "note": n} for u, n in leads]
json.dump(out, open('team12-leads.json','w'), ensure_ascii=False, indent=1)
print("leads:", len(out))
