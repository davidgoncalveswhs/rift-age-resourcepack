import sys; sys.path.insert(0, '.')
from PIL import Image, ImageDraw
import art, catalog
ids = list(catalog.ITEMS)
S = 4; cols = 10; cell = 16 * S + 8
rows = (len(ids) + cols - 1) // cols
sets = list(catalog.SETS)
sheet = Image.new("RGBA", (cols * cell, rows * cell + len(sets) * (32 * 3 + 8) // 1 + 10), (58, 58, 64, 255))
for i, id in enumerate(ids):
    it = catalog.ITEMS[id]
    im = art.icon(it["shape"], it["pal"], it["sparkle"], seed=hash(id) & 0xffff).resize((16 * S, 16 * S), Image.NEAREST)
    sheet.alpha_composite(im, ((i % cols) * cell + 4, (i // cols) * cell + 4))
y = rows * cell + 10
for j, s in enumerate(sets):
    l1, l2 = art.armor_layers(catalog.SETS[s][0], seed=j)
    sheet.alpha_composite(l1.resize((64 * 3, 32 * 3), Image.NEAREST), (4, y))
    sheet.alpha_composite(l2.resize((64 * 3, 32 * 3), Image.NEAREST), (4 + 64 * 3 + 12, y))
    y += 32 * 3 + 8
sheet.save(sys.argv[1])
print(len(ids), "icons")
