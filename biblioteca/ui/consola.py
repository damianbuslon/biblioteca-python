"""Funciones de entrada/salida reutilizables por todos los menús."""
from ..excepciones import ValidacionError

ANCHO = 78


class OperacionCancelada(Exception):
    """El usuario escribió 'cancelar' durante una operación."""


def titulo(texto):
    print("\n" + "=" * ANCHO)
    print(texto.center(ANCHO))
    print("=" * ANCHO)


def ok(mensaje):
    print(f"\n[OK] {mensaje}")


def error(mensaje):
    print(f"\n[ERROR] {mensaje}")


def aviso(mensaje):
    print(f"\n{mensaje}")


def pausar():
    input("\nPresione Enter para continuar...")


def pedir(prompt, validador=None, defecto=None):
    """Pide un dato y repite la pregunta hasta que sea válido.

    - validador: función que devuelve el valor limpio o lanza ValidacionError.
    - defecto:   si se indica, Enter conserva ese valor (útil al actualizar).
    - Escribir 'cancelar' aborta la operación.
    """
    sufijo = f" [{defecto}]" if defecto is not None else ""
    while True:
        entrada = input(f"{prompt}{sufijo}: ").strip()
        if entrada.lower() == "cancelar":
            raise OperacionCancelada()
        if entrada == "" and defecto is not None:
            return defecto
        try:
            return validador(entrada) if validador else entrada
        except ValidacionError as exc:
            print(f"  [!] {exc}")


def elegir(prompt, opciones_validas):
    """Pide una opción que pertenezca a opciones_validas (lista de textos)."""
    def validar(valor):
        if valor not in opciones_validas:
            raise ValidacionError("Opción inválida.")
        return valor

    return pedir(prompt, validar)


def confirmar(pregunta):
    """Pregunta sí/no. Devuelve True o False."""
    while True:
        respuesta = input(f"{pregunta} (s/n): ").strip().lower()
        if respuesta in ("s", "si", "sí", "y", "yes"):
            return True
        if respuesta in ("n", "no"):
            return False
        print("  [!] Responda 's' o 'n'.")


def _recortar(valor, maximo=34):
    texto = str(valor)
    return texto if len(texto) <= maximo else texto[: maximo - 3] + "..."


def mostrar_tabla(columnas, filas):
    """Imprime una tabla ASCII alineada. Muestra aviso si no hay filas."""
    if not filas:
        print("\n  (sin resultados)")
        return
    textos = [[_recortar(celda) for celda in fila] for fila in filas]
    anchos = [max(len(col), *(len(f[i]) for f in textos)) for i, col in enumerate(columnas)]
    linea = "+" + "+".join("-" * (a + 2) for a in anchos) + "+"

    def formatear(fila):
        return "| " + " | ".join(celda.ljust(a) for celda, a in zip(fila, anchos)) + " |"

    print()
    print(linea)
    print(formatear(columnas))
    print(linea)
    for fila in textos:
        print(formatear(fila))
    print(linea)
    print(f"  Total: {len(textos)} registro(s)")
