# The Cold Fusion Calendar — Plan

Strategic state of the project. For granular content gaps see `TODO.md`. For history see `CHANGELOG.md`.

---

## Status snapshot

- **Live**: https://www.lackluster.org/cf/
- **293 events** · **163 URLs across 126 entries** · **27 ICCFs** · **12 patents** · **26 podcasts** · **15 taxonomy categories**
- **Tests passing**, all subscribe formats live (iCal, RSS, embed, OG-per-date)

## What's shipped

### Phase 1 — UX (DONE)

Search box · permalink URLs (`#YYYY-M-D`, `#person/<slug>`, `#year-view`) · filter chips (Type / Origin) · keyboard nav (←→↑↓ T Y / Esc) · year-grid heatmap view · mobile bottom-sheet panel · person index pages with surname disambiguation.

### Phase 2 — Content (mostly done)

| Item | Status |
|---|---|
| 2.1 Verify 7 patents | ✅ 12 patents total now |
| 2.2 Post-2013 events | ⏸️ Blocked on verified dates |
| 2.3 Looser LENR-CANR pass at 60% | ✅ No new valid matches |
| 2.4 Cross-link podcasts to events | ✅ 29 cross-refs |
| 2.5 ICCF presentation highlights | ⬜ Open |
| 2.6 *Too Close to the Sun* URL | ✅ |
| 2.7 Taxonomy normalization | ✅ 24 → 15 categories |
| 2.8 Country normalization | ✅ |

### Phase 3 — Distribution (DONE)

iCal feed (`/calendar.ics`) · RSS feed (`/feed.xml`) · embed widget (`/embed.html?day=today`) · per-date OG images at `/assets/og/MM-DD.png` · OG meta tags swapped on hash change.

### Phase 4 — Polish (DONE)

README expanded · CHANGELOG.md tracking · `tests/test_build_data.py` regression checks · `@media print` stylesheet.

## What's left (open, ordered by impact)

### Content (unblocked, can do now)

1. **More patents** *(~1.5h, Google Patents lookups)*
   - Mitchell Swartz / JET Energy NANOR series
   - Yasuhiro Iwamura / Mitsubishi Heavy Industries (JP + US transmutation)
   - Randell Mills / BlackLight Power (decide scope first — adjacent, controversial)
   - Mizuno R20 / nano-imprint (post-2018)
   - Clean Planet / Tohoku University

2. **2.5 ICCF presentation highlights** *(~1h)*
   - Each ICCF is one entry; notable in-conference moments deserve their own dated sub-events. Source material in CFN podcast notes (Iwamura at ICCF-9, Cravens/Letts laser at ICCF-10, etc.). Adds ~15 entries.

3. **Magazine back-issues** *(open-ended)*
   - Fusion Facts (1989+) per-issue
   - Cold Fusion magazine (1993+) per-issue
   - Infinite Energy per-issue (currently only 1995 launch is in)
   - Source: `~/work/merlib-dump/Infinite Energy Magazines/Vol. 1..Vol. 25/`

### Data quality (incremental)

4. **`tests/test_urls.py`** *(~30 min)*
   - HEAD-check every URL in blurbs; warn on 4xx/timeout. Currently only podcast MP3s + 2 lenr-canr URLs spot-checked. ~140 IMDb/Amazon/archive.org/sciencedirect/etc. URLs untested.

5. **Quote attribution** *(~1h)*
   - 173 aphorisms in quotes.json have no `source` field. Some have trailing "—Author" patterns to parse out.

6. **Real-device mobile testing** *(~30 min, needs phone)*
   - Bottom-sheet only browser-resize tested.

### Content (blocked on verified dates from primary sources)

- Carl Page / Anthropocene Institute funding rounds (~2018–2019)
- Japan MEXT NEDO MHE program kickoff (~2015)
- NASA Bushnell "LENR is real" public statements
- Other post-2013 LENR events with no precise dates in local archives

### Out of scope (deferred)

- Email digest (3.6) — no audience to justify SES/Mailgun yet
- User accounts / favorites / annotations — static-host friendly
- Mobile native app — browser is sufficient
- AI-generated blurb expansion — human-authored only
- Free-energy adjacent content (Tesla / Schauberger / Russell / Moray etc.) — separate "Free Energy Calendar" project if ever built

## Sequencing recommendation

If 1 hour: **2.5 ICCF presentation highlights**.

If 2-3 hours: **More patents** (1.5h) + **`tests/test_urls.py`** (30 min) — biggest content add + catches future URL rot automatically.

If 1 day: All of the above + a magazine back-issue pass (whichever you have most local material for).

If you have verified dates for blocked items: paste them in and we add the events directly.
