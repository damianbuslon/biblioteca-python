"""Punto de entrada del Sistema de Gestión de Biblioteca.

Aquí se "ensambla" la aplicación: se crea la base de datos, los repositorios,
los servicios y los menús, conectándolos entre sí (inyección de dependencias).

Ejecutar con:  python main.py
"""
from biblioteca.database import Database
from biblioteca.repositorios import LibroRepositorio, PrestamoRepositorio, UsuarioRepositorio
from biblioteca.servicios import LibroServicio, PrestamoServicio, UsuarioServicio
from biblioteca.ui.menu import Menu
from biblioteca.ui.menu_libros import MenuLibros
from biblioteca.ui.menu_prestamos import MenuPrestamos
from biblioteca.ui.menu_usuarios import MenuUsuarios


def construir_menu_principal(db):
    repo_libros = LibroRepositorio(db)
    repo_usuarios = UsuarioRepositorio(db)
    repo_prestamos = PrestamoRepositorio(db)

    libros = LibroServicio(repo_libros)
    usuarios = UsuarioServicio(repo_usuarios, repo_prestamos)
    prestamos = PrestamoServicio(repo_prestamos, libros, usuarios)

    principal = Menu("SISTEMA DE GESTIÓN DE BIBLIOTECA", texto_salida="Salir")
    principal.agregar_submenu("Gestión de libros", MenuLibros(libros).construir())
    principal.agregar_submenu("Gestión de usuarios", MenuUsuarios(usuarios).construir())
    principal.agregar_submenu(
        "Gestión de préstamos", MenuPrestamos(prestamos, libros, usuarios).construir()
    )
    return principal


def main():
    db = Database()
    try:
        construir_menu_principal(db).ejecutar()
        print("\nHasta luego.")
    except (KeyboardInterrupt, EOFError):
        print("\n\nSesión finalizada. Hasta luego.")
    finally:
        db.cerrar()


if __name__ == "__main__":
    main()
