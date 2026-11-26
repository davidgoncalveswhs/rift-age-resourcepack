"""Every textured item: (shape, palette, base Java item, kind, bedrock)
kind: armor:<slot> | handheld | generated | bow
bedrock: map it to a Bedrock custom item (False for items whose use the Bedrock client must predict:
pickaxes/drills (mining speed), bows (drawing), and right-click items)."""

SETS = {  # armor sets: palette, Java base material prefix
    "umbral": ("umbral", "diamond"),
    "nightfall": ("nightfall", "netherite"),
    "voidheart": ("voidheart", "netherite"),
    "prismite": ("prismite", "diamond"),
    "stormguard": ("stormguard", "netherite"),
    "celestial": ("celestial", "golden"),
}
SLOTS = {"helmet": "head", "chestplate": "chest", "leggings": "legs", "boots": "feet"}

ITEMS = {}
for s, (pal, base) in SETS.items():
    for piece, slot in SLOTS.items():
        ITEMS[f"{s}_{piece}"] = dict(shape=piece, pal=pal, base=f"{base}_{piece}", kind=f"armor:{slot}", bedrock=True,
                                     sparkle=s in ("voidheart", "celestial"), name=f"{s.title()} {piece.title()}")

def add(id, shape, pal, base, kind, bedrock=True, sparkle=False, name=None):
    ITEMS[id] = dict(shape=shape, pal=pal, base=base, kind=kind, bedrock=bedrock, sparkle=sparkle,
                     name=name or id.replace("_", " ").title())

# weapons and tools
add("umbral_blade", "sword", "umbral", "diamond_sword", "handheld")
add("voidheart_greatsword", "greatsword", "voidheart", "netherite_sword", "handheld", sparkle=True)
add("gloomsteel_scythe", "scythe", "gloomsteel", "netherite_hoe", "handheld")
add("gale_hammer", "hammer", "stormguard", "mace", "handheld")
add("starbow", "bow", "starshard", "bow", "bow", bedrock=False)
add("umbral_pickaxe", "pickaxe", "umbral", "diamond_pickaxe", "handheld", bedrock=False)
add("gloomsteel_pickaxe", "pickaxe", "gloomsteel", "netherite_pickaxe", "handheld", bedrock=False)
add("voidheart_drill", "drill", "voidheart", "netherite_pickaxe", "handheld", bedrock=False, sparkle=True)
add("skysteel_pickaxe", "pickaxe", "skysteel", "netherite_pickaxe", "handheld", bedrock=False)
add("starshard_pickaxe", "pickaxe", "starshard", "netherite_pickaxe", "handheld", bedrock=False)

# materials
add("umbrite_shard", "shard", "umbrite", "amethyst_shard", "generated")
add("umbrite_ingot", "ingot", "umbrite", "popped_chorus_fruit", "generated")
add("void_essence", "bottle", "voidheart", "dragon_breath", "generated")
add("void_pearl", "gem", "voidheart", "ender_eye", "generated", bedrock=False)
add("weavers_heart", "heart", "voidheart", "nether_star", "generated", sparkle=True, name="Weaver's Heart")
add("raw_gloomsteel", "raw", "gloomsteel", "disc_fragment_5", "generated")
add("gloomsteel_ingot", "ingot", "gloomsteel", "nether_brick", "generated")
add("voidheart_shard", "gem", "voidheart", "shulker_shell", "generated", sparkle=True)
add("weaver_silk", "silk", "umbrite", "string", "generated", name="Weaver's Silk")
add("rift_shard", "shard", "prismite", "prismarine_shard", "generated")
add("prismite_ingot", "ingot", "prismite", "prismarine_crystals", "generated")
add("raw_skysteel", "raw", "skysteel", "echo_shard", "generated")
add("skysteel_ingot", "ingot", "skysteel", "iron_ingot", "generated")
add("starshard", "star", "starshard", "ghast_tear", "generated", sparkle=True)
add("colossus_plate", "plate", "colossus", "turtle_scute", "generated")
add("colossus_shell", "plate", "prismite", "armadillo_scute", "generated")
