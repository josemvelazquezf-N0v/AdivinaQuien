"""
Simulacion automatica de partidas para verificar la logica del motor.

    python tests/test_simulacion.py
"""
import sys
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import cargar_bloques
from src.engine import MotorPartida
from src.questions import PREGUNTAS


def simular(bloques, secreto, semilla=None, max_preg=30):
    motor = MotorPartida(bloques, semilla=semilla)
    n_preg = 0
    while not motor.listo_para_adivinar() and n_preg < max_preg:
        siguiente = motor.proxima_pregunta()
        if siguiente is None:
            break
        idx, _ = siguiente
        _, pred = PREGUNTAS[idx]
        motor.responder(idx, pred(secreto))
        n_preg += 1

    # Fase de adivinanza simulada (un "jugador" honesto que dice si solo
    # cuando la propuesta coincide con su bloque secreto)
    n_propuestas = 0
    while True:
        prop = motor.proxima_adivinanza()
        if prop is None:
            return False, n_preg, n_propuestas
        n_propuestas += 1
        if prop["id"] == secreto["id"]:
            motor.confirmar_adivinanza(True)
            return True, n_preg, n_propuestas
        motor.confirmar_adivinanza(False)


def main():
    bloques = cargar_bloques()
    print(f"Total de bloques (generalizados): {len(bloques)}\n")

    rng = random.Random(2026)
    muestras = rng.sample(bloques, 40)

    aciertos = 0
    total_p = 0
    total_prop = 0
    for b in muestras:
        ok, n_preg, n_prop = simular(bloques, b, semilla=hash(b["id"]) & 0xFFFF)
        if ok:
            aciertos += 1
        total_p += n_preg
        total_prop += n_prop
        marker = "OK  " if ok else "MISS"
        familia = " [F]" if b.get("is_family") else "    "
        print(f"  [{marker}]{familia} {b['displayName']:30s} -> {n_preg:2d} preguntas, {n_prop:2d} propuestas")

    n = len(muestras)
    print(f"\nResumen: {aciertos}/{n} adivinados")
    print(f"Promedio preguntas: {total_p/n:.1f}")
    print(f"Promedio propuestas: {total_prop/n:.1f}")


if __name__ == "__main__":
    main()
