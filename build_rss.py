#!/usr/bin/env python3
"""Generate feed.xml — RSS feed of the next 60 days of upcoming anniversaries.

Subscribe in any RSS reader (Feedly, NetNewsWire, etc.):
    https://www.lackluster.org/cf/feed.xml
"""
import json, html
from datetime import date, timedelta
from pathlib import Path
from email.utils import formatdate
from time import mktime
from datetime import datetime

ROOT = Path(__file__).parent
DATA = ROOT / 'datasets' / '40d7f378-7b62-44f6-8196-5bae64a95169' / 'data.json'
OUT = ROOT / 'feed.xml'
SITE = 'https://www.lackluster.org/cf/'
WINDOW_DAYS = 60

events = json.loads(DATA.read_text())
today = date.today()

# Build (target-date, event) pairs for the next WINDOW_DAYS
upcoming = []
for e in events:
    for year_offset in (0, 1):
        try:
            target = date(today.year + year_offset, e['month'], e['date'])
        except ValueError:
            continue
        delta = (target - today).days
        if 0 <= delta <= WINDOW_DAYS:
            upcoming.append((target, e))

upcoming.sort(key=lambda r: r[0])

def ts_2822(d):
    return formatdate(mktime(datetime(d.year, d.month, d.day, 9, 0, 0).timetuple()), usegmt=True)

build_date = formatdate(usegmt=True)

items = []
for target, e in upcoming:
    y_label = f"{e['year']}" if e['year'] > 0 else (f"{abs(e['year'])} BCE" if e['year'] < 0 else "Unspecified era")
    permalink = f"{SITE}#{e['year']}-{e['month']}-{e['date']}"
    title = html.escape(f"{target.strftime('%b %-d')}: {e['name']} ({y_label})")
    description = html.escape(e['blurb'])
    items.append(f"""    <item>
      <title>{title}</title>
      <link>{permalink}</link>
      <guid isPermaLink="false">cf-{e['year']}-{e['month']}-{e['date']}-{target.year}</guid>
      <pubDate>{ts_2822(target)}</pubDate>
      <category>{html.escape(e.get('taxonomy','Research'))}</category>
      <description>{description}</description>
    </item>""")

xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>The Cold Fusion Calendar — Upcoming Anniversaries</title>
    <link>{SITE}</link>
    <description>Yearly anniversaries of milestones in cold fusion / LENR / energy science, looking {WINDOW_DAYS} days ahead.</description>
    <language>en</language>
    <lastBuildDate>{build_date}</lastBuildDate>
    <atom:link href="{SITE}feed.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
  </channel>
</rss>
"""
OUT.write_text(xml)
print(f'Wrote {OUT.name}: {len(items)} upcoming anniversaries (next {WINDOW_DAYS} days)')
