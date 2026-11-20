
from __future__ import annotations

import re
from datetime import date, datetime

from .config import ANIO_MINIMO, MAX_CANTIDAD
from .excepciones import ValidacionError

_RE_ENTERO = re.compile(r"[+-]?[0-9]+")
_RE_TELEFONO = re.compile(r"\+?[0-9\s\-()]+")


def validar_texto(valor, campo, max_len=100, min_len=1):
    """Texto obligatorio: quita espacios sobrantes y controla el largo."""
    texto = " ".join(str(valor if valor is not None else "").split())
    if not texto:
        raise ValidacionError(f"{campo} es obligatorio.")
    if len(texto) < min_len:
        raise ValidacionError(f"{campo} debe tener al menos {min_len} caracteres.")
    if len(texto) > max_len:
        raise ValidacionError(f"{campo} no puede superar {max_len} caracteres.")
    return texto


def validar_entero(valor, campo, minimo=None, maximo=None):
    """Convierte a int de forma estricta (solo dígitos con signo opcional)."""
    texto = str(valor).strip()
    if not _RE_ENTERO.fullmatch(texto):
        raise ValidacionError(f"{campo} debe ser un número entero.")
    numero = int(texto)
    if minimo is not None and maximo is not None and not (minimo <= numero <= maximo):
        raise ValidacionError(f"{campo} debe estar entre {minimo} y {maximo}.")
    if minimo is not None and numero < minimo:
        raise ValidacionError(f"{campo} debe ser mayor o igual a {minimo}.")
    if maximo is not None and numero > maximo:
        raise ValidacionError(f"{campo} debe ser menor o igual a {maximo}.")
    return numero


def validar_id(valor, campo="ID"):
    return validar_entero(valor, campo, minimo=1)


def validar_anio(valor):
    return validar_entero(valor, "Año de publicación", ANIO_MINIMO, date.today().year)


def validar_cantidad(valor):
    return validar_entero(valor, "Cantidad de ejemplares", 1, MAX_CANTIDAD)


def validar_titulo(valor):
    return validar_texto(valor, "Título", 150)


def validar_autor(valor):
    return validar_texto(valor, "Autor", 100)


def validar_editorial(valor):
    return validar_texto(valor, "Editorial", 100)


def _validar_nombre_persona(valor, campo):
    texto = validar_texto(valor, campo, 50)
    if not texto[0].isalpha() or not all(c.isalpha() or c in " '-." for c in texto):
        raise ValidacionError(
            f"{campo} solo puede contener letras, espacios, guiones y apóstrofes."
        )
    return texto


def validar_nombre(valor):
    return _validar_nombre_persona(valor, "Nombre")


def validar_apellido(valor):
    return _validar_nombre_persona(valor, "Apellido")


def validar_direccion(valor):
    return validar_texto(valor, "Dirección", 150, min_len=5)


def validar_telefono(valor):
    """Acepta dígitos, espacios, guiones, paréntesis y un '+' inicial (7 a 15 dígitos)."""
    texto = validar_texto(valor, "Teléfono", 20)
    if not _RE_TELEFONO.fullmatch(texto):
        raise ValidacionError(
            "Teléfono solo puede contener números, espacios, guiones, paréntesis y '+' inicial."
        )
    digitos = sum(c.isdigit() for c in texto)
    if not 7 <= digitos <= 15:
        raise ValidacionError("Teléfono debe tener entre 7 y 15 dígitos.")
    return texto


def validar_fecha(valor, campo="Fecha"):
    """Convierte 'AAAA-MM-DD' a objeto date."""
    try:
        return datetime.strptime(str(valor).strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValidacionError(
            f"{campo} debe tener el formato AAAA-MM-DD (por ejemplo 2026-12-31)."
        ) from None
