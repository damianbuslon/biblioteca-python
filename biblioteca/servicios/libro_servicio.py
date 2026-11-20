"""Reglas de negocio de la gestión de libros."""
from .. import validaciones as v
from ..excepciones import NoEncontradoError, ReglaNegocioError, ValidacionError

CRITERIOS_BUSQUEDA = ("titulo", "autor", "editorial")


class LibroServicio:
    def __init__(self, libros):
        self._libros = libros

    @staticmethod
    def _validar(titulo, autor, editorial, anio, cantidad):
        return (
            v.validar_titulo(titulo),
            v.validar_autor(autor),
            v.validar_editorial(editorial),
            v.validar_anio(anio),
            v.validar_cantidad(cantidad),
        )

    def agregar(self, titulo, autor, editorial, anio, cantidad):
        datos = self._validar(titulo, autor, editorial, anio, cantidad)
        if self._libros.existe_duplicado(*datos[:4]):
            raise ReglaNegocioError(
                "Ya existe un libro con el mismo título, autor, editorial y año. "
                "Actualice su cantidad de ejemplares en lugar de duplicarlo."
            )
        return self.obtener(self._libros.crear(*datos))

    def obtener(self, id_libro):
        id_libro = v.validar_id(id_libro, "ID del libro")
        libro = self._libros.obtener(id_libro)
        if libro is None:
            raise NoEncontradoError(f"No existe un libro con ID {id_libro}.")
        return libro

    def listar(self):
        return self._libros.listar()

    def listar_disponibles(self):
        return self._libros.listar(solo_disponibles=True)

    def buscar(self, criterio, termino):
        if criterio not in CRITERIOS_BUSQUEDA:
            raise ValidacionError("Criterio de búsqueda inválido (use título, autor o editorial).")
        termino = v.validar_texto(termino, "Término de búsqueda", 100)
        return self._libros.buscar(criterio, termino)

    def actualizar(self, id_libro, titulo, autor, editorial, anio, cantidad):
        actual = self.obtener(id_libro)
        datos = self._validar(titulo, autor, editorial, anio, cantidad)
        if self._libros.existe_duplicado(*datos[:4], excluir_id=actual.id):
            raise ReglaNegocioError("Ya existe otro libro con esos mismos datos.")
        prestados = actual.cantidad - actual.disponibles
        if datos[4] < prestados:
            raise ReglaNegocioError(
                f"No puede reducir la cantidad a {datos[4]}: hay {prestados} ejemplar(es) prestado(s)."
            )
        self._libros.actualizar(actual.id, *datos)
        return self.obtener(actual.id)

    def eliminar(self, id_libro):
        libro = self.obtener(id_libro)
        prestados = libro.cantidad - libro.disponibles
        if prestados > 0:
            raise ReglaNegocioError(
                f"No se puede eliminar: tiene {prestados} préstamo(s) vigente(s). Registre las devoluciones primero."
            )
        self._libros.eliminar(libro.id)
        return libro
