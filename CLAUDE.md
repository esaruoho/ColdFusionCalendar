# Cold Fusion Calendar — Project Instructions

Static interactive chronology of cold fusion / LENR milestones.
Live: https://www.lackluster.org/cf/  ·  GitHub: https://github.com/esaruoho/ColdFusionCalendar

## Read these first

At the start of every conversation in this project, read these two files before doing anything else:

1. **`PLAN.md`** — strategic state of the project (what's shipped, what's open, what's blocked, sequencing recommendations)
2. **`TODO.md`** — granular content + data-quality backlog (live patents table, patents to research, books backlog, blocked events, ICCF highlights queue)

For history of changes, see `CHANGELOG.md`.
For user-facing onboarding, see `README.md`.

## Repository map

| Path | Role |
|---|---|
| `index.html` · `style.css` · `main.js` | UI shell, theming, calendar logic |
| `datasets/40d7f378-…/data.json` | **Generated** event database (do not edit by hand) |
| `datasets/40d7f378-…/quotes.json` | **Generated** undated archive aphorisms |
| `datasets/additions.json` | **Hand-curated** entries — ICCFs, modern milestones, URL-enriched movies, podcast cross-refs, patents |
| `datasets/drops.txt` | Exact blurbs to remove (truncated duplicates of better entries) |
| `build_data.py` | Rebuilds data.json + quotes.json from xlsx + original + additions; applies typo fixes, country/taxonomy normalisation, dedup |
| `build_og.py` | Regenerates the static og:image with current event count |
| `build_og_per_date.py` | Generates 200+ per-date og:images at `assets/og/MM-DD.png` |
| `build_ical.py` | Emits `calendar.ics` (yearly recurring events for any subscribe) |
| `build_rss.py` | Emits `feed.xml` (next 60 days of upcoming anniversaries) |
| `tests/test_build_data.py` | Regression tests (counts, schema, dups, iCal/RSS validity) |
| `deploy.sh` | Reads `.env`, runs all builders, rsyncs to lackluster.org |
| `.env` (gitignored) | `DEPLOY_USER` / `DEPLOY_HOST` / `DEPLOY_PATH` / `DEPLOY_URL` |
| `.env.example` | Public template for forks |
| `source_grab/` | Pristine snapshot of the original Ray Studio deployment for reference |

## Editing data — three mechanisms

### Add a new event
Append a JSON object to `datasets/additions.json` with `month`, `date`, `year`, `name`, `taxonomy`, `country`, `blurb`. URLs in blurbs auto-linkify; "Jed Rothwell" mentions auto-link to lenr-canr.org.

### Replace an existing entry
Append a new entry to `additions.json` with the **same `name`** and **matching first 50 normalized characters of `blurb`** — the dedup key collides and `additions.json` always wins.

### Drop a duplicate / outdated entry
Append the exact stub blurb to `datasets/drops.txt`.

### Fix a recurring typo
Add to `TYPO_FIXES` dict in `build_data.py` and rebuild — applies retroactively to every entry.

## Deploy flow

```bash
./deploy.sh
```

Runs in order: `build_data.py` → `build_og.py` → `build_ical.py` → `build_rss.py` → `build_og_per_date.py` → rsync to `lackluster.org/cf/`. Excludes build scripts, tests, `.env`, `.git`, README, PLAN, TODO, source_grab from the deploy.

## Conventions

- **293 events** currently · **15 taxonomies** · **27 ICCFs** · **12 patents** · **26 podcasts** · **163 URLs across 126 entries**
- **Trailing-year stripping** — blurbs ending in "...1989", "(1999)", "*1989", or "Mon DD, YYYY" auto-strip; year is already in the year field and shown in the date chip
- **No guessed dates** — for events without verified dated sources, skip rather than guess. Better 290 honest entries than 295 with fakes.
- **Free-energy adjacent content out of scope** — Tesla / Schauberger / Russell / Moray / EVO / Bedini etc. don't go in this calendar. If ever needed, build a separate "Free Energy Calendar" project.

## When in doubt

- Strategic ("what should I work on?") → `PLAN.md` § What's left
- Tactical ("what's missing in the data?") → `TODO.md`
- Historical ("what changed when?") → `CHANGELOG.md`
- User-facing ("how do I run / subscribe / contribute?") → `README.md`
