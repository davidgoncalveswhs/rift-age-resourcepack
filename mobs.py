"""Rift Age mob and NPC skins. Each design repaints one vanilla mob type that only the server's custom
creatures use: the mob's own shading is kept (so faces and limbs still read), its colors are replaced
by a themed gradient, the brightest details (eyes, glowing bits) turn into an accent glow, and a light
rift speckle is added. The same recipe runs on the Java and the Bedrock vanilla texture so both
editions look alike."""
import random
from PIL import Image


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# name: (gradient dark->light, accent, speckle, java paths, bedrock paths)
E = "assets/minecraft/textures/entity/"
B = "textures/entity/"
DESIGNS = {
    "shade":        (["#12061f", "#3a1660", "#7b3fb8", "#c9a6ff", "#f3e8ff"], "#ff4fd8", "#e0aaff",
                     [E + "illager/vex", E + "illager/vex_charging"], [B + "vex/vex", B + "vex/vex_charging"]),
    "void_wraith":  (["#05030b", "#1a1233", "#3b2a6e", "#7d6bd6", "#d9ccff"], "#c77dff", "#7d6bd6",
                     [E + "phantom/phantom"], [B + "phantom"]),
    "gloom_stalker":(["#0b0712", "#2a1b3d", "#4e3670", "#8a6bb8", "#d7c4ff"], "#e0aaff", "#9b62d6",
                     [E + "hoglin/zoglin"], [B + "zoglin/zoglin"]),
    "cultist":      (["#0f0818", "#2e1a47", "#5b2a86", "#a06cd5", "#f0dcff"], "#ffd27f", "#c77dff",
                     [E + "illager/vindicator"], [B + "vindicator"]),
    "voidwalker":   (["#030106", "#150822", "#341552", "#7a2fb0", "#e6b3ff"], "#ff4fd8", "#c77dff",
                     [E + "strider/strider", E + "strider/strider_cold"], [B + "strider/strider", B + "strider/strider_suffocated"]),
    "crystal_mite": (["#1d0d33", "#4b2380", "#8a48c8", "#c08cf2", "#f4e1ff"], "#ffffff", "#e0aaff",
                     [E + "endermite/endermite"], [B + "endermite"]),
    "riftwalker":   (["#0c1426", "#1e2f4d", "#3e5c8a", "#7fa6d9", "#e6f2ff"], "#7fd8ff", "#ffe45c",
                     [E + "piglin/piglin_brute"], [B + "piglin/piglin_brute"]),
    "rift_crawler": (["#06302f", "#0e6a66", "#1fa9a3", "#6fe3d6", "#e8fffb"], "#ffb7d5", "#e8fffb",
                     [E + "silverfish/silverfish"], [B + "silverfish"]),
    "gale":         (["#0e3a4a", "#2f7f99", "#7fd8ff", "#c9f2ff", "#ffffff"], "#ffe45c", "#ffffff",
                     [E + "breeze/breeze"], [B + "breeze/breeze"]),
    "skyray":       (["#1e2a5a", "#3f63a8", "#6f9fe0", "#a8d4ff", "#e6f6ff"], "#ffb7d5", "#ffb7d5",
                     [E + "ghast/happy_ghast"], [B + "happy_ghast/happy_ghast"]),
    "shellback":    (["#14302c", "#2f6b5e", "#4fa08a", "#9fd9c4", "#e9fff6"], "#ffd27f", "#e9fff6",
                     [E + "hoglin/hoglin"], [B + "hoglin/hoglin"]),
    "wisp":         (["#5a2a4a", "#c06a9a", "#ffb7d5", "#ffe6f2", "#ffffff"], "#7fd8ff", "#ffffff",
                     [E + "allay/allay"], [B + "allay/allay"]),
    "void_weaver":  (["#050108", "#2a0f42", "#4e2178", "#9b62d6", "#ffd6f5"], "#ff4fd8", "#ff4fd8",
                     [E + "illager/evoker"], [B + "illager/evoker"]),
    "colossus":     (["#1a2a33", "#3a5a6a", "#6f95a8", "#b8d8e0", "#f5fbff"], "#ffe07a", "#7fd8ff",
                     [E + "sniffer/sniffer"], [B + "sniffer/sniffer"]),
    "trex":         (["#1b2410", "#3d4f1e", "#6b7f34", "#a8b86a", "#e8f0c8"], "#ff7a2a", "#a8b86a",
                     [E + "illager/ravager"], [B + "illager/ravager"]),
    "pterodactyl":  (["#2a1608", "#5c3416", "#9a5a2a", "#d49a5c", "#f6dcb0"], "#ffd27f", "#d49a5c",
                     [E + "parrot/parrot_" + c for c in ("blue", "green", "grey", "red_blue", "yellow_blue")],
                     [B + "parrot/parrot_" + c for c in ("blue", "green", "grey", "red_blue", "yellow_blue")]),
    # NPC robes: Umbra residents wear the swamp type, Drift residents the jungle type (no villages of either exist).
    "umbra_robes":  (["#140a22", "#3d1a5e", "#6a32a0", "#a77ad9", "#efe0ff"], "#e0aaff", "#c77dff",
                     [E + "villager/type/swamp"], [B + "villager2/biomes/biome_swamp"]),
    "drift_robes":  (["#0b2b30", "#1a6b6b", "#3fb3a8", "#9fe8dc", "#fff6fb"], "#ffb7d5", "#ffe07a",
                     [E + "villager/type/jungle"], [B + "villager2/biomes/biome_jungle"]),
}


def _grad(stops, t):
    t = max(0.0, min(1.0, t)) * (len(stops) - 1)
    i = min(int(t), len(stops) - 2)
    f = t - i
    a, b = stops[i], stops[i + 1]
    return tuple(round(a[k] + (b[k] - a[k]) * f) for k in range(3))


def repaint(src, design, seed=7):
    stops, accent, speck = DESIGNS[design][:3]
    stops = [hexrgb(s) for s in stops]
    accent, speck = hexrgb(accent), hexrgb(speck)
    im = src.convert("RGBA")
    px = im.load()
    w, h = im.size
    lum = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a:
                lum.append(0.299 * r + 0.587 * g + 0.114 * b)
    if not lum:
        return im
    lo, hi = min(lum), max(lum)
    srt = sorted(lum)
    glow = srt[int(len(srt) * 0.95)] if len(srt) > 20 else hi + 1
    # Only small bright details glow (eyes, gems); if "bright" covers big areas, skip the glow.
    bright = sum(1 for y in range(h) for x in range(w) if px[x, y][3] and 0.299 * px[x, y][0] + 0.587 * px[x, y][1] + 0.114 * px[x, y][2] >= glow)
    if bright > 0.08 * len(lum):
        glow = 999
    rnd = random.Random(seed)
    out = Image.new("RGBA", (w, h))
    op = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if not a:
                continue
            l = 0.299 * r + 0.587 * g + 0.114 * b
            sat = max(r, g, b) - min(r, g, b)
            if l >= glow and (sat > 60 or l > 200):  # eyes and bright details glow
                c = accent
            else:
                c = _grad(stops, (l - lo) / max(1, hi - lo))
                if rnd.random() < 0.03:
                    c = tuple(round(c[k] * 0.4 + speck[k] * 0.6) for k in range(3))
            op[x, y] = c + (a,)
    return out
