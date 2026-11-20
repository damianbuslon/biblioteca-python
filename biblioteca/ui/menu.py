"""Menú genérico reutilizable y ejecución segura de acciones."""
import sqlite3

from ..excepciones import BibliotecaError
from . import consola as c


def ejecutar_seguro(accion):
    """Ejecuta una acción capturando los errores esperados.

    Así, ningún dato inválido ni error de base de datos tumba el programa.
    """
    try:
        accion()
    except c.OperacionCancelada:
        c.aviso("Operación cancelada.")
    except BibliotecaError as exc:
        c.error(str(exc))
    except sqlite3.Error as exc:
        c.error(f"Error de base de datos: {exc}")


class Menu:
    def __init__(self, titulo, texto_salida="Volver"):
        self._titulo = titulo
        self._texto_salida = texto_salida
        self._opciones = []  # (texto, función, pausar_al_terminar)

    def agregar(self, texto, accion):
        self._opciones.append((texto, accion, True))

    def agregar_submenu(self, texto, menu):
        self._opciones.append((texto, menu.ejecutar, False))

    def ejecutar(self):
        while True:
            c.titulo(self._titulo)
            for numero, (texto, _, _) in enumerate(self._opciones, start=1):
                print(f"  {numero}. {texto}")
            print(f"  0. {self._texto_salida}")
            entrada = input("\nSeleccione una opción: ").strip()
            if entrada == "0":
                return
            if entrada.isdecimal() and 1 <= int(entrada) <= len(self._opciones):
                _, accion, pausar = self._opciones[int(entrada) - 1]
                ejecutar_seguro(accion)
                if pausar:
                    c.pausar()
            else:
                c.error("Opción inválida. Elija un número del menú.")
