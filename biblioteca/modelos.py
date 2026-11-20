"""Modelos de datos (estructuras que viajan entre capas)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Libro:
    id: int
    titulo: str
    autor: str
    editorial: str
    anio: int
    cantidad: int       # ejemplares totales que posee la biblioteca
    disponibles: int    # ejemplares que no están prestados


@dataclass
class Usuario:
    id: int
    nombre: str
    apellido: str
    direccion: str
    telefono: str

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


@dataclass
class Prestamo:
    id: int
    libro_id: int
    usuario_id: int
    fecha_prestamo: str
    fecha_vencimiento: str
    fecha_devolucion: Optional[str]
    libro_titulo: str
    usuario_nombre: str

    @property
    def vigente(self):
        return self.fecha_devolucion is None

    @property
    def vencido(self):
        return self.vigente and date.fromisoformat(self.fecha_vencimiento) < date.today()

    @property
    def estado(self):
        if not self.vigente:
            return "Devuelto"
        return "VENCIDO" if self.vencido else "Vigente"

    @property
    def dias_retraso(self):
        """Días de atraso hasta hoy (si sigue vigente) o hasta la devolución."""
        referencia = (
            date.fromisoformat(self.fecha_devolucion) if self.fecha_devolucion else date.today()
        )
        return max(0, (referencia - date.fromisoformat(self.fecha_vencimiento)).days)
