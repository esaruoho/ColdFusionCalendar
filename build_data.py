#!/usr/bin/env python3
"""Build data.json from the 2019Spreadsheet.xlsx, cleaning typos and merging."""
import json, re, zipfile, xml.etree.ElementTree as ET, sys, os

XLSX = '/Users/esaruoho/Library/Containers/com.apple.mail/Data/Library/Mail Downloads/85A5DB96-E34C-41BA-ADEB-14815E84B09B/2019Spreadsheet.xlsx'
OUT = '/Users/esaruoho/work/CF_Calendar/datasets/40d7f378-7b62-44f6-8196-5bae64a95169/data.json'
ORIGINAL = '/Users/esaruoho/work/CF_Calendar/datasets/40d7f378-7b62-44f6-8196-5bae64a95169/data.json.original'
ADDITIONS = '/Users/esaruoho/work/CF_Calendar/datasets/additions.json'
QUOTES_OUT = '/Users/esaruoho/work/CF_Calendar/datasets/40d7f378-7b62-44f6-8196-5bae64a95169/quotes.json'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

# Targeted blurb fixes for the worst run-together typos.
BLURB_FIXES = {
    'P.K. Iyengarand Mahadeva Srinivasan et al. Measureanomalousneutronburstsmeasuredfromelectrolytic cells cold fusion cells at BARC in Mumbai, India. 1989':
        'P.K. Iyengar and Mahadeva Srinivasan et al. measure anomalous neutron bursts from electrolytic cold fusion cells at BARC in Mumbai, India. 1989',
    'FrancescoPiantelli, Sergio Focardi, V.Gabbani, V. Montalbano, and S. Veronisi create excess energy of over 900 MegaJoules using nickel and light-hydrogen. *1994':
        'Francesco Piantelli, Sergio Focardi, V. Gabbani, V. Montalbano, and S. Veronisi create excess energy of over 900 MegaJoules using nickel and light-hydrogen. *1994',
}
# Generic typo: missing space between "Francesco" and "Piantelli" appears in multiple blurbs
def fix_runtogether_names(s):
    if not s: return s
    s = re.sub(r'\bFrancescoPiantelli\b', 'Francesco Piantelli', s)
    # Happy Birthday entries: end with "!" not "." for consistent emphasis
    s = re.sub(r'^(Happy Birthday[^!.]*)\.', r'\1!', s)
    return s

def col_letter(ref): return ''.join(c for c in ref if c.isalpha())

TYPO_FIXES = {
    'inititating': 'initiating',
    'devleoped': 'developed',
    'devleop': 'develop',
    'palldium': 'palladium',
    'Pasdium': 'Palladium',
    'prsents': 'presents',
    'col fusion': 'cold fusion',
    'Industy': 'Industry',
    'initiateve': 'initiative',
    'Daejon': 'Daejeon',
    'Annlen': 'Annalen',
    'Intertia': 'Inertia',
    'Postassium': 'Potassium',
    'Comanies': 'Companies',
    'Ghandi': 'Gandhi',
    'Annlen': 'Annalen',
    'Intertia': 'Inertia',
    'Cincinnatti': 'Cincinnati',
    'besteam': 'be steam',
    'heatingand': 'heating and',
    'cleanwater': 'clean water',
    'bothhot': 'both hot',
    'Sytems': 'Systems',
    'succesful': 'successful',
    'exces': 'excess',
    'mange': 'manage',
    'Geoarge': 'George',
    'tevolutionized': 'revolutionized',
    'Devel': 'Development',
    'Sciencetific': 'Scientific',
    'Vittori': 'Vittorio',
    'Fleischmann-Ponds': 'Fleischmann-Pons',
}

def apply_typos(s):
    for bad, good in TYPO_FIXES.items():
        s = re.sub(r'\b' + re.escape(bad) + r'\b', good, s)
    return s

# Canonical ordering: always "Fleischmann & Pons" / "Fleischmann-Pons", never the reverse.
def normalize_fp_order(s):
    if not s: return s
    s = re.sub(r'\bPons\s+&\s+Fleischmann\b', 'Fleischmann & Pons', s)
    s = re.sub(r'\bPons\s+and\s+Fleischmann\b', 'Fleischmann and Pons', s)
    s = re.sub(r'\bPons-Fleischmann\b', 'Fleischmann-Pons', s)
    s = re.sub(r'\bStanley\s+Pons\s+and\s+Martin\s+Fleischmann\b',
               'Martin Fleischmann and Stanley Pons', s)
    return s

def clean_blurb(s):
    if not s: return s
    s = s.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
    # Insert space after comma when followed by a letter (not digit — preserves "4,943,355")
    s = re.sub(r',(?=[A-Za-z])', ', ', s)
    s = re.sub(r' {2,}', ' ', s).strip()
    s = apply_typos(s)
    s = fix_runtogether_names(s)
    s = normalize_fp_order(s)
    # Strip redundant trailing year (and "(YYYY)", "*YYYY", "Mon DD, YYYY" tails) —
    # the year is already in the year field and shown in the UI date chip.
    # Negative lookbehind avoids matching digits inside URLs / longer numbers.
    for _ in range(4):
        new = re.sub(
            r'(?<![0-9A-Za-z/])\s*\.?\s*\(?(?:[A-Z][a-z]+\s+)?(?:\d{1,2},\s*)?\*?(?:1[789]|20)\d{2}\)?\s*\.?\s*$',
            '',
            s,
        )
        if new == s: break
        s = new
    s = s.rstrip(' .')
    # Don't append a trailing period to entries ending in a URL or punctuation
    if s and not s.endswith(('!', '?', '…', '"', '”', ')', '/')) and not re.search(r'https?://\S+$', s):
        s += '.'
    if s in BLURB_FIXES: return BLURB_FIXES[s]
    return s

NAME_FIXES = {
    'Sttorms': 'Storms',
    'Zowadny': 'Zawodny',
    'Czech': 'Czechoslovakia',
    'Appley': 'Appleby',
    'Cincinnatti Group': 'Cincinnati Group',
    'NCUAT': 'NUCAT',
}


