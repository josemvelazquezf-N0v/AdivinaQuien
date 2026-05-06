"""
Interfaz por consola (CLI) del juego.

Es solo una capa de I/O sobre `MotorPartida`. Toda la logica esta en
`engine.py`, asi puede compartirse con la interfaz web.
"""
from typing import Optional, List, Dict, Any

from .database import es_familia, variantes
from .engine import MotorPartida


SI = {"s", "si", "sí", "y", "yes", "1", "true"}
NO = {"n", "no", "0", "false"}
NO_SE = {"x", "no se", "no sé", "ns", "skip", "?"}


def _leer(prompt: str) -> Optional[bool]:
    while True:
        r = input(prompt).strip().lower()
        if r in SI:
            return True
        if r in NO:
            return False
        if r in NO_SE:
            return None
        print("  (Responde 's', 'n' o 'x')")


def _preguntar_variante(bloque: Dict[str, Any]) -> None:
    """Si el bloque acertado tiene variantes, pregunta cual era."""
    vs: List[Dict[str, Any]] = variantes(bloque)
    if not vs:
        return
    print(f"\nGenial. {bloque['displayName']} viene en varias variantes:")
    for i, v in enumerate(vs, 1):
        print(f"  {i:2d}. {v['displayName']}")
    while True:
        s = input("¿Cual era la tuya? (numero o enter para saltar): ").strip()
        if not s:
            return
        if s.isdigit() and 1 <= int(s) <= len(vs):
            print(f"Anotado: {vs[int(s) - 1]['displayName']}.")
            return
        print("  (Numero invalido)")


def jugar_cli(bloques: List[Dict[str, Any]], max_preguntas: int = 25) -> None:
    motor = MotorPartida(bloques)

    print("=" * 60)
    print("  ADIVINA QUIEN - EDICION MINECRAFT")
    print("=" * 60)
    print(f"Piensa en un bloque (de {len(bloques)} familias posibles).")
    print("Responde con: s (si), n (no), x (no se / saltar)\n")

    turno = 0
    while not motor.listo_para_adivinar() and turno < max_preguntas:
        turno += 1
        siguiente = motor.proxima_pregunta()
        if siguiente is None:
            break
        idx, texto = siguiente
        print(f"[Pregunta {turno}] {texto}")
        print(f"  ({motor.total_candidatos()} candidatos restantes)")
        resp = _leer("  > ")
        motor.responder(idx, resp)
        print()

    # Fase de adivinanza
    while True:
        prop = motor.proxima_adivinanza()
        if prop is None:
            print("\nMe rindo, no logre adivinar.")
            return
        print(f"¿Tu bloque es '{prop['displayName']}'?")
        r = _leer("  > ")
        motor.confirmar_adivinanza(r)
        if motor.bloque_acertado:
            print("\n¡Te gane!")
            _preguntar_variante(motor.bloque_acertado)
            return
