"""
Servidor HTTP para la interfaz web.

Usa la stdlib (http.server) - cero dependencias externas.

Endpoints:
    GET  /                    -> sirve web/index.html
    GET  /style.css           -> CSS
    GET  /app.js              -> JS
    POST /api/start           -> inicia partida, devuelve session_id + 1a pregunta
    POST /api/answer          -> {session_id, idx, respuesta} -> siguiente paso
    POST /api/confirm         -> {session_id, acerto}        -> confirma adivinanza
    POST /api/variant         -> {session_id, variant_id}    -> guarda variante final

El estado de cada partida vive en memoria, indexado por session_id.
Para uso real con muchos jugadores deberia persistirse o expirarse, pero
para un proyecto local esta bien.
"""
import json
import secrets
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, Any, List
from urllib.parse import urlparse

from .database import cargar_bloques, es_familia, variantes
from .engine import MotorPartida
from .textures import textura_de_bloque, url_textura


WEB_DIR = Path(__file__).parent.parent / "web"
PARTIDAS: Dict[str, MotorPartida] = {}

# Tipos MIME minimos
MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
}


def _siguiente_paso(motor: MotorPartida) -> Dict[str, Any]:
    """Calcula el siguiente paso a enviar al cliente."""
    if motor.bloque_acertado is not None:
        b = motor.bloque_acertado
        return {
            "fase": "ganado",
            "bloque": _bloque_publico(b),
            "variantes": [_variante_publica(v) for v in variantes(b)] if es_familia(b) else [],
        }

    base = {
        "candidatos": motor.total_candidatos(),
        "grupos": motor.num_grupos(),
        "preview": _preview_candidatos(motor),
    }

    if not motor.listo_para_adivinar():
        siguiente = motor.proxima_pregunta()
        if siguiente is not None:
            idx, texto = siguiente
            return {**base, "fase": "pregunta", "idx": idx, "texto": texto}

    # Fase de adivinanza
    prop = motor.proxima_adivinanza()
    if prop is None:
        return {**base, "fase": "perdido"}
    return {**base, "fase": "adivinanza", "bloque": _bloque_publico(prop)}


def _preview_candidatos(motor: MotorPartida, limite: int = 24) -> List[Dict[str, Any]]:
    """Si quedan pocos candidatos, los devolvemos para mostrarlos como mosaico."""
    if motor.total_candidatos() > limite:
        return []
    return [_bloque_publico(b) for b in motor.candidatos_actuales()]


def _bloque_publico(b: Dict[str, Any]) -> Dict[str, Any]:
    """Subconjunto de campos del bloque que mandamos al cliente."""
    return {
        "id": b["id"],
        "name": b["name"],
        "displayName": b["displayName"],
        "material": b.get("material", ""),
        "hardness": b.get("hardness", 0),
        "transparent": b.get("transparent", False),
        "emitLight": b.get("emitLight", 0),
        "is_family": b.get("is_family", False),
        "textures": textura_de_bloque(b),
    }


def _variante_publica(v: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": v["id"],
        "name": v["name"],
        "displayName": v["displayName"],
        "textures": url_textura(v["name"]),
    }


class Handler(BaseHTTPRequestHandler):
    # Silencia los logs por defecto
    def log_message(self, format, *args):
        return

    def _enviar_json(self, datos: Any, codigo: int = 200) -> None:
        cuerpo = json.dumps(datos).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def _leer_json(self) -> Dict[str, Any]:
        n = int(self.headers.get("Content-Length", 0))
        crudo = self.rfile.read(n) if n else b"{}"
        try:
            return json.loads(crudo.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    # --- GET: servir archivos estaticos ---

    def do_GET(self) -> None:
        ruta = urlparse(self.path).path
        if ruta == "/":
            ruta = "/index.html"
        archivo = WEB_DIR / ruta.lstrip("/")
        try:
            archivo = archivo.resolve()
            archivo.relative_to(WEB_DIR.resolve())  # bloquea ../
        except (ValueError, OSError):
            self.send_error(404)
            return
        if not archivo.is_file():
            self.send_error(404)
            return
        mime = MIME.get(archivo.suffix, "application/octet-stream")
        datos = archivo.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    # --- POST: API ---

    def do_POST(self) -> None:
        ruta = urlparse(self.path).path
        cuerpo = self._leer_json()

        if ruta == "/api/start":
            self._start(cuerpo)
        elif ruta == "/api/answer":
            self._answer(cuerpo)
        elif ruta == "/api/confirm":
            self._confirm(cuerpo)
        elif ruta == "/api/variant":
            self._variant(cuerpo)
        else:
            self.send_error(404)

    def _start(self, cuerpo: Dict[str, Any]) -> None:
        bloques = self.server.bloques  # type: ignore[attr-defined]
        sid = secrets.token_urlsafe(8)
        motor = MotorPartida(bloques)
        PARTIDAS[sid] = motor
        self._enviar_json({
            "session_id": sid,
            "total": motor.total_candidatos(),
            **_siguiente_paso(motor),
        })

    def _answer(self, cuerpo: Dict[str, Any]) -> None:
        sid = cuerpo.get("session_id")
        motor = PARTIDAS.get(sid)
        if motor is None:
            self._enviar_json({"error": "sesion invalida"}, 400)
            return
        idx = cuerpo.get("idx")
        respuesta = cuerpo.get("respuesta")  # True / False / None
        if isinstance(idx, int):
            motor.responder(idx, respuesta)
        self._enviar_json(_siguiente_paso(motor))

    def _confirm(self, cuerpo: Dict[str, Any]) -> None:
        sid = cuerpo.get("session_id")
        motor = PARTIDAS.get(sid)
        if motor is None:
            self._enviar_json({"error": "sesion invalida"}, 400)
            return
        acerto = cuerpo.get("acerto")  # True / False / None
        motor.confirmar_adivinanza(acerto)
        self._enviar_json(_siguiente_paso(motor))

    def _variant(self, cuerpo: Dict[str, Any]) -> None:
        sid = cuerpo.get("session_id")
        motor = PARTIDAS.get(sid)
        if motor is None:
            self._enviar_json({"error": "sesion invalida"}, 400)
            return
        # Solo registramos para fines decorativos; no afecta logica
        self._enviar_json({"ok": True})


def correr(host: str = "127.0.0.1", puerto: int = 8000,
           abrir_navegador: bool = True) -> None:
    bloques = cargar_bloques()
    server = ThreadingHTTPServer((host, puerto), Handler)
    server.bloques = bloques  # type: ignore[attr-defined]

    url = f"http://{host}:{puerto}/"
    print(f"Servidor en {url}")
    print(f"Bloques cargados: {len(bloques)}")
    print("Ctrl+C para detener.\n")

    if abrir_navegador:
        webbrowser.open_new_tab(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo servidor.")
        server.server_close()
