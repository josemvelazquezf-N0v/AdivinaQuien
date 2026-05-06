"""
Carga y manejo de la base de datos de bloques de Minecraft.

Por defecto carga la version generalizada (data/blocks_general.json) en la
que las variantes que solo difieren en color o tipo de madera estan
agrupadas en una sola entrada con un campo `variants`.
"""
import json
from pathlib import Path
from typing import List, Dict, Any


RUTA_DEFECTO = Path(__file__).parent.parent / "data" / "blocks_general.json"


def cargar_bloques(ruta: str | Path | None = None) -> List[Dict[str, Any]]:
    """Lee el JSON y devuelve la lista de bloques.

    Filtra el bloque 'air' y los que carecen de displayName.
    """
    ruta = Path(ruta) if ruta else RUTA_DEFECTO
    with ruta.open("r", encoding="utf-8") as f:
        bloques = json.load(f)

    bloques_validos = [
        b for b in bloques
        if b.get("displayName") and b.get("name") != "air"
    ]
    return bloques_validos


def es_familia(bloque: Dict[str, Any]) -> bool:
    """True si el bloque agrupa varias variantes (lana, hojas, etc.)."""
    return bool(bloque.get("is_family"))


def variantes(bloque: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Lista de variantes de un bloque familia, o [] si no es familia."""
    return bloque.get("variants", [])


def buscar_por_nombre(bloques: List[Dict[str, Any]], texto: str) -> List[Dict[str, Any]]:
    """Busca bloques cuyo displayName o name contenga el texto."""
    texto = texto.lower().strip()
    return [
        b for b in bloques
        if texto in b["displayName"].lower() or texto in b["name"].lower()
    ]
