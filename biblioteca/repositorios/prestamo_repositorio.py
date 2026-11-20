"""Operaciones SQL sobre la tabla prestamos."""
from ..modelos import Prestamo


class PrestamoRepositorio:
    _SELECT = """
        SELECT p.id, p.libro_id, p.usuario_id, p.fecha_prestamo,
               p.fecha_vencimiento, p.fecha_devolucion,
               l.titulo AS libro_titulo,
               u.nombre || ' ' || u.apellido AS usuario_nombre
        FROM prestamos p
        JOIN libros   l ON l.id = p.libro_id
        JOIN usuarios u ON u.id = p.usuario_id
    """

    def __init__(self, db):
        self._conn = db.conn

    def crear(self, libro_id, usuario_id, fecha_prestamo, fecha_vencimiento):
        with self._conn:
            cursor = self._conn.execute(
                """INSERT INTO prestamos (libro_id, usuario_id, fecha_prestamo, fecha_vencimiento)
                   VALUES (?, ?, ?, ?)""",
                (libro_id, usuario_id, fecha_prestamo, fecha_vencimiento),
            )
        return cursor.lastrowid

    def obtener(self, id_prestamo):
        fila = self._conn.execute(f"{self._SELECT} WHERE p.id = ?", (id_prestamo,)).fetchone()
        return Prestamo(**dict(fila)) if fila else None

    def listar(self, solo_vigentes=True):
        if solo_vigentes:
            sql = f"{self._SELECT} WHERE p.fecha_devolucion IS NULL ORDER BY p.fecha_vencimiento, p.id"
        else:
            sql = f"{self._SELECT} ORDER BY p.id DESC"
        return [Prestamo(**dict(f)) for f in self._conn.execute(sql)]

    def contar_vigentes_usuario(self, usuario_id):
        return self._conn.execute(
            "SELECT COUNT(*) FROM prestamos WHERE usuario_id = ? AND fecha_devolucion IS NULL",
            (usuario_id,),
        ).fetchone()[0]

    def existe_vigente(self, libro_id, usuario_id, excluir_id=None):
        fila = self._conn.execute(
            """SELECT 1 FROM prestamos
               WHERE libro_id = ? AND usuario_id = ? AND fecha_devolucion IS NULL AND id <> ?
               LIMIT 1""",
            (libro_id, usuario_id, excluir_id or 0),
        ).fetchone()
        return fila is not None

    def marcar_devuelto(self, id_prestamo, fecha_devolucion):
        with self._conn:
            self._conn.execute(
                "UPDATE prestamos SET fecha_devolucion = ? WHERE id = ?",
                (fecha_devolucion, id_prestamo),
            )

    def actualizar(self, id_prestamo, libro_id, usuario_id, fecha_vencimiento):
        with self._conn:
            self._conn.execute(
                "UPDATE prestamos SET libro_id=?, usuario_id=?, fecha_vencimiento=? WHERE id=?",
                (libro_id, usuario_id, fecha_vencimiento, id_prestamo),
            )

    def eliminar(self, id_prestamo):
        with self._conn:
            self._conn.execute("DELETE FROM prestamos WHERE id = ?", (id_prestamo,))
