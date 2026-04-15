import json
import os # Importamos 'os' para manejar rutas de archivos correctamente

class JuegoAdivina:
    def __init__(self, ruta_json):
        with open(ruta_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            
        self.bloques = datos['bloques']
        self.atributos = datos['atributos']
        self.plantilla = datos['plantilla_pregunta']
        
        # Estado del juego
        self.posibles_bloques = self.bloques.copy()
        self.atributos_usados = set()

    def generar_pregunta(self, id_atributo):
        """Genera la pregunta usando la plantilla y los datos del atributo."""
        attr = self.atributos[id_atributo]
        return self.plantilla.format(accion=attr['accion'], caracteristica=attr['caracteristica'])

    def obtener_mejor_atributo(self):
        """Busca el atributo que divida el set restante lo más cercano al 50/50 (Entropía/Ganancia de Info)."""
        mejor_attr = None
        mejor_diferencia = float('inf')
        mitad = len(self.posibles_bloques) / 2

        for attr_id in self.atributos:
            if attr_id in self.atributos_usados:
                continue
            
            # Contar cuántos bloques restantes tienen esta conexión en el grafo
            con_attr = sum(1 for b in self.posibles_bloques if attr_id in b['conexiones'])
            
            # Ignorar preguntas que no dividen el grupo (todos o ninguno lo tienen)
            if con_attr == 0 or con_attr == len(self.posibles_bloques):
                continue

            diferencia = abs(mitad - con_attr)
            if diferencia < mejor_diferencia:
                mejor_diferencia = diferencia
                mejor_attr = attr_id

        return mejor_attr

    def filtrar_bloques(self, id_atributo, tiene_atributo):
        """Filtra el subgrafo eliminando los nodos (bloques) que no cumplen la condición."""
        self.posibles_bloques = [
            b for b in self.posibles_bloques 
            if (id_atributo in b['conexiones']) == tiene_atributo
        ]
        self.atributos_usados.add(id_atributo)

    def modo_maquina_adivina(self):
        """La máquina hace las preguntas para adivinar tu bloque."""
        print("\n--- MODO: LA MÁQUINA ADIVINA ---")
        print("Piensa en un bloque de Minecraft...")
        
        while len(self.posibles_bloques) > 1:
            mejor_attr = self.obtener_mejor_atributo()
            
            # Si no hay más preguntas útiles que dividan el grupo
            if not mejor_attr:
                break
                
            pregunta = self.generar_pregunta(mejor_attr)
            respuesta = input(f"IA: {pregunta} (s/n): ").strip().lower()
            
            if respuesta == 's':
                self.filtrar_bloques(mejor_attr, True)
            elif respuesta == 'n':
                self.filtrar_bloques(mejor_attr, False)

        if len(self.posibles_bloques) == 1:
            print(f"\n¡Lo tengo! Tu bloque es: {self.posibles_bloques[0]['nombre']}")
        else:
            nombres = [b['nombre'] for b in self.posibles_bloques]
            print(f"\nEstoy dudando entre estos: {', '.join(nombres)}")

    def modo_humano_adivina(self, bloque_secreto):
        """Tú haces las preguntas eligiendo de las plantillas disponibles."""
        print("\n--- MODO: EL HUMANO ADIVINA ---")
        print("He pensado en un bloque. ¡Intenta adivinarlo!")
        
        while True:
            print("\nAtributos disponibles para preguntar:")
            disponibles = {k: v for k, v in self.atributos.items() if k not in self.atributos_usados}
            
            if not disponibles:
                print("¡Te quedaste sin preguntas!")
                break
                
            for k, v in disponibles.items():
                print(f"- [{k}]: {self.generar_pregunta(k)}")
                
            eleccion = input("\nEscribe el ID del atributo entre corchetes para preguntar (o 'rendirse'): ").strip()
            
            if eleccion == 'rendirse':
                print(f"El bloque era: {bloque_secreto['nombre']}")
                break
                
            if eleccion in disponibles:
                self.atributos_usados.add(eleccion)
                if eleccion in bloque_secreto['conexiones']:
                    print("IA: Sí.")
                else:
                    print("IA: No.")
            else:
                print("Opción no válida.")

            intento = input("¿Quieres intentar adivinar el bloque ahora? (s/n): ").strip().lower()
            if intento == 's':
                respuesta = input("Escribe el nombre del bloque: ")
                if respuesta.lower() == bloque_secreto['nombre'].lower():
                    print("¡CORRECTO! ¡Ganaste!")
                    break
                else:
                    print("Fallaste. Sigamos jugando.")

# --- Ejecución del juego ---
if __name__ == "__main__":
    # Construimos la ruta de forma segura para cualquier sistema operativo
    ruta_archivo = os.path.join("Assets", "knowledge_base.json")
    
    juego = JuegoAdivina(ruta_archivo)
    
    modo = input("Elige el modo (1: Máquina adivina, 2: Humano adivina): ").strip()
    if modo == '1':
        juego.modo_maquina_adivina()
    elif modo == '2':
        import random
        # La máquina elige un nodo de bloque al azar del grafo
        bloque_elegido = random.choice(juego.bloques)
        juego.modo_humano_adivina(bloque_elegido)