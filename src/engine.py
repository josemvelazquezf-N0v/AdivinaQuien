"""
Motor de partidas (sin I/O).

Esta clase encapsula el estado de una partida y expone metodos puros que
se pueden invocar tanto desde CLI como desde el servidor web.

Flujo de uso:

    motor = MotorPartida(bloques)
    pregunta = motor.proxima_pregunta()       # texto o None
    motor.responder(True)                     # actualiza el estado
    ...
    if motor.listo_para_adivinar():
        bloque = motor.proxima_adivinanza()   # dict bloque o None
        motor.confirmar_adivinanza(False)     # descarta y sigue
        ...
"""
import random
from typing import List, Dict, Any, Optional, Set, Tuple

from .questions import PREGUNTAS, preguntas_utiles
from .graph import GrafoBloques


class MotorPartida:
    UMBRAL_ADIVINAR = 1  # adivinamos cuando queda 1 candidato

    def __init__(self, bloques: List[Dict[str, Any]],
                 semilla: Optional[int] = None) -> None:
        self.bloques = bloques
        self.grafo = GrafoBloques(bloques)
        self.candidatos: Set[int] = {b["id"] for b in bloques}
        self.preguntas_hechas: Set[int] = set()
        self.rng = random.Random(semilla)

        # Estado de la fase de adivinanza
        self.fase_adivinar = False
        self.cola_adivinanzas: List[int] = []
        self.bloque_propuesto: Optional[int] = None

        # Estado de la fase de variantes (cuando se acerto un bloque familia)
        self.bloque_acertado: Optional[Dict[str, Any]] = None

    # ------- Estado / consultas -------

    def total_candidatos(self) -> int:
        return len(self.candidatos)

    def num_grupos(self) -> int:
        return len(self.grafo.componentes(self.candidatos))

    def candidatos_actuales(self) -> List[Dict[str, Any]]:
        return [self.grafo.nodos[i] for i in self.candidatos]

    def listo_para_adivinar(self) -> bool:
        return self.total_candidatos() <= self.UMBRAL_ADIVINAR or not self._hay_pregunta_util()

    def termino(self) -> bool:
        """La partida termino: no hay mas candidatos o ya se acerto."""
        return self.bloque_acertado is not None or self.total_candidatos() == 0

    # ------- Fase de preguntas -------

    def proxima_pregunta(self) -> Optional[Tuple[int, str]]:
        """Devuelve (indice, texto) de la siguiente pregunta, o None."""
        if self.listo_para_adivinar():
            return None
        idx = self._elegir_pregunta()
        if idx is None:
            return None
        return idx, PREGUNTAS[idx][0]

    def responder(self, idx_pregunta: int, respuesta: Optional[bool]) -> None:
        """Aplica la respuesta a la pregunta.

        respuesta = None significa "no se" (no se filtra nada).
        """
        self.preguntas_hechas.add(idx_pregunta)
        if respuesta is None:
            return
        _, pred = PREGUNTAS[idx_pregunta]
        self.candidatos = {
            bid for bid in self.candidatos
            if pred(self.grafo.nodos[bid]) == respuesta
        }

    # ------- Fase de adivinanza -------

    def proxima_adivinanza(self) -> Optional[Dict[str, Any]]:
        """Propone un bloque candidato. None si no quedan."""
        if not self.fase_adivinar:
            self._iniciar_fase_adivinar()
        while self.cola_adivinanzas:
            bid = self.cola_adivinanzas.pop(0)
            if bid in self.candidatos:
                self.bloque_propuesto = bid
                return self.grafo.nodos[bid]
        return None

    def confirmar_adivinanza(self, acerto: Optional[bool]) -> None:
        """Confirma si la adivinanza es correcta.

        acerto = True   -> guardamos el bloque acertado.
        acerto = False  -> descartamos ese candidato.
        acerto = None   -> "no se", lo dejamos para el final.
        """
        if self.bloque_propuesto is None:
            return
        if acerto is True:
            self.bloque_acertado = self.grafo.nodos[self.bloque_propuesto]
        elif acerto is False:
            self.candidatos.discard(self.bloque_propuesto)
        else:
            # No se: lo enviamos al final de la cola
            self.cola_adivinanzas.append(self.bloque_propuesto)
        self.bloque_propuesto = None

    # ------- Internos -------

    def _hay_pregunta_util(self) -> bool:
        utiles = preguntas_utiles(self.candidatos_actuales(), self.preguntas_hechas)
        return len(utiles) > 0

    def _elegir_pregunta(self) -> Optional[int]:
        """Estrategia actual: pregunta al azar entre las utiles."""
        utiles = preguntas_utiles(self.candidatos_actuales(), self.preguntas_hechas)
        if not utiles:
            return None
        return self.rng.choice(utiles)

    def _iniciar_fase_adivinar(self) -> None:
        self.fase_adivinar = True
        # Ordenamos por grado: bloques mas conectados son mas comunes
        self.cola_adivinanzas = sorted(
            self.candidatos, key=lambda i: -self.grafo.grado(i)
        )
