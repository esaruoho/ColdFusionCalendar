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
}

def apply_typos(s):
    for bad, good in TYPO_FIXES.items():
        s = s.replace(bad, good)
    return s

def clean_blurb(s):
    if not s: return s
    s = s.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
    # Insert space after comma when followed by a letter (not digit — preserves "4,943,355")
    s = re.sub(r',(?=[A-Za-z])', ', ', s)
    s = re.sub(r' {2,}', ' ', s).strip()
    s = apply_typos(s)
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
    'USA': 'US',
    'U.S.': 'US',
    'U.S.A.': 'US',
    'United States': 'US',
    'United States of America': 'US',
    'America': 'US',
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
            'name': r['name'], 'taxonomy': clean_taxonomy(r['taxonomy']),
            'country': clean_country(r['country']), 'blurb': r['blurb'],
        }

# Hand-curated additions (ICCF conferences, modern milestones)
import os
if os.path.exists(ADDITIONS):
    with open(ADDITIONS) as f:
        additions = json.load(f)
    for r in additions:
        merged[dedup_key(r)] = {
            'month': r['month'], 'date': r['date'], 'year': r['year'],
            'name': r['name'], 'taxonomy': clean_taxonomy(r.get('taxonomy', 'Science')),
            'country': clean_country(r.get('country', 'Global')), 'blurb': clean_blurb(r['blurb']),
        }

records = list(merged.values())
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
