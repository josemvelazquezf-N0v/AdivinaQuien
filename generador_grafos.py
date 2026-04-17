import json
import os

def crear_base_conocimiento():
    # 1. Rutas de archivos
    ruta_raw = os.path.join("Assets", "blocks.json")
    ruta_grafo = os.path.join("Assets", "knowledge_base.json")
    
    # 2. Cargar datos crudos
    with open(ruta_raw, 'r', encoding='utf-8') as f:
        bloques_crudos = json.load(f)
        
    # 3. Definir tu plantilla y atributos (La base del grafo)
    grafo = {
        "plantilla_pregunta": "¿El bloque secreto {accion} {caracteristica}?",
        "atributos": {
            "emite_luz": {"accion": "emite", "caracteristica": "luz propia"},
            "es_transparente": {"accion": "es", "caracteristica": "transparente al menos en una parte"},
            "se_puede_minar": {"accion": "es", "caracteristica": "rompible (no es bedrock)"},
            "es_inflamable": {"accion": "puede", "caracteristica": "prenderse en fuego"}
        },
        "bloques": []
    }
    
    # 4. Filtrar y procesar (Ejemplo: tomar solo los primeros 100 bloques válidos)
    bloques_procesados = 0
    
    for b in bloques_crudos:
        if bloques_procesados >= 100:
            break
            
        # Omitir bloques de aire o nulos
        if b['name'] == 'air':
            continue
            
        conexiones = []
        
        # Mapear variables originales a tus nodos de atributo
        if b.get('emitLight', 0) > 0:
            conexiones.append('emite_luz')
            
        if b.get('transparent', False) == True:
            conexiones.append('es_transparente')
            
        if b.get('diggable', True) == True:
            conexiones.append('se_puede_minar')
            
        # Agregar bloque al grafo
        grafo['bloques'].append({
            "nombre": b['displayName'],  # Usa el nombre bonito con mayúsculas
            "conexiones": conexiones
        })
        
        bloques_procesados += 1

    # 5. Guardar el nuevo grafo generado
    with open(ruta_grafo, 'w', encoding='utf-8') as f:
        json.dump(grafo, f, indent=4, ensure_ascii=False)
        
    print(f"¡Grafo generado con éxito! Se procesaron {len(grafo['bloques'])} bloques.")

if __name__ == "__main__":
    crear_base_conocimiento()