TAXONOMY_FIXES = {
    'Utah': 'Federal',
    'F&P': 'Science',
    'DoE': 'Federal',
    'Navy': 'Federal',
    'NASA': 'Federal',
    'TV': 'Publication',
    'History': 'Deep History',
    'Activist': 'Movement',
    'Personal': 'Recognition',
    'Award': 'Recognition',
    'Report': 'Publication',
    'Book': 'Publication',
    'Stupid': 'Reaction',
    'Research': 'Science',
}
def clean_taxonomy(s):
    if not s: return 'Science'
    s = s.strip()
    return TAXONOMY_FIXES.get(s, s)

COUNTRY_FIXES = {
    'US': 'USA',
    'U.S.': 'USA',
    'U.S.A.': 'USA',
    'United States': 'USA',
    'United States of America': 'USA',
    'America': 'USA',
    'Korea': 'South Korea',
    'United Kingdom': 'UK',
    'Great Britain': 'UK',
    'England': 'UK',
}
def clean_country(s):
    if not s: return 'Global'
    s = s.strip()
    return COUNTRY_FIXES.get(s, s)
def clean_name(s):
    if not s: return s
    s = s.strip()
    return NAME_FIXES.get(s, s)

def parse_int(s):
    if s is None: return None
    s = str(s).strip()
    if not s: return None
    # year may be "1989", "*1989", "450 BCE"
    m = re.match(r'^\*?(-?\d+)(?:\s*BCE)?$', s, re.I)
    if m: return int(m.group(1))
    m = re.match(r'^(\d+)\s*BCE$', s, re.I)
    if m: return -int(m.group(1))
    try: return int(float(s))
    except ValueError: return None

with zipfile.ZipFile(XLSX) as z:
    ss_xml = ET.fromstring(z.read('xl/sharedStrings.xml'))
    shared = [''.join((t.text or '') for t in si.findall('.//s:t', NS))
              for si in ss_xml.findall('s:si', NS)]
    sh = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    rows = sh.findall('.//s:row', NS)

records = []
quotes = []
next_id = 1
skipped = 0
for row in rows:
    rn = int(row.attrib.get('r'))
    if rn <= 10: continue  # header / preamble
    rec = {}
    for c in row.findall('s:c', NS):
        col = col_letter(c.attrib['r'])
        t = c.attrib.get('t')
        v = c.find('s:v', NS)
        inline = c.find('s:is', NS)
        val = ''
        if t == 's' and v is not None:
            val = shared[int(v.text)]
        elif t == 'inlineStr' and inline is not None:
            val = ''.join((tt.text or '') for tt in inline.findall('.//s:t', NS))
        elif v is not None:
            val = v.text
        rec[col] = val

    month = parse_int(rec.get('C'))
    date = parse_int(rec.get('D'))
    year = parse_int(rec.get('E'))
    name = (rec.get('G') or '').strip()
    taxonomy = (rec.get('H') or '').strip()
    country = (rec.get('I') or '').strip()
    blurb = clean_blurb(rec.get('K') or '')

    if not blurb: continue
    if month is None or date is None or year is None or not (1 <= (month or 0) <= 12) or not (1 <= (date or 0) <= 31):
        # Aphorism / undated tip — keep for the quote-of-the-day rotator
        # Skip date-locked content (birthdays, dated events, BCE/CE history) that shouldn't rotate as undated quotes
        skip_patterns = ['Happy Birthday', 'Today closed', 'Today is']
        if any(p in blurb for p in skip_patterns) or re.search(r'\bBCE\b|\bCE\b\.|~\d{2,4}', blurb):
            skipped += 1
            continue
        # Skip narrative-style "X did Y" historical sentences without attribution / quote marks
        if not re.search(r'[“"”«»]|—\s*[A-Z]', blurb) and re.search(r'\b(reports?|publishes?|announces?|releases?|founded|launches?|presents?|files?|begins?)\b', blurb, re.I):
            skipped += 1
            continue
        quotes.append(blurb)
        skipped += 1
        continue

    records.append({
        'id': next_id,
        'month': month,
        'date': date,
        'year': year,
        'name': name or 'Unknown',
        'taxonomy': clean_taxonomy(taxonomy) if taxonomy else 'Science',
        'country': clean_country(country) if country else 'Global',
        'blurb': blurb,
    })
    next_id += 1

# Merge with original (website-curated) data so we don't lose curator additions.
def norm(s):
    return re.sub(r'[^a-z0-9]', '', (s or '').lower())

def dedup_key(r):
    # Normalize blurb through clean_blurb first so typo-fixes converge
    return (norm(clean_name(r.get('name',''))), norm(clean_blurb(r.get('blurb','')))[:50])

with open(ORIGINAL) as f:
    original = json.load(f)

# Drop curator entries we have authoritative replacements for (wrong dates / mislabeled)
DROP_BLURB_PREFIXES = [
    'First International Conference on Cold Fusion (ICCF-1)',  # year typo: 1991 -> 1990
    'At ICCF-3, Hideo Ikegami',  # year typo: 1993 -> 1992
    'The first Minoru Toyoda Gold Medal is awarded to Martin Fleischmann at ICCF-10',  # was ICCF-15, not ICCF-10
    'ICCF-17 Conference wraps up in Daejon',  # start date should be Aug 12 not Aug 17
    'The 18th International Conference on Cold Fusion begins in Missouri',  # superseded by canonical ICCF-18 entry below
]
# Exact-blurb drops (keep the more detailed dup of the same event)
DROP_BLURB_EXACT = {
    'Andrea Rossi describes steam generator to NASA. 2011',
}
# Load auto-detected duplicates (shorter blurb where 85%+ of words appear in longer same-date entry)
_drops_path = '/Users/esaruoho/work/CF_Calendar/datasets/drops.txt'
if os.path.exists(_drops_path):
    with open(_drops_path) as _f:
        for _line in _f:
            _line = _line.rstrip('\n')
            if _line: DROP_BLURB_EXACT.add(_line)
def is_dropped(r):
    raw = r.get('blurb', '')
    cleaned = clean_blurb(raw)
    if raw in DROP_BLURB_EXACT or cleaned in DROP_BLURB_EXACT: return True
    return any(raw.startswith(p) or cleaned.startswith(p) for p in DROP_BLURB_PREFIXES)
original = [r for r in original if not is_dropped(r)]
records = [r for r in records if not is_dropped(r)]

