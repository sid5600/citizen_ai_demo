"""Create sample scanned forms (invented data) so the demo can run without real documents.

  sample_clear.png : a clean scan, should be auto-accepted
  sample_poor.png  : a poor scan (blur, noise, skew), fields should be flagged for review
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(__file__).parent / "samples"
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
]

DATA = [
    ("Name", "Anita Rao"),
    ("Date of Birth", "14-Mar-1998"),
    ("ID Number", "AB1234567"),
    ("Mobile", "9876543210"),
    ("Address", "Ward 12 Gandhi Road Vizag"),
]


def font(size):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)


def draw_form(poor=False):
    img = Image.new("L", (1100, 650), 245)
    d = ImageDraw.Draw(img)
    d.text((40, 30), "SAMPLE CERTIFICATE APPLICATION FORM", font=font(34), fill=20)
    d.text((40, 80), "(Demo data only. Not a real document)", font=font(22), fill=90)
    y = 160
    for label, value in DATA:
        d.text((40, y), f"{label}: {value}", font=font(36), fill=15)
        y += 80
    if poor:
        random.seed(7)
        img = img.rotate(1.0, expand=False, fillcolor=240)
        img = img.filter(ImageFilter.GaussianBlur(1.1))
        px = img.load()
        for _ in range(25000):  # speckle noise like a bad photocopy
            x, yy = random.randrange(img.width), random.randrange(img.height)
            px[x, yy] = max(0, min(255, px[x, yy] + random.randint(-70, 70)))
        # smudge the last line (address) the way a folded or stained form would look
        smudge = img.crop((40, 480, 1060, 560)).filter(ImageFilter.GaussianBlur(3.2))
        img.paste(smudge, (40, 480))
    return img


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    draw_form(poor=False).save(OUT / "sample_clear.png")
    draw_form(poor=True).save(OUT / "sample_poor.png")
    print("Saved samples to", OUT)
