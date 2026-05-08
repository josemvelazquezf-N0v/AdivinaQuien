"""
Generaliza la base de datos de bloques: fusiona variantes que solo difieren
en color o tipo de madera en una sola entrada con un campo `variants`.

Por ejemplo, los 16 colores de lana se vuelven una sola entrada "Wool"
con variants = [white, orange, magenta, ...].

Uso:
    python tools/generalize.py

Lee data/blocks.json y escribe data/blocks_general.json
"""
import json
from pathlib import Path
from collections import defaultdict


# Patrones (sufijo_en_name, displayName_general).
# IMPORTANTE: el orden importa porque los sufijos largos deben evaluarse
# primero (p. ej. _concrete_powder antes que _concrete).
PATRONES = [
    # Mas especificos primero
    ("_concrete_powder", "Concrete Powder"),
    ("_glazed_terracotta", "Glazed Terracotta"),
    ("_stained_glass_pane", "Stained Glass Pane"),
    ("_wall_banner", "Wall Banner"),
    ("_wall_sign", "Wall Sign"),
    ("_hanging_sign", "Hanging Sign"),
    ("_wall_hanging_sign", "Wall Hanging Sign"),
    ("_pressure_plate", "Pressure Plate"),
    ("_fence_gate", "Fence Gate"),
    ("_trapdoor", "Trapdoor"),
    ("_stripped_log", "Stripped Log"),
    ("_stripped_wood", "Stripped Wood"),
    # Variantes de color
    ("_wool", "Wool"),
    ("_concrete", "Concrete"),
    ("_terracotta", "Terracotta"),
    ("_stained_glass", "Stained Glass"),
    ("_carpet", "Carpet"),
    ("_bed", "Bed"),
    ("_banner", "Banner"),
    ("_shulker_box", "Shulker Box"),
    ("_candle", "Candle"),
    # Variantes de tipo de arbol
    ("_leaves", "Leaves"),
    ("_sapling", "Sapling"),
    ("_log", "Log"),
    ("_wood", "Wood"),
    ("_planks", "Planks"),
    ("_door", "Door"),
    ("_fence", "Fence"),
    ("_button", "Button"),
    ("_sign", "Sign"),
    ("_boat", "Boat"),
]

# Prefijos conocidos de variantes (color o tipo de arbol)
PREFIJOS_VARIANTE = {
    # Colores
    "white", "orange", "magenta", "light_blue", "yellow", "lime",
    "pink", "gray", "light_gray", "cyan", "purple", "blue", "brown",
    "green", "red", "black",
    # Maderas
    "oak", "spruce", "birch", "jungle", "acacia", "dark_oak",
    "mangrove", "cherry", "bamboo", "crimson", "warped",
}


def detectar_variante(name: str, sufijo: str) -> str | None:
    """Si `name` tiene la forma `<variante><sufijo>`, devuelve la variante.
    Si no, devuelve None."""
    if not name.endswith(sufijo):
        return None
    prefijo = name[: -len(sufijo)]
    if prefijo in PREFIJOS_VARIANTE:
        return prefijo
    return None


def generalizar(bloques: list[dict]) -> list[dict]:
    """Devuelve una nueva lista con las variantes agrupadas."""
    # Indice: clave de familia -> lista de bloques que pertenecen
    familias: dict[str, list[dict]] = defaultdict(list)
    # Bloques que no encajan en ninguna familia
    sueltos: list[dict] = []

    for b in bloques:
        nombre = b.get("name", "")
        agrupado = False
        for sufijo, _display in PATRONES:
            variante = detectar_variante(nombre, sufijo)
            if variante is not None:
                familias[sufijo].append(b)
                agrupado = True
                break
        if not agrupado:
            sueltos.append(b)

    # Construir entradas generalizadas. Mantenemos el id del primer miembro
    # como id "representativo" y agregamos `variants`.
    resultado: list[dict] = list(sueltos)

    for sufijo, miembros in familias.items():
        # Buscar el displayName general en la tabla
        display_general = next(d for s, d in PATRONES if s == sufijo)
        # Si solo hay un miembro, no tiene sentido generalizar
        if len(miembros) <= 1:
            resultado.extend(miembros)
            continue

        repr_block = miembros[0]
        variantes = [
            {
                "name": m["name"],
                "displayName": m["displayName"],
                "id": m["id"],
                "variant": detectar_variante(m["name"], sufijo),
            }
            for m in miembros
        ]
        general = {
            **repr_block,
            "name": sufijo.lstrip("_"),
            "displayName": display_general,
            "variants": variantes,
            "is_family": True,
        }
        # Quitamos campos que ya no son representativos
        general.pop("states", None)
        general.pop("harvestTools", None)
        general.pop("drops", None)
        resultado.append(general)

    return resultado


def main() -> None:
    raiz = Path(__file__).parent.parent
    entrada = raiz / "data" / "blocks.json"
    salida = raiz / "data" / "blocks_general.json"

    with entrada.open("r", encoding="utf-8") as f:
        bloques = json.load(f)

    generalizado = generalizar(bloques)

    with salida.open("w", encoding="utf-8") as f:
        json.dump(generalizado, f, indent=2, ensure_ascii=False)

    print(f"Originales:    {len(bloques)} bloques")
    print(f"Generalizados: {len(generalizado)} bloques")
    print(f"Familias creadas:")
    for b in generalizado:
        if b.get("is_family"):
            n = len(b["variants"])
            print(f"  - {b['displayName']:25s} ({n} variantes)")
    print(f"\nGuardado en: {salida}")


if __name__ == "__main__":
    main()
