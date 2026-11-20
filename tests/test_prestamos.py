from biblioteca.excepciones import NoEncontradoError, ReglaNegocioError, ValidacionError
from tests.base import BaseTest


class TestPrestamos(BaseTest):
    def setUp(self):
        super().setUp()
        self.libro = self.crear_libro(cantidad=2)
        self.usuario = self.crear_usuario()

    def test_registrar_descuenta_disponibles_y_calcula_vencimiento(self):
        p = self.prestamos.registrar(self.libro.id, self.usuario.id)
        self.assertEqual((p.fecha_prestamo, p.fecha_vencimiento), ("2020-01-10", "2020-01-24"))
        self.assertTrue(p.vigente)
        self.assertEqual(self.libros.obtener(self.libro.id).disponibles, 1)

    def test_dias_personalizados_y_validacion(self):
        p = self.prestamos.registrar(self.libro.id, self.usuario.id, 7)
        self.assertEqual(p.fecha_vencimiento, "2020-01-17")
        otro = self.crear_usuario(nombre="Otro", telefono="098111222")
        for malo in ("0", "-5", "91", "abc"):
            with self.assertRaises(ValidacionError, msg=malo):
                self.prestamos.registrar(self.libro.id, otro.id, malo)

    def test_libro_o_usuario_inexistente(self):
        with self.assertRaises(NoEncontradoError):
            self.prestamos.registrar(99, self.usuario.id)
        with self.assertRaises(NoEncontradoError):
            self.prestamos.registrar(self.libro.id, 99)

    def test_sin_ejemplares_disponibles(self):
        unico = self.crear_libro(titulo="Unico", cantidad=1)
        self.prestamos.registrar(unico.id, self.usuario.id)
        otro = self.crear_usuario(nombre="Luis", telefono="098765432")
        with self.assertRaises(ReglaNegocioError):
            self.prestamos.registrar(unico.id, otro.id)

    def test_mismo_usuario_no_puede_llevar_dos_veces_el_mismo_libro(self):
        self.prestamos.registrar(self.libro.id, self.usuario.id)
        with self.assertRaises(ReglaNegocioError):
            self.prestamos.registrar(self.libro.id, self.usuario.id)

    def test_limite_de_prestamos_por_usuario(self):
        for i in range(3):
            self.prestamos.registrar(self.crear_libro(titulo=f"L{i}").id, self.usuario.id)
        with self.assertRaises(ReglaNegocioError):
            self.prestamos.registrar(self.crear_libro(titulo="L9").id, self.usuario.id)

    def test_devolver_libera_ejemplar_y_registra_fecha(self):
        p = self.prestamos.registrar(self.libro.id, self.usuario.id)
        d = self.prestamos.devolver(p.id)
        self.assertEqual(d.fecha_devolucion, "2020-01-10")
        self.assertFalse(d.vigente)
        self.assertEqual(self.libros.obtener(self.libro.id).disponibles, 2)
        self.assertEqual(self.prestamos.listar_vigentes(), [])

    def test_no_se_puede_devolver_dos_veces(self):
        p = self.prestamos.registrar(self.libro.id, self.usuario.id)
        self.prestamos.devolver(p.id)
        with self.assertRaises(ReglaNegocioError):
            self.prestamos.devolver(p.id)

    def test_tras_devolver_puede_volver_a_prestarse_al_mismo_usuario(self):
        p = self.prestamos.registrar(self.libro.id, self.usuario.id)
        self.prestamos.devolver(p.id)
        self.prestamos.registrar(self.libro.id, self.usuario.id)

    def test_listados(self):
        p1 = self.prestamos.registrar(self.libro.id, self.usuario.id)
        p2 = self.prestamos.registrar(self.crear_libro(titulo="B").id, self.usuario.id)
        self.prestamos.devolver(p1.id)
        self.assertEqual([p.id for p in self.prestamos.listar_vigentes()], [p2.id])
        self.assertEqual({p.id for p in self.prestamos.listar_historial()}, {p1.id, p2.id})

    def test_estado_vencido_y_dias_de_retraso(self):
        p = self.prestamos.registrar(self.libro.id, self.usuario.id)  # vence en 2020: ya vencido
        self.assertTrue(p.vencido)
        self.assertEqual(p.estado, "VENCIDO")
        self.assertGreater(p.dias_retraso, 0)
        d = self.prestamos.devolver(p.id)
        self.assertEqual((d.estado, d.dias_retraso), ("Devuelto", 0))

    def test_actualizar_fecha_vencimiento(self):
        p = self.prestamos.registrar(self.libro.id, self.usuario.id)
        n = self.prestamos.actualizar(p.id, p.libro_id, p.usuario_id, "2999-12-31")
        self.assertEqual(n.fecha_vencimiento, "2999-12-31")
        self.assertFalse(n.vencido)

    def test_actualizar_fecha_invalida_o_anterior(self):
        p = self.prestamos.registrar(self.libro.id, self.usuario.id)
        for malo in ("31/12/2030", "2030-02-30", "hola", ""):
            with self.assertRaises(ValidacionError, msg=malo):
                self.prestamos.actualizar(p.id, p.libro_id, p.usuario_id, malo)
        with self.assertRaises(ValidacionError):
            self.prestamos.actualizar(p.id, p.libro_id, p.usuario_id, "2019-12-31")

    def test_actualizar_a_otro_libro(self):
        p = self.prestamos.registrar(self.libro.id, self.usuario.id)
        otro = self.crear_libro(titulo="Otro", cantidad=1)
        n = self.prestamos.actualizar(p.id, otro.id, p.usuario_id, p.fecha_vencimiento)
        self.assertEqual(n.libro_id, otro.id)
        self.assertEqual(self.libros.obtener(self.libro.id).disponibles, 2)
        self.assertEqual(self.libros.obtener(otro.id).disponibles, 0)

    def test_actualizar_a_libro_sin_stock_falla(self):
        p = self.prestamos.registrar(self.libro.id, self.usuario.id)
        agotado = self.crear_libro(titulo="Agotado", cantidad=1)
        self.prestamos.registrar(agotado.id, self.crear_usuario(nombre="Luis", telefono="098765432").id)
        with self.assertRaises(ReglaNegocioError):
            self.prestamos.actualizar(p.id, agotado.id, p.usuario_id, p.fecha_vencimiento)

    def test_actualizar_a_otro_usuario(self):
        p = self.prestamos.registrar(self.libro.id, self.usuario.id)
        otro = self.crear_usuario(nombre="Luis", telefono="098765432")
        n = self.prestamos.actualizar(p.id, p.libro_id, otro.id, p.fecha_vencimiento)
        self.assertEqual(n.usuario_id, otro.id)

    def test_actualizar_a_usuario_que_ya_tiene_ese_libro_falla(self):
        otro = self.crear_usuario(nombre="Luis", telefono="098765432")
        self.prestamos.registrar(self.libro.id, otro.id)
        p = self.prestamos.registrar(self.libro.id, self.usuario.id)
        with self.assertRaises(ReglaNegocioError):
            self.prestamos.actualizar(p.id, p.libro_id, otro.id, p.fecha_vencimiento)

    def test_actualizar_a_usuario_en_el_limite_falla(self):
        lleno = self.crear_usuario(nombre="Luis", telefono="098765432")
        for i in range(3):
            self.prestamos.registrar(self.crear_libro(titulo=f"L{i}").id, lleno.id)
        p = self.prestamos.registrar(self.libro.id, self.usuario.id)
        with self.assertRaises(ReglaNegocioError):
            self.prestamos.actualizar(p.id, p.libro_id, lleno.id, p.fecha_vencimiento)

    def test_no_se_actualiza_prestamo_devuelto(self):
        p = self.prestamos.registrar(self.libro.id, self.usuario.id)
        self.prestamos.devolver(p.id)
        with self.assertRaises(ReglaNegocioError):
            self.prestamos.actualizar(p.id, p.libro_id, p.usuario_id, "2999-01-01")

    def test_eliminar_prestamo_vigente_libera_ejemplar(self):
        p = self.prestamos.registrar(self.libro.id, self.usuario.id)
        self.prestamos.eliminar(p.id)
        self.assertEqual(self.libros.obtener(self.libro.id).disponibles, 2)
        with self.assertRaises(NoEncontradoError):
            self.prestamos.obtener(p.id)

    def test_eliminar_inexistente(self):
        with self.assertRaises(NoEncontradoError):
            self.prestamos.eliminar(99)

    def test_eliminar_usuario_con_historial_devuelto_borra_el_historial(self):
        p = self.prestamos.registrar(self.libro.id, self.usuario.id)
        self.prestamos.devolver(p.id)
        self.usuarios.eliminar(self.usuario.id)
        self.assertEqual(self.prestamos.listar_historial(), [])
