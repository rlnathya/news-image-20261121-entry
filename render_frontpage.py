#!/usr/bin/env python3
"""Render the front page for the make.fun news-image-20261121 entry.

One image summing up Saturday 21 November 2026 as a newspaper front page.
Fully deterministic: no timestamps, no randomness, no network access, and
fixed fonts with a fixed layout, so every run writes identical PNG bytes.

Usage: python3 render_frontpage.py [output-path]
Without an argument, the output is entry.png next to this script.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

PAGE_W, PAGE_H = 1024, 1024
EDGE = 36
CONTENT_W = PAGE_W - 2 * EDGE  # content width: 952

INK = (17, 17, 17)
RED = (192, 0, 0)
DEEP_BLUE = (31, 58, 95)
GREY = (102, 102, 102)
PALE = (242, 242, 242)
PAPER = (255, 255, 255)
LEAF = (0, 128, 0)
EMBER = (230, 120, 0)
GOLD = (255, 180, 0)
SKY = (120, 170, 220)
SEA = (70, 120, 180)
NAVY = (10, 20, 50)

SERIF_HEAVY = "/usr/share/fonts/truetype/noto/NotoSerif-Black.ttf"
SERIF_STRONG = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SANS_HEAVY = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
SANS_PLAIN = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"

_font_store = {}


def load_font(path, size):
    key = (path, size)
    if key not in _font_store:
        _font_store[key] = ImageFont.truetype(path, size)
    return _font_store[key]


def wrap_words(text, fnt, max_width):
    """Greedy word wrap. Returns the lines that fit inside max_width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if fnt.getlength(trial) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def line_height(fnt):
    ascent, descent = fnt.getmetrics()
    return ascent + descent


def draw_centred(draw, cx, y, text, fnt, fill):
    width = fnt.getlength(text)
    draw.text((cx - width / 2, y), text, font=fnt, fill=fill)
    return line_height(fnt)


def draw_lines(draw, x, y, lines, fnt, fill, leading):
    """Draw wrapped lines left-aligned. Returns the y below the block."""
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def hrule(draw, x0, x1, y, weight=2, fill=INK):
    draw.rectangle([x0, y, x1, y + weight - 1], fill=fill)


# ---------------------------------------------------------------------------
# Small illustrations, drawn with PIL shapes only.
# Each one takes the draw object and a box (x0, y0, x1, y1) to fill.
# ---------------------------------------------------------------------------

def pic_missile(draw, x0, y0, x1, y1):
    """A cruise missile streaking down to an explosion over fields."""
    draw.rectangle([x0, y0, x1, y1], fill=(38, 48, 68))
    bw = x1 - x0
    bh = y1 - y0
    # ground: a dark green strip along the bottom
    ground_y = y1 - bh // 4
    draw.rectangle([x0, ground_y, x1, y1], fill=(52, 96, 52))
    # explosion burst above the ground, right of centre
    bx = x0 + int(bw * 0.62)
    by = ground_y - 6
    for radius, colour in (
            (34, (255, 200, 60)),
            (24, (255, 140, 30)),
            (13, (255, 220, 120))):
        draw.ellipse(
            [bx - radius, by - radius, bx + radius, by + radius],
            fill=colour)
    # smoke puffs
    for px, py, radius in (
            (bx - 34, by - 26, 12),
            (bx + 30, by - 34, 14),
            (bx + 44, by - 12, 9)):
        draw.ellipse(
            [px - radius, py - radius, px + radius, py + radius],
            fill=(150, 150, 150))
    # missile: grey body flying down-left to right, with a flame trail
    tip_x = x0 + int(bw * 0.22)
    tip_y = y0 + int(bh * 0.22)
    draw.line(
        [(tip_x - 46, tip_y - 26), (tip_x, tip_y)],
        fill=(255, 160, 40), width=4)
    draw.polygon(
        [(tip_x, tip_y), (tip_x + 26, tip_y + 8), (tip_x + 4, tip_y + 16)],
        fill=(210, 210, 210))
    draw.polygon(
        [(tip_x + 26, tip_y + 8), (tip_x + 34, tip_y + 10),
         (tip_x + 28, tip_y + 16)],
        fill=RED)
    draw.rectangle(
        [tip_x + 2, tip_y + 12, tip_x + 16, tip_y + 20],
        fill=(120, 120, 120))
    # stars
    for px, py in (
            (x0 + 20, y0 + 14), (x0 + 70, y0 + 40),
            (x1 - 30, y0 + 18), (x1 - 80, y0 + 52)):
        draw.ellipse([px, py, px + 3, py + 3], fill=PAPER)


