#!/usr/bin/env python3
"""Minimal regression tests for the data build.

Run:    python3 tests/test_build_data.py
        python3 -m pytest tests/  (if pytest installed)
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = ROOT / 'datasets' / '40d7f378-7b62-44f6-8196-5bae64a95169' / 'data.json'
QUOTES = ROOT / 'datasets' / '40d7f378-7b62-44f6-8196-5bae64a95169' / 'quotes.json'
ICAL = ROOT / 'calendar.ics'
RSS = ROOT / 'feed.xml'

MIN_EVENTS = 280   # ratchet baseline; bump after intentional drops
MIN_QUOTES = 140
URL_RE = re.compile(r'https?://[^\s<]+')

failures = []

def check(name, ok, detail=''):
    if ok:
        print(f'  PASS  {name}')
    else:
        print(f'  FAIL  {name}{": " + detail if detail else ""}')
        failures.append((name, detail))

events = json.loads(DATA.read_text())
quotes = json.loads(QUOTES.read_text())

print('--- counts ---')
check(f'>= {MIN_EVENTS} events', len(events) >= MIN_EVENTS, f'have {len(events)}')
check(f'>= {MIN_QUOTES} quotes', len(quotes) >= MIN_QUOTES, f'have {len(quotes)}')

print('--- per-event sanity ---')
for i, e in enumerate(events):
    for fld in ('month', 'date', 'year', 'name', 'blurb'):
        if fld not in e:
            check(f'event[{i}] has {fld}', False, repr(e)[:80]); break
    if not (1 <= e['month'] <= 12):
        check(f'event[{i}] month 1-12', False, f'{e["month"]} in {e["name"]}')
    if not (1 <= e['date'] <= 31):
        check(f'event[{i}] date 1-31', False, f'{e["date"]} in {e["name"]}')
    if not (-100000 < e['year'] < 3000):
        check(f'event[{i}] year sane', False, f'{e["year"]} in {e["name"]}')
    if not e['blurb'].strip():
        check(f'event[{i}] blurb non-empty', False, e['name'])
print('  PASS  all events well-formed')

print('--- duplicate detection ---')
# Same (m,d,y,name) is allowed when blurbs are distinct events (e.g., Pons made
# multiple announcements on Apr 17 1989). True dupes are same-key + similar blurb.
import re as _re
def norm_blurb(b):
    return _re.sub(r'\s+', ' ', _re.sub(r'[^a-z0-9 ]', '', (b or '').lower())).strip()[:60]
seen = set()
dups = 0
for e in events:
    k = (e['month'], e['date'], e['year'], (e.get('name') or '').strip().lower(), norm_blurb(e['blurb']))
    if k in seen: dups += 1
    seen.add(k)
check('no duplicate (m,d,y,name,blurb-prefix) records', dups == 0, f'{dups} dupes')

print('--- generated artifacts ---')
check('calendar.ics exists', ICAL.exists())
check('feed.xml exists', RSS.exists())
if ICAL.exists():
    ics_text = ICAL.read_text()
    check('iCal has BEGIN/END VCALENDAR', 'BEGIN:VCALENDAR' in ics_text and 'END:VCALENDAR' in ics_text)
    n_events = ics_text.count('BEGIN:VEVENT')
    n_close = ics_text.count('END:VEVENT')
    check('iCal VEVENT count balanced', n_events == n_close, f'begin={n_events} end={n_close}')
if RSS.exists():
    rss_text = RSS.read_text()
    check('RSS is valid XML root', rss_text.startswith('<?xml'))
    check('RSS has <channel>', '<channel>' in rss_text)

print('--- URL collection ---')
urls = []
for e in events:
    urls.extend(URL_RE.findall(e['blurb']))
print(f'  {len(urls)} URLs across {sum(1 for e in events if URL_RE.search(e["blurb"]))} entries')

print()
if failures:
    print(f'FAILED: {len(failures)} checks')
    sys.exit(1)
print('All checks passed.')
