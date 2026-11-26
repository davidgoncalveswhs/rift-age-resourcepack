"""Builds the Rift Age gear packs:
  build/rift-age-java.zip        Java resource pack (item models + armor layers), hosted on GitHub, sent on join
  build/rift-age-bedrock.mcpack  Bedrock resource pack (icons + worn armor), sent by Geyser
  build/bteam_mappings.json      Geyser custom item mappings (format 2, keyed by the Java item_model)
Run: python3 make_pack.py
"""
import json, os, shutil, sys, uuid, zipfile, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import art, catalog

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "build")
NS = "bteam"
VERSION = [1, 0, 0]


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(data, (dict, list)):
        data = json.dumps(data, indent=2)
    with open(path, "w") as f:
        f.write(data)


def zipdir(src, dest):
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(src):
            for fn in sorted(files):
                full = os.path.join(root, fn)
                info = zipfile.ZipInfo(os.path.relpath(full, src), date_time=(2026, 1, 1, 0, 0, 0))  # stable hash
                info.compress_type = zipfile.ZIP_DEFLATED
                with open(full, "rb") as f:
                    z.writestr(info, f.read())


def seed(id):
    return int(hashlib.md5(id.encode()).hexdigest()[:6], 16)


def java():
    root = os.path.join(OUT, "java")
    a = os.path.join(root, "assets", NS)
    write(os.path.join(root, "pack.mcmeta"), {"pack": {
        "description": "Rift Age gear: Umbra & Drift armor and weapons", "min_format": 97, "max_format": 97}})
    shutil.copy(os.path.join(OUT, "pack.png"), os.path.join(root, "pack.png"))
    for id, it in catalog.ITEMS.items():
        art.icon(it["shape"], it["pal"], it["sparkle"], seed(id)).save(os.path.join(mk(a, "textures/item"), id + ".png"))
        if it["kind"] == "bow":
            for st in ("bow_pulling_0", "bow_pulling_1", "bow_pulling_2"):
                art.icon(st, it["pal"], it["sparkle"], seed(id)).save(os.path.join(a, "textures/item", id + st[3:] + ".png"))
                write(os.path.join(a, "models/item", id + st[3:] + ".json"),
                      {"parent": "minecraft:item/bow", "textures": {"layer0": f"{NS}:item/{id}{st[3:]}"}})
            write(os.path.join(a, "models/item", id + ".json"), {"parent": "minecraft:item/bow", "textures": {"layer0": f"{NS}:item/{id}"}})
            m = lambda n: {"type": "minecraft:model", "model": f"{NS}:item/{n}"}
            write(os.path.join(a, "items", id + ".json"), {"model": {
                "type": "minecraft:condition", "property": "minecraft:using_item",
                "on_false": m(id),
                "on_true": {"type": "minecraft:range_dispatch", "property": "minecraft:use_duration", "scale": 0.05,
                            "fallback": m(id + "_pulling_0"),
                            "entries": [{"threshold": 0.65, "model": m(id + "_pulling_1")},
                                        {"threshold": 0.9, "model": m(id + "_pulling_2")}]}}})
            continue
        parent = "minecraft:item/handheld" if it["kind"] == "handheld" else "minecraft:item/generated"
        write(os.path.join(a, "models/item", id + ".json"), {"parent": parent, "textures": {"layer0": f"{NS}:item/{id}"}})
        write(os.path.join(a, "items", id + ".json"), {"model": {"type": "minecraft:model", "model": f"{NS}:item/{id}"}})
    for j, (s, (pal, _)) in enumerate(catalog.SETS.items()):
        l1, l2 = art.armor_layers(pal, seed(s))
        l1.save(os.path.join(mk(a, "textures/entity/equipment/humanoid"), s + ".png"))
        l2.save(os.path.join(mk(a, "textures/entity/equipment/humanoid_leggings"), s + ".png"))
        write(os.path.join(a, "equipment", s + ".json"), {"layers": {
            "humanoid": [{"texture": f"{NS}:{s}"}], "humanoid_leggings": [{"texture": f"{NS}:{s}"}]}})
    dest = os.path.join(OUT, "rift-age-java.zip")
    zipdir(root, dest)
    return dest


