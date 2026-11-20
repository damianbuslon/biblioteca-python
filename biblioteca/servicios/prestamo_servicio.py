"""Reglas de negocio de la gestión de préstamos."""
from datetime import date, timedelta

from .. import validaciones as v
from ..config import DIAS_PRESTAMO, MAX_DIAS_PRESTAMO, MAX_PRESTAMOS_POR_USUARIO
from ..excepciones import NoEncontradoError, ReglaNegocioError, ValidacionError


class PrestamoServicio:
    def __init__(self, prestamos, libro_servicio, usuario_servicio, reloj=date.today):
        self._prestamos = prestamos
        self._libros = libro_servicio
        self._usuarios = usuario_servicio
        self._hoy = reloj  # inyectable para poder probar con fechas fijas

    # ---------- reglas reutilizables ----------
    @staticmethod
    def _chequear_disponibilidad(libro):
        if libro.disponibles <= 0:
            raise ReglaNegocioError(
                f"No hay ejemplares disponibles de '{libro.titulo}' (todos están prestados)."
            )

    def _chequear_limite(self, usuario):
        if self._prestamos.contar_vigentes_usuario(usuario.id) >= MAX_PRESTAMOS_POR_USUARIO:
            raise ReglaNegocioError(
                f"{usuario.nombre_completo} ya tiene el máximo de {MAX_PRESTAMOS_POR_USUARIO} préstamos vigentes."
            )

    def _chequear_duplicado(self, id_libro, id_usuario, excluir_id=None):
        if self._prestamos.existe_vigente(id_libro, id_usuario, excluir_id):
            raise ReglaNegocioError("Ese usuario ya tiene un préstamo vigente de ese mismo libro.")

    # ---------- operaciones ----------
    def registrar(self, id_libro, id_usuario, dias=None):
        if dias is None or str(dias).strip() == "":
            dias = DIAS_PRESTAMO
        else:
            dias = v.validar_entero(dias, "Días de préstamo", 1, MAX_DIAS_PRESTAMO)
        libro = self._libros.obtener(id_libro)
        usuario = self._usuarios.obtener(id_usuario)

        self._chequear_disponibilidad(libro)
        self._chequear_limite(usuario)
        self._chequear_duplicado(libro.id, usuario.id)

        hoy = self._hoy()
        id_prestamo = self._prestamos.crear(
            libro.id, usuario.id, hoy.isoformat(), (hoy + timedelta(days=dias)).isoformat()
        )
        return self.obtener(id_prestamo)

    def obtener(self, id_prestamo):
        id_prestamo = v.validar_id(id_prestamo, "ID del préstamo")
        prestamo = self._prestamos.obtener(id_prestamo)
        if prestamo is None:
            raise NoEncontradoError(f"No existe un préstamo con ID {id_prestamo}.")
        return prestamo

    def listar_vigentes(self):
        return self._prestamos.listar(solo_vigentes=True)

    def listar_historial(self):
        return self._prestamos.listar(solo_vigentes=False)

    def devolver(self, id_prestamo):
        prestamo = self.obtener(id_prestamo)
        if not prestamo.vigente:
            raise ReglaNegocioError(f"Este libro ya fue devuelto el {prestamo.fecha_devolucion}.")
        self._prestamos.marcar_devuelto(prestamo.id, self._hoy().isoformat())
        return self.obtener(prestamo.id)

    def actualizar(self, id_prestamo, id_libro, id_usuario, fecha_vencimiento):
        prestamo = self.obtener(id_prestamo)
        if not prestamo.vigente:
            raise ReglaNegocioError("Solo se pueden modificar préstamos vigentes (este ya fue devuelto).")

        id_libro = v.validar_id(id_libro, "ID del libro")
        id_usuario = v.validar_id(id_usuario, "ID del usuario")
        vencimiento = v.validar_fecha(fecha_vencimiento, "Fecha de vencimiento")
        if vencimiento < date.fromisoformat(prestamo.fecha_prestamo):
            raise ValidacionError("El vencimiento no puede ser anterior a la fecha del préstamo.")

        libro = self._libros.obtener(id_libro)
        usuario = self._usuarios.obtener(id_usuario)
        # Solo se re-verifica lo que cambió: el ejemplar/cupo actual ya estaba ocupado por este préstamo.
        if libro.id != prestamo.libro_id:
            self._chequear_disponibilidad(libro)
        if usuario.id != prestamo.usuario_id:
            self._chequear_limite(usuario)
        self._chequear_duplicado(libro.id, usuario.id, excluir_id=prestamo.id)

        self._prestamos.actualizar(prestamo.id, libro.id, usuario.id, vencimiento.isoformat())
        return self.obtener(prestamo.id)

    def eliminar(self, id_prestamo):
        prestamo = self.obtener(id_prestamo)
        self._prestamos.eliminar(prestamo.id)
        return prestamo
