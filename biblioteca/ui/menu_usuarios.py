"""Menú de gestión de usuarios."""
from .. import validaciones as v
from . import consola as c
from .menu import Menu


class MenuUsuarios:
    def __init__(self, servicio):
        self._s = servicio

    @staticmethod
    def _tabla(usuarios):
        c.mostrar_tabla(
            ["ID", "Nombre", "Apellido", "Dirección", "Teléfono"],
            [(u.id, u.nombre, u.apellido, u.direccion, u.telefono) for u in usuarios],
        )

    def construir(self):
        menu = Menu("GESTIÓN DE USUARIOS")
        menu.agregar("Agregar usuario", self.agregar)
        menu.agregar("Listar usuarios registrados", self.listar)
        menu.agregar("Buscar usuarios (nombre o apellido)", self.buscar)
        menu.agregar("Actualizar usuario", self.actualizar)
        menu.agregar("Eliminar usuario", self.eliminar)
        return menu

    def agregar(self):
        c.titulo("AGREGAR USUARIO")
        print("(escriba 'cancelar' en cualquier momento para abortar)\n")
        nombre = c.pedir("Nombre", v.validar_nombre)
        apellido = c.pedir("Apellido", v.validar_apellido)
        direccion = c.pedir("Dirección", v.validar_direccion)
        telefono = c.pedir("Teléfono", v.validar_telefono)
        usuario = self._s.agregar(nombre, apellido, direccion, telefono)
        c.ok(f"Usuario agregado con ID {usuario.id}.")

    def listar(self):
        c.titulo("USUARIOS REGISTRADOS")
        self._tabla(self._s.listar())

    def buscar(self):
        c.titulo("BUSCAR USUARIOS")
        termino = c.pedir("Nombre o apellido a buscar", lambda x: x)
        self._tabla(self._s.buscar(termino))

    def actualizar(self):
        c.titulo("ACTUALIZAR USUARIO")
        usuario = self._s.obtener(c.pedir("ID del usuario a actualizar", v.validar_id))
        self._tabla([usuario])
        print("\nPresione Enter para mantener el valor actual.")
        nombre = c.pedir("Nombre", v.validar_nombre, usuario.nombre)
        apellido = c.pedir("Apellido", v.validar_apellido, usuario.apellido)
        direccion = c.pedir("Dirección", v.validar_direccion, usuario.direccion)
        telefono = c.pedir("Teléfono", v.validar_telefono, usuario.telefono)
        actualizado = self._s.actualizar(usuario.id, nombre, apellido, direccion, telefono)
        c.ok(f"Usuario {actualizado.id} actualizado.")
        self._tabla([actualizado])

    def eliminar(self):
        c.titulo("ELIMINAR USUARIO")
        usuario = self._s.obtener(c.pedir("ID del usuario a eliminar", v.validar_id))
        self._tabla([usuario])
        if c.confirmar("¿Seguro que desea eliminarlo? (se borra también su historial de préstamos)"):
            self._s.eliminar(usuario.id)
            c.ok("Usuario eliminado.")
        else:
            c.aviso("No se eliminó nada.")
