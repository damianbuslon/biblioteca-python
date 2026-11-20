"""Operaciones SQL sobre la tabla usuarios."""
from ..modelos import Usuario
from ..texto import escapar_like, normalizar

_COLUMNAS = "id, nombre, apellido, direccion, telefono"


class UsuarioRepositorio:
    def __init__(self, db):
        self._conn = db.conn

    def crear(self, nombre, apellido, direccion, telefono):
        with self._conn:
            cursor = self._conn.execute(
                "INSERT INTO usuarios (nombre, apellido, direccion, telefono) VALUES (?, ?, ?, ?)",
                (nombre, apellido, direccion, telefono),
            )
        return cursor.lastrowid

    def obtener(self, id_usuario):
        fila = self._conn.execute(
            f"SELECT {_COLUMNAS} FROM usuarios WHERE id = ?", (id_usuario,)
        ).fetchone()
        return Usuario(**dict(fila)) if fila else None

    def listar(self):
        filas = self._conn.execute(
            f"SELECT {_COLUMNAS} FROM usuarios ORDER BY apellido COLLATE NOCASE, nombre COLLATE NOCASE, id"
        )
        return [Usuario(**dict(f)) for f in filas]

    def buscar(self, termino):
        """Busca en nombre, apellido o 'nombre apellido' (sin acentos ni mayúsculas)."""
        patron = f"%{escapar_like(normalizar(termino))}%"
        filas = self._conn.execute(
            f"""SELECT {_COLUMNAS} FROM usuarios
                WHERE normalizar(nombre || ' ' || apellido) LIKE ? ESCAPE '\\'
                ORDER BY apellido COLLATE NOCASE, nombre COLLATE NOCASE, id""",
            (patron,),
        )
        return [Usuario(**dict(f)) for f in filas]

    def actualizar(self, id_usuario, nombre, apellido, direccion, telefono):
        with self._conn:
            self._conn.execute(
                "UPDATE usuarios SET nombre=?, apellido=?, direccion=?, telefono=? WHERE id=?",
                (nombre, apellido, direccion, telefono, id_usuario),
            )

    def eliminar(self, id_usuario):
        with self._conn:
            self._conn.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))

    def existe_duplicado(self, nombre, apellido, telefono, excluir_id=None):
        fila = self._conn.execute(
            """SELECT 1 FROM usuarios
               WHERE normalizar(nombre) = ? AND normalizar(apellido) = ?
                 AND telefono = ? AND id <> ?
               LIMIT 1""",
            (normalizar(nombre), normalizar(apellido), telefono, excluir_id or 0),
        ).fetchone()
        return fila is not None
