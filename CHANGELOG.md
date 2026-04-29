# Changelog

All notable changes to The Cold Fusion Calendar.

## 2026-04-29

### Added
- **Search box** with live filtering of all panels and dimming of non-matching grid markers (`/` to focus)
- **Permalink URLs** — `#YYYY-M-D`, `#year-view`, `#person/<slug>` are shareable
- **Filter chips** — Type and Origin chips above the calendar; multi-select; URL-shareable
- **Keyboard navigation** — ←/→ months, ↑/↓ years, T today, Y year-grid, / search, Esc clear
- **Year-grid view** — 12 mini-calendars with heatmap density per day
- **Mobile bottom-sheet** — phone viewport gets full-width calendar with drag-to-close panel
- **Person index pages** — every event card name links to a chronological list of all entries referencing that person
- **iCal feed** at `/calendar.ics` — yearly-recurring all-day events, subscribe in any calendar app
- **RSS feed** at `/feed.xml` — next 60 days of upcoming anniversaries
- **Embed widget** at `/embed.html?day=today` — Today in Cold Fusion History card for iframe embedding
- **Per-date OG images** at `/assets/og/MM-DD.png` — sharing a specific date previews that day's milestones

### Changed
- Country names normalized: USA / U.S. / United States → "US"; Korea → "South Korea"; United Kingdom / Great Britain / England → "UK"
- Footer adds "📅 iCal", "📡 RSS", "⎘ Embed" links

### Content
- Added *Too Close to the Sun* (1994) IMDb tt2331825 + YouTube `?v=CZKRXabsa4I`
- Mitsubishi Estate / Clean Planet investment milestone (~2018)

## 2026-04-28

### Added
- 26 Cold Fusion Now! podcast episodes (Jan 2018 → Sep 2019) imported with full YAML frontmatter — guests, dates, audio URLs
- 27 ICCF conferences linked to lenr-canr.org proceedings (1–15) and iccf##.org / iscmns.org (16–27)
- 3 Cold Fusion Now! documentaries: Miles 2016 (Anomalous Effects in Deuterated Systems / Navy LENR Series), Storms 2017 (Hydroton), Biberian 2024 (Hydrogen Metal Energy Nanopowder)
- 4 verified cold fusion patents: Pons & Fleischmann US 4,943,355; Belton/BHP WO 1990/013124; Ikegami/Technova EP 0477018 A1; Andrea Rossi 2008 Italian / WO 2009/125444
- 17 LENR-CANR PDF papers cross-referenced from `articles/cold-fusion-patents-kron-russell-analysis.md` and bibliography
- 8 books linked to archive.org / lenr-canr / publishers (Storms 2007, Peat 1989, Mallove 1991/1999, Krivit 2004, Kozima 2006, Chubb 2008, Manning/Garbon 2009, Biberian 2012, Cold Fusion magazine 1993)
- 2019 Google Nature paper "Revisiting the cold case of cold fusion" (DOI 10.1038/s41586-019-1256-6)
- Heavy Watergate (Nov 20, 1998) + IMDb link
- TODO.md backlog tracking
- PLAN.md full development plan

### Fixed
- Comma-spacing regex no longer mangles patent numbers like "US 4,943,355"
- Drop checks now respect typo-cleaned blurbs (originally matched only raw)
- 45 truncated duplicate entries removed (kept the more detailed version)
- ICCF-1 year typo: 1991 → 1990
- ICCF-3 year typo: 1993 → 1992
- ICCF-17 start date: Aug 17 → Aug 12
- Toyoda Gold Medal entry: corrected from ICCF-10 → ICCF-15
- 11 typos: inititating → initiating, devleoped → developed, palldium → palladium, prsents → presents, col fusion → cold fusion, Industy → Industry, initiateve → initiative, Annlen → Annalen, Intertia → Inertia, Postassium → Potassium, Comanies → Companies
- Name fixes: Sttorms → Storms, Zowadny → Zawodny, Czech → Czechoslovakia
- Single MITI duplicate de-dup'd (MITI 1989 was appearing twice due to typo difference between original and xlsx)
- "Stupid" taxonomy renamed to "Reaction"
- Sticky panel headers now solid-bg (no scrolling-through-text)

### Changed
- Layout fix: constrain grid children so calendar doesn't stretch with side-panel content
- "Today / This Month / Upcoming Anniversaries" panel order
- Card layout: header row (date · country · taxonomy), then name, then blurb
- Quote-of-the-Day strip with three buttons (copy current, copy all, shuffle)
- Buttons fixed-width so ✓ glyph doesn't reflow them
- Today auto-highlighted on page load
- "Upcoming Anniversaries" anchors to viewed month, not always today

### Removed
- Ray watermark + Mixpanel beacons stripped from original deployment

## 2026-04-28 (initial)

### Added
- Initial repo published at https://github.com/esaruoho/ColdFusionCalendar
- Live deploy at https://www.lackluster.org/cf/
- Year-input box (Ruby's request — type a year to jump there)
- Today button + system-date awareness
- Auto-shown panel (no clicks required) with three sections: Today, This Month, Upcoming Anniversaries
- Click-day → highlight + scroll to matching event cards
- Build pipeline: `build_data.py` (xlsx + additions.json + drops.txt → data.json)
- 199 events imported from 2019 spreadsheet by Ruby Carat (Cold Fusion Now!)
- Auto-linked URLs and "Jed Rothwell" mentions in blurbs
- OG / Twitter Card meta tags + favicon + apple-touch-icon
- 1200×630 og-cf-calendar.png with dynamic event count
- Footer links: coldfusionnow.org, lenr-canr.org, lenr-forum.com, lenr-news.com, GitHub source
- "Copy All" button — every event as markdown for LLM ingestion
