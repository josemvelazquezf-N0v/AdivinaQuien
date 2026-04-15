import streamlit as st
import json
import os

# --- 1. Cargar Datos ---
@st.cache_data
def cargar_datos():
    ruta = os.path.join("Assets", "knowledge_base.json")
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)

datos = cargar_datos()

# --- 2. Inicializar la "Memoria" del juego ---
if 'posibles_bloques' not in st.session_state:
    st.session_state.posibles_bloques = datos['bloques'].copy()
    st.session_state.atributos_usados = set()

def reiniciar_juego():
    st.session_state.posibles_bloques = datos['bloques'].copy()
    st.session_state.atributos_usados = set()

# --- 3. Lógica del Grafo (Adaptada para la web) ---
def obtener_mejor_atributo():
    mejor_attr = None
    mejor_diferencia = float('inf')
    mitad = len(st.session_state.posibles_bloques) / 2

    for attr_id in datos['atributos']:
        if attr_id in st.session_state.atributos_usados:
            continue
        con_attr = sum(1 for b in st.session_state.posibles_bloques if attr_id in b['conexiones'])
        if con_attr == 0 or con_attr == len(st.session_state.posibles_bloques):
            continue

        diferencia = abs(mitad - con_attr)
        if diferencia < mejor_diferencia:
            mejor_diferencia = diferencia
            mejor_attr = attr_id
    return mejor_attr

def filtrar_bloques(id_atributo, tiene_atributo):
    st.session_state.posibles_bloques = [
        b for b in st.session_state.posibles_bloques 
        if (id_atributo in b['conexiones']) == tiene_atributo
    ]
    st.session_state.atributos_usados.add(id_atributo)

# --- 4. Interfaz Visual (GUI) ---
st.title("Adivina Quién: Minecraft ")
st.write("Piensa en un bloque y yo adivinaré cuál es.")

# Verificar si el juego terminó
if len(st.session_state.posibles_bloques) == 1:
    st.success(f"¡Lo tengo! Tu bloque es: **{st.session_state.posibles_bloques[0]['nombre']}**")
    st.button("Jugar de nuevo", on_click=reiniciar_juego)
    
elif len(st.session_state.posibles_bloques) == 0:
    st.error("Me quedé sin opciones. ¡Creo que pensaste en un bloque que no está en mi base de datos o respondiste mal!")
    st.button("Jugar de nuevo", on_click=reiniciar_juego)
    
else:
    mejor_attr = obtener_mejor_atributo()
    
    if not mejor_attr:
        nombres = [b['nombre'] for b in st.session_state.posibles_bloques]
        st.warning(f"Me quedé sin preguntas útiles. Estoy dudando entre: {', '.join(nombres)}")
        st.button("Jugar de nuevo", on_click=reiniciar_juego)
    else:
        # Generar la pregunta
        attr_data = datos['atributos'][mejor_attr]
        pregunta = datos['plantilla_pregunta'].format(
            accion=attr_data['accion'], 
            caracteristica=attr_data['caracteristica']
        )
        
        st.subheader(f" IA: {pregunta}")
        
        # Botones de Sí y No
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Sí", use_container_width=True):
                filtrar_bloques(mejor_attr, True)
                st.rerun() # Recarga la página con los nuevos datos
        with col2:
            if st.button("No", use_container_width=True):
                filtrar_bloques(mejor_attr, False)
                st.rerun()

    # Mostrar progreso en la parte inferior
    st.divider()
    st.write(f"Bloques posibles restantes: **{len(st.session_state.posibles_bloques)}**")