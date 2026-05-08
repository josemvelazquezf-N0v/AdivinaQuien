import json
import os
import random

class Atributo:
    def __init__(self, id_atributo, pregunta, predicado):
        self.id = id_atributo
        self.pregunta = pregunta
        self.predicado = predicado

class JuegoAdivina:
    def __init__(self, ruta_json, ruta_frecuencias):
        self.ruta_json = ruta_json
        self.ruta_frecuencias = ruta_frecuencias
        self.frecuencias = self._cargar_frecuencias()
        self.bloques = self._cargar_bloques()
        self.atributos = self._crear_atributos()
        self.reset()

    def _cargar_frecuencias(self):
        """Carga el historial de bloques más elegidos desde un JSON."""
        if os.path.exists(self.ruta_frecuencias):
            try:
                with open(self.ruta_frecuencias, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _guardar_frecuencia(self, id_bloque):
        """Aumenta el contador del bloque adivinado y guarda el JSON."""
        if id_bloque is None:
            return
            
        str_id = str(id_bloque)
        self.frecuencias[str_id] = self.frecuencias.get(str_id, 0) + 1
        
        with open(self.ruta_frecuencias, 'w', encoding='utf-8') as f:
            json.dump(self.frecuencias, f, indent=4)

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
            # Propiedades físicas básicas
            Atributo('diggable', '¿Se puede romper o minar?', lambda b: bool(b.get('diggable', True))),
            Atributo('transparente', '¿Es transparente o deja pasar la luz (ej: vidrio, hojas)?', lambda b: bool(b.get('transparent'))),
            Atributo('emite_luz', '¿Emite luz propia?', lambda b: int(b.get('emitLight', 0)) > 0),
            Atributo('solido', '¿Es un bloque de forma completa (cubo sólido)?', lambda b: b.get('boundingBox') == 'block'),
            Atributo('stackable', '¿Se apila en grupos de 64?', lambda b: int(b.get('stackSize', 64)) > 1),
            Atributo('irrompible', '¿Es prácticamente irrompible (ej: Bedrock)?', lambda b: float(b.get('hardness', 0)) < 0),
            
            # Categorías temáticas e inteligentes
            Atributo('es_madera', '¿Es un bloque de madera (tronco, tablones, etc)?', lambda b: any(p in str(b.get('name','')).lower() for p in ['wood', 'log', 'planks', 'oak', 'birch'])),
            Atributo('es_piedra', '¿Es un tipo de piedra, roca o mineral?', lambda b: any(p in str(b.get('name','')).lower() for p in ['stone', 'cobblestone', 'ore', 'granite', 'diorite', 'andesite', 'deepslate'])),
            Atributo('es_mineral', '¿Es un mineral precioso u obtenido de uno (hierro, oro, diamante)?', lambda b: any(p in str(b.get('name','')).lower() for p in ['ore', 'diamond', 'gold', 'iron', 'emerald', 'copper', 'lapis'])),
            Atributo('es_vegetacion', '¿Es vegetación, planta o parte de un árbol?', lambda b: any(p in str(b.get('name','')).lower() for p in ['leaves', 'flower', 'sapling', 'grass', 'plant'])),
            Atributo('del_nether', '¿Proviene de la dimensión del Nether?', lambda b: any(p in str(b.get('name','')).lower() for p in ['nether', 'soul', 'crimson', 'warped', 'quartz', 'blackstone', 'magma'])),
            Atributo('del_end', '¿Proviene de la dimensión del End?', lambda b: any(p in str(b.get('name','')).lower() for p in ['end', 'purpur', 'chorus', 'shulker'])),
            Atributo('redstone', '¿Es un componente de Redstone o mecanismo?', lambda b: any(p in str(b.get('name','')).lower() for p in ['redstone', 'piston', 'observer', 'repeater', 'comparator', 'dispenser', 'dropper', 'hopper'])),
            Atributo('utilidad', '¿Es un bloque funcional donde puedes interactuar (mesas, hornos, cofres)?', lambda b: any(p in str(b.get('name','')).lower() for p in ['chest', 'table', 'furnace', 'anvil', 'barrel', 'smoker'])),
            Atributo('liquido', '¿Es un líquido (agua o lava)?', lambda b: b.get('name') in ('water', 'lava')),
        ]

        herramientas = [
            ('pickaxe', '¿Se rompe más rápido usando un PICO?'),
            ('shovel', '¿Se rompe más rápido usando una PALA?'),
            ('axe', '¿Se rompe más rápido usando un HACHA?'),
            ('hoe', '¿Se rompe más rápido usando una AZADA?'),
        ]

        for herramienta, pregunta in herramientas:
            atributos.append(
                Atributo(
                    f'herramienta_{herramienta}',
                    pregunta,
                    lambda b, h=herramienta: h in str(b.get('material', '')).lower()
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

    def filtrar_bloques(self, atributo, tiene):
        self.posibles_bloques = [
            b for b in self.posibles_bloques
            if atributo.predicado(b) == tiene
        ]
        self.atributos_usados.add(atributo.id)

    def nombre_bloque(self, bloque):
        return str(bloque.get('displayName') or bloque.get('name') or bloque.get('nombre'))

    def modo_maquina_adivina(self):
        self.reset()
        print('\n--- MODO: LA MÁQUINA ADIVINA ---')
        print('Piensa en un bloque de Minecraft que exista en la lista.')

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
            bloque_final = self.posibles_bloques[0]
            nombre = self.nombre_bloque(bloque_final)
            
            while True:
                respuesta = self._leer_respuesta(f'\nIA: ¿Estoy pensando en... {nombre}? (s/n): ')
                if respuesta is None:
                    continue
                break
                
            if respuesta:
                print('¡Lo sabía! He aprendido de esta partida.')
                self._guardar_frecuencia(bloque_final.get('id'))
            else:
                print('Vaya, parece que me he equivocado de bloque o has respondido algo distinto.')
            return

        if self.posibles_bloques:
            self._adivinar_bloque_final(self.posibles_bloques)
        else:
            print('\nNo pude adivinar el bloque con esas respuestas.')

    def modo_humano_adivina(self, bloque_secreto):
        # Mantiene la misma lógica anterior del modo humano
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

        # APRENDIZAJE: Ordena los bloques según su frecuencia histórica de mayor a menor
        bloques_ordenados = sorted(bloques, key=lambda b: self.frecuencias.get(str(b.get('id')), 0), reverse=True)

        print(f'\nHe reducido las opciones a {len(bloques_ordenados)} bloques. Preguntaré por los más comunes primero.')
        for bloque in bloques_ordenados:
            nombre = self.nombre_bloque(bloque)
            while True:
                respuesta = self._leer_respuesta(f'IA: ¿Tu bloque es {nombre}? (s/n): ')
                if respuesta is None:
                    print('Respuesta no válida. Por favor escribe "s" o "n".')
                    continue
                break

            if respuesta:
                print(f'\n¡Perfecto! Tu bloque es: {nombre}')
                self._guardar_frecuencia(bloque.get('id'))
                return

        print('\nNo pude adivinar con certeza. Estas fueron las opciones restantes:')
        self._mostrar_bloques_posibles(bloques_ordenados)

if __name__ == '__main__':
    # Rutas dinámicas para la carpeta Assets
    ruta_assets = os.path.join(os.path.dirname(__file__), 'Assets')
    if not os.path.exists(ruta_assets):
        os.makedirs(ruta_assets)
        
    ruta_archivo = os.path.join(ruta_assets, 'blocks.json')
    ruta_frecuencias = os.path.join(ruta_assets, 'frecuencias.json')
    
    juego = JuegoAdivina(ruta_archivo, ruta_frecuencias)

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