"""
Punto de entrada principal: arranca el servidor web y abre el juego en el
navegador en una pestana nueva.

    python main.py

Opciones:
    --host 0.0.0.0    -> aceptar conexiones desde otras maquinas (LAN)
    --port 8080       -> usar otro puerto
    --no-open         -> no abrir el navegador automaticamente
"""
import argparse
from src.server import correr


def main() -> None:
    parser = argparse.ArgumentParser(description="Adivina el Bloque - servidor web")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-open", action="store_true",
                        help="No abrir el navegador automaticamente")
    args = parser.parse_args()

    correr(host=args.host, puerto=args.port, abrir_navegador=not args.no_open)


if __name__ == "__main__":
    main()
