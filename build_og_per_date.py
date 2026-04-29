#!/usr/bin/env python3
"""Generate per-date og:images at assets/og/MM-DD.png for every (month, date) with events.

Used by per-date sharing — when someone shares lackluster.org/cf/#1989-3-23,
JavaScript can swap the og:image meta tag to assets/og/03-23.png.
"""
import json, random
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent
DATA = ROOT / 'datasets' / '40d7f378-7b62-44f6-8196-5bae64a95169' / 'data.json'
OUT_DIR = ROOT / 'assets' / 'og'
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1200, 630
BG = (5, 7, 10); GOLD = (212, 175, 55); CYAN = (0, 229, 255)
WHITE = (240, 246, 252); GREY = (139, 148, 158); SOFT = (200, 210, 220)

MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]

def font(size):
    for c in [
        '/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf',
        '/System/Library/Fonts/Supplemental/Times New Roman.ttf',
        '/System/Library/Fonts/Supplemental/Georgia Bold.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
    ]:
        try: return ImageFont.truetype(c, size)
        except OSError: continue
    return ImageFont.load_default()

events = json.loads(DATA.read_text())
by_date = defaultdict(list)
for e in events:
    by_date[(e['month'], e['date'])].append(e)

label_f = font(28); date_f = font(96); name_f = font(34); blurb_f = font(22); foot_f = font(22); count_f = font(48)

def wrap(draw, text, fnt, max_w):
    """Naive word-wrap to fit max_w."""
    words = text.split(); lines = []; cur = ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

count = 0
for (m, d), evs in by_date.items():
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img, 'RGBA')

    random.seed(m * 100 + d)
    for _ in range(140):
        x, y = random.randint(0, W), random.randint(0, H)
        s, a = random.randint(1, 2), random.randint(20, 90)
        c = CYAN if random.random() < 0.6 else GOLD
        draw.ellipse((x, y, x+s, y+s), fill=(c[0], c[1], c[2], a))

    draw.text((80, 60), "THE COLD FUSION CALENDAR", font=label_f, fill=GOLD)
    draw.text((80, 120), f"{MONTHS[m-1]} {d}", font=date_f, fill=WHITE)
    draw.text((80, 230), f"{len(evs)} milestone{'s' if len(evs) != 1 else ''} on this day", font=label_f, fill=CYAN)

    # Show up to 3 events
    y = 290
    for ev in evs[:3]:
        yr = f"{ev['year']}" if ev['year'] > 0 else (f"{abs(ev['year'])} BCE" if ev['year'] < 0 else 'Unspecified era')
        draw.text((80, y), f"{yr} · {ev['name']}", font=name_f, fill=WHITE)
        y += 42
        for line in wrap(draw, ev['blurb'][:200] + ('…' if len(ev['blurb']) > 200 else ''), blurb_f, W - 160)[:2]:
            draw.text((100, y), line, font=blurb_f, fill=SOFT); y += 30
        y += 12
        if y > 530: break
    if len(evs) > 3:
        draw.text((80, 540), f"+ {len(evs) - 3} more", font=label_f, fill=GREY)

    draw.line([(80, H-72), (W-80, H-72)], fill=(255,255,255,40))
    url = "lackluster.org/cf"
    bbox = draw.textbbox((0, 0), url, font=foot_f)
    draw.text((W - bbox[2] - 80, H - 50), url, font=foot_f, fill=CYAN)

    out_path = OUT_DIR / f"{m:02d}-{d:02d}.png"
    img.save(out_path, 'PNG', optimize=True)
    count += 1

print(f'Wrote {count} per-date og:images to {OUT_DIR.relative_to(ROOT)}/')
