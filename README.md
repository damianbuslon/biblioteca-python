# Sistema de Gestión de Biblioteca

Aplicación de consola desarrollada en **Python 3** (solo biblioteca estándar) con
base de datos local **SQLite**. Permite gestionar libros, usuarios y préstamos.

## Requisitos
- Python 3.8 o superior. No hay que instalar nada más.

## Ejecución
```bash
python main.py
```
La base de datos se crea sola en `datos/biblioteca.db` la primera vez.

## Pruebas automáticas
```bash
python -m unittest discover -v
```

## Funcionalidades
| Módulo | Operaciones |
|---|---|
| Libros | Agregar, listar todos, listar disponibles, buscar (título/autor/editorial), actualizar, eliminar |
| Usuarios | Agregar, listar, buscar (nombre/apellido), actualizar, eliminar |
| Préstamos | Registrar, listar vigentes, historial, devolver, actualizar, eliminar |

## Reglas de negocio
- No se presta un libro sin ejemplares disponibles.
- Máximo 3 préstamos vigentes por usuario (configurable en `biblioteca/config.py`).
- Un usuario no puede tener dos préstamos vigentes del mismo libro.
- No se elimina un libro ni un usuario con préstamos vigentes.
- No se puede reducir la cantidad de ejemplares por debajo de los ya prestados.
- No se permiten libros ni usuarios duplicados (sin distinguir mayúsculas ni acentos).
- Los préstamos vencidos se marcan como `VENCIDO` con los días de retraso.

## Arquitectura (por capas)
```
main.py                      Punto de entrada: ensambla la aplicación
biblioteca/
  config.py                  Parámetros y reglas ajustables
  excepciones.py             Errores propios (validación / no encontrado / regla de negocio)
  validaciones.py            Validación y limpieza de datos
  texto.py                   Normalización de texto (búsquedas sin acentos)
  modelos.py                 Libro, Usuario, Prestamo
  database.py                Conexión SQLite y esquema
  repositorios/              Acceso a datos (solo SQL)
  servicios/                 Reglas de negocio
  ui/                        Menús de consola
tests/                       Pruebas automáticas (unittest)
datos/                       Base de datos local (no se sube a Git)
```
Flujo: `ui  ->  servicios  ->  repositorios  ->  SQLite`. Cada capa solo conoce a la siguiente.

## Modelo de datos
```
libros(id, titulo, autor, editorial, anio, cantidad)
usuarios(id, nombre, apellido, direccion, telefono)
prestamos(id, libro_id -> libros, usuario_id -> usuarios,
          fecha_prestamo, fecha_vencimiento, fecha_devolucion)
```
Los ejemplares disponibles no se guardan: se calculan como
`cantidad - préstamos vigentes`, así nunca pueden quedar inconsistentes.
