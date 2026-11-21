#!/usr/bin/env python3
"""Build the 21 November 2026 world-news front page (1024x1024).

Build-time tool only. Pillow runs on this machine; the graded entry is
the composed JPEG that main.py copies to /output, the pattern the kit
starter uses.

Page plan, 1024x1024:
  masthead  0..116   kicker + date
  hero      118..430 the day's lead story
  row 1     430..700 three stories
  row 2     700..946 three stories
  ticker    946..1024 one more angle from the day

Variant A leads with the Strait of Hormuz standoff. Variant B leads
with the Shenzhen peace declaration. The other six panels are the same
in both; only the hero slot and the Hormuz/Shenzhen slots swap.

Type is drawn with PIL, never baked into the photos, so no letter
comes out garbled. Each photo keeps its own light and colour: the
Hormuz hero is hazy dusk, the court is pale wood and daylight, Poland
is cold grey, Shenzhen is bright indoors, the Red Sea is clear blue,
the data-centre platform is overcast grey-blue, Odisha is wet monsoon
grey-green. The scrim under the type is a moderate bottom gradient;
it deepens only where the words sit.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

INK = (9, 20, 32)
GOLD = (255, 179, 0)
WHITE = (255, 255, 255)
PALE = (226, 232, 238)


def load_font(path, size):
    return ImageFont.truetype(path, size)


def fit(im, tw, th, fx=0.5, fy=0.5):
    """Scale the photo so it covers tw x th, then crop to the focus."""
    sw, sh = im.size
    scale = max(tw / sw, th / sh)
    im = im.resize((round(sw * scale), round(sh * scale)), Image.LANCZOS)
    ox = round((im.width - tw) * fx) if im.width > tw else 0
    oy = round((im.height - th) * fy) if im.height > th else 0
    return im.crop((ox, oy, ox + tw, oy + th))


def shade(page, box, top_alpha=0, bottom_alpha=185):
    """A black gradient over the lower half of a panel, for the type."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for i in range(h):
        t = i / max(h - 1, 1)
        a = int(top_alpha + (bottom_alpha - top_alpha) * t ** 1.7)
        ld.line([(0, i), (w, i)], fill=(0, 0, 0, a))
    page.paste(layer, (x0, y0), layer)


