from biblioteca.excepciones import NoEncontradoError, ReglaNegocioError, ValidacionError
from tests.base import BaseTest


class TestLibros(BaseTest):
    def test_agregar_libro_valido(self):
        libro = self.crear_libro()
        self.assertEqual(libro.id, 1)
        self.assertEqual(libro.cantidad, 2)
        self.assertEqual(libro.disponibles, 2)

    def test_agregar_limpia_espacios(self):
        libro = self.libros.agregar("  Rayuela   Nueva ", "A", "B", 2000, 1)
        self.assertEqual(libro.titulo, "Rayuela Nueva")

    def test_campos_obligatorios(self):
        for campo in range(3):
            datos = ["T", "A", "E"]
            datos[campo] = "   "
            with self.assertRaises(ValidacionError):
                self.libros.agregar(*datos, 2000, 1)

    def test_anio_invalido(self):
        for anio in ("abc", "999", "2999", "", "20.5", "1_000"):
            with self.assertRaises(ValidacionError, msg=anio):
                self.libros.agregar("T", "A", "E", anio, 1)

    def test_cantidad_invalida(self):
        for cantidad in ("0", "-1", "x", "", "5000"):
            with self.assertRaises(ValidacionError, msg=cantidad):
                self.libros.agregar("T", "A", "E", 2000, cantidad)

    def test_duplicado_ignora_mayusculas_y_acentos(self):
        self.crear_libro()
        with self.assertRaises(ReglaNegocioError):
            self.libros.agregar("RAYUELA", "julio cortazar", "sudamericana", 1963, 1)

    def test_mismo_titulo_otro_anio_no_es_duplicado(self):
        self.crear_libro()
        self.libros.agregar("Rayuela", "Julio Cortázar", "Sudamericana", 1970, 1)
        self.assertEqual(len(self.libros.listar()), 2)

    def test_buscar_por_cada_criterio(self):
        self.crear_libro()
        self.libros.agregar("El Aleph", "Jorge Luis Borges", "Emecé", 1949, 1)
        self.assertEqual(self.libros.buscar("titulo", "aleph")[0].titulo, "El Aleph")
        self.assertEqual(self.libros.buscar("autor", "CORTAZAR")[0].titulo, "Rayuela")
        self.assertEqual(self.libros.buscar("editorial", "emece")[0].titulo, "El Aleph")
        self.assertEqual(self.libros.buscar("titulo", "inexistente"), [])

    def test_buscar_trata_comodines_como_texto(self):
        self.crear_libro()
        self.assertEqual(self.libros.buscar("titulo", "%"), [])
        self.assertEqual(self.libros.buscar("titulo", "_"), [])

    def test_buscar_criterio_o_termino_invalido(self):
        with self.assertRaises(ValidacionError):
            self.libros.buscar("isbn", "x")
        with self.assertRaises(ValidacionError):
            self.libros.buscar("titulo", "  ")

    def test_busqueda_resistente_a_inyeccion_sql(self):
        self.crear_libro()
        self.assertEqual(self.libros.buscar("titulo", "'; DROP TABLE libros; --"), [])
        self.assertEqual(len(self.libros.listar()), 1)

    def test_listar_disponibles_excluye_agotados(self):
        libro = self.crear_libro(cantidad=1)
        otro = self.crear_libro(titulo="El Aleph")
        usuario = self.crear_usuario()
        self.prestamos.registrar(libro.id, usuario.id)
        ids = [x.id for x in self.libros.listar_disponibles()]
        self.assertEqual(ids, [otro.id])
        self.assertEqual(len(self.libros.listar()), 2)

    def test_actualizar(self):
        libro = self.crear_libro()
        nuevo = self.libros.actualizar(libro.id, "Rayuela 2", "J. Cortázar", "Alfaguara", 1965, 5)
        self.assertEqual((nuevo.titulo, nuevo.editorial, nuevo.cantidad), ("Rayuela 2", "Alfaguara", 5))

    def test_actualizar_a_duplicado_falla(self):
        self.crear_libro()
        otro = self.crear_libro(titulo="El Aleph")
        with self.assertRaises(ReglaNegocioError):
            self.libros.actualizar(otro.id, "Rayuela", "Julio Cortázar", "Sudamericana", 1963, 1)

    def test_actualizar_con_los_mismos_datos_es_valido(self):
        libro = self.crear_libro()
        self.libros.actualizar(libro.id, libro.titulo, libro.autor, libro.editorial, libro.anio, 4)
        self.assertEqual(self.libros.obtener(libro.id).cantidad, 4)

    def test_no_se_puede_reducir_cantidad_bajo_lo_prestado(self):
        libro = self.crear_libro(cantidad=3)
        for n in ("Ana", "Beto"):
            self.prestamos.registrar(libro.id, self.crear_usuario(nombre=n).id)
        with self.assertRaises(ReglaNegocioError):
            self.libros.actualizar(libro.id, libro.titulo, libro.autor, libro.editorial, libro.anio, 1)
        self.libros.actualizar(libro.id, libro.titulo, libro.autor, libro.editorial, libro.anio, 2)

    def test_eliminar(self):
        libro = self.crear_libro()
        self.libros.eliminar(libro.id)
        with self.assertRaises(NoEncontradoError):
            self.libros.obtener(libro.id)

    def test_no_se_elimina_libro_con_prestamo_vigente(self):
        libro = self.crear_libro()
        self.prestamos.registrar(libro.id, self.crear_usuario().id)
        with self.assertRaises(ReglaNegocioError):
            self.libros.eliminar(libro.id)

    def test_eliminar_libro_con_historial_devuelto_borra_el_historial(self):
        libro = self.crear_libro()
        prestamo = self.prestamos.registrar(libro.id, self.crear_usuario().id)
        self.prestamos.devolver(prestamo.id)
        self.libros.eliminar(libro.id)
        self.assertEqual(self.prestamos.listar_historial(), [])

    def test_obtener_inexistente_o_id_invalido(self):
        with self.assertRaises(NoEncontradoError):
            self.libros.obtener(99)
        for malo in ("abc", "0", "-3", ""):
            with self.assertRaises(ValidacionError, msg=malo):
                self.libros.obtener(malo)
