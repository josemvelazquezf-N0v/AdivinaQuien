# Adivina Quien: Minecraft Edition

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Minecraft](https://img.shields.io/badge/Minecraft-1.20+-62B037?style=for-the-badge&logo=minecraft&logoColor=white)
![Status](https://img.shields.io/badge/Status-Learning_AI-orange?style=for-the-badge)

Un juego de deduccion logica basado en la terminal donde puedes desafiar a una IA o intentar adivinar los bloques mas iconicos de Minecraft. Ahora con un sistema de aprendizaje dinamico.

---

## Como Jugar

### 1. Requisitos Previos
Asegurate de tener Python instalado y los archivos organizados de la siguiente manera:

### 2. Ejecucion
Inicia el juego abriendo tu terminal en la carpeta del proyecto y ejecutando:
```bash
python main.py
```
### 3. Modos de Juego
#### La Maquina Adivina
Piensa en un bloque de la lista oficial de Minecraft.
Responde con s (si) o n (no) a las preguntas que te haga la IA.
Si la IA adivina tu bloque, este sumara puntos de frecuencia y la maquina aprendera a priorizarlo en el futuro.

#### El Humano Adivina
La IA elegira un bloque al azar y lo mantendra en secreto.
La terminal te mostrara una lista de IDs de atributos. Escribe el ID del atributo que deseas preguntar.
Puedes escribir lista en cualquier momento para ver que bloques aun coinciden con las pistas.
Cuando sepas la respuesta, escribe el nombre del bloque para intentar ganar. Escribe rendirse si no encuentras la respuesta.

### Caracteristicas Principales
IA con Entropia: La maquina no pregunta al azar; calcula matematicamente que pregunta elimina la mayor cantidad de opciones.

Sistema de Aprendizaje: Gracias al archivo frecuencias.json, la IA aprende que bloques prefieren los usuarios y ajusta su estrategia para ser mas rapida.

Duelo de Modos: Puedes tomar el rol de adivinador o dejar que la maquina lea tus respuestas.

Base de Datos Extensa: Cientos de bloques con atributos detallados (transparencia, luz, herramientas, etc.).

El Cerebro de la IA: frecuencias.json
Este proyecto implementa una forma de Machine Learning por refuerzo basico:

Cada vez que un bloque es adivinado correctamente en el modo maquina, su contador interno aumenta.

Cuando la IA llega a un punto donde varios bloques tienen las mismas caracteristicas, consultara el archivo de frecuencias.

La IA preguntara primero por el bloque mas popular, optimizando el tiempo de respuesta basandose en la popularidad y el comportamiento historico de los jugadores.

### Atributos Analizados
El motor de busqueda filtra los bloques basandose en:

Fisica: Solidez, transparencia y emision de luz.

Dimensiones: Origen del bloque (Overworld, Nether o End).

Herramientas: Si requiere pico, pala, hacha o azada para minarse de forma optima.

Categorias: Materiales como madera, roca, mineral, vegetacion o componentes de redstone.
