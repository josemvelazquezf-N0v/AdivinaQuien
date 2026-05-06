"""
Mapeo de nombres de bloque a URLs de textura.

Usa el CDN publico mcasset.cloud, mantenido por inventivetalent, que
sirve los assets oficiales del juego desde GitHub. La ruta es:

    https://mcasset.cloud/<version>/assets/minecraft/textures/block/<archivo>.png

Para muchos bloques el archivo se llama igual que `block.name`. Para los
que no, ofrecemos varios candidatos y dejamos que el cliente caiga al
siguiente si la imagen falla al cargar.

No hay descargas: las URLs son externas y se referencian desde el HTML.
"""
from typing import Dict, Any, List


VERSION = "latest"
BASE = f"https://mcasset.cloud/{VERSION}/assets/minecraft/textures/block"


# Mapeos especiales: bloques cuyo `name` no coincide con el archivo PNG.
# Solo los casos comunes; el resto usa <name>.png con fallback a otros sufijos.
ESPECIALES: Dict[str, List[str]] = {
    "grass_block":      ["grass_block_side", "grass_block_top"],
    "dirt_path":        ["dirt_path_side", "dirt_path_top"],
    "podzol":           ["podzol_side", "podzol_top"],
    "mycelium":         ["mycelium_side", "mycelium_top"],
    "snow_block":       ["snow"],
    "tnt":              ["tnt_side", "tnt_top"],
    "furnace":          ["furnace_front", "furnace_side"],
    "blast_furnace":    ["blast_furnace_front", "blast_furnace_side"],
    "smoker":           ["smoker_front", "smoker_side"],
    "lectern":          ["lectern_sides", "lectern_front"],
    "loom":             ["loom_front", "loom_side"],
    "stonecutter":      ["stonecutter_top", "stonecutter_side"],
    "cartography_table": ["cartography_table_side1", "cartography_table_side3"],
    "fletching_table":  ["fletching_table_front", "fletching_table_side"],
    "smithing_table":   ["smithing_table_front", "smithing_table_side"],
    "barrel":           ["barrel_top", "barrel_side"],
    "campfire":         ["campfire_log"],
    "soul_campfire":    ["soul_campfire_log_lit"],
    "spawner":          ["spawner"],
    "command_block":    ["command_block_front"],
    "chain_command_block": ["chain_command_block_front"],
    "repeating_command_block": ["repeating_command_block_front"],
    "ender_chest":      ["ender_chest_front"],
    "lava":             ["lava_still"],
    "water":            ["water_still"],
    "fire":             ["fire_0"],
    "soul_fire":        ["soul_fire_0"],
    "redstone_wire":    ["redstone_dust_dot"],
    "tripwire":         ["string"],
    "tripwire_hook":    ["tripwire_hook"],
    "ladder":           ["ladder"],
    "vine":             ["vine"],
    "lily_pad":         ["lily_pad"],
    "kelp":             ["kelp"],
    "kelp_plant":       ["kelp_plant"],
    "seagrass":         ["seagrass"],
    "tall_seagrass":    ["tall_seagrass_top"],
    "sea_pickle":       ["sea_pickle"],
    "torch":            ["torch"],
    "wall_torch":       ["torch"],
    "soul_torch":       ["soul_torch"],
    "soul_wall_torch":  ["soul_torch"],
    "redstone_torch":   ["redstone_torch"],
    "redstone_wall_torch": ["redstone_torch"],
    "lantern":          ["lantern"],
    "soul_lantern":     ["soul_lantern"],
    "chain":            ["chain"],
    "end_rod":          ["end_rod"],
    "lightning_rod":    ["lightning_rod"],
    "bell":             ["bell_bottom"],
    "conduit":          ["conduit"],
    "beacon":           ["beacon"],
    "scaffolding":      ["scaffolding_side", "scaffolding_top"],
    # Familias generalizadas: tomamos la variante mas iconica
    "wool":             ["white_wool"],
    "carpet":           ["white_carpet", "white_wool"],
    "concrete":         ["white_concrete"],
    "concrete_powder":  ["white_concrete_powder"],
    "terracotta":       ["white_terracotta", "terracotta"],
    "stained_glass":    ["white_stained_glass", "glass"],
    "stained_glass_pane": ["white_stained_glass", "glass_pane_top"],
    "glazed_terracotta": ["white_glazed_terracotta"],
    "shulker_box":      ["shulker_box"],
    "candle":           ["white_candle"],
    "bed":              ["white_wool"],            # las camas no tienen textura cuadrada
    "banner":           ["white_wool"],
    "wall_banner":      ["white_wool"],
    "log":              ["oak_log"],
    "stripped_log":     ["stripped_oak_log"],
    "wood":             ["oak_log"],
    "stripped_wood":    ["stripped_oak_log"],
    "planks":           ["oak_planks"],
    "leaves":           ["oak_leaves"],
    "sapling":          ["oak_sapling"],
    "door":             ["oak_door_top"],
    "fence":            ["oak_planks"],
    "fence_gate":       ["oak_planks"],
    "trapdoor":         ["oak_trapdoor"],
    "pressure_plate":   ["oak_planks"],
    "button":           ["oak_planks"],
    "sign":             ["oak_planks"],
    "wall_sign":        ["oak_planks"],
    "hanging_sign":     ["oak_planks"],
    "wall_hanging_sign": ["oak_planks"],
}


def candidatos_archivos(name: str) -> List[str]:
    """Devuelve nombres candidatos de archivo (sin extension) para `name`.

    El cliente intenta cargarlos en orden hasta que una imagen funcione.
    """
    if name in ESPECIALES:
        return ESPECIALES[name] + [name]
    # Fallbacks generales: el archivo puede tener sufijos comunes
    return [name, f"{name}_side", f"{name}_top", f"{name}_front", f"{name}_0"]


def url_textura(name: str) -> List[str]:
    """Lista de URLs candidatas para la textura de un bloque."""
    return [f"{BASE}/{f}.png" for f in candidatos_archivos(name)]


def textura_de_bloque(bloque: Dict[str, Any]) -> List[str]:
    """URLs de la textura representativa de un bloque (familia o no)."""
    # Si es una familia, preferimos la primera variante (suele ser blanca/oak)
    variantes = bloque.get("variants") or []
    if variantes:
        return url_textura(variantes[0]["name"])
    return url_textura(bloque["name"])