def pic_bridge(draw, x0, y0, x1, y1):
    """A suspension bridge over a river, smoke over one span."""
    draw.rectangle([x0, y0, x1, y1], fill=PALE)
    bw = x1 - x0
    bh = y1 - y0
    water_top = y1 - max(8, bh // 4)
    deck_y = water_top - 4
    draw.rectangle([x0, water_top, x1, y1], fill=SEA)
    post_a = x0 + bw // 4
    post_b = x0 + 3 * bw // 4
    tower_top = y0 + 4
    for post_x in (post_a, post_b):
        draw.rectangle(
            [post_x - 3, tower_top, post_x + 3, deck_y], fill=DEEP_BLUE)
    cable = []
    for i in range(21):
        t = i / 20.0
        cable.append((
            int(post_a + t * (post_b - post_a)),
            int(tower_top + 6 * 4 * t * (1 - t))))
    draw.line(cable, fill=DEEP_BLUE, width=2)
    draw.rectangle([x0 + 4, deck_y, x1 - 4, deck_y + 3], fill=INK)
    # flame + smoke over the right span
    flame_x = x0 + int(bw * 0.68)
    draw.polygon(
        [(flame_x - 8, deck_y), (flame_x, deck_y - 14),
         (flame_x + 8, deck_y)],
        fill=EMBER)
    for px, py, radius in (
            (flame_x - 5, y0 + 5, 5), (flame_x + 5, y0 + 2, 6)):
        draw.ellipse(
            [px - radius, py - radius, px + radius, py + radius],
            fill=(130, 130, 130))


def pic_ship(draw, x0, y0, x1, y1):
    """A grey warship on the sea, a blockade line of small boats."""
    draw.rectangle([x0, y0, x1, y1], fill=PALE)
    bw = x1 - x0
    bh = y1 - y0
    water_top = y1 - max(8, bh // 3)
    draw.rectangle([x0, water_top, x1, y1], fill=SEA)
    # waves
    for wave_x in range(x0 + 6, x1 - 6, 26):
        draw.arc(
            [wave_x, water_top + 4, wave_x + 22, water_top + 14],
            0, 180, fill=PAPER, width=2)
    centre_x = x0 + bw // 2
    deck_y = water_top - 2
    # hull
    draw.polygon(
        [(centre_x - 90, deck_y), (centre_x + 90, deck_y),
         (centre_x + 70, deck_y + 10), (centre_x - 70, deck_y + 10)],
        fill=(90, 90, 90))
    # superstructure + mast + flag
    draw.rectangle(
        [centre_x - 34, deck_y - 16, centre_x + 10, deck_y],
        fill=(120, 120, 120))
    draw.rectangle(
        [centre_x - 4, deck_y - 28, centre_x, deck_y - 16],
        fill=(90, 90, 90))
    draw.rectangle(
        [centre_x, deck_y - 28, centre_x + 18, deck_y - 20], fill=RED)
    # small escort boats
    for boat_x in (x0 + 26, x1 - 46):
        draw.polygon(
            [(boat_x, water_top + 2), (boat_x + 20, water_top + 2),
             (boat_x + 16, water_top + 8), (boat_x + 4, water_top + 8)],
            fill=DEEP_BLUE)


def pic_cyclone(draw, x0, y0, x1, y1):
    """A cyclone spiral over the coast, with rain streaks."""
    draw.rectangle([x0, y0, x1, y1], fill=PALE)
    bw = x1 - x0
    bh = y1 - y0
    centre_x = x0 + int(bw * 0.22)
    centre_y = (y0 + y1) // 2
    # spiral: three arcs, shrinking
    for radius, colour in (
            (18, DEEP_BLUE), (13, (60, 110, 180)), (8, RED)):
        draw.arc(
            [centre_x - radius, centre_y - radius,
             centre_x + radius, centre_y + radius],
            20, 300, fill=colour, width=3)
    # rain streaks across the box
    for rain_x in range(x0 + int(bw * 0.42), x1 - 4, 22):
        draw.line(
            [(rain_x, y0 + 4), (rain_x - 8, y1 - 4)],
            fill=(60, 110, 180), width=2)
    # coast label band: a small green strip at the bottom right
    draw.rectangle([x1 - 130, y1 - 10, x1, y1], fill=(52, 96, 52))


def pic_chip(draw, x0, y0, x1, y1):
    """A processor chip with pins, and a bold 900K label."""
    draw.rectangle([x0, y0, x1, y1], fill=PALE)
    bw = x1 - x0
    bh = y1 - y0
    centre_x = x0 + 34
    centre_y = (y0 + y1) // 2
    # pins
    for i in range(3):
        pin_y = centre_y - 12 + i * 12
        draw.rectangle(
            [centre_x - 26, pin_y, centre_x - 16, pin_y + 3], fill=GOLD)
        draw.rectangle(
            [centre_x + 16, pin_y, centre_x + 26, pin_y + 3], fill=GOLD)
    # chip body
    draw.rectangle(
        [centre_x - 16, centre_y - 16, centre_x + 16, centre_y + 16],
        fill=INK)
    draw.rectangle(
        [centre_x - 9, centre_y - 9, centre_x + 9, centre_y + 9],
        fill=DEEP_BLUE)
    # label, vertically centred in the strip
    label_font = load_font(SANS_HEAVY, 24)
    draw.text(
        (x0 + 78, centre_y - 13), "900,000",
        font=label_font, fill=INK)


def pic_voyager(draw, x0, y0, x1, y1):
    """Voyager 1 in deep space: gold dish, dark sky, Earth far below."""
    draw.rectangle([x0, y0, x1, y1], fill=NAVY)
    bw = x1 - x0
    bh = y1 - y0
    # stars
    for px, py, radius in (
            (12, 10, 2), (44, 26, 1), (78, 8, 2), (104, 30, 1),
            (28, 52, 1), (96, 58, 2), (60, 14, 1), (118, 70, 1)):
        draw.ellipse(
            [x0 + px - radius, y0 + py - radius,
             x0 + px + radius, y0 + py + radius],
            fill=PAPER)
    centre_x = x0 + bw // 2
    centre_y = y0 + bh // 2 - 4
    # dish (gold cone) + body + boom
    draw.polygon(
        [(centre_x - 26, centre_y - 18), (centre_x + 26, centre_y - 18),
         (centre_x, centre_y + 2)],
        fill=GOLD)
    draw.rectangle(
        [centre_x - 12, centre_y + 2, centre_x + 12, centre_y + 14],
        fill=(200, 200, 200))
    draw.rectangle(
        [centre_x + 12, centre_y + 6, centre_x + 34, centre_y + 9],
        fill=(160, 160, 160))
    draw.ellipse(
        [centre_x + 34, centre_y + 3, centre_x + 40, centre_y + 12],
        fill=RED)
    # Earth, small and far away at the bottom left
    draw.ellipse([x0 + 8, y1 - 22, x0 + 26, y1 - 4], fill=SEA)
    draw.arc(
        [x0 + 10, y1 - 20, x0 + 24, y1 - 6], 200, 340, fill=LEAF, width=2)


PICTURES = {
    "missile": pic_missile,
    "bridge": pic_bridge,
    "ship": pic_ship,
    "cyclone": pic_cyclone,
    "chip": pic_chip,
    "voyager": pic_voyager,
}

# ---------------------------------------------------------------------------
# Stories. Wording checked against reporting of 20-21 November 2026:
# a Russian Kh-101 cruise missile and two more objects come down in
# south-east Poland near the Coalition of the Willing exercise (Tusk calls
# it a deliberate provocation; NATO's Rutte calls it a grave violation;
# jets are scrambled; nobody is hurt); Russia's overnight assault on
# Ukraine: 400+ drones, 110+ missiles, three Kyiv bridges damaged, at
# least 9 killed; a Kryvyi Rih double-tap strike kills a boy aged 7 and a
# paramedic, 42 hurt; Trump says a decision on new Iran strikes can wait
# until next year while the naval blockade continues and Qatar talks are
# stalled; Cyclone Akvan crosses near Gopalpur, Odisha, with gusts to
# 90 km/h and 300,000+ evacuated; a House panel discloses 879,000
# Nvidia/AMD AI chip approvals for China, Dec 2025-May 2026; Voyager 1
# reaches one light-day from Earth after 49 years in flight.
# ---------------------------------------------------------------------------

LEAD_STORY = {
    "kicker": ("POLAND  •  " "NATO"),
    "headline": ("RUSSIAN MISSILE LANDS " "IN POLAND"),
    "subhead": ("A Russian missile crashes in Poland near allied "
                "drills. Tusk calls it a provocation; NATO jets scramble."),
    "art": "missile",
}

STORIES = [
    {
        "kicker": ("KYIV  •  " "WAR"),
        "headline": ("RUSSIA'S BIGGEST AIR " "ASSAULT HITS KYIV"),
        "subhead": ("400 drones and 110 missiles hit three Kyiv "
                    "bridges; at least 9 killed. A double-tap strike "
                    "in Kryvyi Rih kills a boy, 7, and a paramedic; 42 hurt."),
        "art": "bridge",
    },
    {
        "kicker": ("WASHINGTON  •  " "IRAN"),
        "headline": ("TRUMP: NO RUSH " "ON NEW IRAN STRIKES"),
        "subhead": ("The president says a decision on more strikes "
                    "can wait until next year, as the US naval "
                    "blockade goes on and Qatar-mediated talks stall."),
        "art": "ship",
    },
    {
        "kicker": ("ODISHA  •  " "WEATHER"),
        "headline": ("CYCLONE AKVAN SLAMS " "INDIA'S EAST COAST"),
        "subhead": ("The storm crosses near Gopalpur with gusts "
                    "to 90 km/h. More than 300,000 people are "
                    "evacuated to shelters; no deaths reported yet."),
        "art": "cyclone",
    },
    {
        "kicker": ("WASHINGTON  •  " "TECHNOLOGY"),
        "headline": ("US LET 900,000 AI " "CHIPS GO TO CHINA"),
        "subhead": ("A House panel discloses approvals for Nvidia "
                    "and AMD chips from Dec 2025 to May 2026 — "
                    "150,000 for Tencent, 75,000 for Alibaba."),
        "art": "chip",
    },
]

CLOSER_STORY = {
    "kicker": ("SPACE  •  " "NASA"),
    "headline": ("VOYAGER 1, ONE " "LIGHT-DAY AWAY"),
    "subhead": ("After 49 years in flight, the probe is the "
                "first human-made object a full day away by light. "
                "A signal now takes 24 hours to reach it."),
    "art": "voyager",
}

TICKER = [
    "Estonia to shut road borders with Russia  •  "
    "Sweden summons envoy after blast near Kyiv embassy",
    "Ukraine fields laser air defence in Kyiv  •  UNICEF: "
    "1,144 children killed or injured in Ukraine this year",
]


def build_front_page():
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    draw = ImageDraw.Draw(img)

    y = 14
    # ---- Masthead ----
    hrule(draw, EDGE, PAGE_W - EDGE, y, 3)
    y += 6
    mast_font = load_font(SERIF_HEAVY, 84)
    draw_centred(draw, PAGE_W // 2, y, "THE WORLD", mast_font, INK)
    y += line_height(mast_font) + 2
    hrule(draw, EDGE, PAGE_W - EDGE, y, 2)
    y += 6
    # ---- Dateline: the day must be unmistakable ----
    date_font = load_font(SANS_HEAVY, 36)
    draw_centred(
        draw, PAGE_W // 2, y, "SATURDAY, 21 NOVEMBER 2026", date_font, RED)
    y += line_height(date_font) + 6
    hrule(draw, EDGE, PAGE_W - EDGE, y, 4)
    y += 10

    # ---- Lead story (full width, art on the right) ----
    lead_top = y
    art_width = 300
    art_x0 = PAGE_W - EDGE - art_width
    text_width = art_x0 - 24 - EDGE
    kick_font = load_font(SANS_HEAVY, 18)
    head_font = load_font(SERIF_STRONG, 44)
    sub_font = load_font(SANS_PLAIN, 21)
    draw.text(
        (EDGE, lead_top), LEAD_STORY["kicker"], font=kick_font, fill=RED)
    head_y = lead_top + 24
    head_lines = wrap_words(
        LEAD_STORY["headline"], head_font, text_width)
    head_y = draw_lines(
        draw, EDGE, head_y, head_lines, head_font, INK, 48)
    sub_lines = wrap_words(LEAD_STORY["subhead"], sub_font, text_width)
    sub_y = head_y + 6
    sub_y = draw_lines(draw, EDGE, sub_y, sub_lines, sub_font, INK, 25)
    text_h = sub_y - lead_top
    art_h = max(text_h, 150)
    PICTURES[LEAD_STORY["art"]](
        draw, art_x0, lead_top, PAGE_W - EDGE, lead_top + art_h)
    y = lead_top + max(art_h, text_h) + 10
    hrule(draw, EDGE, PAGE_W - EDGE, y, 2)
    y += 6

    # ---- Body stories: two columns, two rows.
    # Each cell's height is measured from its own wrapped text, so no
    # divider ever crosses a line of text.
    cell_w = (CONTENT_W - 24) // 2
    for row in range(2):
        row_top = y
        row_bottom = row_top
        for col in range(2):
            story = STORIES[row * 2 + col]
            left = EDGE + col * (cell_w + 24)
            yy = row_top
            PICTURES[story["art"]](draw, left, yy, left + cell_w, yy + 40)
            yy += 40 + 5
            kf = load_font(SANS_HEAVY, 16)
            draw.text((left, yy), story["kicker"], font=kf, fill=RED)
            yy += 20
            hf = load_font(SERIF_STRONG, 31)
            lines = wrap_words(story["headline"], hf, cell_w)
            yy = draw_lines(draw, left, yy, lines, hf, INK, 36)
            yy += 3
            sf = load_font(SANS_PLAIN, 18)
            slines = wrap_words(story["subhead"], sf, cell_w)
            yy = draw_lines(draw, left, yy, slines, sf, INK, 21)
            row_bottom = max(row_bottom, yy)
        y = row_bottom + 10
        hrule(draw, EDGE, PAGE_W - EDGE, y, 2)
        y += 6

    # ---- Closer story (full width, art on the left) ----
    closer_top = y
    art_w2 = 130
    PICTURES[CLOSER_STORY["art"]](
        draw, EDGE, closer_top, EDGE + art_w2, closer_top + 100)
    tx = EDGE + art_w2 + 20
    tw = PAGE_W - EDGE - tx
    kf = load_font(SANS_HEAVY, 16)
    draw.text((tx, closer_top), CLOSER_STORY["kicker"], font=kf, fill=RED)
    cy = closer_top + 20
    hf = load_font(SERIF_STRONG, 36)
    lines = wrap_words(CLOSER_STORY["headline"], hf, tw)
    cy = draw_lines(draw, tx, cy, lines, hf, INK, 42)
    cy += 2
    sf = load_font(SANS_PLAIN, 19)
    slines = wrap_words(CLOSER_STORY["subhead"], sf, tw)
    cy = draw_lines(draw, tx, cy, slines, sf, INK, 23)
    y = max(closer_top + 100, cy) + 10
    hrule(draw, EDGE, PAGE_W - EDGE, y, 2)
    y += 6

    # ---- Bottom ticker ----
    ticker_h = 42
    assert y + ticker_h <= PAGE_H - 8, (
        "layout overflow: ticker ends at %d" % (y + ticker_h))
    draw.rectangle(
        [EDGE, y, PAGE_W - EDGE, y + ticker_h], fill=RED)
    tf = load_font(SANS_HEAVY, 17)
    ty = y + 3
    for line in TICKER:
        twd = tf.getlength(line)
        draw.text((PAGE_W // 2 - twd / 2, ty), line, font=tf, fill=PAPER)
        ty += 19

    return img


def run():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = build_front_page()
    img.save(out, format="PNG")
    print("wrote", out, img.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    run()
