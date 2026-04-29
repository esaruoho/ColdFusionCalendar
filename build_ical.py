#!/usr/bin/env python3
"""Generate calendar.ics — yearly-recurring all-day events for every dated milestone.

Subscribe in macOS Calendar / Google Calendar:
    https://www.lackluster.org/cf/calendar.ics
"""
import json, hashlib
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / 'datasets' / '40d7f378-7b62-44f6-8196-5bae64a95169' / 'data.json'
OUT = ROOT / 'calendar.ics'

PRODID = '-//Lackluster//Cold Fusion Calendar//EN'

def fold(line):
    """RFC 5545 line folding at 75 octets."""
    out = []
    while len(line.encode('utf-8')) > 75:
        cut = 75
        # back off to a byte boundary
        while len(line[:cut].encode('utf-8')) > 75:
            cut -= 1
        out.append(line[:cut])
        line = ' ' + line[cut:]
    out.append(line)
    return '\r\n'.join(out)

def escape(s):
    return (s or '').replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n').replace('\r', '')

def fmt_date(d):
    return d.strftime('%Y%m%d')

events = json.loads(DATA.read_text())
events.sort(key=lambda e: (e['year'], e['month'], e['date']))

now_stamp = date.today().strftime('%Y%m%dT000000Z')

lines = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    f'PRODID:{PRODID}',
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    'X-WR-CALNAME:The Cold Fusion Calendar',
    'X-WR-CALDESC:Yearly anniversaries of milestones in cold fusion / LENR / energy science. Source: https://www.lackluster.org/cf/',
    'X-WR-TIMEZONE:UTC',
    'REFRESH-INTERVAL;VALUE=DURATION:P1D',
]

skipped = 0
for e in events:
    y, m, d = e['year'], e['month'], e['date']
    # iCal yearly recurrence needs DTSTART as a real date. For ancient/BCE/leap-day
    # entries we fall back to a representative anchor in the current era so the
    # recurrence renders in modern calendar apps.
    try:
        if y < 1:  # BCE / antiquity — anchor to year 1 for display
            dtstart = date(1, m, d)
        else:
            dtstart = date(y, m, d)
    except ValueError:
        # Feb 29 on a non-leap year, or other invalid date — fall back to year 1
        try: dtstart = date(1, m, min(d, 28))
        except ValueError: skipped += 1; continue

    dtend = dtstart + timedelta(days=1)
    uid = 'cf-' + hashlib.sha1(f"{y}-{m}-{d}-{e.get('name','')}-{e['blurb'][:40]}".encode()).hexdigest()[:16] + '@lackluster.org'

    year_str = f'{y}' if y > 0 else (f'{abs(y)} BCE' if y < 0 else 'Unspecified era')
    summary = f"{e['name']} ({year_str})"
    parts = [
        e['blurb'],
        '',
        f"Year: {year_str}",
        f"Type: {e.get('taxonomy','Research')}",
        f"Origin: {e.get('country','Global')}",
        '',
        f"Source: https://www.lackluster.org/cf/#{y}-{m}-{d}",
    ]
    description = '\n'.join(parts)

    lines += [
        'BEGIN:VEVENT',
        f'UID:{uid}',
        f'DTSTAMP:{now_stamp}',
        f'DTSTART;VALUE=DATE:{fmt_date(dtstart)}',
        f'DTEND;VALUE=DATE:{fmt_date(dtend)}',
        'RRULE:FREQ=YEARLY',
        f'SUMMARY:{escape(summary)}',
        f'DESCRIPTION:{escape(description)}',
        f'CATEGORIES:{escape(e.get("taxonomy","Research"))}',
        f'URL:https://www.lackluster.org/cf/#{y}-{m}-{d}',
        'TRANSP:TRANSPARENT',
        'END:VEVENT',
    ]

lines.append('END:VCALENDAR')
folded = '\r\n'.join(fold(line) for line in lines)
OUT.write_text(folded + '\r\n')
print(f'Wrote {OUT.name}: {len(events) - skipped} events ({skipped} skipped due to invalid dates)')
