"""Configuración central de la aplicación.

Todos los valores "ajustables" viven aquí, de modo que cambiar una regla
(por ejemplo, el máximo de préstamos por usuario) no exige tocar la lógica.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "datos"

# Se puede sobrescribir con la variable de entorno BIBLIOTECA_DB (útil para pruebas).
DB_PATH = Path(os.environ.get("BIBLIOTECA_DB", DATA_DIR / "biblioteca.db"))

# Reglas de negocio
MAX_PRESTAMOS_POR_USUARIO = 3
DIAS_PRESTAMO = 14
MAX_DIAS_PRESTAMO = 90

# Límites de validación
ANIO_MINIMO = 1000
MAX_CANTIDAD = 1000
