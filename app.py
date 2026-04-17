import streamlit as st
import json
import os

# Configuracion de la pagina
st.set_page_config(page_title="Minecraft Guess Who", page_icon="None")

# --- 1. Cargar Datos ---
@st.cache_data
def cargar_datos():
    ruta = os.path.join("Assets", "knowledge_base.json")
    if not os.path.exists(ruta):
        st.error(f"Error: No se encontro el archivo en {ruta}. Ejecuta el generador primero.")
        return None
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)

datos = cargar_datos()

# --- 2. Inicializar Estado ---
if 'posibles_bloques' not in st.session_state:
    st.session_state.posibles_bloques = datos['bloques'].copy() if datos else []
    st.session_state.atributos_usados = set()
    st.session_state.historial = []

def reiniciar_juego():
    st.session_state.posibles_bloques = datos['bloques'].copy()
    st.session_state.atributos_usados = set()
    st.session_state.historial = []

# --- 3. Logica del Grafo ---
def obtener_mejor_atributo():
    mejor_attr = None
    mejor_diferencia = float('inf')
    total_actual = len(st.session_state.posibles_bloques)
    if total_actual <= 1: return None
    
    mitad = total_actual / 2

    for attr_id in datos['atributos']:
        if attr_id in st.session_state.atributos_usados:
            continue
        con_attr = sum(1 for b in st.session_state.posibles_bloques if attr_id in b['conexiones'])
        if con_attr == 0 or con_attr == total_actual:
            continue

        diferencia = abs(mitad - con_attr)
        if diferencia < mejor_diferencia:
            mejor_diferencia = diferencia
            mejor_attr = attr_id
    return mejor_attr

def filtrar_bloques(id_atributo, tiene_atributo):
    attr_info = datos['atributos'][id_atributo]
    valor = "Si" if tiene_atributo else "No"
    st.session_state.historial.append(f"{attr_info['caracteristica']}: {valor}")
    
    st.session_state.posibles_bloques = [
        b for b in st.session_state.posibles_bloques 
        if (id_atributo in b['conexiones']) == tiene_atributo
    ]
    st.session_state.atributos_usados.add(id_atributo)

# --- 4. Interfaz Visual ---
st.title("Minecraft Guess Who")
st.sidebar.header("Estado del Juego")

if datos:
    total_inicial = len(datos['bloques'])
    quedan = len(st.session_state.posibles_bloques)
    progreso = 1.0 - (max(0, quedan - 1) / (total_inicial - 1))
    
    st.sidebar.progress(progreso)
    st.sidebar.write(f"Bloques restantes: {quedan}")
    
    if st.sidebar.button("Reiniciar Partida", use_container_width=True):
        reiniciar_juego()
        st.rerun()

    if st.session_state.historial:
        st.sidebar.divider()
        st.sidebar.write("Historial de respuestas:")
        for h in st.session_state.historial:
            st.sidebar.caption(h)

    # Logica Principal
    if quedan == 1:
        st.success(f"Resultado final: El bloque es {st.session_state.posibles_bloques[0]['nombre']}")
        if st.button("Jugar de nuevo"):
            reiniciar_juego()
            st.rerun()

    elif quedan == 0:
        st.error("Sin resultados: No hay bloques que coincidan con las respuestas proporcionadas.")
        if st.button("Reiniciar"):
            reiniciar_juego()
            st.rerun()

    else:
        mejor_attr = obtener_mejor_atributo()
        
        if not mejor_attr:
            nombres = [b['nombre'] for b in st.session_state.posibles_bloques]
            st.warning("No es posible filtrar mas. Posibles coincidencias:")
            st.write(", ".join(nombres))
        else:
            attr_data = datos['atributos'][mejor_attr]
            pregunta = datos['plantilla_pregunta'].format(
                accion=attr_data['accion'], 
                caracteristica=attr_data['caracteristica']
            )
            
            with st.container(border=True):
                st.subheader(f"IA: {pregunta}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("SI", use_container_width=True, type="primary"):
                        filtrar_bloques(mejor_attr, True)
                        st.rerun()
                with col2:
                    if st.button("NO", use_container_width=True):
                        filtrar_bloques(mejor_attr, False)
                        st.rerun()

    with st.expander("Lista de bloques posibles"):
        cols = st.columns(3)
        for i, b in enumerate(st.session_state.posibles_bloques):
            cols[i % 3].caption(f"- {b['nombre']}")