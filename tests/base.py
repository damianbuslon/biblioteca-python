"""Clase base: arma una aplicación completa sobre una base de datos en memoria."""
import unittest
from datetime import date

from biblioteca.database import Database
from biblioteca.repositorios import LibroRepositorio, PrestamoRepositorio, UsuarioRepositorio
from biblioteca.servicios import LibroServicio, PrestamoServicio, UsuarioServicio

FECHA_FIJA = date(2020, 1, 10)


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.addCleanup(self.db.cerrar)
        repo_prestamos = PrestamoRepositorio(self.db)
        self.libros = LibroServicio(LibroRepositorio(self.db))
        self.usuarios = UsuarioServicio(UsuarioRepositorio(self.db), repo_prestamos)
        self.prestamos = PrestamoServicio(
            repo_prestamos, self.libros, self.usuarios, reloj=lambda: FECHA_FIJA
        )

    def crear_libro(self, titulo="Rayuela", autor="Julio Cortázar", editorial="Sudamericana",
                    anio=1963, cantidad=2):
        return self.libros.agregar(titulo, autor, editorial, anio, cantidad)

    def crear_usuario(self, nombre="Ana", apellido="Pérez", direccion="Av. Italia 1234",
                      telefono="099123456"):
        return self.usuarios.agregar(nombre, apellido, direccion, telefono)
