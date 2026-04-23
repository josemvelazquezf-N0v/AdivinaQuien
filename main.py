import json
import os
import random

class Atributo:
    def __init__(self, id_atributo, pregunta, predicado):
        self.id = id_atributo
        self.pregunta = pregunta
        self.predicado = predicado

class NodoBusqueda:
    def __init__(self, bloques, atributo=None):
        self.bloques = bloques
        self.atributo = atributo
        self.si = None
        self.no = None

    def es_hoja(self):
        return self.atributo is None or len(self.bloques) <= 1

class JuegoAdivina:
    def __init__(self, ruta_json):
        self.ruta_json = ruta_json
        self.bloques = self._cargar_bloques()
        self.atributos = self._crear_atributos()
        self.reset()

    def _cargar_bloques(self):
        with open(self.ruta_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)

        if isinstance(datos, dict) and 'bloques' in datos:
            bloques = datos['bloques']
        else:
            bloques = datos

        return [b for b in bloques if isinstance(b, dict)]

    def reset(self):
        self.posibles_bloques = self.bloques.copy()
        self.atributos_usados = set()

    def _crear_atributos(self):
        atributos = [
            Atributo('diggable', '¿Se puede romper?', lambda b: bool(b.get('diggable'))),
            Atributo('transparente', '¿Se puede ver a través de él?', lambda b: bool(b.get('transparent'))),
            Atributo('emite_luz', '¿Brilla o genera luz?', lambda b: int(b.get('emitLight', 0)) > 0),
            Atributo('liquido', '¿Es un líquido como agua o lava?', lambda b: b.get('name') in ('water', 'lava') or 'liquid' in str(b.get('material', '')).lower()),
            Atributo('solido', '¿Es un bloque sólido? (no aire, no líquido)', lambda b: b.get('boundingBox') == 'block'),
            Atributo('aire', '¿Es aire?', lambda b: b.get('name') == 'air'),
            Atributo('tiene_estado', '¿Tiene variantes o niveles?', lambda b: bool(b.get('states'))),
            Atributo('filtra_luz', '¿Permite que pase algo de luz?', lambda b: int(b.get('filterLight', 0)) > 0),
            Atributo('stackable', '¿Se puede apilar en el inventario?', lambda b: int(b.get('stackSize', 0)) > 1),
            Atributo('hardness_baja', '¿Se rompe muy fácilmente?', lambda b: float(b.get('hardness', 0)) < 1.0),
            Atributo('hardness_media', '¿Se rompe con dificultad moderada?', lambda b: 1.0 <= float(b.get('hardness', 0)) < 2.5),
            Atributo('hardness_alta', '¿Es difícil de romper?', lambda b: float(b.get('hardness', 0)) >= 2.5),
        ]

        materiales = {str(b.get('material', '')).lower() for b in self.bloques}
        herramientas = [
            ('pickaxe', '¿Se extrae con pico?'),
            ('shovel', '¿Se extrae con pala?'),
            ('axe', '¿Se extrae con hacha?'),
            ('hoe', '¿Se extrae con azada?'),
        ]

        for herramienta, pregunta in herramientas:
            if any(herramienta in material for material in materiales):
                atributos.append(
                    Atributo(
                        f'material_{herramienta}',
                        pregunta,
                        lambda b, herramienta=herramienta: herramienta in str(b.get('material', '')).lower()
                    )
                )

        if any('wool' in material for material in materiales):
            atributos.append(Atributo('material_wool', '¿Es de lana?', lambda b: 'wool' in str(b.get('material', '')).lower()))
        if any('plant' in material for material in materiales):
            atributos.append(Atributo('material_plant', '¿Es una planta o algo vegetal?', lambda b: 'plant' in str(b.get('material', '')).lower()))
        if any('leaves' in material for material in materiales):
            atributos.append(Atributo('material_leaves', '¿Son hojas o un árbol?', lambda b: 'leaves' in str(b.get('material', '')).lower()))

        return atributos

        materiales = {str(b.get('material', '')).lower() for b in self.bloques}
        herramientas = [
            ('pickaxe', '¿Se extrae con pico?'),
            ('shovel', '¿Se extrae con pala?'),
            ('axe', '¿Se tala con hacha?'),
            ('hand', '¿Se puede romper con la mano?'),
        ]

        for herramienta, pregunta in herramientas:
            if any(herramienta in material for material in materiales):
                atributos.append(
                    Atributo(
                        f'material_{herramienta}',
                        pregunta,
                        lambda b, herramienta=herramienta: herramienta in str(b.get('material', '')).lower()
                    )
                )

        return atributos

    def obtener_mejor_atributo(self, bloques, atributos):
        mejor_atributo = None
        mejor_diferencia = float('inf')
        mitad = len(bloques) / 2

        for atributo in atributos:
            verdadero = sum(1 for b in bloques if atributo.predicado(b))
            if verdadero == 0 or verdadero == len(bloques):
                continue

            diferencia = abs(mitad - verdadero)
            if diferencia < mejor_diferencia:
                mejor_diferencia = diferencia
                mejor_atributo = atributo

        return mejor_atributo

    def construir_arbol_busqueda(self, bloques=None, atributos=None):
        bloques = self.bloques if bloques is None else bloques
        atributos = self.atributos if atributos is None else atributos

        if len(bloques) <= 1 or not atributos:
            return NodoBusqueda(bloques)

        atributo = self.obtener_mejor_atributo(bloques, atributos)
        if not atributo:
            return NodoBusqueda(bloques)

        nodo = NodoBusqueda(bloques, atributo)
        si_bloques = [b for b in bloques if atributo.predicado(b)]
        no_bloques = [b for b in bloques if not atributo.predicado(b)]

        nodo.si = self.construir_arbol_busqueda(si_bloques, [a for a in atributos if a.id != atributo.id])
        nodo.no = self.construir_arbol_busqueda(no_bloques, [a for a in atributos if a.id != atributo.id])
        return nodo

    def filtrar_bloques(self, atributo, tiene):
        self.posibles_bloques = [
            b for b in self.posibles_bloques
            if atributo.predicado(b) == tiene
        ]
        self.atributos_usados.add(atributo.id)

    def generar_pregunta(self, atributo):
        return atributo.pregunta

    def nombre_bloque(self, bloque):
        return str(bloque.get('displayName') or bloque.get('name') or bloque.get('nombre'))

    def modo_maquina_adivina(self):
        self.reset()
        print('\n--- MODO: LA MÁQUINA ADIVINA ---')
        print('Piensa en un bloque de Minecraft que exista en Assets/blocks.json.')

        atributos_disponibles = self.atributos.copy()
        while len(self.posibles_bloques) > 1 and atributos_disponibles:
            atributo = self.obtener_mejor_atributo(self.posibles_bloques, atributos_disponibles)
            if not atributo:
                break

            respuesta = self._leer_respuesta(f'IA: {atributo.pregunta} (s/n): ')
            if respuesta is None:
                print('Respuesta no válida. Por favor escribe "s" o "n".')
                continue

            self.filtrar_bloques(atributo, respuesta)
            atributos_disponibles = [a for a in atributos_disponibles if a.id != atributo.id]

        if len(self.posibles_bloques) == 1:
            print(f'\n¡Lo tengo! Tu bloque es: {self.nombre_bloque(self.posibles_bloques[0])}')
            return

        if self.posibles_bloques:
            self._adivinar_bloque_final(self.posibles_bloques)
        else:
            print('\nNo pude adivinar el bloque con esas respuestas.')

    def modo_humano_adivina(self, bloque_secreto):
        self.reset()
        print('\n--- MODO: EL HUMANO ADIVINA ---')
        print('He pensado en un bloque de Minecraft. ¡Haz preguntas sobre sus atributos!')
        print('Escribe "lista" para ver bloques posibles o "rendirse" para terminar.')

        while True:
            self._mostrar_atributos_disponibles()
            eleccion = input('\nElige el ID del atributo para preguntar, "lista" o "rendirse": ').strip().lower()

            if eleccion == 'rendirse':
                print(f'El bloque era: {self.nombre_bloque(bloque_secreto)}')
                break
            if eleccion == 'lista':
                self._mostrar_bloques_posibles()
                continue

            atributo = next((a for a in self.atributos if a.id == eleccion), None)
            if not atributo or atributo.id in self.atributos_usados:
                print('Opción no válida o atributo ya usado. Intenta de nuevo.')
                continue

            self.atributos_usados.add(atributo.id)
            if atributo.predicado(bloque_secreto):
                print('IA: Sí.')
            else:
                print('IA: No.')

            if self._preguntar_adivinar():
                intento = input('Escribe el nombre del bloque: ').strip().lower()
                if intento == self.nombre_bloque(bloque_secreto).lower() or intento == str(bloque_secreto.get('name', '')).lower():
                    print('¡CORRECTO! ¡Ganaste!')
                    break
                print('Fallaste. Sigamos jugando.')

            if len(self.atributos_usados) == len(self.atributos):
                print('No quedan más atributos para preguntar.')
                print(f'El bloque era: {self.nombre_bloque(bloque_secreto)}')
                break

    def _leer_respuesta(self, pregunta):
        respuesta = input(pregunta).strip().lower()
        if respuesta == 's':
            return True
        if respuesta == 'n':
            return False
        return None

    def _mostrar_atributos_disponibles(self):
        print('\nAtributos disponibles:')
        for atributo in self.atributos:
            if atributo.id not in self.atributos_usados:
                print(f'- [{atributo.id}]: {atributo.pregunta}')

    def _mostrar_bloques_posibles(self, bloques=None):
        bloques = self.posibles_bloques if bloques is None else bloques
        cantidad = len(bloques)
        print(f'Hay {cantidad} bloques posibles según lo preguntado hasta ahora.')
        if cantidad <= 20:
            for bloque in bloques:
                print(f'- {self.nombre_bloque(bloque)}')
            return

        for bloque in bloques[:20]:
            print(f'- {self.nombre_bloque(bloque)}')
        print('...')

    def _preguntar_adivinar(self):
        respuesta = input('¿Quieres intentar adivinar el bloque ahora? (s/n): ').strip().lower()
        return respuesta == 's'

    def _adivinar_bloque_final(self, bloques):
        if not bloques:
            print('\nNo pude adivinar el bloque con esas respuestas.')
            return

        print(f'\nHe reducido las opciones a {len(bloques)} bloques. Voy a adivinar uno por uno.')
        for bloque in bloques:
            nombre = self.nombre_bloque(bloque)
            while True:
                respuesta = self._leer_respuesta(f'IA: ¿Tu bloque es {nombre}? (s/n): ')
                if respuesta is None:
                    print('Respuesta no válida. Por favor escribe "s" o "n".')
                    continue
                break

            if respuesta:
                print(f'\n¡Perfecto! Tu bloque es: {nombre}')
                return

        print('\nNo pude adivinar con certeza. Estas fueron las opciones restantes:')
        self._mostrar_bloques_posibles(bloques)

    def _mostrar_resultados_parciales(self, bloques=None):
        bloques = self.posibles_bloques if bloques is None else bloques
        cantidad = len(bloques)
        if cantidad == 0:
            print('\nNo pude adivinar el bloque con esas respuestas.')
            return

        print(f'\nEstoy dudando entre {cantidad} bloques:')
        for bloque in bloques[:10]:
            print(f'- {self.nombre_bloque(bloque)}')
        if cantidad > 10:
            print('...')

if __name__ == '__main__':
    ruta_archivo = os.path.join(os.path.dirname(__file__), 'Assets', 'blocks.json')
    juego = JuegoAdivina(ruta_archivo)

    print('Bienvenido a Adivina Quién con bloques de Minecraft (terminal).')
    while True:
        modo = input('\nElige el modo:\n1) Máquina adivina\n2) Humano adivina\n3) Salir\nTu opción: ').strip()
        if modo == '1':
            juego.modo_maquina_adivina()
        elif modo == '2':
            secreto = random.choice(juego.bloques)
            juego.modo_humano_adivina(secreto)
        elif modo == '3':
            print('Gracias por jugar. ¡Hasta luego!')
            break
        else:
            print('Opción no válida. Elige 1, 2 o 3.')
