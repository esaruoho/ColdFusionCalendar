# Cold Fusion Calendar — TODO

## Patents

### Live in calendar (12)

| Patent | Inventor / Assignee | URL |
|---|---|---|
| US 4,943,355 (1990) | Pons + Fleischmann / U of Utah | patents.google.com/patent/US4943355A |
| WO 1990/013124 (1990) | Belton / BHP Australia | patents.google.com/patent/WO1990013124A1 |
| EP 0477018 A1 (1991) | Ikegami / Technova Japan | patents.google.com/patent/EP0477018A1 |
| US 5,318,675 (1994) | Patterson / CETI | patents.google.com/patent/US5318675A |
| US 5,372,688 (1994) | Patterson / CETI | patents.google.com/patent/US5372688A |
| US 5,494,559 (1996) | Patterson / CETI | patents.google.com/patent/US5494559A |
| IT/RM2008A000352 / WO 2009/125444 (2008) | Rossi / Leonardo Corp | patents.google.com/patent/WO2009125444A1 |
| US 8,419,919 (2013) | Hagelstein / MIT | patents.google.com/patent/US8419919 |
| US 8,485,791 (2013) | Rossi / Leonardo Corp | patents.google.com/patent/US8485791B2 |
| US 8,728,235 (2014) | Storms | patents.google.com/patent/US8728235 |
| US 9,115,913 (2015) | Godes / Brillouin Energy | patents.google.com/patent/US9115913B1 |

### Still to research

- Mitchell Swartz / JET Energy NANOR patents — search "Swartz JET Energy NANOR"
- Yasuhiro Iwamura / Mitsubishi Heavy Industries — JP + US transmutation patents
- Randell Mills / BlackLight Power hydrino patents — adjacent / controversial; decide whether in scope
- Mizuno R20 / nano-imprint patents (post-2018)
- Clean Planet / Tohoku University LENR patents

## Books still unlinked

- Fox / Fusion Facts magazine (1989+) back-issues archive
- Cold Fusion magazine (1993+, Wayne Green / Mallove) back-issues
- Per-issue Infinite Energy magazine entries (currently only the 1995 launch)

## Recent post-2013 events to research and add

These have local-archive references but no precise dates — supply verified dates and they go in:

- **Carl Page / Anthropocene Institute** funding rounds for LENR research (~2018–2019)
- **Japan MEXT NEDO MHE program** kickoff (~2015)
- **NASA Bushnell** "LENR is real" public statements (Glenn / Langley)
- ICCF presentation highlights as standalone sub-events (Iwamura at ICCF-9, Cravens/Letts laser at ICCF-10, etc.) — currently only conference start dates are calendar entries

## Data quality

- Verify all ~160 URLs in blurbs with `tests/test_urls.py` — only 2 lenr-canr 404s + 18 podcast MP3s have been spot-checked. Other IMDb / Amazon / archive.org / sciencedirect URLs may have rotted.
- Aphorism quotes need attribution — 173 quotes in the rotator have no `source` field. Some are clearly attributed in the original ("--Dr. McKubre"), others bare. Consider parsing trailing "—Author" patterns.
- Mobile testing on real iOS / Android — bottom-sheet was implemented but only browser-resize tested.

## Process

1. Search https://patents.google.com for inventor + "cold fusion" / "deuterium palladium" / "LENR"
2. Confirm filing/grant dates and inventor identity
3. Add to `datasets/additions.json` with `taxonomy: "Patent"`
4. Run `./deploy.sh`

For book/article links: prefer in this order — DOI → publisher → archive.org → Google Books.
