"""Capa de acceso a datos: aquí vive todo el SQL, y nada de reglas de negocio."""
from .libro_repositorio import LibroRepositorio
from .prestamo_repositorio import PrestamoRepositorio
from .usuario_repositorio import UsuarioRepositorio

__all__ = ["LibroRepositorio", "UsuarioRepositorio", "PrestamoRepositorio"]