def lines_for(draw, text, fnt, max_w):
    """Greedy wrap of text to a pixel width."""
    out, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def story(page, photo, box, tag, head, sub, head_px=22, sub_px=17,
          fy=0.5, fx=0.5, head_max=3):
    x0, y0, x1, y1 = box
    tw, th = x1 - x0, y1 - y0
    im = Image.open(photo).convert("RGB")
    page.paste(fit(im, tw, th, fx, fy), (x0, y0))
    shade(page, (x0, y0 + th // 2, x1, y1))
    d = ImageDraw.Draw(page)
    pad = 16
    tx = x0 + pad
    sub_f = load_font(SANS, sub_px)
    sub_lines = lines_for(d, sub, sub_f, tw - 2 * pad)
    sub_h = len(sub_lines) * (sub_px + 5)
    head_f = load_font(SANS_B, head_px)
    head_lines = lines_for(d, head, head_f, tw - 2 * pad)[:head_max]
    head_h = len(head_lines) * (head_px + 4)
    tag_f = load_font(SANS_B, 16)
    ty = y1 - pad - sub_h - head_h - 26
    tag_w = d.textlength(tag, font=tag_f)
    chip = Image.new("RGBA", (int(tag_w) + 16, 26), (9, 20, 32, 205))
    page.paste(chip, (tx - 8, ty - 3), chip)
    d = ImageDraw.Draw(page)
    d.text((tx, ty), tag, font=tag_f, fill=GOLD)
    hy = ty + 26
    for ln in head_lines:
        d.text((tx, hy), ln, font=head_f, fill=WHITE,
               stroke_width=1, stroke_fill=(0, 0, 0))
        hy += head_px + 4
    sy = hy + 2
    for ln in sub_lines:
        d.text((tx, sy), ln, font=sub_f, fill=PALE,
               stroke_width=1, stroke_fill=(0, 0, 0))
        sy += sub_px + 5


HORMUZ = dict(
    photo="media-generation-panel-hero-hormuz-0-a6104054-013e-427c-98cd-8470dcc1db52.webp",
    tag="STRAIT OF HORMUZ",
    head="TRUMP HOLDS OFF STRIKING IRAN AS TANKERS TEST THE BLOCKADE",
    sub=("Washington puts the decision off until the new year. Iran "
         "readies a tanker convoy from Kharg Island to run the US naval "
         "blockade, and its oil income is forecast to reach zero by "
         "mid-December."),
)
HORMUZ_SMALL = dict(
    photo=HORMUZ["photo"],
    tag="STRAIT OF HORMUZ",
    head="TRUMP HOLDS OFF STRIKING IRAN",
    sub=("Iran readies a tanker convoy from Kharg Island. Its oil "
         "income is forecast to reach zero by mid-December."),
)
SHENZHEN = dict(
    photo="media-generation-panel-shenzhen-v2-0-0585998e-f66b-4f81-a120-be5402693e2c.webp",
    tag="SHENZHEN",
    head="TRUMP, XI AND PUTIN: NUCLEAR CONFLICT MUST NEVER HAPPEN",
    sub=("The three leaders sign the Shenzhen Peace Declaration, the "
         "headline of the day's live coverage."),
)
SHENZHEN_SMALL = dict(
    photo=SHENZHEN["photo"],
    tag="SHENZHEN",
    head="TRUMP, XI AND PUTIN SIGN PEACE DECLARATION",
    sub='"Nuclear conflict must never happen," the three leaders agree.',
)
ICJ = dict(
    photo="media-generation-panel-icj-0-7722693b-7086-4d2d-aaaa-4c5e6007f236.webp",
    tag="THE HAGUE",
    head="WORLD COURT FINDS MYANMAR GUILTY OF GENOCIDE AGAINST THE ROHINGYA",
    sub=("The first time the court holds a state responsible for "
         "genocide. Myanmar must investigate those responsible and "
         "allow safe return."),
)
POLAND = dict(
    photo="media-generation-panel-poland-0-6ac85fd2-42bc-4565-a889-46f6e0c55d36.webp",
    tag="LUBLIN, POLAND",
    head="RUSSIAN MISSILE LANDS IN POLISH VILLAGE",
    sub="Warsaw calls it a provocation. No one is hurt.",
)
HOUTHI = dict(
    photo="media-generation-panel-houthi-0-d19d7174-3afb-43cc-9ee4-0ce960d43edf.webp",
    tag="RED SEA",
    head="SAUDI-LED COALITION SHOOTS DOWN HOUTHI MISSILE",
    sub="Reported in Al Jazeera's live coverage of the Iran war.",
)
DATACENTRE = dict(
    photo="media-generation-panel-datacentre-0-942a534c-f0f2-46e3-8d66-60deee9b30a2.webp",
    tag="WASHINGTON",
    head="TRUMP EYES DATA CENTRES OFFSHORE",
    sub="The president targets floating data centres off the US coast.",
)
CYCLONE = dict(
    photo="media-generation-panel-cyclone-v2-0-04a29929-1a63-4105-b531-7f4955dc8705.webp",
    tag="ODISHA, INDIA",
    head="CYCLONE AKVAN WEAKENS AFTER LANDFALL NEAR GOPALPUR",
    sub=("372,000 people are evacuated and 41 trains cancelled. "
         "Odisha escapes major damage."),
)

TICKER_TOP = ("ALSO TODAY:   Israel urges strikes on Iran; Turkey, "
              "Pakistan and Gulf states lobby Washington")
TICKER_LOW = ("The Shenzhen declaration, signed by Trump, Xi and Putin, "
              "leads the day's live coverage")


def build(variant):
    page = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(page)
    d.text((W // 2, 30), "THE WORLD IN ONE DAY",
           font=load_font(SANS_B, 21), fill=GOLD, anchor="ma")
    d.text((W // 2, 52), "SATURDAY 21 NOVEMBER 2026",
           font=load_font(SERIF, 46), fill=WHITE, anchor="ma")
    d.line([(24, 116), (W - 24, 116)], fill=GOLD, width=3)

    hero = HORMUZ if variant == "a" else SHENZHEN
    small_lead = SHENZHEN_SMALL if variant == "a" else HORMUZ_SMALL
    story(page, os.path.join(ASSETS, hero["photo"]),
          (0, 118, W, 430), hero["tag"], hero["head"], hero["sub"],
          head_px=36, sub_px=20, fy=0.4, head_max=2)

    gx, gy = 10, 430
    cw, ch, gut = 328, 270, 10
    row1 = [small_lead, ICJ, POLAND]
    for i, s in enumerate(row1):
        x = gx + i * (cw + gut)
        story(page, os.path.join(ASSETS, s["photo"]),
              (x, gy, x + cw, gy + ch), s["tag"], s["head"], s["sub"],
              fy=0.45)

    gy2, ch2 = 700, 246
    row2 = [HOUTHI, DATACENTRE, CYCLONE]
    for i, s in enumerate(row2):
        x = gx + i * (cw + gut)
        story(page, os.path.join(ASSETS, s["photo"]),
              (x, gy2, x + cw, gy2 + ch2), s["tag"], s["head"], s["sub"],
              fy=0.45)

    d.rectangle([(0, 956), (W, H)], fill=(7, 16, 26))
    d.line([(0, 956), (W, 956)], fill=GOLD, width=2)
    d.text((24, 964), TICKER_TOP, font=load_font(SANS_B, 18), fill=GOLD)
    d.text((24, 989), TICKER_LOW, font=load_font(SANS, 18), fill=PALE)
    return page


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=["a", "b"], default="a")
    ap.add_argument("--out", default="entry.png")
    args = ap.parse_args()
    page = build(args.variant)
    # JPEG bytes under the entry.png name: the gate reads the format
    # from the magic bytes. JPEG keeps this photo page well under the
    # 1 MiB cap; PNG ran over it for the same layout yesterday.
    page.save(args.out, format="JPEG", quality=88, optimize=True)
    size = os.path.getsize(args.out)
    print(f"wrote {args.out} variant {args.variant.upper()} "
          f"{page.size} {size} bytes")
    if size > 1_048_576:
        sys.exit(f"over the 1 MiB cap: {size} bytes")


if __name__ == "__main__":
    main()
