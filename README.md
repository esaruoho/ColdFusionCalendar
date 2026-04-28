# The Cold Fusion Calendar

An interactive chronology of Low Energy Nuclear Reactions (LENR) and energy science — every milestone of cold fusion from antiquity to the present, navigable by month and year.

**Live: https://www.lackluster.org/cf/**

## What it does

- 255+ historical milestones — from Newton's *New Theory of Light and Colors* (1671) to ICCF-27 (2026)
- Click any highlighted day to surface that day's events
- Today's anniversaries shown automatically — no clicking required
- "Quote of the Day" rotator (173 undated archive aphorisms)
- Year input — type `1989` and jump there directly
- Copy All button — dump every event as markdown for an LLM
- Auto-linked URLs and author names (e.g., every "Jed Rothwell" mention links to lenr-canr.org)
- All 27 ICCF / ICCMNS conferences indexed with verified dates and locations
- Footer links: coldfusionnow.org, lenr-canr.org, lenr-forum.com, lenr-news.com

## Run it locally

```bash
git clone https://github.com/esaruoho/ColdFusionCalendar.git
cd ColdFusionCalendar
python3 -m http.server 8765
open http://localhost:8765/
```

That's it — no build step, no dependencies for the runtime.

## Project layout

```
ColdFusionCalendar/
├─ index.html               UI shell
├─ style.css                Theming
├─ main.js                  Calendar logic, event rendering, quote rotator
├─ datasets/
│  ├─ 40d7f378-…/data.json  Generated event database (do not edit by hand)
│  ├─ 40d7f378-…/quotes.json Generated undated archive quotes
│  ├─ additions.json        Hand-curated entries (ICCF conferences, modern milestones, URL-enriched movies)
│  └─ drops.txt             Exact blurbs to remove (truncated duplicates of better entries)
├─ build_data.py            Rebuilds data.json + quotes.json from xlsx + original + additions
└─ source_grab/             Pristine copy of the original deployment for reference
```

## How the data is built

`data.json` is **generated**, not hand-edited. The pipeline merges three sources:

1. **`data.json.original`** — the curator-edited dataset from the original deployment (189 entries)
2. **`2019Spreadsheet.xlsx`** — an external spreadsheet with 379 rows (199 dated events + 173 undated aphorisms + duplicates of the curator data)
3. **`additions.json`** — hand-written corrections and additions (canonical ICCF entries, IMDb/DOI/YouTube links, modern post-xlsx milestones)

The build script:

- Cleans typos via `TYPO_FIXES` (e.g., `inititating` → `initiating`)
- Normalizes whitespace, line breaks, comma-spacing
- De-duplicates by `(name, normalized blurb-prefix[:50])`
- Drops short stub blurbs listed in `drops.txt` when a longer version exists for the same event
- Reindexes everything sorted by year → month → day

```bash
python3 build_data.py
# wrote 255 events and 173 quotes
```

## Adding or correcting entries

### Add a new event

Append an object to `datasets/additions.json`:

```json
{
  "month": 8,
  "date": 17,
  "year": 2017,
  "name": "Storms / Cold Fusion Now!",
  "taxonomy": "Movie",
  "country": "US",
  "blurb": "“Hydroton — A Model of Cold Fusion” by Edmund Storms, produced by Cold Fusion Now!. Watch: https://www.youtube.com/watch?v=D4BPtwzsgiw"
}
```

Then `python3 build_data.py`.

URLs in blurbs are auto-linkified at render time (open in new tab).

### Correct a typo across all entries

Add it to the `TYPO_FIXES` dict in `build_data.py` and rebuild.

### Drop a duplicate / outdated entry

Append the exact stub blurb to `datasets/drops.txt`.

### Replace an existing entry

Add a new entry to `additions.json` with the **same `name` and matching first 50 normalized characters of `blurb`** — the dedup key collides and `additions.json` always wins.

## Acknowledgements

- Original interactive calendar template: Ray Studio
- 2019 spreadsheet of milestones: cold fusion archival community
- Updated content and improvements: Esa Ruoho, with Ruby Carat (Cold Fusion Now!) feedback driving the year-jump and "today" features

## License

Code: MIT. Historical data is sourced from public archives — please attribute the cold fusion archival community when re-publishing.
