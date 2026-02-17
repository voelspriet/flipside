"""Generate document-style thumbnail images for sample documents.

Each thumbnail looks like a miniature first page of the document:
- White paper with subtle border
- Document title at the top
- Horizontal lines representing text
- A colored accent bar for visual identity
"""
import base64
import json
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

DOCS = {
    'lease': {
        'title': 'QUICKRENT',
        'subtitle': 'LEASE AGREEMENT',
        'accent': (196, 75, 40),     # rust
        'lines': 12,
    },
    'insurance': {
        'title': 'SAFEGUARD',
        'subtitle': 'INSURANCE POLICY',
        'accent': (45, 100, 160),    # blue
        'lines': 14,
    },
    'tos': {
        'title': 'CLOUDVAULT',
        'subtitle': 'TERMS OF SERVICE',
        'accent': (80, 80, 80),      # dark gray
        'lines': 13,
    },
    'employment': {
        'title': 'TECHFORWARD',
        'subtitle': 'EMPLOYMENT',
        'accent': (60, 120, 80),     # green
        'lines': 11,
    },
    'loan': {
        'title': 'QUICKCASH',
        'subtitle': 'LOAN AGREEMENT',
        'accent': (160, 60, 60),     # dark red
        'lines': 12,
    },
    'gym': {
        'title': 'IRONCLAD',
        'subtitle': 'MEMBERSHIP',
        'accent': (180, 120, 30),    # gold
        'lines': 10,
    },
    'medical': {
        'title': 'LAKEWOOD',
        'subtitle': 'CONSENT FORM',
        'accent': (40, 130, 150),    # teal
        'lines': 13,
    },
    'hoa': {
        'title': 'CRESTVIEW',
        'subtitle': 'HOA COVENANTS',
        'accent': (100, 80, 60),     # brown
        'lines': 12,
    },
    'coupon': {
        'title': 'MEGAMART',
        'subtitle': 'COUPON BOOK',
        'accent': (200, 50, 50),     # bright red
        'lines': 9,
    },
}

W, H = 200, 280
MARGIN = 16
LINE_H = 10
LINE_GAP = 6

thumbnails = {}

for key, doc in DOCS.items():
    img = Image.new('RGB', (W, H), (255, 255, 253))
    draw = ImageDraw.Draw(img)

    # Subtle page border
    draw.rectangle([0, 0, W - 1, H - 1], outline=(220, 216, 210))

    # Accent bar at top
    bar_h = 6
    draw.rectangle([0, 0, W, bar_h], fill=doc['accent'])

    # Title text
    y = bar_h + 14
    try:
        font_title = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 14)
        font_sub = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 10)
        font_small = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 7)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = font_title
        font_small = font_title

    # Title
    draw.text((MARGIN, y), doc['title'], fill=doc['accent'], font=font_title)
    y += 20

    # Subtitle
    draw.text((MARGIN, y), doc['subtitle'], fill=(100, 96, 90), font=font_sub)
    y += 18

    # Thin separator line
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=(220, 216, 210), width=1)
    y += 12

    # Simulated text lines (varying lengths for realism)
    import random
    random.seed(hash(key))
    for i in range(doc['lines']):
        line_w = random.randint(int((W - 2 * MARGIN) * 0.5), W - 2 * MARGIN)
        color = (190, 186, 180) if i % 4 != 0 else (160, 155, 148)
        draw.rectangle(
            [MARGIN, y, MARGIN + line_w, y + 3],
            fill=color,
        )
        y += LINE_GAP + 3
        if y > H - 20:
            break

    # Section headers (slightly darker, shorter)
    # Already mixed in via the color variation above

    # Save as base64 JPEG
    buf = BytesIO()
    img.save(buf, format='JPEG', quality=75)
    thumbnails[key] = base64.b64encode(buf.getvalue()).decode()

    # Also save as file for preview
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    os.makedirs(static_dir, exist_ok=True)
    img.save(os.path.join(static_dir, f'thumb_{key}.jpg'), quality=75)

# Output as Python dict literal
print("SAMPLE_THUMBNAILS = {")
for key, b64 in thumbnails.items():
    print(f"    '{key}': '{b64}',")
print("}")

print(f"\nGenerated {len(thumbnails)} thumbnails")
