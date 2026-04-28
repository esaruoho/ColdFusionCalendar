#!/usr/bin/env python3
"""Regenerate the og:image (1200x630) using the current event count from data.json."""
import json, random
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / 'datasets' / '40d7f378-7b62-44f6-8196-5bae64a95169' / 'data.json'
OUT = ROOT / 'assets' / 'og-cf-calendar.png'

W, H = 1200, 630
BG = (5, 7, 10)
GOLD = (212, 175, 55)
CYAN = (0, 229, 255)
WHITE = (240, 246, 252)
GREY = (139, 148, 158)

def font(size):
    for c in [
        '/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf',
        '/System/Library/Fonts/Supplemental/Times New Roman.ttf',
        '/System/Library/Fonts/Supplemental/Georgia Bold.ttf',
        '/System/Library/Fonts/Supplemental/Georgia.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
    ]:
        try: return ImageFont.truetype(c, size)
        except OSError: continue
    return ImageFont.load_default()

count = len(json.load(open(DATA)))
# Find the latest ICCF mentioned to keep the subtitle accurate
import re
events = json.load(open(DATA))
iccfs = []
for e in events:
    m = re.match(r'ICCF-(\d+)', e.get('name', ''))
    if m: iccfs.append(int(m.group(1)))
latest_iccf = max(iccfs) if iccfs else 27

img = Image.new('RGB', (W, H), BG)
draw = ImageDraw.Draw(img, 'RGBA')

# Particle field
random.seed(42)
for _ in range(220):
    x, y = random.randint(0, W), random.randint(0, H)
    s, a = random.randint(1, 3), random.randint(20, 120)
    c = CYAN if random.random() < 0.6 else GOLD
    draw.ellipse((x, y, x+s, y+s), fill=(c[0], c[1], c[2], a))

label_f, title_f, sub_f, foot_f = font(28), font(96), font(40), font(24)

draw.text((80, 88), "HISTORICAL ARCHIVE", font=label_f, fill=GOLD)
draw.text((80, 138), "THE COLD FUSION", font=title_f, fill=WHITE)
draw.text((80, 248), "CALENDAR", font=title_f, fill=GOLD)
draw.text((80, 380), "An interactive chronology of LENR & energy science", font=sub_f, fill=GREY)

# Stat row — count is dynamic
stat_y = 470
draw.text((80, stat_y), str(count), font=title_f, fill=CYAN)
bbox = draw.textbbox((80, stat_y), str(count), font=title_f)
draw.text((bbox[2] + 24, stat_y + 30),
          f"milestones from antiquity to ICCF-{latest_iccf}",
          font=sub_f, fill=WHITE)

draw.line([(80, H-72), (W-80, H-72)], fill=(255, 255, 255, 40))
url = "lackluster.org/cf"
bbox = draw.textbbox((0, 0), url, font=foot_f)
draw.text((W - bbox[2] - 80, H - 50), url, font=foot_f, fill=CYAN)

OUT.parent.mkdir(exist_ok=True)
img.save(OUT, 'PNG', optimize=True)
print(f'Wrote {OUT.name}: {count} milestones, latest ICCF-{latest_iccf}')