merged = {}
# Original first (curator-added entries take precedence on collision)
for r in original:
    merged[dedup_key(r)] = {
        'month': r['month'], 'date': r['date'], 'year': r['year'],
        'name': clean_name(r.get('name', 'Unknown')), 'taxonomy': clean_taxonomy(r.get('taxonomy', 'Science')),
        'country': clean_country(r.get('country', 'Global')), 'blurb': clean_blurb(r.get('blurb', '')),
    }
# Add xlsx records not already present
for r in records:
    k = dedup_key(r)
    if k not in merged:
        merged[k] = {
            'month': r['month'], 'date': r['date'], 'year': r['year'],
            'name': clean_name(r['name']), 'taxonomy': clean_taxonomy(r['taxonomy']),
            'country': clean_country(r['country']), 'blurb': r['blurb'],
        }

# Hand-curated additions (ICCF conferences, modern milestones)
import os

# Auto-generated name overrides for displayed event titles.
# Keyed by (year, month, day, original_name) → new_display_name.
NAME_OVERRIDES = {
    (150, 9, 10, "Hero"): "Hero of Alexandria Invents the Aeolipile",
    (1926, 9, 17, "Paneth, Peters"): "Paneth & Peters Report Possible Nuclear Fusion",
    (1926, 10, 13, "Paneth, Peters"): "Paneth & Peters Report Hydrogen-to-Helium Transmutation",
    (1927, 3, 29, "Fleischmann"): "Happy Birthday, Martin Fleischmann!",
    (1938, 9, 7, "Bethe"): "Hans Bethe: Energy Production in Stars",
    (1942, 12, 2, "Fermi"): "First Nuclear Chain Reaction at Chicago",
    (1943, 2, 9, "Pons, Stanley"): "Happy Birthday, Stanley Pons!",
    (1956, 3, 8, "Hubbert, M King"): "Hubbert: Nuclear Energy and Fossil Fuels",
    (1987, 7, 28, "Jones, Rafelski"): "Rafelski & Jones: Cold Nuclear Fusion in Sci. American",
    (1989, 2, 23, "Fleischmann, Pons, Jones"): "Fleischmann & Pons Visit Steve Jones at BYU",
    (1989, 3, 8, "Rossi, Hugo"): "Hugo Rossi Coins 'F-Day' Term",
    (1989, 3, 11, "F&P"): "Fleischmann & Pons Submit Research to JEC",
    (1989, 3, 23, "F&P"): "Fleischmann & Pons Announce Cold Fusion at Utah",
    (1989, 4, 10, "F&P"): "Fleischmann, Pons & Hawkins Publish in JEC",
    (1989, 5, 9, "F&P"): "Fleischmann & Pons at Electrochemical Society LA",
    (1989, 5, 10, "F&P"): "Fleischmann, Pons & Hawkins Publish JEC Errata",
    (1990, 7, 25, "F&P"): "Fleischmann & Pons: Pd-D2O Calorimetry",
    (1990, 12, 30, "F&P"): "Fleischmann & Pons Leave Utah for Nice, France",
    (1991, 3, 17, "Miles, Bush"): "Miles & Bush: Helium-4 as Cold Fusion By-Product",
    (1990, 3, 28, "ICCF-1"): "ICCF-1: First Cold Fusion Conference",
    (1993, 3, 29, "Clarke, Arthur"): "Arthur C. Clarke: Coming Age of Hydrogen Power",
    (1989, 3, 24, "SRI"): "SRI International Begins Cold Fusion Experiments",
    (1989, 3, 25, "Bangerter, Norm"): "Utah Governor Convenes Funding Session",
    (1989, 3, 25, "Navy"): "Navy China Lake Cold Fusion Program Begins",
    (1989, 3, 30, "Jones"): "Steve Jones Announces BYU Cold Fusion Work",
    (1989, 3, 31, "Csikai, Szaricskai"): "Hungary Reports Neutron Detection",
    (1989, 3, 31, "Fleischmann, Rubbia"): "Rubbia Hosts Fleischmann at CERN",
    (1989, 4, 2, "Iyengar, BARC"): "BARC India Begins Cold Fusion Experiments",
    (1989, 4, 4, "Oyama"): "Oyama Reports Excess Heat at Tokyo University",
    (1989, 4, 6, "Bockris, John"): "Bockris Finds Tritium in Electrolytic Cells",
    (1989, 4, 7, "Utah"): "Utah Cold Fusion Research Legislation",
    (1989, 4, 8, "Utah"): "Utah Approves $5M for Cold Fusion Research",
    (1989, 4, 10, "Texas A&M"): "Texas A&M Reports 60-80% Excess Heat",
    (1989, 4, 12, "Kuzmin, Runar"): "Tass: Moscow University Detects Neutrons",
    (1989, 4, 12, "Pons, Stanley"): "Pons at ACS President's Event",
    (1989, 4, 14, "Seaborg, Bush"): "Seaborg Tells Bush Utah Claims 'Not Right'",
    (1989, 4, 17, "Pons, Stanley"): "Pons Announces 800-Hour Sustained Reaction",
    (1989, 4, 18, "Stanford"): "Stanford Reports Excess Heat",
    (1989, 4, 25, "Tata Institute"): "Tata Institute Reports Excess Heat from Titanium",
    (1989, 4, 26, "Pons, Stanley"): "Pons Briefs U.S. Congress on Cold Fusion",
    (1989, 4, 27, "Jones"): "Steve Jones Publishes Observation of Cold Nuclear Fusion",
    (1989, 4, 28, "MITI"): "Japan's MITI Begins Cold Fusion Studies",
    (1989, 5, 1, "APS"): "APS Meeting Denounces Cold Fusion",
    (1989, 5, 1, "Chubb, APS"): "Chubb Organizes First Cold Fusion APS Session",
    (1989, 5, 4, "Bockris"): "Bockris Confirms at Texas A&M",
    (1989, 5, 18, "BARC"): "Ten Teams Report FPE Replication",
    (1989, 6, 12, "Fox"): "First Issue of Fusion Facts Published",
    (1989, 6, 26, "MIT"): "MIT 'Wake for Cold Fusion' Party",
    (1989, 6, 26, "Storms, Talcott"): "Storms & Talcott Detect Tritium at LANL",
    (1989, 7, 13, "Jones"): "Cold Nuclear Fusion Paper by S.E. Jones et al",
    (1989, 7, 31, "Japan"): "Ten Teams Report Cold Fusion Success in Japan",
    (1989, 8, 16, "Piantelli"): "Piantelli Discovers Excess Heat in Ni-H System",
    (1989, 9, 1, "Miley, George"): "Fusion Technology Special Section on Cold Fusion",
    (1989, 10, 16, "Electrochemical Society"): "Electrochemical Society Hollywood Meeting",
    (1989, 10, 18, "NSF, EPRI"): "NSF & EPRI Confirm New Phenomenon",
    (1989, 12, 12, "Peat"): "F. David Peat: The Making of a Scientific Controversy",
    (1990, 3, 20, "Matsumoto"): "Matsumoto Reports Hokkaido Cold Fusion Results",
    (1990, 7, 26, "Oriani"): "Oriani: Calorimetric Excess Power Measurement",
    (1990, 7, 27, "Storms, Talcott"): "Storms & Talcott: Electrolytic Tritium Production",
    (1990, 8, 18, "Cornell"): "Cornell Assembles Cold Fusion Archives",
    (1990, 10, 6, "Fusion Facts"): "Fusion Facts: 112 Confirming Papers from 16 Countries",
    (1990, 10, 22, "BYU"): "BYU Cold Fusion Conference: Proof Below Critical Mass",
    (1991, 3, 3, "Takahashi, Akito"): "Takahashi Detects Lower-Energy Neutrons at Osaka",
    (1991, 4, 6, "Mizuno, Tadahiko"): "Mizuno Witnesses 'Heat After Death'",
    (1991, 4, 30, "Zhang Xinwie"): "Three Lab Explosions in China",
    (1991, 5, 22, "Mallove"): "Mallove Publishes 'Fire from Ice'",
    (1991, 6, 7, "Mallove"): "Mallove Resigns from MIT News Office",
    (1991, 6, 16, "Fusion Facts"): "Fusion Facts: 242 Positive Papers from 23 Countries",
    (1991, 6, 28, "Bush, Eagleton"): "Bush & Eagleton Report Record Excess Heat",
    (1991, 7, 2, "Miles, Bush"): "Miles & Bush Present Heat-Helium at ICCF-2",
    (1991, 11, 10, "Matsumoto"): "Matsumoto et al. Report Heavy Element Transmutation",
    (1991, 11, 11, "Schwinger"): "Schwinger: Pathological Skepticism Talk at MIT",
    (1991, 11, 17, "Yun"): "Yun et al. Report Heat Bursts in Seoul",
    (1992, 1, 5, "Piantelli, Francesco"): "Piantelli: Excess Heat from Ni-H Cell",
    (1992, 1, 27, "Takahashi, Akito"): "Massive Excess Heat at Osaka",
    (1992, 2, 12, "Mallove, Swartz, DoE"): "Mallove & Swartz Meet DoE Secretary Watkins",
    (1992, 3, 27, "Noninski"): "Noninski et al. Report Ni-H Excess Heat",
    (1992, 7, 8, "MITI"): "Japan's MITI Funds 4-Year Cold Fusion Program",
    (1992, 7, 27, "Storms"): "Storms Replicates Takahashi Excess Heat",
    (1992, 8, 7, "Swartz"): "Re-Analysis of MIT 1989 Cold Fusion Data",
    (1992, 9, 18, "MITI"): "MITI Announces New Hydrogen Energy Program",
    (1992, 9, 24, "McKubre"): "McKubre Presents SRI Cold Fusion Summary at MIT",
    (1992, 9, 28, "Karabut, Kucherov, Savvatimova"): "Glow Discharge Nuclear Product Ratio (Russia)",
    (1992, 10, 2, "Notoya"): "Notoya: Large Excess Heat at Hokkaido",
    (1993, 5, 5, "Storms"): "Storms Testifies Before U.S. Congress",
    (1993, 11, 30, "Will, Fritz"): "Reproducible Tritium in Pd Cathodes (NCFI)",
    (1994, 2, 7, "Piantelli, Focardi, Habel"): "Focardi, Habel & Piantelli: High-Temperature Anomalous Heat",
    (1994, 7, 1, "McKubre, Tanzella"): "McKubre & Tanzella: Isothermal Flow Calorimetry",
    (1994, 9, 14, "Piantelli, focardi, habel"): "Piantelli/Focardi/Habel: 900 MJ from Ni-H",
    (1994, 11, 23, "Reifenschweiler"): "Reifenschweiler: Reduced Tritium Radioactivity",
    (1994, 11, 24, "Reifenschweiler"): "Reifenschweiler: Reduced Radioactivity of Tritium",
    (1994, 12, 7, "Dash"): "John Dash: Surface Morphology & Excess Heat",
    (1994, 12, 13, "Patterson / CETI"): "Patterson / CETI: Electrolysis Patent",
    (1995, 1, 21, "MIT"): "Cold Fusion Day at MIT",
    (1995, 2, 14, "Mizuno, Tadahiko"): "Mizuno: Pd Analysis Shows Transmutations",
    (1995, 4, 20, "Biberian"): "Biberian: Excess Heat in AlLaO3:D",
    (1995, 6, 19, "Texas A&M"): "First LENR/Transmutation Conference at Texas A&M",
    (1995, 12, 6, "CETI"): "CETI Demonstrates Patterson Power Cell",
    (1996, 2, 16, "NASA"): "NASA Lewis: Replication of Excess Heat Effect",
    (1996, 2, 27, "Patterson / CETI"): "Patterson / CETI: Electrolytic Cell Patent",
    (1996, 3, 2, "China"): "China Reviews Normal Temp. Nuclear Fusion",
    (1996, 3, 26, "Oriani"): "Oriani: Excess Heat Using Mizuno Method",
    (1996, 9, 13, "Miley, Patterson"): "Miley & Patterson: Nuclear Transmutations",
    (1996, 11, 9, "Miley, Patterson"): "Miley & Patterson: Ni Thin-Film Transmutations",
    (1996, 11, 23, "Srinivasan"): "Srinivasan: Anomalous Pd Emissions",
    (1997, 4, 4, "The Saint"): "Movie 'The Saint' Released",
    (1997, 6, 11, "CETI"): "CETI on ABC Good Morning America & Nightline",
    (1997, 12, 4, "Mizuno, Tadahiko"): "Mizuno: 'Nuclear Transmutation' Book",
    (1998, 2, 15, "China"): "Third Normal Temp Nuclear Fusion Conference (China)",
    (1998, 4, 19, "Swartz"): "Swartz: Optimal Operating Point Characteristics",
    (1998, 4, 30, "Swartz"): "Swartz: Optimal Operating Point Characteristics",
    (1998, 5, 2, "Case, Leslie"): "Case Demonstrates D2 Gas-Loaded Cell",
    (1998, 6, 5, "Clarke, Arthur"): "Arthur C. Clarke Calls Cold Fusion Greatest Scandal",
    (1998, 11, 2, "Wired"): "Wired: 'Dirty Science: Strange Rebirth of Cold Fusion'",
    (1999, 1, 31, "Biberian"): "Biberian at 16th Science Frontiers Festival",
    (1999, 3, 1, "Mallove"): "Mallove: 'MIT and Cold Fusion: A Special Report'",
    (1999, 4, 1, "Fire From Water"): "'Cold Fusion: Fire From Water' Documentary",
    (2000, 5, 3, "Beaudette"): "Beaudette: 'Excess Heat' Book Released",
    (2002, 2, 17, "Godes, Robert"): "Brillouin: First Successful Reaction Control",
    (2002, 5, 21, "JCMNS"): "Journal of Condensed Matter Nuclear Science",
    (2002, 7, 15, "Iwamura, Mitsubishi"): "Iwamura/Mitsubishi: Pd-D2O Thin-Film Results",
    (2003, 8, 26, "Swartz, Dash"): "Swartz & Dash Demonstrate Cells at MIT",
    (2003, 8, 27, "Letts"): "Cravens & Letts: Laser Stimulation at ICCF-10",
    (2003, 11, 21, "ISCMNS"): "ISCMNS Founded",
    (2004, 10, 1, "Krivit"): "Krivit & Winocur: 'Rebirth of Cold Fusion'",
    (2004, 12, 17, "Rothwell"): "Rothwell: 'Cold Fusion and the Future' Released",
    (2004, 12, 28, "Piantelli"): "Piantelli's New Lab at Siena University",
    (2005, 5, 28, "LANR/CF"): "First LANR/CF Colloquium at MIT",
    (2005, 11, 29, "Allan, Sterling"): "Sterling Allan: New Energy Congress Founded",
    (2006, 10, 10, "Kozima"): "Kozima: 'Science of the Cold Fusion Phenomenon'",
    (2006, 12, 13, "DTRA"): "DTRA High Energy Workshop on LENR",
    (2007, 3, 31, "ACS"): "ACS Cold Fusion Sessions Resume",
    (2007, 6, 29, "DTRA"): "DTRA Supports LENR Research",
    (2008, 4, 9, "Rossi, Andrea"): "Rossi Files Italian Patent for Ni-H Process",
    (2008, 8, 5, "Chubb, APS"): "Chubb: 'Cold Fusion: Clean Energy for the Future'",
    (2008, 11, 20, "Martinez"): "James Martinez: Cold Fusion Radio Launch",
    (2009, 1, 6, "Brillouin Energy"): "Brillouin Energy Founded",
    (2009, 4, 19, "CBS 60"): "CBS 60 Minutes: 'More Than Junk Science'",
    (2009, 10, 8, "Toyoda Gold Medal"): "First Toyoda Gold Medal: Fleischmann at ICCF-15",
    (2009, 11, 19, "Rossi, Andrea"): "Rossi Demonstrates E-Cat in New Hampshire",
    (2010, 5, 13, "Cold Fusion Now"): "Ruby Carat Founds Cold Fusion Now",
    (2011, 1, 11, "Rossi, Andrea"): "Rossi Demonstrates Cold Fusion Steam Generator",
    (2011, 6, 11, "Swartz"): "Swartz LANR/CF Colloquium at MIT",
    (2011, 9, 23, "NASA"): "NASA LENR Workshop",
    (2011, 10, 3, "NUCAT"): "First Commercial LENR Course (NUCAT)",
    (2011, 10, 28, "Rossi, Andrea"): "EU Workshop on Emerging Energy Materials",
    (2011, 11, 11, "Violante"): "Violante on Toyota's Long Cold Fusion Support",
    (2012, 3, 21, "Miley, George"): "Miley: LENR Spacecraft Power Generator",
    (2012, 3, 22, "Celani, Srivastava"): "Celani & Srivastava on LENR at CERN",
    (2012, 10, 12, "Believers"): "'The Believers' Wins Best Documentary",
    (2012, 12, 3, "Biberian"): "Biberian: 'All About Fusion' Released",
    (2014, 5, 20, "Storms"): "Storms Granted US 8,728,235 Cold Fusion Patent",
    (2018, 1, 3, "CFN Podcast #001"): "CFN Podcast #001 — Dr. David J. Nagel: Intro to Condensed Matter Nuclear Science",
    (2018, 1, 10, "CFN Podcast #002"): "CFN Podcast #002 — Dr. Michael McKubre: SRI International's 30-Year LENR Program",
    (2018, 1, 20, "CFN Podcast #003"): "CFN Podcast #003 — Dr. Andrew Meulenberg: Deep Electron Orbits Theory",
    (2018, 2, 14, "CFN Podcast #004"): "CFN Podcast #004 — Dr. Jean-Paul Biberian: LENR Research in France",
    (2018, 3, 6, "CFN Podcast #005"): "CFN Podcast #005 — Alan Smith: LookingForHeat & Open Science Reactors",
    (2018, 3, 14, "CFN Podcast #006"): "CFN Podcast #006 — William Collis: ISCMNS",
    (2018, 3, 23, "CFN Podcast #007"): "CFN Podcast #007 — Dr. Mahadeva Srinivasan: BARC India & Transmutation",
    (2018, 4, 3, "CFN Podcast #008"): "CFN Podcast #008 — David J. French: LENR Patents & IP",
    (2018, 4, 13, "CFN Podcast #009"): "CFN Podcast #009 — Abd ul-Rahman Lomax: Rossi vs Industrial Heat",
    (2018, 4, 23, "CFN Podcast #010"): "CFN Podcast #010 — Mats Lewan: Andrea Rossi, E-Cat & New Energy",
    (2018, 5, 3, "CFN Podcast #011"): "CFN Podcast #011 — Dr. Vladimir Vysotskii: Biological Transmutations",
    (2018, 5, 13, "CFN Podcast #012"): "CFN Podcast #012 — Dr. Melvin Miles: The Heat-Helium Discovery",
    (2018, 7, 2, "CFN Podcast #013"): "CFN Podcast #013 — Dr. Michael McKubre: Fleischmann-Pons Heat — What We Know",
    (2018, 9, 3, "CFN Podcast #014"): "CFN Podcast #014 — Alan Goldwater: Open Science LENR Research",
    (2018, 9, 13, "CFN Podcast #015"): "CFN Podcast #015 — Dr. Dennis Cravens: Seven Watts Excess Heat & Laser Experiments",
    (2018, 9, 23, "CFN Podcast #016"): "CFN Podcast #016 — Dr. Pamela Mosier-Boss: CR-39 Nuclear Evidence from Navy SPAWAR",
    (2018, 10, 13, "CFN Podcast #017"): "CFN Podcast #017 — Dr. Francis Tanzella: 29 Years of LENR at SRI International",
    (2018, 10, 23, "CFN Podcast #018"): "CFN Podcast #018 — David Daggett: From Aerospace to LENR to Politics",
    (2019, 1, 13, "CFN Podcast #019"): "CFN Podcast #019 — Dr. Edmund Storms: Hydroton Model & 30 Years of LENR",
    (2019, 1, 15, "CFN Podcast #020"): "CFN Podcast #020 — Robert Godes: Brillouin Energy — 2X Thermal Gain",
    (2019, 2, 19, "CFN Podcast #021"): "CFN Podcast #021 — Dr. Yasuhiro Iwamura: Transmutation & Clean Planet",
    (2019, 3, 18, "CFN Podcast #022"): "CFN Podcast #022 — Dr. Stephen C. Bannister: Energy Economics & Industrial Revolutions",
    (2019, 4, 28, "CFN Podcast #023"): "CFN Podcast #023 — Dr. Dimiter Alexandrov: Helium Production in Transition Metals",
    (2019, 6, 5, "CFN Podcast #024"): "CFN Podcast #024 — Dr. Sveinn Olafsson: Ultra-Dense Hydrogen & Rydberg Matter",
    (2019, 7, 3, "CFN Podcast #025"): "CFN Podcast #025 — Sergei Tcvetkov: Titanium-Deuterium LENR Research in Russia",
    (2019, 9, 22, "CFN Podcast #026"): "CFN Podcast #026 — Frank Acland: E-Cat World & Following Andrea Rossi",
    # User-flagged batch — formatting + descriptive titles
    (1989, 3, 13, "Fleischmann & Pons / U of Utah"): "Fleischmann & Pons File US 4,943,355 Patent",
    (1989, 8, 5, "U of Utah"): "U of Utah Approves National Cold Fusion Institute",
    (1994, 3, 21, "Too Close to the Sun"): "Documentary: Too Close to the Sun",
    (1997, 4, 4, "The Saint"): "Movie: The Saint (Eugene Mallove as Technical Consultant)",
    (1994, 6, 7, "Patterson / CETI"): "Patent: US 5,318,675 — Patterson / CETI Electrolysis",
    (1998, 11, 20, "Heavy Watergate"): "Documentary: Heavy Watergate — The War Against Cold Fusion",
    (2003, 11, 21, "ISCMNS Founded"): "International Society of Condensed Matter Nuclear Science (ISCMNS) Founded",
    (2012, 10, 12, "Believers"): "Documentary: The Believers (Best Documentary, Chicago)",
    (2015, 8, 25, "Godes / Brillouin Energy"): "Patent: US 9,115,913 — Brillouin Energy (Robert Godes)",
    (2016, 1, 1, "Cold Fusion Now! / Miles"): "Documentary: Anomalous Effects in Deuterated Systems (Melvin Miles)",
    (2017, 8, 17, "Storms / Cold Fusion Now!"): "Documentary: Hydroton — A Model of Cold Fusion (Edmund Storms)",
    (1999, 4, 1, "Fire From Water"): "Documentary: Cold Fusion — Fire From Water (Scotty Doohan)",
    (2000, 12, 1, "Johnson"): "Movie: Breaking Symmetry (MIT Prof. Keith Johnson)",
    # Second-pass sweep — comprehensive title fixes
    (1989, 4, 7, "Frascati"): "Frascati: Scaramuzzi Detects Neutrons",
    (1989, 4, 17, "FIC"): "Fusion Information Center Founded",
    (1989, 4, 18, "Scaramuzzi"): "Scaramuzzi & ENEA Announce Neutron Detection",
    (1989, 4, 21, "Huggins"): "Huggins (Stanford) Replicates FPE",
    (1989, 4, 21, "BARC"): "BARC India: Anomalous Neutron Bursts",
    (1989, 4, 24, "DoE Watkins"): "Watkins Establishes DoE Cold Fusion Review Panel",
    (1989, 4, 28, "Case Western"): "Case Western Reports Excess Heat & Tritium",
    (1989, 5, 7, "Bombay"): "India: Ten Teams Replicate Fleischmann-Pons",
    (1989, 5, 8, "Unknown"): "F-Day at Electrochemical Society Meeting",
    (1989, 5, 22, "labs"): "Multi-Lab Confirmations of Fleischmann-Pons Effect",
    (1989, 5, 23, "LANL"): "First LANL Workshop on Cold Fusion",
    (1989, 5, 25, "labs"): "Mexican Scientists Confirm Solid-State Fusion",
    (1989, 6, 23, "BARC"): "BARC: Tritium Increase from Cold Fusion Cells",
    (1989, 7, 18, "Fox"): "Hal Fox Founds Fusion Information Center",
    (1989, 8, 14, "NCFI"): "U.S. National Cold Fusion Institute Formed",
    (1989, 8, 24, "Ikegami"): "Japan Forms National Cold Fusion Working Group",
    (1989, 10, 21, "Appleby"): "Texas A&M: 'Something Nuclear Taking Place'",
    (1989, 10, 31, "DoE ERAB"): "DoE ERAB Approves Final Report Dismissing Cold Fusion",
    (1989, 11, 1, "ERAB"): "DoE ERAB: Cold Fusion Evidence 'Not Persuasive'",
    (1990, 1, 2, "Fusion Facts"): "Fusion Facts: Fleischmann & Pons Scientists of the Year",
    (1990, 1, 22, "DoE GajewskyFederal"): "DoE Gajewsky Tracks Cold Fusion Funding",
    (1990, 2, 1, "NCFI Will, Fritz"): "Fritz Will Heads National Cold Fusion Institute",
    (1990, 5, 15, "Karabut, Kucherov, Savvatimova"): "Russian Glow-Discharge Cold Fusion Observation",
    (1990, 5, 19, "Sttorms"): "Storms Surveys 16 Tritium Successes at LANL",
    (1990, 10, 23, "BYU"): "BYU: Helium-4 Detection in Pd Electrodes",
    (1990, 11, 11, "NCFI"): "National Cold Fusion Institute Hosts Scientific Review",
    (1991, 4, 23, "Mills"): "Randall Mills: Excess Heat from Ni & Light Water",
    (1991, 5, 12, "Navy"): "Stan Szpak: Pd-D Co-deposition Method",
    (1991, 5, 31, "Gluck"): "Gluck & Palibroda: Pd Thin-Foil Cold Fusion",
    (1991, 6, 29, "ICCF-2"): "ICCF-2: 2nd International Cold Fusion Conference",
    (1991, 6, 30, "NCFI"): "National Cold Fusion Institute Closes",
    (1991, 8, 1, "Mills"): "Mills: K2CO3 Aqueous Excess Heat Experiment",
    (1991, 11, 3, "Chambers"): "Naval Research Lab Detects Neutrons",
    (1991, 12, 15, "Nielson"): "Denmark: Anomalous Ni-H Behavior",
    (1992, 9, 8, "Arata-Zhang"): "Arata & Zhang: Reproducible Cold Fusion Reaction",
    (1992, 9, 16, "Bush"): "Robert Bush: Light-Water Excess Heat (Alkali-H Fusion)",
    (1992, 10, 21, "ICCF-3"): "ICCF-3: 3rd International Cold Fusion Conference",
    (1993, 12, 6, "ICCF-4"): "ICCF-4: 4th International Cold Fusion Conference",
    (1993, 12, 9, "Mallove"): "Cold Fusion Magazine Launches with Mallove as Editor",
    (1995, 4, 9, "IE"): "Infinite Energy Magazine Launches",
    (1995, 4, 9, "ICCF-5"): "ICCF-5: 5th International Cold Fusion Conference",
    (1996, 9, 21, "Navy"): "Navy: Anomalous Effects in Deuterated Systems",
    (1996, 10, 5, "Li"): "Xing Zhong Li: Gas-Loaded D/Pd Excess Heat",
    (1996, 10, 13, "ICCF-6"): "ICCF-6: 6th International Cold Fusion Conference",
    (1997, 1, 14, "Arata-Zhang"): "Arata: Solid-State Plasma Fusion Paper",
    (1997, 6, 3, "ANS"): "American Nuclear Society Features LENR",
    (1997, 6, 23, "Cincinnati Group"): "Cincinnati Group: LENT Radioactive Waste Remediation",
    (1997, 12, 25, "NEP"): "New Energy Partners Begins Investing in Cold Fusion",
    (1998, 4, 19, "ICCF-7"): "ICCF-7: 7th International Cold Fusion Conference",
    (1998, 4, 25, "Celani"): "Celani: Cincinnati Group Cell Preliminary Results",
    (1998, 11, 20, "Heavy Watergate"): "'Heavy Watergate: The War Against Cold Fusion' Released",
    (1999, 4, 29, "State Dept."): "Conference on Free Energy at U.S. State Department",
    (2000, 5, 21, "ICCF-8"): "ICCF-8: 8th International Cold Fusion Conference",
    (2000, 12, 1, "Johnson"): "'Breaking Symmetry' (MIT Prof. Keith Johnson) Released",
    (2002, 2, 3, "Navy"): "Naval Tech Report 1862: Pd/D Thermal & Nuclear",
    (2002, 5, 19, "ICCF-9"): "ICCF-9: 9th International Cold Fusion Conference",
    (2003, 8, 24, "ICCF-10"): "ICCF-10: 10th International Cold Fusion Conference",
    (2003, 8, 28, "Dardik"): "Dardik: Superwaves Intensify LENR Cells",
    (2004, 10, 31, "ICCF-11"): "ICCF-11: 11th International Conference (CMNS)",
    (2004, 12, 1, "DoE ERAB"): "DoE Issues Second LENR Review (More Favorable)",
    (2005, 11, 27, "ICCF-12"): "ICCF-12: 12th International Conference (CMNS)",
    (2007, 6, 25, "ICCF-13"): "ICCF-13: 13th International Conference (CMNS)",
    (2007, 7, 9, "Storms"): "Storms: 'The Science of Low Energy Nuclear Reaction'",
    (2008, 5, 21, "Arata-Zhang"): "Arata Demonstrates Cold Fusion Cell Live (25x Return)",
    (2008, 5, 22, "Arata-Zhang"): "Arata & Zhang: Solid Fusion Reactor Paper",
    (2008, 8, 10, "ICCF-14"): "ICCF-14: 14th International Conference (CMNS)",
    (2009, 8, 12, "Zowadny"): "Joseph Zawodny (NASA): LENR Energetics Revolution",
    (2009, 10, 5, "ICCF-15"): "ICCF-15: 15th International Conference (CMNS)",
    (2009, 11, 13, "DIA"): "U.S. DIA Recommends Support for LENR",
    (2011, 2, 6, "ICCF-16"): "ICCF-16: 16th International Conference (CMNS)",
    (2011, 6, 18, "NCUAT"): "Nagel Forms NUCAT Energy",
    (2011, 7, 14, "Rossi, Andrea"): "Rossi Describes Steam Generator to NASA",
    (2011, 9, 22, "NASA"): "NASA Glenn Hosts LENR Workshop",
    (2012, 1, 30, "MIT JET"): "MIT Cold Fusion 101: JET Energy NANOR Display",
    (2012, 8, 6, "Celani"): "Celani Demos Ni-H Cell at NIWeek 2012",
    (2012, 8, 12, "ICCF-17"): "ICCF-17: 17th International Conference (CMNS)",
    (2013, 7, 21, "ICCF-18"): "ICCF-18: 18th International Conference (CMNS)",
    (2015, 4, 13, "ICCF-19"): "ICCF-19: 19th International Conference (CMNS)",
    (2016, 10, 2, "ICCF-20"): "ICCF-20: 20th International Conference (CMNS)",
    (2018, 6, 3, "ICCF-21"): "ICCF-21: 21st International Conference (CMNS)",
    (2019, 5, 27, "Google"): "Google's $10M Cold Fusion Program (Nature paper)",
    (2019, 9, 8, "ICCF-22"): "ICCF-22: 22nd International Conference (CMNS)",
    (2021, 6, 9, "ICCF-23"): "ICCF-23: 23rd International Conference (CMNS)",
    (2022, 7, 25, "ICCF-24"): "ICCF-24: 24th International Conference (CMNS)",
    (2023, 8, 27, "ICCF-25"): "ICCF-25: 25th International Conference (Cold Fusion)",
    (2025, 5, 26, "ICCF-26"): "ICCF-26: 26th International Conference (CMNS)",
    (2026, 8, 31, "ICCF-27"): "ICCF-27: 27th International Conference (CMNS)",
    # Additional user-flagged fixes
    (1990, 7, 23, "U of Hawaii"): "Liebert & Liaw at U Hawaii: 500% Excess Power",
    (1991, 9, 19, "Ikegami / Technova"): "Ikegami/Technova Files EP 0477018 A1",
    (2009, 1, 2, "Jeane Manning, Joel Garbon"): "Breakthrough Power Book Released",
    (2011, 6, 18, "NUCAT"): "Nagel Forms NUCAT Energy",
    (2012, 2, 10, "U of Missouri"): "Duncan Forms SKINR at U Missouri",
    # Pre-cold-fusion historical entries — descriptive titles
    (-50000, 1, 1, "Primitive man"): "Humans Tame Fire",
    (1856, 7, 10, "Tesla"): "Happy Birthday, Nikola Tesla!",
    (-450, 1, 8, "Leucippus of Miletus and Democritus"): "Leucippus & Democritus: Atoms",
    (150, 9, 10, "Hero"): "Hero of Alexandria Invents the Aeolipile",
    (500, 11, 5, "Alchemy"): "Alchemists Seek to Transmute Base Metals",
    (1671, 2, 19, "Newton"): "Newton's 'New Theory of Light and Colors'",
    (1803, 10, 21, "Dalton"): "John Dalton Presents Atomic Theory",
    (1824, 6, 1, "Carnot"): "Carnot: 'Reflections on the Motive Power of Fire'",
    (1905, 9, 27, "Einstein"): "Einstein: Inertia, Energy & Mass-Energy Equivalence",
}

