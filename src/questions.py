from typing import Callable, Dict, Any, List, Tuple

Predicado = Callable[[Dict[str, Any]], bool]
Pregunta = Tuple[str, Predicado]

def _contiene(bloque: Dict[str, Any], palabra: str) -> bool:
    """True si el name o displayName contiene la palabra (ignora mayúsculas)."""
    palabra = palabra.lower()
    return (
        palabra in bloque.get("name", "").lower()
        or palabra in bloque.get("displayName", "").lower()
    )

# Banco de preguntas optimizado para la base de datos de 300 bloques
PREGUNTAS: List[Pregunta] = [
    # --- Propiedades de juego y Físicas ---
    ("¿Es un bloque afectado por la gravedad (arena, grava, lodo)?", 
     lambda b: any(_contiene(b, p) for p in ["sand", "gravel", "mud", "arena", "grava"])),
    
    ("¿Emite luz propia (antorchas, glowstone, linternas)?", 
     lambda b: b.get("emitLight", 0) > 0 or any(_contiene(b, p) for p in ["torch", "glow", "lantern", "lamp", "fuego", "fire"])),
    
    ("¿Es transparente o deja pasar la luz (vidrio, hojas, aire)?", 
     lambda b: b.get("transparent", False) or _contiene(b, "vidrio") or _contiene(b, "glass") or _contiene(b, "hojas")),

    ("¿Es extremadamente duro o irrompible (obsidiana, bedrock, restos ancestrales)?", 
     lambda b: b.get("hardness", 0) >= 30 or b.get("hardness", 0) == -1),

    ("¿Es un líquido (agua, lava)?", 
     lambda b: any(_contiene(b, p) for p in ["water", "lava", "agua"])),

    # --- Categorías de Materiales (Simplificadas) ---
    ("¿Es un tipo de madera (tablones, troncos, vallas)?", 
     lambda b: _contiene(b, "madera") or _contiene(b, "wood") or _contiene(b, "log") or _contiene(b, "plank")),

    ("¿Es parte de la vegetación (hojas, flores, plantas, musgo)?", 
     lambda b: any(_contiene(b, p) for p in ["hojas", "leaves", "flower", "flor", "moss", "musgo", "plant", "sapling"])),

    ("¿Es un mineral 'bruto' (contiene la palabra mineral u 'ore')?", 
     lambda b: _contiene(b, "ore") or _contiene(b, "mineral")),

    ("¿Es un bloque de metal precioso o gema (bloque de diamante, oro, hierro, esmeralda)?", 
     lambda b: _contiene(b, "block") and any(_contiene(b, p) for p in ["diamond", "gold", "iron", "emerald", "netherite", "oro", "hierro"])),

    ("¿Es un tipo de piedra natural (granito, diorita, andesita, pizarra)?", 
     lambda b: any(_contiene(b, p) for p in ["stone", "granite", "diorite", "andesite", "deepslate", "piedra", "tuff", "toba"])),

    # --- Funcionalidad y Utilidad ---
    ("¿Es una mesa de trabajo o herramienta funcional (horno, mesa, yunque, atril)?", 
     lambda b: any(_contiene(b, p) for p in ["table", "mesa", "furnace", "horno", "anvil", "yunque", "smoker", "barrel", "cauldron"])),

    ("¿Sirve para almacenar objetos (cofre, barril, tolva, caja)?", 
     lambda b: any(_contiene(b, p) for p in ["chest", "barrel", "hopper", "shulker", "cofre", "barril", "tolva"])),

    ("¿Es un componente de Redstone (mecanismo, sensor, pistón, cable)?", 
     lambda b: any(_contiene(b, p) for p in ["redstone", "piston", "observer", "repeater", "comparator", "dispenser", "dropper", "target"])),

    ("¿Es un medio de transporte (raíl, vagoneta, andamio)?", 
     lambda b: any(_contiene(b, p) for p in ["rail", "scaffolding", "andamio"])),

    # --- Dimensiones ---
    ("¿Es originario del Nether (netherrack, cuarzo, piedra negra)?", 
     lambda b: any(_contiene(b, p) for p in ["nether", "quartz", "blackstone", "soul", "alma", "crimson", "warped"])),

    ("¿Es originario del End (piedra del end, purpur, huevo de dragón)?", 
     lambda b: _contiene(b, "end") or _contiene(b, "purpur") or _contiene(b, "chorus")),

    ("¿Se encuentra comúnmente bajo el agua (prismarina, coral, esponja)?", 
     lambda b: any(_contiene(b, p) for p in ["prismarine", "coral", "sponge", "esponja", "sea", "mar"])),

    # --- Formas de Construcción ---
    ("¿Es una variante decorativa (losa, escalera, muro, valla)?", 
     lambda b: any(_contiene(b, p) for p in ["slab", "losa", "stairs", "escalera", "wall", "muro", "fence", "valla"])),

    ("¿Es un tipo de ladrillo (bricks)?", 
     lambda b: _contiene(b, "brick") or _contiene(b, "ladrillo")),
]

def preguntas_utiles(candidatos: List[Dict[str, Any]], ya_hechas: set[int]) -> List[int]:
    """Calcula qué preguntas dividen mejor el grupo de candidatos restantes."""
    utiles = []
    for i, (_, pred) in enumerate(PREGUNTAS):
        if i in ya_hechas:
            continue
        n_si = sum(1 for b in candidatos if pred(b))
        # Una pregunta es útil si al menos un bloque dice SI y otro dice NO
        if 0 < n_si < len(candidatos):
            utiles.append(i)
    return utiles