def bedrock():
    root = os.path.join(OUT, "bedrock")
    ns = uuid.UUID("6b1e3c52-5c1f-4b7e-9a51-2f6f1d7f2a10")
    write(os.path.join(root, "manifest.json"), {
        "format_version": 2,
        "header": {"name": "Rift Age Gear", "description": "Umbra & Drift armor and weapons", "uuid": str(uuid.uuid5(ns, "header")),
                   "version": VERSION, "min_engine_version": [1, 21, 0]},
        "modules": [{"type": "resources", "uuid": str(uuid.uuid5(ns, "resources")), "version": VERSION}]})
    shutil.copy(os.path.join(OUT, "pack.png"), os.path.join(root, "pack_icon.png"))
    tex = {}
    mappings = {}
    for id, it in catalog.ITEMS.items():
        if not it["bedrock"]:
            continue
        icon = f"{NS}_{id}"
        art.icon(it["shape"], it["pal"], it["sparkle"], seed(id)).save(os.path.join(mk(root, "textures/items"), icon + ".png"))
        tex[icon] = {"textures": f"textures/items/{icon}"}
        opts = {"icon": icon, "creative_category": "equipment" if it["kind"] != "generated" else "items"}
        comps = {}
        if it["kind"].startswith("armor:"):
            slot = it["kind"].split(":")[1]
            opts["allow_offhand"] = False
            opts["protection_value"] = {"head": 3, "chest": 8, "legs": 6, "feet": 3}[slot]
            comps = {"minecraft:equippable": {"slot": slot}, "minecraft:max_stack_size": 1}
            attachable(root, id, it, slot)
        elif it["kind"] == "handheld":
            opts["display_handheld"] = True
            opts["allow_offhand"] = True
        entry = {"type": "definition", "model": f"{NS}:{id}", "bedrock_identifier": f"{NS}:{id}",
                 "display_name": it["name"], "bedrock_options": opts}
        if comps:
            entry["components"] = comps
        mappings.setdefault("minecraft:" + it["base"], []).append(entry)
    for s, (pal, _) in catalog.SETS.items():
        l1, l2 = art.armor_layers(pal, seed(s))
        l1.save(os.path.join(mk(root, "textures/models/armor"), f"{NS}_{s}_1.png"))
        l2.save(os.path.join(root, "textures/models/armor", f"{NS}_{s}_2.png"))
    write(os.path.join(root, "textures/item_texture.json"),
          {"resource_pack_name": "rift_age", "texture_name": "atlas.items", "texture_data": tex})
    dest = os.path.join(OUT, "rift-age-bedrock.mcpack")
    zipdir(root, dest)
    write(os.path.join(OUT, "bteam_mappings.json"), {"format_version": 2, "items": mappings})
    return dest


GEO = {"head": ("helmet", "helmet_layer_visible", 1), "chest": ("chestplate", "chest_layer_visible", 1),
       "legs": ("leggings", "leg_layer_visible", 2), "feet": ("boots", "boot_layer_visible", 1)}


def attachable(root, id, it, slot):
    geo, var, layer = GEO[slot]
    s = id.rsplit("_", 1)[0]
    write(os.path.join(root, "attachables", f"{NS}_{id}.json"), {
        "format_version": "1.10.0",
        "minecraft:attachable": {"description": {
            "identifier": f"{NS}:{id}",
            "materials": {"default": "armor", "enchanted": "armor_enchanted"},
            "textures": {"default": f"textures/models/armor/{NS}_{s}_{layer}", "enchanted": "textures/misc/enchanted_item_glint"},
            "geometry": {"default": f"geometry.humanoid.armor.{geo}"},
            "scripts": {"parent_setup": f"variable.{var} = 0.0;"},
            "render_controllers": ["controller.render.armor"]}}})


def mk(*parts):
    p = os.path.join(*parts)
    os.makedirs(p, exist_ok=True)
    return p


def pack_icon():
    from PIL import Image
    img = Image.new("RGBA", (128, 128), (20, 10, 34, 255))
    a = art.icon("star", "starshard", True, 1).resize((64, 64), Image.NEAREST)
    b = art.icon("gem", "voidheart", True, 2).resize((64, 64), Image.NEAREST)
    img.alpha_composite(b, (8, 32))
    img.alpha_composite(a, (56, 32))
    img.save(os.path.join(OUT, "pack.png"))


if __name__ == "__main__":
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT)
    pack_icon()
    j = java()
    b = bedrock()
    sha1 = hashlib.sha1(open(j, "rb").read()).hexdigest()
    write(os.path.join(OUT, "java.sha1"), sha1)
    print("java", j, os.path.getsize(j), "sha1", sha1)
    print("bedrock", b, os.path.getsize(b))
    print("mappings", sum(len(v) for v in json.load(open(os.path.join(OUT, "bteam_mappings.json")))["items"].values()), "bedrock items")
