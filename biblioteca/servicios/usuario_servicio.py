"""Reglas de negocio de la gestión de usuarios."""
from .. import validaciones as v
from ..excepciones import NoEncontradoError, ReglaNegocioError


class UsuarioServicio:
    def __init__(self, usuarios, prestamos):
        self._usuarios = usuarios
        self._prestamos = prestamos

    @staticmethod
    def _validar(nombre, apellido, direccion, telefono):
        return (
            v.validar_nombre(nombre),
            v.validar_apellido(apellido),
            v.validar_direccion(direccion),
            v.validar_telefono(telefono),
        )

    def agregar(self, nombre, apellido, direccion, telefono):
        nombre, apellido, direccion, telefono = self._validar(nombre, apellido, direccion, telefono)
        if self._usuarios.existe_duplicado(nombre, apellido, telefono):
            raise ReglaNegocioError("Ya existe un usuario con el mismo nombre, apellido y teléfono.")
        return self.obtener(self._usuarios.crear(nombre, apellido, direccion, telefono))

    def obtener(self, id_usuario):
        id_usuario = v.validar_id(id_usuario, "ID del usuario")
        usuario = self._usuarios.obtener(id_usuario)
        if usuario is None:
            raise NoEncontradoError(f"No existe un usuario con ID {id_usuario}.")
        return usuario

    def listar(self):
        return self._usuarios.listar()

    def buscar(self, termino):
        termino = v.validar_texto(termino, "Término de búsqueda", 100)
        return self._usuarios.buscar(termino)

    def actualizar(self, id_usuario, nombre, apellido, direccion, telefono):
        actual = self.obtener(id_usuario)
        nombre, apellido, direccion, telefono = self._validar(nombre, apellido, direccion, telefono)
        if self._usuarios.existe_duplicado(nombre, apellido, telefono, excluir_id=actual.id):
            raise ReglaNegocioError("Ya existe otro usuario con el mismo nombre, apellido y teléfono.")
        self._usuarios.actualizar(actual.id, nombre, apellido, direccion, telefono)
        return self.obtener(actual.id)

    def eliminar(self, id_usuario):
        usuario = self.obtener(id_usuario)
        vigentes = self._prestamos.contar_vigentes_usuario(usuario.id)
        if vigentes > 0:
            raise ReglaNegocioError(
                f"No se puede eliminar: el usuario tiene {vigentes} préstamo(s) vigente(s)."
            )
        self._usuarios.eliminar(usuario.id)
        return usuario
