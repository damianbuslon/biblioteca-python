"""Conexión y creación del esquema de la base de datos SQLite."""
import sqlite3
from pathlib import Path

from .config import DB_PATH
from .texto import normalizar

ESQUEMA = """
CREATE TABLE IF NOT EXISTS libros (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo    TEXT    NOT NULL,
    autor     TEXT    NOT NULL,
    editorial TEXT    NOT NULL,
    anio      INTEGER NOT NULL CHECK (anio >= 1000),
    cantidad  INTEGER NOT NULL CHECK (cantidad >= 0)
);

CREATE TABLE IF NOT EXISTS usuarios (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre    TEXT NOT NULL,
    apellido  TEXT NOT NULL,
    direccion TEXT NOT NULL,
    telefono  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prestamos (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    libro_id          INTEGER NOT NULL REFERENCES libros(id)   ON DELETE CASCADE,
    usuario_id        INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    fecha_prestamo    TEXT NOT NULL,
    fecha_vencimiento TEXT NOT NULL,
    fecha_devolucion  TEXT
);

CREATE INDEX IF NOT EXISTS idx_prestamos_libro   ON prestamos(libro_id);
CREATE INDEX IF NOT EXISTS idx_prestamos_usuario ON prestamos(usuario_id);
"""


class Database:
    """Envuelve la conexión SQLite. Usar ':memory:' para pruebas."""

    def __init__(self, ruta=DB_PATH):
        ruta = str(ruta)
        if ruta != ":memory:":
            Path(ruta).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(ruta)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        # Función SQL propia para buscar sin distinguir mayúsculas ni acentos.
        self.conn.create_function("normalizar", 1, normalizar, deterministic=True)
        self.conn.executescript(ESQUEMA)

    def cerrar(self):
        self.conn.close()
