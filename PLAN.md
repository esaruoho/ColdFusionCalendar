# The Cold Fusion Calendar — Development Plan

Ordered backlog of every improvement currently scoped. Each item has effort estimate, files to touch, and acceptance criteria. Work the list top-to-bottom; later items build on earlier scaffolding.

---

## Phase 1 — UX wins (the calendar feels modern)

### 1.1 — Search box  *(~30 min)*

**Why:** 292 events; no current way to type "Mizuno" and filter.

**Touch:**
- `index.html` — add `<input id="searchBox" type="search" placeholder="Search events…">` in the header `.controls` block.
- `main.js` — add `searchTerm` state on `FusionCalendar`; in `renderPanel()` filter `monthEvents` and `upcoming` by `term ⊂ blurb|name|year`. Calendar grid `event-marker` dots also gate on the same filter so the grid reflects the filter visually.
- `style.css` — input styling consistent with `#yearInput`.

**Done when:** typing "mizuno" filters all panels live; clearing the box restores the full view; the calendar grid dots dim on days that have no matching events.

### 1.2 — Permalink URLs  *(~20 min)*

**Why:** Sharing a specific date currently impossible.

**Touch:**
- `main.js` — on render, `history.replaceState({}, '', '#' + ev.year + '-' + month + '-' + day)`. On load, parse `location.hash`; if it matches `^#\d{4}-\d{1,2}-\d{1,2}$`, set `currentDate` + `selectedDay` accordingly before first render. Also handle `#today` and `#YYYY` (year-only).

**Done when:** `lackluster.org/cf/#1989-03-23` opens the calendar pre-scrolled to F&P announcement.

### 1.3 — Filter chips (taxonomy + country)  *(~45 min)*

**Why:** 24 taxonomies / 30+ countries currently scrolled past invisibly. Filter-by-category surfaces them.

**Touch:**
- `index.html` — add `<div id="filterChips" class="filter-chips"></div>` between `.main-header` and `.calendar-container`.
- `main.js` — `buildFilterChips()` enumerates unique `taxonomy` values (sorted by frequency); each chip is a toggle. Multiple selected chips OR-combine. URL hash extends to `#date,tax=Patent,Conference&country=Italy`.
- `style.css` — pill-style chips with active/inactive states.

**Done when:** clicking "Patent" filters to 4 entries; clicking "Italy" filters by country; combined filters AND-combine across categories but OR-combine within each category.

### 1.4 — Keyboard navigation  *(~20 min)*

**Touch:**
- `main.js` — global `keydown` handler:
  - `←/→` previous/next month
  - `↑/↓` previous/next year
  - `/` focus search box
  - `t` jump to today
  - `Esc` clear search + filters
  - `?` show keyboard shortcut help overlay

**Done when:** all five shortcuts work; `Esc` clears state cleanly.

### 1.5 — Year grid view  *(~1 h)*

**Why:** Quickly spot decades/months with dense activity.

**Touch:**
- `index.html` — add a `view` toggle button group: Month / Year.
- `main.js` — `renderYearGrid(year)` draws 12 mini-calendars (Jan–Dec); each day cell shows event-count saturation (heatmap).
- `style.css` — mini-calendar layout using `grid-template-columns: repeat(4, 1fr)` (4×3 month grid).

**Done when:** clicking "Year" switches to a 12-month overview with heatmap cells; clicking a mini-cell jumps back to month view at that day.

### 1.6 — Mobile responsiveness  *(~45 min)*

**Why:** Current 1024px breakpoint collapses the side panel below the calendar; phones get a tiny calendar with a wall of text below.

**Touch:**
- `style.css` — at `<= 600px`:
  - Calendar fills the viewport
  - Side panel becomes a bottom sheet that slides up when a day is tapped (`transform: translateY(...)` + drag-to-close)
  - Header controls reflow to multiple rows
- `main.js` — touch handlers for the bottom-sheet drag.

**Done when:** iPhone-sized viewport shows a clean calendar with bottom-sheet panel that drag-dismisses.

### 1.7 — Person index pages  *(~1.5 h)*

**Why:** Author-centric browsing (every Mizuno / Storms / Fleischmann mention in one place).

**Touch:**
- `build_data.py` — generate `datasets/people.json` keyed by normalized surname → list of event IDs that mention that person (search `name` + extract surnames from `blurb`).
- New file `people.html` and `people.js` — renders `/people/<slug>/` style routes (or `?person=mizuno` query string for static-host friendliness).
- `style.css` — person-page styling.
- Calendar `event-card .name` becomes clickable: `<a href="people.html?p=mizuno">`.
- README — document the `/people/` index.

**Done when:** clicking "Mizuno" on any event card lands on a page listing every entry referencing him, sorted chronologically.

---