# Entries fully removed from the calendar (out of scope per CLAUDE.md — free-energy adjacent).
# Format: (year, month, date, name) tuples
DROP_EVENTS = {
    (-50000, 1, 1, "Primitive man"),  # too tangential — humans-tame-fire predates cold fusion
    (2005, 11, 29, "Allan, Sterling"),  # Sterling Allan — out of scope per user
    (1994, 11, 23, "Reifenschweiler"),  # near-duplicate of the Nov-24 entry; keep the longer one
}

if os.path.exists(ADDITIONS):
    with open(ADDITIONS) as f:
        additions = json.load(f)
    for r in additions:
        merged[dedup_key(r)] = {
            'month': r['month'], 'date': r['date'], 'year': r['year'],
            'name': clean_name(r.get('name','')), 'taxonomy': clean_taxonomy(r.get('taxonomy', 'Science')),
            'country': clean_country(r.get('country', 'Global')), 'blurb': clean_blurb(r['blurb']),
        }

records = list(merged.values())
records.sort(key=lambda r: (r['year'], r['month'], r['date']))
# Drop out-of-scope events (free-energy adjacent etc.)
records = [r for r in records if (r['year'], r['month'], r['date'], r['name']) not in DROP_EVENTS]
# Apply hand-curated event-title overrides (NAME_OVERRIDES defined at end of file)
for r in records:
    key = (r['year'], r['month'], r['date'], r['name'])
    if key in NAME_OVERRIDES:
        r['name'] = NAME_OVERRIDES[key]
    # Canonical ordering across name + blurb (drift across original/additions)
    r['name'] = normalize_fp_order(r['name'])
    r['blurb'] = normalize_fp_order(r['blurb'])

