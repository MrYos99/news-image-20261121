#!/usr/bin/env python3
"""Compose the news-image-20261121 entry: a dense newspaper front page.

THE WORLD IN ONE DAY — Saturday 21 November 2026.
47 real stories reported on 21 Nov 2026, 7 regions, 18 fields.
Flat vector illustrations (generated with the image model, no real photos).
All type drawn with PIL. Output: 1024x1024 JPEG bytes saved as entry.png.
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets2")

W, H = 1024, 1024
PAPER = (246, 240, 220)
INK = (28, 26, 22)
GREY = (107, 100, 85)
RULE = (28, 26, 22)
RED = (163, 29, 29)
LAND = (227, 217, 189)
LAND_LINE = (150, 138, 110)
SEA = (223, 232, 228)

SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, s, f, max_w, max_lines=None):
    """Word-wrap s to max_w; returns list of lines (clamped to max_lines)."""
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + "...", font=f) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1] + "..."
    return lines


def fit_check(draw, s, f, max_w, max_lines, label):
    lines = wrap(draw, s, f, max_w, None)
    if len(lines) > max_lines:
        print(f"OVERFLOW {label}: {len(lines)} lines > {max_lines}: {s[:60]}")
    return lines


def cover(im, w, h):
    """Centre-crop image to fill w x h."""
    iw, ih = im.size
    s = max(w / iw, h / ih)
    im = im.resize((round(iw * s), round(ih * s)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


CONF_COLORS = {
    "CONFIRMED": (30, 107, 58),
    "REPORTED": (43, 95, 138),
    "CLAIM": (163, 91, 0),
    "FORECAST": (107, 91, 149),
    "OFFICIAL": (28, 26, 22),
}


def chip(draw, x, y, text, f, fill):
    w = draw.textlength(text, font=f) + 10
    h = 14
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=fill)
    draw.text((x + 5, y + 2), text, font=f, fill=(255, 255, 255))
    return w


def num_chip(draw, x, y, n, size=16):
    f = font(SANSB, 10 if size <= 16 else 12)
    draw.rectangle([x, y, x + size, y + size], fill=RED)
    t = str(n)
    tw = draw.textlength(t, font=f)
    draw.text((x + (size - tw) / 2, y + (size - 12) / 2 + 1), t, font=f,
              fill=(255, 255, 255))


# ---------------------------------------------------------------- data
# (num, image, region, field, confidence, headline, summary, source)
HEROES = [
    (1, "hero-hormuz.png", "MIDDLE EAST", "WAR", "CONFIRMED",
     "TRUMP DELAYS IRAN STRIKE TO NEXT YEAR",
     "No decision on new strikes until after the new year. Iran readies a "
     "Kharg convoy to test the blockade; oil income hits zero by mid-Dec.",
     "World Watch · Independent · Iran Intl"),
    (2, "hero-houthi.png", "MIDDLE EAST", "WAR", "CONFIRMED",
     "SAUDI DEFENCES DOWN THREE HOUTHI MISSILES",
     "Coalition air defences intercept three Houthi ballistic missiles "
     "targeting Riyadh, then a Houthi drone.",
     "Arab News · Reuters · AFP"),
    (3, "hero-cyclone.png", "ASIA", "WEATHER", "CONFIRMED",
     "CYCLONE AKVAN FADES; ODISHA SPARED",
     "Akvan weakens after landfall near Gopalpur. 372,000 evacuated, "
     "41 trains cancelled; no major damage reported.",
     "The Hindu · Indian Express"),
    (4, "hero-datacentre.png", "NORTH AMERICA", "TECH", "CONFIRMED",
     "TRUMP THREATENS DATA-CENTRE TAX",
     "US tech firms that build AI data centres overseas will face "
     "tremendous penalties and taxes, Trump says.",
     "AP · Guardian · NYT · Axios · SBS"),
]

# (num, image, region, field, confidence, headline, summary, source)
NUMBERED = [
    (5, "small-poland.png", "EUROPE", "WAR", "REPORTED",
     "EUROPE CONDEMNS MISSILES IN POLAND",
     "Leaders react to Friday's landings; NATO calls it a violation.",
     "Guardian"),
    (6, "small-voyager.png", "NORTH AMERICA", "SPACE", "OFFICIAL",
     "VOYAGER 1 PASSES ONE LIGHT-DAY FROM EARTH",
     "First spacecraft to travel more than a light-day from home.",
     "Reuters · NASA"),
    (7, "small-dragon.png", "NORTH AMERICA", "SPACE", "REPORTED",
     "SPACEX DRAGON HEADS HOME FOR SPLASHDOWN",
     "Cargo craft leaves the station; splashdown due off California.",
     "Xinhua"),
    (8, "small-euuk.png", "EUROPE", "POLITICS", "REPORTED",
     "EU-UK AGREE CLOSEST TIES SINCE BREXIT",
     "Farm trade eased, carbon markets linked, youth mobility from 2028.",
     "BBC · Xinhua"),
    (9, "small-taragas.png", "MIDDLE EAST", "SHIPPING", "REPORTED",
     "LPG TANKER HIT AGAIN IN THE STRAIT",
     "Tara Gas attacked a second time off Oman; a seafarer is missing.",
     "The Hindu"),
    (10, "small-yemen.png", "MIDDLE EAST", "WAR", "CLAIM",
     "41 KILLED IN YEMEN AIRSTRIKES, MEDIA SAY",
     "Strikes attributed to Saudi Arabia kill 41, including 11 children.",
     "Xinhua · al-Masirah"),
    (11, "small-denmark.png", "EUROPE", "ESPIONAGE", "CLAIM",
     "DENMARK EXPELS DIPLOMAT OVER PLOT",
     "Copenhagen expels a diplomat over an alleged plot on Danish soil.",
     "Al Jazeera"),
    (12, "small-ebola.png", "AFRICA", "HEALTH", "REPORTED",
     "CONGO EBOLA OUTBREAK PASSES 11,000 CASES",
     "Bundibugyo strain spreads fast; 5,500 dead, no licensed cure.",
     "Reuters"),
    (13, "small-gupta.png", "NORTH AMERICA", "LAW", "OFFICIAL",
     "US COURT JAILS GUPTA 19 YEARS OVER PLOT",
     "Nikhil Gupta gets 235 months for the plot to kill Pannun in NY.",
     "The Hindu · Reuters"),
    (14, "small-maya.png", "LATIN AMERICA", "SCIENCE", "REPORTED",
     "MAYA STUCCO HEADS UNVEILED IN GUATEMALA",
     "Life-sized 7th-8th century heads unearthed in the Mirador Basin.",
     "Reuters"),
    (15, "small-cummins.png", "OCEANIA", "SPORT", "CONFIRMED",
     "CUMMINS KEEPS THE AUSTRALIAN CAPTAINCY",
     "Pat Cummins will retain the captaincy after meeting Cricket Aus.",
     "ABC"),
    (16, "small-delhi.png", "ASIA", "ENVIRONMENT", "REPORTED",
     "DELHI WAKES TO POOR AIR AS AQI HITS 279",
     "The capital's air stays poor on Saturday morning.",
     "Indian Express"),
]

# (num, headline, confidence) grouped by region for the ALSO columns
ALSO = [
    ("MIDDLE EAST", [
        (17, "US and Israel weigh new strikes on Iran", "REPORTED"),
        (18, "Araghchi rules out uranium transfer", "REPORTED"),
        (19, "Hormuz shipping 65% below pre-war levels", "REPORTED"),
        (20, "Tanker explodes after hitting mines, IRGC says", "CLAIM"),
        (21, "Iran says its strikes on Israel concluded", "CLAIM"),
    ]),
    ("ASIA", [
        (22, "Saudi to triple crude stored in Japan", "REPORTED"),
        (23, "Japan and Chile agree minerals, defence ties", "REPORTED"),
        (24, "Japan weighs nuclear-powered submarines", "REPORTED"),
        (25, "Japan education minister pressed to resign", "REPORTED"),
        (26, "Trump, Xi: humans keep charge of military AI", "REPORTED"),
        (27, "India takes note of Shenzhen summit", "OFFICIAL"),
        (28, "India asks UAE to probe flydubai co-pilot", "REPORTED"),
        (29, "HK seawater fuel from waste heat", "REPORTED"),
        (30, "Homo erectus mastered rainforest in China", "REPORTED"),
        (31, "Nara opens first NY solo show in a decade", "REPORTED"),
    ]),
    ("EUROPE", [
        (32, "Germany, France end FCAS fighter project", "REPORTED"),
        (33, "Coalition troops train in war's shadow", "REPORTED"),
        (34, "Kushner cites Russian openness on guarantees", "CLAIM"),
        (35, "US resumes intel sharing on missile threats", "REPORTED"),
        (36, "New explosions in Kyiv amid drone alert", "REPORTED"),
        (37, "Students rally across Europe over costs, war", "REPORTED"),
        (38, "Drones fly over Karup base in Denmark", "REPORTED"),
        (39, "Russian implant regrows bone, scientists say", "REPORTED"),
        (40, "Newcastle host Arsenal in late kick-off", "FORECAST"),
    ]),
    ("AFRICA", [
        (41, "Kenya debates marital consent", "REPORTED"),
        (42, "Ghana MP: where is GH¢100m coders fund?", "REPORTED"),
        (43, "Nigeria mega churches face succession heat", "REPORTED"),
        (44, "Peter Obi declares vote-defence holiday", "REPORTED"),
        (45, "Nigeria Customs suspends 3,852 recruits", "REPORTED"),
    ]),
    ("LATIN AMERICA", [
        (46, "Ecuador extends emergency by 30 days", "REPORTED"),
        (47, "Brazil recalls envoy to Argentina", "REPORTED"),
    ]),
]

DATECHECK = [
    "Shenzhen Peace Declaration — signed THU 19 NOV",
    "ICJ: Myanmar guilty of Rohingya genocide — THU 19 NOV",
    "Russian missile lands in Poland — FRI 20 NOV",
    "Australia-China agree AI talks — FRI 20 NOV",
    "US/Venezuela strike on ELN camp — 3-4 NOV",
    "Starship catch; Vulcan's first failure — 14 NOV",
    "ICEYE to buy Avio; NATO Starlift — 17 NOV",
    "NASA RS-25 engine test for Artemis — 19 NOV",
]

# (time, short label, story num) — chronological, evenly spaced stops
TIMELINE = [
    ("00:37", "Houthi missiles down", 2),
    ("01:39", "US-Israel weigh strikes", 17),
    ("01:49", "Cyclone fades", 3),
    ("02:29", "Kharg convoy", 1),
    ("02:41", "Poland reaction", 5),
    ("03:04", "Cummins keeps captaincy", 15),
    ("03:11", "Hormuz shipping -65%", 19),
    ("23:41", "Tanker hits mines", 20),
]

HOW_SURE = [
    ("CONFIRMED", "several major outlets agree"),
    ("REPORTED", "one major outlet"),
    ("CLAIM", "single source, unverified"),
    ("FORECAST", "a prediction, not a result"),
    ("OFFICIAL", "a government or court statement"),
]


# ------------------------------------------------------------ world map
# Simplified continent outlines, (lon, lat). Schematic, not to scale.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-75, 62),
     (-65, 60), (-55, 47), (-70, 42), (-75, 35), (-80, 32), (-85, 30),
     (-90, 21), (-97, 16), (-105, 20), (-110, 23), (-120, 34), (-125, 40),
     (-130, 55), (-150, 60), (-165, 60)],
    # Greenland
    [(-58, 64), (-45, 60), (-30, 68), (-40, 76), (-60, 76), (-68, 70)],
    # South America
    [(-80, 10), (-75, 5), (-60, 5), (-50, 0), (-40, -5), (-35, -10),
     (-40, -20), (-48, -28), (-55, -35), (-65, -45), (-70, -55), (-73, -40),
     (-72, -20), (-80, -5), (-81, 0)],
    # Africa
    [(-17, 15), (-10, 30), (-5, 35), (10, 37), (20, 32), (32, 31), (35, 28),
     (40, 15), (48, 11), (51, 10), (45, 0), (40, -10), (35, -18), (32, -28),
     (25, -35), (18, -35), (15, -25), (12, -10), (9, 4), (-8, 5), (-15, 10)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (25, 65), (20, 70),
     (15, 70), (10, 64), (5, 60), (-5, 58), (-10, 55), (-12, 50), (-10, 44)],
    # Asia
    [(30, 62), (40, 68), (60, 70), (80, 73), (100, 76), (120, 73), (140, 72),
     (160, 70), (178, 66), (170, 60), (162, 56), (158, 50), (150, 45),
     (140, 40), (130, 35), (127, 33), (122, 30), (120, 25), (110, 20),
     (105, 10), (100, 8), (95, 15), (90, 22), (85, 20), (80, 10), (77, 8),
     (72, 20), (66, 25), (60, 25), (55, 26), (50, 30), (45, 30), (40, 32),
     (35, 36), (30, 36)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32), (137, -35),
     (140, -38), (145, -38), (150, -37), (153, -27), (150, -22), (146, -19),
     (142, -11), (136, -12), (132, -11), (126, -14), (122, -17), (118, -20)],
    # Japan
    [(130, 31), (133, 34), (137, 35), (140, 38), (142, 42), (145, 44),
     (140, 40), (135, 34), (130, 32)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 52)],
]

# (story num, lon, lat, place) — pins on the map (nudged so neighbours
# do not overlap at this scale; no pin for 9 Musandam, it sits on Hormuz)
PINS = [
    (1, 55.0, 28.0, "Hormuz"),
    (2, 46.0, 24.5, "Riyadh"),
    (3, 84.9, 19.3, "Gopalpur"),
    (4, -77.0, 38.9, "Washington"),
    (5, 24.0, 50.5, "Lublin"),
    (8, -1.0, 52.0, "London"),
    (10, 42.0, 14.0, "Sanaa"),
    (11, 11.0, 58.5, "Copenhagen"),
    (12, 15.3, -4.3, "Kinshasa"),
    (13, -74.0, 40.7, "New York"),
    (14, -90.5, 14.6, "Guatemala"),
    (15, 151.2, -33.9, "Sydney"),
    (16, 77.2, 28.6, "Delhi"),
]


def draw_map(draw, x0, y0, w, h):
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=SEA, outline=RULE, width=1)
    lon0, lon1, lat0, lat1 = -180, 180, 82, -58  # top, bottom
    def px(lon, lat):
        return (x0 + (lon - lon0) / (lon1 - lon0) * w,
                y0 + (lat0 - lat) / (lat0 - lat1) * h)
    for poly in CONTINENTS:
        pts = [px(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_LINE)
    f = font(SANSB, 7)
    for n, lon, lat, place in PINS:
        cx, cy = px(lon, lat)
        r = 5
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                     outline=(255, 255, 255), width=1)
        t = str(n)
        tw = draw.textlength(t, font=f)
        draw.text((cx - tw / 2, cy - 4), t, font=f, fill=(255, 255, 255))


# ------------------------------------------------------------ compose
def compose():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    MX = 12  # side margin
    CW = W - 2 * MX  # 1000

    # ---- masthead
    f_title = font(SERIF, 54)
    title = "THE WORLD IN ONE DAY"
    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, 6), title, font=f_title, fill=INK)
    f_date = font(SANSB, 19)
    date = "SATURDAY 21 NOVEMBER 2026"
    tw = d.textlength(date, font=f_date)
    d.text(((W - tw) / 2, 68), date, font=f_date, fill=INK)
    f_kick = font(SANS, 12)
    d.text((MX, 94), "47 STORIES · 7 REGIONS · 18 FIELDS",
           font=f_kick, fill=INK)
    right = "ALL TIMES UTC · EVERY STORY SOURCED"
    tw = d.textlength(right, font=f_kick)
    d.text((W - MX - tw, 94), right, font=f_kick, fill=INK)
    d.line([(MX, 112), (W - MX, 112)], fill=RULE, width=3)
    d.line([(MX, 116), (W - MX, 116)], fill=RULE, width=1)

    # ---- timeline: the day in order (evenly spaced stops, times shown)
    y = 121
    f_tl = font(SANSB, 11)
    d.text((MX, y), "THE DAY, IN ORDER", font=f_tl, fill=INK)
    d.text((W - MX - d.textlength("UTC", font=f_tl), y), "UTC",
           font=f_tl, fill=GREY)
    bar_y = 162
    d.line([(MX, bar_y), (W - MX, bar_y)], fill=RULE, width=2)
    n = len(TIMELINE)
    slot = CW / n
    f_time = font(SANSB, 10)
    f_lab = font(SANS, 9)
    for i, (t, lab, num) in enumerate(TIMELINE):
        cx = MX + slot * (i + 0.5)
        d.ellipse([cx - 4, bar_y - 4, cx + 4, bar_y + 4], fill=RED)
        above = (i % 2 == 0)
        tw1 = d.textlength(t, font=f_time)
        tw2 = d.textlength(lab, font=f_lab)
        tx = min(max(cx - max(tw1, tw2) / 2, MX), W - MX - max(tw1, tw2))
        if above:
            d.text((tx, bar_y - 28), t, font=f_time, fill=RED)
            d.text((tx, bar_y - 16), lab, font=f_lab, fill=INK)
        else:
            d.text((tx, bar_y + 8), t, font=f_time, fill=RED)
            d.text((tx, bar_y + 20), lab, font=f_lab, fill=INK)

    # ---- heroes: 4 across
    hy = 196
    col_w = (CW - 3 * 8) // 4  # 244
    f_tag = font(SANSB, 9)
    f_hhead = font(SANSB, 16)
    f_hsum = font(SANS, 10)
    f_src = font(SANS, 9)
    for i, (num, image, region, field, conf, head, summ, src) in enumerate(HEROES):
        x = MX + i * (col_w + 8)
        num_chip(d, x, hy, num)
        tag = f"{region} · {field}"
        d.text((x + 21, hy + 2), tag, font=f_tag, fill=GREY)
        chip(d, x + col_w - 62, hy + 1, conf, font(SANSB, 8),
             CONF_COLORS[conf])
        im = Image.open(os.path.join(ASSETS, image)).convert("RGB")
        img.paste(cover(im, col_w, 104), (x, hy + 20))
        lines = fit_check(d, head, f_hhead, col_w, 2, f"hero {num} head")
        yy = hy + 130
        for ln in lines:
            d.text((x, yy), ln, font=f_hhead, fill=INK)
            yy += 19
        lines = fit_check(d, summ, f_hsum, col_w, 3, f"hero {num} sum")
        yy += 3
        for ln in lines:
            d.text((x, yy), ln, font=f_hsum, fill=INK)
            yy += 13
        src_lines = wrap(d, src, f_src, col_w, 1)
        d.text((x, yy + 2), src_lines[0], font=f_src, fill=GREY)
    d.line([(MX, 424), (W - MX, 424)], fill=RULE, width=2)

    # ---- numbered: 4 cols x 3 rows
    ny = 432
    cell_w, cell_h = col_w, 78
    f_nhead = font(SANSB, 11)
    f_nsum = font(SANS, 9)
    f_ntag = font(SANSB, 8)
    for i, (num, image, region, field, conf, head, summ, src) in enumerate(NUMBERED):
        col, row = i % 4, i // 4
        x = MX + col * (col_w + 8)
        y = ny + row * (cell_h + 6)
        im = Image.open(os.path.join(ASSETS, image)).convert("RGB")
        img.paste(cover(im, 66, 58), (x, y + 8))
        num_chip(d, x, y + 8, num)
        tx = x + 72
        tw_text = col_w - 72
        tag = f"{region} · {field} · {conf}"
        d.text((tx, y), tag, font=f_ntag, fill=GREY)
        lines = fit_check(d, head, f_nhead, tw_text, 2, f"n{num} head")
        yy = y + 11
        for ln in lines:
            d.text((tx, yy), ln, font=f_nhead, fill=INK)
            yy += 13
        lines = fit_check(d, summ, f_nsum, tw_text, 2, f"n{num} sum")
        for ln in lines:
            d.text((tx, yy), ln, font=f_nsum, fill=INK)
            yy += 11
        d.text((tx, y + 66), src, font=f_ntag, fill=GREY)
    d.line([(MX, 682), (W - MX, 682)], fill=RULE, width=2)

    # ---- map (left) + ALSO (right)
    my = 690
    f_sec = font(SANSB, 12)
    d.text((MX, my), "WHERE IT HAPPENED — SCHEMATIC", font=f_sec, fill=INK)
    map_w, map_h = 324, 170
    draw_map(d, MX, my + 20, map_w, map_h)
    # pin legend, 4 columns
    f_leg = font(SANS, 8)
    leg_y = my + 194
    per_col = 4
    for ci in range(4):
        lx = MX + ci * 82
        for ri in range(per_col):
            idx = ci * per_col + ri
            if idx >= len(PINS):
                break
            n, lon, lat, place = PINS[idx]
            d.text((lx, leg_y + ri * 11), f"{n} {place}", font=f_leg, fill=INK)

    ax = MX + map_w + 12  # 348
    aw = W - MX - ax  # 664
    d.text((ax, my), "ALSO ON 21 NOVEMBER", font=f_sec, fill=INK)
    f_sub = font(SANSB, 10)
    f_item = font(SANS, 10)
    # split ALSO groups into two columns: col A = ME + Asia, col B = rest
    col_a = ALSO[0:2]
    col_b = ALSO[2:5]
    sub_w = (aw - 8) // 2  # 328
    for ci, groups in enumerate((col_a, col_b)):
        cx = ax + ci * (sub_w + 8)
        yy = my + 20
        for region, items in groups:
            d.text((cx, yy), region, font=f_sub, fill=RED)
            yy += 12
            for num, head, conf in items:
                line = f"{num}. {head} — {conf}"
                lines = wrap(d, line, f_item, sub_w, None)
                if len(lines) > 1:
                    print(f"OVERFLOW also {num}: {line[:60]}")
                d.text((cx, yy), lines[0], font=f_item, fill=INK)
                yy += 11
    d.line([(MX, 936), (W - MX, 936)], fill=RULE, width=2)

    # ---- bottom: DATE CHECK (left) + HOW SURE (right)
    by = 944
    f_bt = font(SANSB, 11)
    d.text((MX, by), "DATE CHECK — LEFT OUT ON PURPOSE", font=f_bt, fill=INK)
    f_dc = font(SANS, 10)
    dc_w = 660
    dc_col = dc_w // 2
    for i, item in enumerate(DATECHECK):
        cx = MX + (i // 4) * dc_col
        cy = by + 16 + (i % 4) * 11
        d.text((cx, cy), "· " + item, font=f_dc, fill=INK)
    hx = MX + dc_w + 12
    d.text((hx, by), "HOW SURE ARE WE?", font=f_bt, fill=INK)
    yy = by + 16
    f_hs = font(SANS, 9)
    for tag, expl in HOW_SURE:
        d.text((hx, yy), tag, font=font(SANSB, 9), fill=CONF_COLORS[tag])
        tw_tag = d.textlength(tag, font=font(SANSB, 9))
        d.text((hx + tw_tag + 4, yy), "— " + expl, font=f_hs, fill=INK)
        yy += 10
    # footer
    f_ft = font(SANS, 9)
    foot = ("SOURCES: Reuters · AP · AFP · BBC · The Guardian · The Hindu · "
            "Al Jazeera · Arab News · Kyodo · Xinhua · ABC · SBS · "
            "Iran International · World Watch · NASA · UKMTO")
    tw = d.textlength(foot, font=f_ft)
    d.text(((W - tw) / 2, 1014), foot, font=f_ft, fill=GREY)
    return img


if __name__ == "__main__":
    page = compose()
    page.save(os.path.join(BASE, "entry.png"), "JPEG", quality=88)
    print("wrote entry.png", page.size)