## Phase 2 — Content wins (more right things in the DB)

### 2.1 — Verify and add 7 more patents  *(~1.5 h, requires patents.google.com lookups)*

From `TODO.md`:

| Patentee | Likely number | Action |
|---|---|---|
| Patterson / CETI | US 5,318,675 (Jun 1994) | Verify on Google Patents → add to `additions.json` |
| Patterson / CETI | US 5,372,688 (Dec 1994) | Same |
| Patterson / CETI | US 5,494,559 (Feb 1996) | Same |
| Swartz / JET Energy | NANOR series | Search "Swartz JET Energy NANOR" |
| Hagelstein / MIT | Theoretical method | Search "Hagelstein MIT phonon LENR" |
| Rossi / Leonardo | US 8,485,791 (granted 2013) | Add as separate entry from existing 2008 Italian filing |
| Godes / Brillouin Energy | US 9,115,913 | Verify |
| Storms | US 8,728,235 (2014) | Hydroton-related |
| Iwamura / Mitsubishi | US/JP transmutation patents | Multiple |

**Done when:** at least 7 new verified `Patent` entries with working Google Patents URLs appear in the calendar.

### 2.2 — Post-2013 event backfill  *(~1 h, mining CFN podcast notes for dates)*

Specific events to add:

- **Carl Page / Anthropocene Institute** funding rounds (~2018–2019) — research dates from anthropoceneinstitute.com news
- **MEXT NEDO MHE program** announcement (~2015) — Tohoku, $3.5M
- **Brillouin 2X thermal gain** announcement — date from CFN podcast #20 (2019-01-15)
- **Iwamura / Clean Planet** Tohoku launch — CFN podcast #21 (2019-02-19)
- **NASA Bushnell** "LENR is real" Aviation Week interview — research date
- **Google Nature companion announcements** — already have main paper; add UBC/MIT/LBNL companion press releases

**Touch:** `datasets/additions.json` for each, with sources cited in blurbs.

### 2.3 — Looser LENR-CANR pass at 60%  *(~30 min + manual review)*

**Touch:**
- `build_data.py` — temporarily lower threshold; run script that emits candidate matches; manually review for false positives; commit only verified ones.

**Done when:** 5+ additional Key Experiments / Publications carry lenr-canr.org PDF URLs.

### 2.4 — Cross-link podcasts to event entries  *(~1 h)*

**Why:** CFN podcast #12 (Miles heat-helium) is about a paper that's already in the calendar. Reader should see both linked.

**Touch:**
- For each podcast entry whose `guest`/topic matches a known calendar entry, append `(see also [Apr 27, 1991 entry](#1991-04-27))` style cross-references to the blurb. Build a script in `build_data.py` that does this matching.

### 2.5 — ICCF presentation highlights  *(~1 h)*

**Why:** Each ICCF is currently one entry; notable in-conference moments deserve their own.

**Touch:** Add ~15 dated sub-events: Iwamura's ICCF-9 transmutation results (date within May 19–24 2002), Letts/Cravens laser at ICCF-10 (Aug 2003), etc. Source: existing data + CFN podcast notes.

### 2.6 — Find *Too Close to the Sun* (1994) URL  *(~10 min)*

**Why:** Only unlinked movie. Likely on YouTube/archive.org/Vimeo.

**Touch:** `datasets/additions.json` — add link once found.

### 2.7 — Taxonomy normalization  *(~30 min)*

**Why:** Currently 24 categories with single-instance noise (Utah, F&P, DoE, Navy, Award, Patent, TV, History, Stupid→Reaction-already-done).

**Touch:** Map redundant taxonomies in `build_data.py` (`TAXONOMY_FIXES = {'Utah': 'Federal', 'F&P': 'Science', 'DoE': 'Federal', ...}`).

**Done when:** taxonomy count drops from 24 to ~12 stable categories.

### 2.8 — Country normalization  *(~10 min)*

**Why:** "US" / "USA" / "United States" mixed; same for "Japan, China" combos.

**Touch:** `COUNTRY_FIXES` dict in `build_data.py`.

---

## Phase 3 — Distribution wins (more people see it)

### 3.1 — iCal feed  *(~1 h)*

**Why:** Users subscribe in macOS Calendar / Google Calendar → "Today: ICCF-21 began (2018)" pops up automatically.

**Touch:**
- New `build_ical.py` — reads `data.json`, emits `calendar.ics` with one VEVENT per dated entry as a yearly-recurring all-day event (RRULE:FREQ=YEARLY). UID per entry-id. SUMMARY = name. DESCRIPTION = blurb (with URLs preserved).
- `deploy.sh` — add `python3 build_ical.py` step.
- `index.html` — add a "📅 Subscribe (iCal)" link in the footer pointing at `https://www.lackluster.org/cf/calendar.ics`.

