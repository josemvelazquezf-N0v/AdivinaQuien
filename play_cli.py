"""
Modo consola del juego (sin navegador).

    python play_cli.py
"""
from src.database import cargar_bloques
from src.game import jugar_cli


if __name__ == "__main__":
    bloques = cargar_bloques()
    jugar_cli(bloques)
