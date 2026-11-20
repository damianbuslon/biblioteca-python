"""Operaciones SQL sobre la tabla libros."""
from ..modelos import Libro
from ..texto import escapar_like, normalizar


class LibroRepositorio:
    # 'disponibles' se calcula (ejemplares - préstamos vigentes) para que
    # nunca pueda quedar desincronizado con la tabla de préstamos.
    _SELECT = """
        SELECT l.id, l.titulo, l.autor, l.editorial, l.anio, l.cantidad,
               l.cantidad - (SELECT COUNT(*) FROM prestamos p
                             WHERE p.libro_id = l.id
                               AND p.fecha_devolucion IS NULL) AS disponibles
        FROM libros l
    """
    # Lista blanca: el nombre de columna nunca viene directo del usuario.
    _COLUMNAS_BUSQUEDA = {"titulo": "l.titulo", "autor": "l.autor", "editorial": "l.editorial"}

    def __init__(self, db):
        self._conn = db.conn

    def crear(self, titulo, autor, editorial, anio, cantidad):
        with self._conn:
            cursor = self._conn.execute(
                "INSERT INTO libros (titulo, autor, editorial, anio, cantidad) VALUES (?, ?, ?, ?, ?)",
                (titulo, autor, editorial, anio, cantidad),
            )
        return cursor.lastrowid

    def obtener(self, id_libro):
        fila = self._conn.execute(f"{self._SELECT} WHERE l.id = ?", (id_libro,)).fetchone()
        return Libro(**dict(fila)) if fila else None

    def listar(self, solo_disponibles=False):
        sql = f"SELECT * FROM ({self._SELECT})"
        if solo_disponibles:
            sql += " WHERE disponibles > 0"
        sql += " ORDER BY titulo COLLATE NOCASE, id"
        return [Libro(**dict(f)) for f in self._conn.execute(sql)]

    def buscar(self, campo, termino):
        columna = self._COLUMNAS_BUSQUEDA[campo]
        patron = f"%{escapar_like(normalizar(termino))}%"
        sql = (
            f"{self._SELECT} WHERE normalizar({columna}) LIKE ? ESCAPE '\\' "
            "ORDER BY l.titulo COLLATE NOCASE, l.id"
        )
        return [Libro(**dict(f)) for f in self._conn.execute(sql, (patron,))]

    def actualizar(self, id_libro, titulo, autor, editorial, anio, cantidad):
        with self._conn:
            self._conn.execute(
                "UPDATE libros SET titulo=?, autor=?, editorial=?, anio=?, cantidad=? WHERE id=?",
                (titulo, autor, editorial, anio, cantidad, id_libro),
            )

    def eliminar(self, id_libro):
        with self._conn:
            self._conn.execute("DELETE FROM libros WHERE id = ?", (id_libro,))

    def existe_duplicado(self, titulo, autor, editorial, anio, excluir_id=None):
        fila = self._conn.execute(
            """SELECT 1 FROM libros
               WHERE normalizar(titulo) = ? AND normalizar(autor) = ?
                 AND normalizar(editorial) = ? AND anio = ? AND id <> ?
               LIMIT 1""",
            (normalizar(titulo), normalizar(autor), normalizar(editorial), anio, excluir_id or 0),
        ).fetchone()
        return fila is not None
