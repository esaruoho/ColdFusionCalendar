# Cold Fusion Calendar — TODO

Granular content & data-quality backlog. Strategic outlook is in `PLAN.md`.

---

## Patents

### Live in calendar (12)

| Patent | Inventor / Assignee | Year |
|---|---|---|
| US 4,943,355 | Pons + Fleischmann / U of Utah | 1990 |
| WO 1990/013124 | Belton / BHP Australia | 1990 |
| EP 0477018 A1 | Ikegami / Technova Japan | 1991 |
| US 5,318,675 | Patterson / CETI | 1994 |
| US 5,372,688 | Patterson / CETI | 1994 |
| US 5,494,559 | Patterson / CETI | 1996 |
| IT/RM2008A000352 / WO 2009/125444 | Rossi / Leonardo Corp | 2008 |
| US 8,419,919 | Hagelstein / MIT | 2013 |
| US 8,485,791 | Rossi / Leonardo Corp | 2013 |
| US 8,728,235 | Storms | 2014 |
| US 9,115,913 | Godes / Brillouin Energy | 2015 |

### To research and add

- **Mitchell Swartz / JET Energy** NANOR-series patents — search "Swartz JET Energy NANOR" on patents.google.com
- **Yasuhiro Iwamura / Mitsubishi Heavy Industries** — JP + US transmutation patents (deuterium gas permeation through nano-multi-layer thin films)
- **Mizuno** R20 / nano-imprint patents (post-2018)
- **Clean Planet / Tohoku University** LENR commercialisation patents
- **Randell Mills / BlackLight Power** hydrino patents — adjacent / controversial; decide scope before adding

### Process for each
1. Search patents.google.com for inventor + "cold fusion" / "deuterium palladium" / "LENR"
2. Confirm filing/grant dates and inventor identity
3. Add to `datasets/additions.json` with `taxonomy: "Patent"`
4. Run `./deploy.sh`

---

## Books / publications still unlinked

- Fusion Facts magazine (1989+) — back-issue archive integration
- Cold Fusion magazine (1993+, Wayne Green / Mallove) — back-issue archive
- Per-issue Infinite Energy magazine entries — currently only 1995 launch is in calendar; 25 volumes in `~/work/merlib-dump/Infinite Energy Magazines/`

---

## Post-2013 events — blocked on verified dates

These have local-archive references but no precise dates. Paste in dated sources and they go in:

- **Carl Page / Anthropocene Institute** funding rounds for LENR research (~2018–2019)
- **Japan MEXT NEDO MHE program** kickoff (~2015)
- **NASA Bushnell** "LENR is real" public statements (multiple, Glenn / Langley)

---

## ICCF presentation highlights

Each ICCF currently has one entry on its start date. Notable in-conference moments deserve their own dated sub-events. Material in CFN podcast notes:

- Iwamura's spectacular transmutation results — within ICCF-9 week (May 19-24, 2002)
- Cravens / Letts laser stimulation — within ICCF-10 week (Aug 24-29, 2003)
- Toyoda Gold Medal awards at multiple ICCFs
- Mosier-Boss CR-39 papers at multiple ICCFs

Adds ~15 entries when fully mined.

---

## Data quality

- **URL rot test** — `tests/test_urls.py` HEAD-checking all 163 URLs; only podcast MP3s + 2 lenr-canr URLs verified so far. ~140 IMDb/Amazon/archive.org/sciencedirect/etc. URLs untested.
- **Quote attribution** — 173 aphorisms in `quotes.json` have no `source` field. Some have trailing "—Author" patterns parseable.
- **Real-device mobile testing** — bottom-sheet implemented but only browser-resize tested.

---

## Notes

- For book/article links prefer in this order: DOI → publisher → archive.org → Google Books
- For events without dated sources: do not guess. Skip until verified.
- Free-energy / over-unity / Tesla / Schauberger / Russell / Moray / etc. are **out of scope** — they belong in a hypothetical separate "Free Energy Calendar" project, not this one.
