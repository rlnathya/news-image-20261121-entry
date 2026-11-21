#!/usr/bin/env python3
"""Draw the front page for the make.fun news-image-20261121 entry.

A newspaper front page summing up Saturday 21 November 2026 in one image.
Deterministic: no timestamps, no randomness, no network, fixed fonts and
fixed layout, so the script always writes the same PNG bytes.

Usage: python3 render_frontpage.py [output-path]
Default output: entry.png next to this script.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
CW = W - 2 * MARGIN  # content width: 952

BLACK = (17, 17, 17)
RED = (192, 0, 0)
DARK_BLUE = (31, 58, 95)
GREY = (102, 102, 102)
LIGHT_GREY = (242, 242, 242)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
ORANGE = (230, 120, 0)
GOLD = (255, 180, 0)
SKY = (120, 170, 220)
SEA = (70, 120, 180)
NAVY = (10, 20, 50)

SERIF_BLACK = "/usr/share/fonts/truetype/noto/NotoSerif-Black.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def wrap(text, fnt, max_width):
    """Greedy word wrap. Returns a list of lines that fit max_width."""
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


def text_height(fnt):
    ascent, descent = fnt.getmetrics()
    return ascent + descent


def draw_centered(draw, cx, y, text, fnt, fill):
    w = fnt.getlength(text)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return text_height(fnt)


def draw_block(draw, x, y, lines, fnt, fill, leading):
    """Draw wrapped lines left-aligned. Returns the y after the block."""
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def rule(draw, x0, x1, y, weight=2, fill=BLACK):
    draw.rectangle([x0, y, x1, y + weight - 1], fill=fill)


# ---------------------------------------------------------------------------
# Small illustrations, drawn only with PIL shapes.
# Each takes the draw object and a box (x0, y0, x1, y1) to fill.
# ---------------------------------------------------------------------------

def art_missile(draw, x0, y0, x1, y1):
    """A cruise missile streaking down to an explosion over fields."""
    draw.rectangle([x0, y0, x1, y1], fill=(38, 48, 68))
    w = x1 - x0
    h = y1 - y0
    # ground: dark green strip at the bottom
    ground = y1 - h // 4
    draw.rectangle([x0, ground, x1, y1], fill=(52, 96, 52))
    # explosion burst over the ground, right of centre
    ex = x0 + int(w * 0.62)
    ey = ground - 6
    for r, col in ((34, (255, 200, 60)), (24, (255, 140, 30)),
                   (13, (255, 220, 120))):
        draw.ellipse([ex - r, ey - r, ex + r, ey + r], fill=col)
    # smoke puffs
    for sx, sy, r in ((ex - 34, ey - 26, 12), (ex + 30, ey - 34, 14),
                      (ex + 44, ey - 12, 9)):
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(150, 150, 150))
    # missile: grey body flying down-left to right, with a flame trail
    mx, my = x0 + int(w * 0.22), y0 + int(h * 0.22)
    draw.line([(mx - 46, my - 26), (mx, my)], fill=(255, 160, 40), width=4)
    draw.polygon([(mx, my), (mx + 26, my + 8), (mx + 4, my + 16)],
                 fill=(210, 210, 210))
    draw.polygon([(mx + 26, my + 8), (mx + 34, my + 10), (mx + 28, my + 16)],
                 fill=RED)
    draw.rectangle([mx + 2, my + 12, mx + 16, my + 20], fill=(120, 120, 120))
    # stars
    for sx, sy in ((x0 + 20, y0 + 14), (x0 + 70, y0 + 40),
                   (x1 - 30, y0 + 18), (x1 - 80, y0 + 52)):
        draw.ellipse([sx, sy, sx + 3, sy + 3], fill=WHITE)


def art_bridge(draw, x0, y0, x1, y1):
    """A suspension bridge over a river, smoke over one span."""
    draw.rectangle([x0, y0, x1, y1], fill=LIGHT_GREY)
    w = x1 - x0
    h = y1 - y0
    sea_top = y1 - max(8, h // 4)
    deck = sea_top - 4
    draw.rectangle([x0, sea_top, x1, y1], fill=SEA)
    t1 = x0 + w // 4
    t2 = x0 + 3 * w // 4
    top = y0 + 4
    for tx in (t1, t2):
        draw.rectangle([tx - 3, top, tx + 3, deck], fill=DARK_BLUE)
    pts = []
    for i in range(21):
        t = i / 20.0
        pts.append((int(t1 + t * (t2 - t1)),
                    int(top + 6 * 4 * t * (1 - t))))
    draw.line(pts, fill=DARK_BLUE, width=2)
    draw.rectangle([x0 + 4, deck, x1 - 4, deck + 3], fill=BLACK)
    # flame + smoke over the right span
    fx = x0 + int(w * 0.68)
    draw.polygon([(fx - 8, deck), (fx, deck - 14), (fx + 8, deck)],
                 fill=ORANGE)
    for sx, sy, r in ((fx - 5, y0 + 5, 5), (fx + 5, y0 + 2, 6)):
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(130, 130, 130))


def art_ship(draw, x0, y0, x1, y1):
    """A grey warship on the sea, a blockade line of small boats."""
    draw.rectangle([x0, y0, x1, y1], fill=LIGHT_GREY)
    w = x1 - x0
    h = y1 - y0
    sea_top = y1 - max(8, h // 3)
    draw.rectangle([x0, sea_top, x1, y1], fill=SEA)
    # waves
    for wx in range(x0 + 6, x1 - 6, 26):
        draw.arc([wx, sea_top + 4, wx + 22, sea_top + 14], 0, 180,
                 fill=WHITE, width=2)
    cx = x0 + w // 2
    deck = sea_top - 2
    # hull
    draw.polygon([(cx - 90, deck), (cx + 90, deck), (cx + 70, deck + 10),
                  (cx - 70, deck + 10)], fill=(90, 90, 90))
    # superstructure + mast + flag
    draw.rectangle([cx - 34, deck - 16, cx + 10, deck], fill=(120, 120, 120))
    draw.rectangle([cx - 4, deck - 28, cx, deck - 16], fill=(90, 90, 90))
    draw.rectangle([cx, deck - 28, cx + 18, deck - 20], fill=RED)
    # small escort boats
    for bx in (x0 + 26, x1 - 46):
        draw.polygon([(bx, sea_top + 2), (bx + 20, sea_top + 2),
                      (bx + 16, sea_top + 8), (bx + 4, sea_top + 8)],
                     fill=DARK_BLUE)


def art_cyclone(draw, x0, y0, x1, y1):
    """A cyclone spiral over the coast, with rain streaks."""
    draw.rectangle([x0, y0, x1, y1], fill=LIGHT_GREY)
    w = x1 - x0
    h = y1 - y0
    cx = x0 + int(w * 0.22)
    cy = (y0 + y1) // 2
    # spiral: three arcs, shrinking
    for r, col in ((18, DARK_BLUE), (13, (60, 110, 180)), (8, RED)):
        draw.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=col,
                 width=3)
    # rain streaks across the box
    for rx in range(x0 + int(w * 0.42), x1 - 4, 22):
        draw.line([(rx, y0 + 4), (rx - 8, y1 - 4)], fill=(60, 110, 180),
                  width=2)
    # coast label band: a small green strip at the bottom right
    draw.rectangle([x1 - 130, y1 - 10, x1, y1], fill=(52, 96, 52))


def art_chip(draw, x0, y0, x1, y1):
    """A processor chip with pins, and a bold 900K label."""
    draw.rectangle([x0, y0, x1, y1], fill=LIGHT_GREY)
    w = x1 - x0
    h = y1 - y0
    cx = x0 + 34
    cy = (y0 + y1) // 2
    # pins
    for i in range(3):
        py = cy - 12 + i * 12
        draw.rectangle([cx - 26, py, cx - 16, py + 3], fill=GOLD)
        draw.rectangle([cx + 16, py, cx + 26, py + 3], fill=GOLD)
    # chip body
    draw.rectangle([cx - 16, cy - 16, cx + 16, cy + 16], fill=BLACK)
    draw.rectangle([cx - 9, cy - 9, cx + 9, cy + 9], fill=DARK_BLUE)
    # label, vertically centred in the strip
    fnt = font(SANS_BOLD, 24)
    draw.text((x0 + 78, cy - 13), "900,000", font=fnt, fill=BLACK)


def art_voyager(draw, x0, y0, x1, y1):
    """Voyager 1 in deep space: gold dish, dark sky, Earth far below."""
    draw.rectangle([x0, y0, x1, y1], fill=NAVY)
    w = x1 - x0
    h = y1 - y0
    # stars
    for sx, sy, r in ((12, 10, 2), (44, 26, 1), (78, 8, 2), (104, 30, 1),
                      (28, 52, 1), (96, 58, 2), (60, 14, 1), (118, 70, 1)):
        draw.ellipse([x0 + sx - r, y0 + sy - r, x0 + sx + r, y0 + sy + r],
                     fill=WHITE)
    cx = x0 + w // 2
    cy = y0 + h // 2 - 4
    # dish (gold cone) + body + boom
    draw.polygon([(cx - 26, cy - 18), (cx + 26, cy - 18), (cx, cy + 2)],
                 fill=GOLD)
    draw.rectangle([cx - 12, cy + 2, cx + 12, cy + 14], fill=(200, 200, 200))
    draw.rectangle([cx + 12, cy + 6, cx + 34, cy + 9], fill=(160, 160, 160))
    draw.ellipse([cx + 34, cy + 3, cx + 40, cy + 12], fill=RED)
    # Earth, small and far away at the bottom left
    draw.ellipse([x0 + 8, y1 - 22, x0 + 26, y1 - 4], fill=SEA)
    draw.arc([x0 + 10, y1 - 20, x0 + 24, y1 - 6], 200, 340, fill=GREEN,
             width=2)


ART = {
    "missile": art_missile,
    "bridge": art_bridge,
    "ship": art_ship,
    "cyclone": art_cyclone,
    "chip": art_chip,
    "voyager": art_voyager,
}

# ---------------------------------------------------------------------------
# Stories. Wording verified against reporting of 20-21 November 2026:
# Russian Kh-101 cruise missile + two more objects land in south-east
# Poland near the Coalition of the Willing exercise (Tusk: deliberate
# provocation; NATO's Rutte: grave violation; jets scrambled; nobody hurt);
# Russia's overnight assault on Ukraine: 400+ drones, 110+ missiles, three
# Kyiv bridges damaged, at least 9 killed; Kryvyi Rih double-tap strike
# kills a boy aged 7 and a paramedic, 42 hurt; Trump says a decision on new
# Iran strikes can wait until next year, naval blockade goes on, Qatar
# talks stalled; Cyclone Akvan crosses near Gopalpur, Odisha, gusts to
# 90 km/h, 300,000+ evacuated; House panel discloses 879,000 Nvidia/AMD AI
# chip approvals for China, Dec 2025-May 2026; Voyager 1 reaches one
# light-day from Earth after 49 years in flight.
# ---------------------------------------------------------------------------

LEAD = {
    "kicker": "POLAND  •  NATO",
    "headline": "RUSSIAN MISSILE LANDS IN POLAND",
    "subhead": ("A Russian missile crashes in Poland near allied drills. "
                "Tusk calls it a provocation; NATO jets scramble."),
    "art": "missile",
}

BODY = [
    {
        "kicker": "KYIV  •  WAR",
        "headline": "RUSSIA'S BIGGEST AIR ASSAULT HITS KYIV",
        "subhead": ("400 drones and 110 missiles hit three Kyiv bridges; "
                    "at least 9 killed. A double-tap strike in Kryvyi Rih "
                    "kills a boy, 7, and a paramedic; 42 hurt."),
        "art": "bridge",
    },
    {
        "kicker": "WASHINGTON  •  IRAN",
        "headline": "TRUMP: NO RUSH ON NEW IRAN STRIKES",
        "subhead": ("The president says a decision on more strikes can "
                    "wait until next year, as the US naval blockade goes "
                    "on and Qatar-mediated talks stall."),
        "art": "ship",
    },
    {
        "kicker": "ODISHA  •  WEATHER",
        "headline": "CYCLONE AKVAN SLAMS INDIA'S EAST COAST",
        "subhead": ("The storm crosses near Gopalpur with gusts to 90 "
                    "km/h. More than 300,000 people are evacuated to "
                    "shelters; no deaths reported yet."),
        "art": "cyclone",
    },
    {
        "kicker": "WASHINGTON  •  TECHNOLOGY",
        "headline": "US LET 900,000 AI CHIPS GO TO CHINA",
        "subhead": ("A House panel discloses approvals for Nvidia and AMD "
                    "chips from Dec 2025 to May 2026 — 150,000 for "
                    "Tencent, 75,000 for Alibaba."),
        "art": "chip",
    },
]

CLOSER = {
    "kicker": "SPACE  •  NASA",
    "headline": "VOYAGER 1, ONE LIGHT-DAY AWAY",
    "subhead": ("After 49 years in flight, the probe is the first "
                "human-made object a full day away by light. A signal now "
                "takes 24 hours to reach it."),
    "art": "voyager",
}

TICKER_LINES = [
    "Estonia to shut road borders with Russia  •  Sweden summons envoy "
    "after blast near Kyiv embassy",
    "Ukraine fields laser air defence in Kyiv  •  UNICEF: 1,144 children "
    "killed or injured in Ukraine this year",
]


def render():
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    y = 14
    # ---- Masthead ----
    rule(draw, MARGIN, W - MARGIN, y, 3)
    y += 6
    mast_fnt = font(SERIF_BLACK, 84)
    draw_centered(draw, W // 2, y, "THE WORLD", mast_fnt, BLACK)
    y += text_height(mast_fnt) + 2
    rule(draw, MARGIN, W - MARGIN, y, 2)
    y += 6
    # ---- Dateline: the day must be unmistakable ----
    date_fnt = font(SANS_BOLD, 36)
    draw_centered(draw, W // 2, y, "SATURDAY, 21 NOVEMBER 2026", date_fnt,
                  RED)
    y += text_height(date_fnt) + 6
    rule(draw, MARGIN, W - MARGIN, y, 4)
    y += 10

    # ---- Lead story (full width, art on the right) ----
    lead_top = y
    art_w = 300
    art_x0 = W - MARGIN - art_w
    text_w = art_x0 - 24 - MARGIN
    kicker_fnt = font(SANS_BOLD, 18)
    head_fnt = font(SERIF_BOLD, 44)
    sub_fnt = font(SANS, 21)
    draw.text((MARGIN, lead_top), LEAD["kicker"], font=kicker_fnt, fill=RED)
    hy = lead_top + 24
    head_lines = wrap(LEAD["headline"], head_fnt, text_w)
    hy = draw_block(draw, MARGIN, hy, head_lines, head_fnt, BLACK, 48)
    sub_lines = wrap(LEAD["subhead"], sub_fnt, text_w)
    sy = hy + 6
    sy = draw_block(draw, MARGIN, sy, sub_lines, sub_fnt, BLACK, 25)
    content_h = sy - lead_top
    art_h = max(content_h, 150)
    ART[LEAD["art"]](draw, art_x0, lead_top, W - MARGIN, lead_top + art_h)
    y = lead_top + max(art_h, content_h) + 10
    rule(draw, MARGIN, W - MARGIN, y, 2)
    y += 6

    # ---- Body stories: two columns, two rows.
    # Each cell's height is measured from its own wrapped text, so no
    # divider ever crosses a line of text.
    col_w = (CW - 24) // 2
    for row in range(2):
        row_top = y
        row_bottom = row_top
        for col in range(2):
            story = BODY[row * 2 + col]
            x0 = MARGIN + col * (col_w + 24)
            cy = row_top
            ART[story["art"]](draw, x0, cy, x0 + col_w, cy + 40)
            cy += 40 + 5
            kf = font(SANS_BOLD, 16)
            draw.text((x0, cy), story["kicker"], font=kf, fill=RED)
            cy += 20
            hf = font(SERIF_BOLD, 31)
            lines = wrap(story["headline"], hf, col_w)
            cy = draw_block(draw, x0, cy, lines, hf, BLACK, 36)
            cy += 3
            sf = font(SANS, 18)
            slines = wrap(story["subhead"], sf, col_w)
            cy = draw_block(draw, x0, cy, slines, sf, BLACK, 21)
            row_bottom = max(row_bottom, cy)
        y = row_bottom + 10
        rule(draw, MARGIN, W - MARGIN, y, 2)
        y += 6

    # ---- Closer story (full width, art on the left) ----
    closer_top = y
    art_w2 = 130
    ART[CLOSER["art"]](draw, MARGIN, closer_top, MARGIN + art_w2,
                       closer_top + 100)
    tx = MARGIN + art_w2 + 20
    tw = W - MARGIN - tx
    kf = font(SANS_BOLD, 16)
    draw.text((tx, closer_top), CLOSER["kicker"], font=kf, fill=RED)
    cy = closer_top + 20
    hf = font(SERIF_BOLD, 36)
    lines = wrap(CLOSER["headline"], hf, tw)
    cy = draw_block(draw, tx, cy, lines, hf, BLACK, 42)
    cy += 2
    sf = font(SANS, 19)
    slines = wrap(CLOSER["subhead"], sf, tw)
    cy = draw_block(draw, tx, cy, slines, sf, BLACK, 23)
    y = max(closer_top + 100, cy) + 10
    rule(draw, MARGIN, W - MARGIN, y, 2)
    y += 6

    # ---- Bottom ticker ----
    ticker_h = 42
    assert y + ticker_h <= H - 8, "layout overflow: ticker ends at %d" % (
        y + ticker_h)
    draw.rectangle([MARGIN, y, W - MARGIN, y + ticker_h], fill=RED)
    tf = font(SANS_BOLD, 17)
    ty = y + 3
    for line in TICKER_LINES:
        twd = tf.getlength(line)
        draw.text((W // 2 - twd / 2, ty), line, font=tf, fill=WHITE)
        ty += 19

    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = render()
    img.save(out, format="PNG")
    print("wrote", out, img.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