# Build podcast# → entry-date map, then rewrite generic "See also CFN podcast #N" cross-refs
# to point at that episode's specific entry on lackluster.org/cf.
_pod_map = {}
for r in records:
    m = re.search(r'Podcast Ep\.\s*0?(\d+)', r['blurb'])
    if m and 'CFN_0' in r['blurb']:
        _pod_map[int(m.group(1))] = f"{r['year']}-{r['month']}-{r['date']}"
def _link_podcast(match):
    n = int(match.group(1))
    if n in _pod_map:
        return f"(See also CFN Podcast #{n}: https://www.lackluster.org/cf/#{_pod_map[n]})"
    return match.group(0)
for r in records:
    r['blurb'] = re.sub(r'\(See also CFN podcast #(\d+):\s*https://coldfusionnow\.org/cfnpodcast/\)?',
                        _link_podcast, r['blurb'])

# Post-rename dedup: when two records share (year, month, date, name), keep the longer blurb.
_dedup = {}
for r in records:
    k = (r['year'], r['month'], r['date'], r['name'])
    if k not in _dedup or len(r['blurb']) > len(_dedup[k]['blurb']):
        _dedup[k] = r
records = list(_dedup.values())
records.sort(key=lambda r: (r['year'], r['month'], r['date']))
for i, r in enumerate(records, 1):
    r['id'] = i

with open(OUT, 'w') as f:
    json.dump(records, f, ensure_ascii=False)

# De-duplicate quotes preserving order
seen = set()
quotes_unique = [q for q in quotes if not (q in seen or seen.add(q))]
with open(QUOTES_OUT, 'w') as f:
    json.dump(quotes_unique, f, ensure_ascii=False)

print(f'wrote {len(records)} events and {len(quotes_unique)} quotes ({skipped} undated rows)')
