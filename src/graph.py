"""
Grafo de bloques.

Cada bloque es un nodo. Hay una arista entre dos bloques si comparten
algun atributo "categoria" (mismo material, ambos transparentes, ambos
emiten luz, etc.). Esto permite:

  - Mantener un subgrafo de candidatos durante la partida.
  - Consultar vecindarios (bloques similares) cuando quedan pocos candidatos.
  - Servir de base para estrategias de pregunta mas inteligentes en el futuro
    (p. ej. elegir la pregunta que mejor parta el subgrafo).

Implementacion: lista de adyacencia con sets, sin dependencias externas.
"""
from typing import Dict, List, Any, Set, Iterable


class GrafoBloques:
    def __init__(self, bloques: List[Dict[str, Any]]):
        # nodos indexados por id de bloque
        self.nodos: Dict[int, Dict[str, Any]] = {b["id"]: b for b in bloques}
        self.ady: Dict[int, Set[int]] = {b["id"]: set() for b in bloques}
        self._construir_aristas()

    def _categorias(self, b: Dict[str, Any]) -> Set[str]:
        """Etiquetas categoricas que definen 'similitud' entre bloques."""
        cats = {f"material::{b.get('material', '')}",
                f"bbox::{b.get('boundingBox', '')}"}
        if b.get("transparent"):
            cats.add("transparente")
        if b.get("emitLight", 0) > 0:
            cats.add("emite_luz")
        if not b.get("diggable", True):
            cats.add("indestructible")
        # Bucket por dureza (categorias gruesas)
        h = b.get("hardness", 0)
        if h <= 0:
            cats.add("dureza::0")
        elif h <= 1:
            cats.add("dureza::baja")
        elif h <= 3:
            cats.add("dureza::media")
        else:
            cats.add("dureza::alta")
        return cats

    def _construir_aristas(self) -> None:
        """Conecta bloques que compartan al menos una categoria.

        Para no crear un grafo gigantesco usamos un indice invertido:
        categoria -> lista de ids. Conectamos pares dentro de cada categoria.
        """
        indice: Dict[str, List[int]] = {}
        for bid, b in self.nodos.items():
            for cat in self._categorias(b):
                indice.setdefault(cat, []).append(bid)

        for cat, ids in indice.items():
            # Saltamos categorias gigantes (poco informativas) para mantener
            # el grafo manejable: si una categoria agrupa a mas del 60% de
            # los bloques, no la usamos como fuente de aristas.
            if len(ids) > 0.6 * len(self.nodos):
                continue
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    a, b = ids[i], ids[j]
                    self.ady[a].add(b)
                    self.ady[b].add(a)

    # --- Operaciones del juego ---

    def vecinos(self, bid: int) -> Set[int]:
        return self.ady.get(bid, set())

    def subgrafo(self, ids: Iterable[int]) -> Dict[int, Set[int]]:
        """Devuelve la lista de adyacencia restringida a los ids dados."""
        ids_set = set(ids)
        return {i: (self.ady[i] & ids_set) for i in ids_set}

    def componentes(self, ids: Iterable[int]) -> List[Set[int]]:
        """Componentes conexas del subgrafo inducido por los ids."""
        sub = self.subgrafo(ids)
        visitados: Set[int] = set()
        comps: List[Set[int]] = []
        for nodo in sub:
            if nodo in visitados:
                continue
            # BFS
            comp: Set[int] = set()
            cola = [nodo]
            while cola:
                x = cola.pop()
                if x in visitados:
                    continue
                visitados.add(x)
                comp.add(x)
                cola.extend(sub[x] - visitados)
            comps.append(comp)
        return comps

    def grado(self, bid: int) -> int:
        return len(self.ady.get(bid, set()))
