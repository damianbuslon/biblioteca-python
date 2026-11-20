"""Menú de gestión de libros."""
from .. import validaciones as v
from . import consola as c
from .menu import Menu

_CRITERIOS = {"1": ("titulo", "título"), "2": ("autor", "autor"), "3": ("editorial", "editorial")}


class MenuLibros:
    def __init__(self, servicio):
        self._s = servicio

    @staticmethod
    def _tabla(libros):
        c.mostrar_tabla(
            ["ID", "Título", "Autor", "Editorial", "Año", "Total", "Disp."],
            [(x.id, x.titulo, x.autor, x.editorial, x.anio, x.cantidad, x.disponibles) for x in libros],
        )

    def construir(self):
        menu = Menu("GESTIÓN DE LIBROS")
        menu.agregar("Agregar libro", self.agregar)
        menu.agregar("Listar todos los libros", self.listar)
        menu.agregar("Listar libros disponibles", self.listar_disponibles)
        menu.agregar("Buscar libros (título / autor / editorial)", self.buscar)
        menu.agregar("Actualizar libro", self.actualizar)
        menu.agregar("Eliminar libro", self.eliminar)
        return menu

    def agregar(self):
        c.titulo("AGREGAR LIBRO")
        print("(escriba 'cancelar' en cualquier momento para abortar)\n")
        titulo = c.pedir("Título", v.validar_titulo)
        autor = c.pedir("Autor", v.validar_autor)
        editorial = c.pedir("Editorial", v.validar_editorial)
        anio = c.pedir("Año de publicación", v.validar_anio)
        cantidad = c.pedir("Cantidad de ejemplares", v.validar_cantidad)
        libro = self._s.agregar(titulo, autor, editorial, anio, cantidad)
        c.ok(f"Libro agregado con ID {libro.id}.")

    def listar(self):
        c.titulo("TODOS LOS LIBROS")
        self._tabla(self._s.listar())

    def listar_disponibles(self):
        c.titulo("LIBROS DISPONIBLES")
        self._tabla(self._s.listar_disponibles())

    def buscar(self):
        c.titulo("BUSCAR LIBROS")
        print("Buscar por:\n  1. Título\n  2. Autor\n  3. Editorial")
        opcion = c.elegir("Opción", list(_CRITERIOS))
        campo, nombre = _CRITERIOS[opcion]
        termino = c.pedir(f"Texto a buscar en {nombre}", lambda x: x)
        self._tabla(self._s.buscar(campo, termino))

    def actualizar(self):
        c.titulo("ACTUALIZAR LIBRO")
        libro = self._s.obtener(c.pedir("ID del libro a actualizar", v.validar_id))
        self._tabla([libro])
        print("\nPresione Enter para mantener el valor actual.")
        titulo = c.pedir("Título", v.validar_titulo, libro.titulo)
        autor = c.pedir("Autor", v.validar_autor, libro.autor)
        editorial = c.pedir("Editorial", v.validar_editorial, libro.editorial)
        anio = c.pedir("Año de publicación", v.validar_anio, libro.anio)
        cantidad = c.pedir("Cantidad total de ejemplares", v.validar_cantidad, libro.cantidad)
        actualizado = self._s.actualizar(libro.id, titulo, autor, editorial, anio, cantidad)
        c.ok(f"Libro {actualizado.id} actualizado.")
        self._tabla([actualizado])

    def eliminar(self):
        c.titulo("ELIMINAR LIBRO")
        libro = self._s.obtener(c.pedir("ID del libro a eliminar", v.validar_id))
        self._tabla([libro])
        if c.confirmar("¿Seguro que desea eliminarlo? (se borra también su historial de préstamos)"):
            self._s.eliminar(libro.id)
            c.ok("Libro eliminado.")
        else:
            c.aviso("No se eliminó nada.")