**Done when:** subscribing the URL in macOS Calendar.app shows yearly recurring events for every dated milestone.

### 3.2 — RSS feed of upcoming anniversaries  *(~45 min)*

**Why:** Discord / Slack / Mastodon all consume RSS. "Upcoming this week" feed auto-posts to community channels.

**Touch:**
- New `build_rss.py` — emits `feed.xml` with the next 30 days of upcoming anniversaries; rebuilt nightly via cron OR on each deploy.
- `deploy.sh` — add `python3 build_rss.py` step.
- `index.html` footer — RSS link.

**Done when:** the URL validates at https://validator.w3.org/feed/ and shows up correctly in Feedly/NetNewsWire.

### 3.3 — Embed widget  *(~1.5 h)*

**Why:** Coldfusionnow.org / lenr-forum.com / lenr-news.com could embed "Today in Cold Fusion History" as a sidebar widget.

**Touch:**
- New `embed.html` — minimal page, no header/footer, just today's events card. Reads `?day=today|YYYY-MM-DD` from query string.
- `style.css` — `body.embed` mode strips chrome.
- README — document `<iframe src="https://www.lackluster.org/cf/embed.html?day=today" width="320" height="200">`.

**Done when:** the iframe renders standalone with no cross-origin issues.

### 3.4 — Per-date OG images  *(~1.5 h)*

**Why:** Sharing `lackluster.org/cf/#1989-03-23` should preview F&P's announcement, not the static "256 milestones" card.

**Touch:**
- Extend `build_og.py` → `build_og_per_date.py` that for each unique `(month, date)` with events, renders a card showing those events. Output to `assets/og/MM-DD.png`.
- `index.html` — JS that on load with a `#date` hash dynamically swaps the `og:image` meta tag to point at the per-date PNG. (For server-side rendering, add a tiny PHP/Python redirector at `/cf/og/?d=MM-DD`.)
- `deploy.sh` — call the new script.

**Caveat:** Twitter/Facebook cache OG images aggressively; URL-fragment changes don't bust their cache. Real-world this works best for new shares, not edits.

### 3.5 — Per-date OG via static query handler  *(alternate to 3.4)*

If 3.4's nginx static serving turns out limited, add a tiny `og.html` that uses `<meta http-equiv="refresh">` to redirect after setting the OG meta dynamically. Document the limitation.

### 3.6 — Email digest  *(~3 h, optional — needs server)*

**Why:** Weekly upcoming anniversaries email — low-frequency, high-signal subscriber loop.

**Touch:** Out of scope for static hosting. Defer until there's volume to justify SES/Mailgun setup.

---

## Phase 4 — Polish + maintenance

### 4.1 — README expansion  *(~30 min)*

Document:
- Search/filter/keyboard UI
- iCal subscription URL
- RSS URL
- Embed widget snippet
- Issue templates
- Contributor flow (PR-based or issue-based)

### 4.2 — CHANGELOG.md  *(~15 min, ongoing)*

Track major content drops + UX changes per deploy.

### 4.3 — `tests/` — minimal regression check  *(~1 h)*

- `tests/test_build_data.py` — assert event count >= last known count, all entries have month/date/year, all URLs in blurbs are reachable (`HEAD` request, allow 200/301/302).
- GitHub Action: run on PR.

### 4.4 — Print stylesheet  *(~30 min)*

`@media print` — hide chrome; print one month per page; readable typography.

---

## Sequencing recommendation

If only 2 hours: **1.1 (search) + 1.2 (permalinks) + 2.6 (Too Close URL)**.

If 1 day: Phase 1 entirely + 2.1 (verified patents) + 3.1 (iCal).

If 3 days: All Phases 1-3 except 3.4/3.5 (per-date OG) and 3.6 (email digest).

Each phase commits separately; each item is self-contained. A new contributor can pick any item from this list and ship it without coordinating with anything else.

---

## Tracked debt (from earlier work)

These are already captured in `TODO.md` but worth re-stating here:

- 24+ unlinked books (Mizuno 1998 paperback, Mallove pre-1991 articles, etc.)
- Cold Fusion magazine back-issue archive integration
- Fusion Facts magazine back-issue integration
- Per-author bio cards (subset of 1.7)
- Multilingual (Italian, Japanese, Finnish, French) — defer until search/filter exist

---

## Out-of-scope (explicitly deferred)

- User accounts / favorites / annotations — static-host friendly to stay free
- Real-time collaboration features
- Mobile native app — browser is sufficient
- AI-generated blurb expansion — quality risk too high; human-authored only
- Pulling adjacent free-energy content (Tesla/Schauberger/Russell/Moray etc.) — separate project ("Free Energy Calendar") if ever built
