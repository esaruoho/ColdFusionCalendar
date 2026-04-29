# The Cold Fusion Calendar

An interactive chronology of Low Energy Nuclear Reactions (LENR) and energy science — every milestone of cold fusion from antiquity to the present, navigable by month and year.

**Live: https://www.lackluster.org/cf/**

## What it does

- 290+ historical milestones — from Newton's *New Theory of Light and Colors* (1671) to ICCF-27 (2026)
- All 27 ICCF / ICCMNS conferences indexed with verified dates and proceedings PDFs
- 26 Cold Fusion Now! podcast episodes (2018-2019) imported with audio links
- 17+ LENR-CANR PDF papers cross-referenced; 4 verified cold fusion patents on Google Patents
- Today's anniversaries shown automatically; "Quote of the Day" rotator
- Auto-linked URLs and "Jed Rothwell" mentions

## Browse + share

| Feature | How |
|---|---|
| Search | `/` to focus, type to filter every panel live |
| Filter chips | Toggle Type / Origin chips above the calendar; multi-select; URL-shareable |
| Year input | Type `1989` in the year box and Enter — Ruby's request |
| Year-grid view | "Year" button (or `Y` key) shows 12-month heatmap |
| Today | "Today" button (or `T` key) jumps to today's date |
| Permalinks | `/cf/#1989-3-23` opens F&P announcement; `/cf/#person/mizuno` lists every Mizuno entry |
| Person pages | Click any name in an event card |
| Copy All | Dumps every event as markdown for ChatGPT / Claude / etc. |
| Mobile | Full bottom-sheet panel; drag handle (or tap) to dismiss |

### Keyboard shortcuts

| Key | Action |
|---|---|
| `←` / `→` | Previous / next month |
| `↑` / `↓` | Previous / next year |
| `T` | Jump to today |
| `Y` | Toggle year-grid view |
| `/` | Focus search box |
| `Esc` | Clear search and filters |

### Subscribe

| Format | URL | What it gives you |
|---|---|---|
| iCal | `https://www.lackluster.org/cf/calendar.ics` | Yearly-recurring events in macOS Calendar / Google Calendar |
| RSS | `https://www.lackluster.org/cf/feed.xml` | Next 60 days of upcoming anniversaries in any feed reader |
| Embed | `<iframe src="https://www.lackluster.org/cf/embed.html?day=today" width="320" height="200">` | "Today in Cold Fusion History" widget for your blog / forum |

### Footer links

coldfusionnow.org · lenr-canr.org · lenr-forum.com · lenr-news.com · GitHub source · iCal · RSS · Embed

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

## Deploying your own copy

1. Copy `.env.example` to `.env` and edit it:

   ```bash
   cp .env.example .env
   $EDITOR .env
   ```

   Set `DEPLOY_USER`, `DEPLOY_HOST`, `DEPLOY_PATH` and (optionally) `DEPLOY_URL`. SSH key access to the host is required — `ssh "$DEPLOY_USER@$DEPLOY_HOST"` should already work non-interactively.

2. Run the deployer:

   ```bash
   ./deploy.sh
   ```

   It will:
   - Rebuild `data.json` from `data.json.original` + xlsx + `additions.json` + `drops.txt`
   - Regenerate `assets/og-cf-calendar.png` with the current event count and latest ICCF
   - rsync the static site to your server (excluding sources, build scripts, `.git`, README, `.env`)

`.env` is gitignored — your credentials and server paths stay private. `.env.example` is the public template forks should copy from.

## Acknowledgements

- Original interactive calendar template: [Ray Studio](http://raybrowser.com/) running on Ray Browser
- 2019 spreadsheet of milestones: [Ruby Carat](https://coldfusionnow.org/) of [Cold Fusion Now!](https://coldfusionnow.org/)
- Updated content and improvements: Esa Ruoho, with Ruby Carat (Cold Fusion Now!) feedback driving the year-jump and "today" features

## License

Code: MIT. Historical data is sourced from public archives — please attribute the cold fusion archival community when re-publishing.
