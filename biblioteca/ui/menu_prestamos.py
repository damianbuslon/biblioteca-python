"""Menú de gestión de préstamos."""
from .. import validaciones as v
from ..config import DIAS_PRESTAMO, MAX_DIAS_PRESTAMO
from . import consola as c
from .menu import Menu


class MenuPrestamos:
    def __init__(self, servicio, libro_servicio, usuario_servicio):
        self._s = servicio
        self._libros = libro_servicio
        self._usuarios = usuario_servicio

    @staticmethod
    def _estado(p):
        if p.vencido:
            return f"VENCIDO ({p.dias_retraso} d)"
        if not p.vigente and p.dias_retraso > 0:
            return f"Devuelto con {p.dias_retraso} d de retraso"
        return p.estado

    def _tabla(self, prestamos):
        c.mostrar_tabla(
            ["ID", "Libro", "Usuario", "Prestado", "Vence", "Devuelto", "Estado"],
            [
                (
                    p.id, p.libro_titulo, p.usuario_nombre, p.fecha_prestamo,
                    p.fecha_vencimiento, p.fecha_devolucion or "-", self._estado(p),
                )
                for p in prestamos
            ],
        )

    def construir(self):
        menu = Menu("GESTIÓN DE PRÉSTAMOS")
        menu.agregar("Registrar préstamo", self.registrar)
        menu.agregar("Listar préstamos vigentes", self.listar_vigentes)
        menu.agregar("Listar historial completo", self.listar_historial)
        menu.agregar("Devolver libro", self.devolver)
        menu.agregar("Actualizar préstamo", self.actualizar)
        menu.agregar("Eliminar préstamo", self.eliminar)
        return menu

    def registrar(self):
        c.titulo("REGISTRAR PRÉSTAMO")
        print("(escriba 'cancelar' en cualquier momento para abortar)")
        print("\nLibros con ejemplares disponibles:")
        disponibles = self._libros.listar_disponibles()
        c.mostrar_tabla(
            ["ID", "Título", "Autor", "Disp."],
            [(x.id, x.titulo, x.autor, x.disponibles) for x in disponibles],
        )
        if not disponibles:
            return
        id_libro = c.pedir("\nID del libro", v.validar_id)

        print("\nUsuarios registrados:")
        usuarios = self._usuarios.listar()
        c.mostrar_tabla(
            ["ID", "Nombre", "Apellido"], [(u.id, u.nombre, u.apellido) for u in usuarios]
        )
        if not usuarios:
            return
        id_usuario = c.pedir("\nID del usuario", v.validar_id)

        dias = c.pedir(
            f"Días de préstamo (1-{MAX_DIAS_PRESTAMO})",
            lambda x: v.validar_entero(x, "Días de préstamo", 1, MAX_DIAS_PRESTAMO),
            DIAS_PRESTAMO,
        )
        prestamo = self._s.registrar(id_libro, id_usuario, dias)
        c.ok(
            f"Préstamo {prestamo.id} registrado: '{prestamo.libro_titulo}' a "
            f"{prestamo.usuario_nombre}. Vence el {prestamo.fecha_vencimiento}."
        )

    def listar_vigentes(self):
        c.titulo("PRÉSTAMOS VIGENTES")
        self._tabla(self._s.listar_vigentes())

    def listar_historial(self):
        c.titulo("HISTORIAL DE PRÉSTAMOS")
        self._tabla(self._s.listar_historial())

    def devolver(self):
        c.titulo("DEVOLVER LIBRO")
        vigentes = self._s.listar_vigentes()
        self._tabla(vigentes)
        if not vigentes:
            return
        prestamo = self._s.devolver(c.pedir("\nID del préstamo a devolver", v.validar_id))
        mensaje = f"Devolución registrada: '{prestamo.libro_titulo}' de {prestamo.usuario_nombre}."
        if prestamo.dias_retraso:
            mensaje += f" Retraso: {prestamo.dias_retraso} día(s)."
        c.ok(mensaje)

    def actualizar(self):
        c.titulo("ACTUALIZAR PRÉSTAMO")
        prestamo = self._s.obtener(c.pedir("ID del préstamo a actualizar", v.validar_id))
        self._tabla([prestamo])
        if not prestamo.vigente:
            c.error("Solo se pueden modificar préstamos vigentes (este ya fue devuelto).")
            return
        print("\nPresione Enter para mantener el valor actual.")
        id_libro = c.pedir("ID del libro", v.validar_id, prestamo.libro_id)
        id_usuario = c.pedir("ID del usuario", v.validar_id, prestamo.usuario_id)
        vencimiento = c.pedir(
            "Fecha de vencimiento (AAAA-MM-DD)",
            lambda x: v.validar_fecha(x, "Fecha de vencimiento").isoformat(),
            prestamo.fecha_vencimiento,
        )
        actualizado = self._s.actualizar(prestamo.id, id_libro, id_usuario, vencimiento)
        c.ok(f"Préstamo {actualizado.id} actualizado.")
        self._tabla([actualizado])

    def eliminar(self):
        c.titulo("ELIMINAR PRÉSTAMO")
        prestamo = self._s.obtener(c.pedir("ID del préstamo a eliminar", v.validar_id))
        self._tabla([prestamo])
        if prestamo.vigente:
            c.aviso("Atención: el préstamo sigue vigente; al eliminarlo el ejemplar vuelve a quedar disponible.")
        if c.confirmar("¿Seguro que desea eliminar este registro?"):
            self._s.eliminar(prestamo.id)
            c.ok("Préstamo eliminado.")
        else:
            c.aviso("No se eliminó nada.")
