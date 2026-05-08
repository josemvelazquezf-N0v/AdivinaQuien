"""
Banco de preguntas para el Adivina Quien.

Cada pregunta es una tupla (texto, predicado) donde el predicado
es una funcion que recibe un bloque (dict) y devuelve True/False.

Para agregar preguntas nuevas basta con anadir una entrada a PREGUNTAS.
"""
from typing import Callable, Dict, Any, List, Tuple

Predicado = Callable[[Dict[str, Any]], bool]
Pregunta = Tuple[str, Predicado]


def _contiene(bloque: Dict[str, Any], palabra: str) -> bool:
    """Util: True si el name o displayName del bloque contiene la palabra."""
    palabra = palabra.lower()
    return (
        palabra in bloque.get("name", "").lower()
        or palabra in bloque.get("displayName", "").lower()
    )


# Lista de preguntas disponibles. (texto, predicado)
PREGUNTAS: List[Pregunta] = [
    # --- Propiedades fisicas ---
    ("¿Es transparente?", lambda b: b.get("transparent", False)),
    ("¿Se puede excavar/romper?", lambda b: b.get("diggable", False)),
    ("¿Emite luz propia?", lambda b: b.get("emitLight", 0) > 0),
    ("¿Bloquea totalmente la luz?", lambda b: b.get("filterLight", 0) >= 15),
    ("¿Es muy duro (hardness > 3)?", lambda b: b.get("hardness", 0) > 3),
    ("¿Es practicamente irrompible (hardness >= 50)?", lambda b: b.get("hardness", 0) >= 50),
    ("¿Es muy resistente a explosiones (resistance > 6)?", lambda b: b.get("resistance", 0) > 6),
    ("¿Tiene caja delimitadora completa (es un bloque solido)?",
     lambda b: b.get("boundingBox") == "block"),
    ("¿Se apila en grupos pequenos (stackSize < 64)?",
     lambda b: b.get("stackSize", 64) < 64),
    ("¿Suelta algo al romperlo?", lambda b: len(b.get("drops", [])) > 0),

    # --- Material / herramienta ---
    ("¿Se mina con pico?", lambda b: "mineable/pickaxe" in b.get("material", "")),
    ("¿Se mina con hacha?", lambda b: "mineable/axe" in b.get("material", "")),
    ("¿Se mina con pala?", lambda b: "mineable/shovel" in b.get("material", "")),
    ("¿Se rompe mas rapido con hoz/azada?", lambda b: "mineable/hoe" in b.get("material", "")),
    ("¿Es una planta?", lambda b: "plant" in b.get("material", "")),
    ("¿Es de lana?", lambda b: b.get("material") == "wool"),
    ("¿Es una hoja de arbol?", lambda b: "leaves" in b.get("material", "")),

    # --- Categorias por nombre ---
    ("¿Es un tipo de madera (su nombre incluye 'wood' o 'log' o 'plank')?",
     lambda b: _contiene(b, "wood") or _contiene(b, "log") or _contiene(b, "plank")),
    ("¿Es un tipo de piedra (su nombre incluye 'stone')?",
     lambda b: _contiene(b, "stone")),
    ("¿Es un mineral (su nombre incluye 'ore')?",
     lambda b: _contiene(b, "ore")),
    ("¿Es un tipo de ladrillo ('brick')?",
     lambda b: _contiene(b, "brick")),
    ("¿Es de cristal ('glass')?", lambda b: _contiene(b, "glass")),
    ("¿Es una losa ('slab')?", lambda b: _contiene(b, "slab")),
    ("¿Es una escalera ('stairs')?", lambda b: _contiene(b, "stairs")),
    ("¿Es una valla o puerta ('fence', 'gate', 'door')?",
     lambda b: _contiene(b, "fence") or _contiene(b, "gate") or _contiene(b, "door")),
    ("¿Esta relacionado con agua o lava?",
     lambda b: _contiene(b, "water") or _contiene(b, "lava")),
    ("¿Es de coral?", lambda b: _contiene(b, "coral")),
    ("¿Es una flor o cultivo?",
     lambda b: any(_contiene(b, p) for p in ["flower", "tulip", "rose", "wheat", "carrot", "potato"])),
    ("¿Tiene 'deepslate' en el nombre?", lambda b: _contiene(b, "deepslate")),
    ("¿Tiene 'nether' en el nombre?", lambda b: _contiene(b, "nether")),
    ("¿Tiene 'end' en el nombre (relacionado al End)?",
     lambda b: b.get("name", "").startswith("end_") or "end_stone" in b.get("name", "")),

    # --- Colores (utiles para lana, concreto, vidrio tenido, terracota, etc.) ---
    ("¿Es de un color claro (blanco, amarillo, rosa, verde lima, naranja)?",
     lambda b: any(_contiene(b, c) for c in ["white", "yellow", "pink", "lime", "orange"])),
    ("¿Es de un color oscuro (negro, gris, marron, azul oscuro)?",
     lambda b: any(_contiene(b, c) for c in ["black", "gray", "brown", "blue"])
              and not _contiene(b, "light_")),
    ("¿Su nombre incluye 'red' o 'rojo'?", lambda b: _contiene(b, "red")),
    ("¿Su nombre incluye 'blue' o 'azul'?", lambda b: _contiene(b, "blue")),
    ("¿Su nombre incluye 'green' o 'verde'?", lambda b: _contiene(b, "green")),
    ("¿Su nombre incluye 'white' o 'blanco'?", lambda b: _contiene(b, "white")),
    ("¿Su nombre incluye 'black' o 'negro'?", lambda b: _contiene(b, "black")),
    ("¿Su nombre incluye 'yellow' o 'amarillo'?", lambda b: _contiene(b, "yellow")),
    ("¿Su nombre incluye 'purple' o 'morado'?", lambda b: _contiene(b, "purple")),
    ("¿Su nombre incluye 'pink' o 'rosa'?", lambda b: _contiene(b, "pink")),
    ("¿Su nombre incluye 'orange' o 'naranja'?", lambda b: _contiene(b, "orange")),
    ("¿Su nombre incluye 'cyan' o 'cian'?", lambda b: _contiene(b, "cyan")),
    ("¿Su nombre incluye 'magenta'?", lambda b: _contiene(b, "magenta")),
    ("¿Su nombre incluye 'lime' (verde lima)?", lambda b: _contiene(b, "lime")),
    ("¿Su nombre incluye 'gray' o 'gris'?", lambda b: _contiene(b, "gray")),
    ("¿Su nombre incluye 'brown' o 'marron'?", lambda b: _contiene(b, "brown")),

    # --- Tipos de madera especificos ---
    ("¿Su nombre incluye 'oak' (roble)?", lambda b: _contiene(b, "oak")),
    ("¿Su nombre incluye 'birch' (abedul)?", lambda b: _contiene(b, "birch")),
    ("¿Su nombre incluye 'spruce' (abeto/pino)?", lambda b: _contiene(b, "spruce")),
    ("¿Su nombre incluye 'jungle' (jungla)?", lambda b: _contiene(b, "jungle")),
    ("¿Su nombre incluye 'acacia'?", lambda b: _contiene(b, "acacia")),
    ("¿Su nombre incluye 'cherry' (cerezo)?", lambda b: _contiene(b, "cherry")),
    ("¿Su nombre incluye 'bamboo' (bambu)?", lambda b: _contiene(b, "bamboo")),
    ("¿Su nombre incluye 'mangrove'?", lambda b: _contiene(b, "mangrove")),
    ("¿Su nombre incluye 'crimson' o 'warped' (madera del Nether)?",
     lambda b: _contiene(b, "crimson") or _contiene(b, "warped")),
]


def preguntas_utiles(candidatos: List[Dict[str, Any]],
                     ya_hechas: set[int]) -> List[int]:
    """Devuelve los indices de preguntas que aun discriminan candidatos.

    Una pregunta es util si parte el conjunto de candidatos en dos grupos
    no vacios (algunos responden si y otros no). Las preguntas ya hechas
    se descartan.
    """
    utiles = []
    for i, (_, pred) in enumerate(PREGUNTAS):
        if i in ya_hechas:
            continue
        n_si = sum(1 for b in candidatos if pred(b))
        if 0 < n_si < len(candidatos):
            utiles.append(i)
    return utiles
