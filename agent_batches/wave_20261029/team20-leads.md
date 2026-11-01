# TEAM 20 — Leads (wave_20261029) — grouplink.com.in Malayalam Islamic

## Result
- **Slice exhausted, zero new links.** The Malayalam Islamic listing page
  (http://grouplink.com.in/malayalam-islamic-whatsapp-group-links/) was scraped in full:
  35 invite codes extracted (28 direct `chat.whatsapp.com/<code>` + 7 `/invite/<code>` variants),
  all mapped to group names — and **all 35 codes already exist** in the union of
  groups.json + .existing_codes.json. So: fresh=0, pending=0.
- Retired pages (Indian govt jobs, All India Study, sports, UAE/KW/SA) untouched as ordered.
- No /sex/ /xxx/ /adult/ pages visited; no adult content on this slice.

## Page structure note (for future runs)
- 35 rows across 5 sections: Quran Study Groups (6), Lectures & Islamic Media (7),
  Community & Knowledge (9 incl. Niswa Group — women's group, kept since no suggestive content),
  Daily Reminders & Info (7), Urdu Devotional (4: Ashiq E Raza, Deen-e-Mustafa, Allah Ke Bande, etc.).
- A previous wave clearly ingested this entire page; suggest the coordinator mark
  grouplink.com.in Malayalam Islamic as DONE/skip to avoid re-assigning it.

## Content filter check
- No titles matched the banned regex or suggestive-emoji rules; nothing dropped on content grounds
  (all 35 dropped only on dedupe).

## Flags
- NONE. Page re-crawled fine (HTTP 200, ~197KB). No 429s, no verification needed (nothing fresh to verify).
