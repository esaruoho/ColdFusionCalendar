# Cold Fusion Calendar — TODO

## Patents to add (verify each before linking)

The merlib-dump archive at `~/work/merlib-dump/sources/patent/` (1042 PDFs) contains free-energy-adjacent patents but only a few cold-fusion-specific ones. Below are cold-fusion patents that should be added as calendar entries — each must be verified on patents.google.com before adding.

### Verified, ready to add

| Patent | Inventor / Assignee | Filed | Issued | URL |
|---|---|---|---|---|
| **US 4,943,355** | Pons + Fleischmann / U of Utah Research Foundation | 1989-03-13 | 1990-07-24 | https://patents.google.com/patent/US4943355A/en |
| **EP 0477018 A1** | Ikegami / Technova Inc. (Tokyo) — *Apparatus and method for utilizing heat generated owing to Pons-Fleischmann effect* | 1991-09-19 | — | https://patents.google.com/patent/EP0477018A1/en |
| **WO 1990/013124 A1** | Belton / Broken Hill Proprietary Co. (BHP, Australia) — *Cold Nuclear Fusion Method and Apparatus* — gas-phase D loader | 1990-04-20 | — | https://patents.google.com/patent/WO1990013124A1/en |
| **WO 1990/010935** | Pons et al. — referenced in Ikegami EP prior art | 1990 | — | — |

Source: `~/work/merlib-dump/articles/cold-fusion-patents-kron-russell-analysis.md`

### Probably exist — need lookup before adding

| Likely patentee | Approx. filing | Note |
|---|---|---|
| James Patterson / CETI | US 5,318,675 (Jun 1994), US 5,372,688 (Dec 1994), US 5,494,559 (Feb 1996) | Patterson Power Cell |
| Mitchell Swartz / JET Energy | US 8,303,011 ?, NANOR cell patents | Verify via patents.google.com search "Swartz JET Energy NANOR" |
| Peter Hagelstein / MIT | Theoretical-method patents | Verify before linking |
| Andrea Rossi / Leonardo Corp | US 8,485,791 (granted 2013) | Calendar already has 2008 Italian filing — could add 2013 US grant as separate entry |
| Robert Godes / Brillouin Energy | US 9,115,913 etc. | Multiple |
| Edmund Storms | US 8,728,235 (2014) | Hydroton-related |
| Yasuhiro Iwamura / Mitsubishi Heavy Industries | JP + US transmutation patents | |
| Randell Mills / BlackLight Power | Many hydrino patents | Adjacent / controversial |

### Process
1. Search https://patents.google.com for inventor + "cold fusion" / "deuterium palladium" / "LENR"
2. Confirm filing/grant dates and inventor identity
3. Add to `datasets/additions.json` with `taxonomy: "Patent"`
4. Run `./deploy.sh`

## Books still unlinked

Run a more aggressive `archive.org` and `lenr-canr.org/wordpress` search for these:

- Kozima 2006 *The Science of the Cold Fusion Phenomenon*
- Chubb 2008 *Cold Fusion: Clean Energy for the Future*
- Biberian 2012 *All About Fusion / Cold Fusion / ITER / Alchemy / Biological Transmutations*
- Manning & Garbon 2009 *Breakthrough Power*
- Mallove 1999 *MIT and Cold Fusion: A Special Report*
- Swartz 1992 MIT re-analysis paper
- Fox / Fusion Facts magazine (1989+) — back issues archive
- Cold Fusion magazine (1993+, Wayne Green / Mallove) — back issues
- *Too Close to the Sun* (1994 documentary) — find video URL

## Recent post-2013 events to research and add (with dates + sources)

- **Carl Page / Anthropocene Institute** funding rounds for LENR research (~2018–2019)
- **Japan MEXT NEDO MHE program** (2015–2018, Tohoku, ~$3.5M follow-on)
- **Brillouin Energy 2X thermal gain** announcement (referenced in CFN podcast #20, Jan 15 2019 — could surface as standalone calendar entry)
- **Iwamura / Clean Planet** Tohoku University announcements (CFN podcast #21, Feb 19 2019)
- **NASA Bushnell** statements on LENR (Glenn / Langley, multiple years)
- Other ICCF-19 through ICCF-26 notable presentations beyond conference start dates

## Looser LENR-CANR matching pass

Currently 17 entries cross-referenced at 70%+ title overlap. A 60% pass with stricter author check could surface 5–10 more from the Key Experiment / Publication categories. False-positive risk requires manual review.

## Data quality

- Standardize taxonomy (currently 24 categories, several with single-instance noise: "Stupid" → "Reaction" already done; "Utah" → "Federal", "F&P" → "Science", "DoE" → "Federal", "Navy" → "Federal" still pending)
- Verify all blurbs for run-on typos like the previously-fixed "inititating", "devleoped", "palldium" pattern
- Standardize country naming ("US" vs "USA" vs "United States" — currently US dominates)
