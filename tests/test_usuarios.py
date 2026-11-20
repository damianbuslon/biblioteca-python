from biblioteca.excepciones import NoEncontradoError, ReglaNegocioError, ValidacionError
from tests.base import BaseTest


class TestUsuarios(BaseTest):
    def test_agregar_usuario_valido(self):
        u = self.crear_usuario()
        self.assertEqual((u.id, u.nombre_completo), (1, "Ana Pérez"))

    def test_nombres_con_acentos_guiones_y_apostrofes(self):
        self.usuarios.agregar("María José", "O'Connor-Núñez", "Calle Falsa 123", "+598 99 123 456")

    def test_nombre_invalido(self):
        for malo in ("", "  ", "Ana3", "123", "-Ana", "A@na"):
            with self.assertRaises(ValidacionError, msg=malo):
                self.usuarios.agregar(malo, "Pérez", "Calle 12345", "099123456")
        with self.assertRaises(ValidacionError):
            self.usuarios.agregar("Ana", "Pérez2", "Calle 12345", "099123456")

    def test_direccion_invalida(self):
        for malo in ("", "abc", "x" * 151):
            with self.assertRaises(ValidacionError, msg=malo):
                self.usuarios.agregar("Ana", "Pérez", malo, "099123456")

    def test_telefono_invalido(self):
        for malo in ("", "abc", "123", "12345678901234567", "099-abc-123", "09912345+6"):
            with self.assertRaises(ValidacionError, msg=malo):
                self.usuarios.agregar("Ana", "Pérez", "Calle 12345", malo)

    def test_telefonos_validos(self):
        for i, tel in enumerate(("099123456", "+598 99 123 456", "(02) 123-4567")):
            self.usuarios.agregar(f"Ana{'a' * i}", "Pérez", "Calle 12345", tel)

    def test_duplicado(self):
        self.crear_usuario()
        with self.assertRaises(ReglaNegocioError):
            self.crear_usuario(nombre="ANA", apellido="perez")

    def test_buscar_por_nombre_apellido_y_completo(self):
        self.crear_usuario()
        self.crear_usuario(nombre="Luis", apellido="Gómez", telefono="098765432")
        self.assertEqual(len(self.usuarios.buscar("ana")), 1)
        self.assertEqual(self.usuarios.buscar("GOMEZ")[0].nombre, "Luis")
        self.assertEqual(self.usuarios.buscar("luis gomez")[0].apellido, "Gómez")
        self.assertEqual(self.usuarios.buscar("zzz"), [])

    def test_listar_ordenado_por_apellido(self):
        self.crear_usuario(nombre="Zoe", apellido="Zapata", telefono="1111111")
        self.crear_usuario(nombre="Ana", apellido="Alvarez", telefono="2222222")
        self.assertEqual([u.apellido for u in self.usuarios.listar()], ["Alvarez", "Zapata"])

    def test_actualizar(self):
        u = self.crear_usuario()
        n = self.usuarios.actualizar(u.id, "Ana María", "Pérez", "Otra calle 55", "099000111")
        self.assertEqual((n.nombre, n.direccion, n.telefono), ("Ana María", "Otra calle 55", "099000111"))

    def test_actualizar_a_duplicado_falla(self):
        self.crear_usuario()
        otro = self.crear_usuario(nombre="Luis", telefono="098765432")
        with self.assertRaises(ReglaNegocioError):
            self.usuarios.actualizar(otro.id, "Ana", "Pérez", "Calle 12345", "099123456")

    def test_eliminar(self):
        u = self.crear_usuario()
        self.usuarios.eliminar(u.id)
        with self.assertRaises(NoEncontradoError):
            self.usuarios.obtener(u.id)

    def test_no_se_elimina_usuario_con_prestamo_vigente(self):
        u = self.crear_usuario()
        self.prestamos.registrar(self.crear_libro().id, u.id)
        with self.assertRaises(ReglaNegocioError):
            self.usuarios.eliminar(u.id)
