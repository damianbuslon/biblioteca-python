"""Utilidades de texto para búsquedas insensibles a mayúsculas y acentos."""
import unicodedata


def normalizar(texto):
    """Devuelve el texto en minúsculas y sin acentos ('Cortázar' -> 'cortazar')."""
    if texto is None:
        return ""
    descompuesto = unicodedata.normalize("NFD", str(texto))
    sin_acentos = "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")
    return sin_acentos.casefold()


def escapar_like(texto):
    """Escapa los comodines de SQL LIKE para que se busquen como texto literal."""
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
