"""Excepciones propias del sistema.

Separar los tipos de error permite que la interfaz muestre mensajes claros
al usuario sin que el programa se caiga.
"""


class BibliotecaError(Exception):
    """Clase base de todos los errores controlados de la aplicación."""


class ValidacionError(BibliotecaError):
    """Un dato ingresado no cumple el formato o los límites esperados."""


class NoEncontradoError(BibliotecaError):
    """El registro solicitado (libro, usuario o préstamo) no existe."""


class ReglaNegocioError(BibliotecaError):
    """La operación es válida en formato pero viola una regla del negocio."""
