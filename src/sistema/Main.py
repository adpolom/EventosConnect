import os
import sys

# Permite ejecutar este archivo directamente (boton "Run" de VS Code o
# "python src/sistema/Main.py"), ademas de "python -m src.sistema.Main".
# Solo agrega la carpeta raiz del proyecto a la ruta de importacion para
# que funcionen los imports "from src...."; no guarda datos del programa.
RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if RAIZ_PROYECTO not in sys.path:
    sys.path.insert(0, RAIZ_PROYECTO)

from src.sistema.ControlEvento import ControlEvento, a_entero


# ======================================================================
# Utilidades de entrada y salida
# ======================================================================
def linea():
    print("-" * 60)


def titulo(texto):
    print()
    print("=" * 60)
    print("  " + texto)
    print("=" * 60)


def pausa():
    input("\nPresione Enter para continuar...")


def mostrar_resultado(resultado):
    if resultado.exito:
        print("[OK] " + resultado.mensaje)
    else:
        print("[ERROR] " + resultado.mensaje)


def leer_texto(mensaje):
    """Pide un texto hasta que no venga vacio."""
    while True:
        texto = input(mensaje).strip()
        if texto != "":
            return texto
        print("  Este campo no puede quedar vacío.")


def leer_entero(mensaje, minimo=1):
    """Pide un numero entero mayor o igual a 'minimo'."""
    while True:
        numero = a_entero(input(mensaje))
        if numero is not None and numero >= minimo:
            return numero
        print("  Ingrese un número entero mayor o igual a " + str(minimo) + ".")


def leer_cedula(mensaje="Cédula: "):
    """Pide una cedula formada solo por digitos (entre 5 y 12)."""
    while True:
        cedula = input(mensaje).strip()
        if cedula.isdigit() and len(cedula) >= 5 and len(cedula) <= 12:
            return cedula
        print("  La cédula debe tener solo números (entre 5 y 12 dígitos).")


def leer_categoria():
    print("Categoría:  1. General   2. VIP   3. Organizador")
    while True:
        opcion = input("Seleccione (Enter = General): ").strip()
        if opcion == "" or opcion == "1":
            return "General"
        elif opcion == "2":
            return "VIP"
        elif opcion == "3":
            return "Organizador"
        print("  Opción no válida.")


# ======================================================================
# Submenu 1: Asistentes (Lista Enlazada)
# ======================================================================
def menu_asistentes(control):
    while True:
        titulo("ASISTENTES  ·  Padrón (Lista Enlazada)")
        print("  1. Inscribir asistente")
        print("  2. Buscar asistente por cédula")
        print("  3. Ver padrón completo")
        print("  4. Eliminar asistente del padrón")
        print("  0. Volver al menú principal")
        linea()
        opcion = input("Opción: ").strip()

        if opcion == "1":
            cedula = leer_cedula()
            nombre = leer_texto("Nombre completo: ")
            categoria = leer_categoria()
            mostrar_resultado(control.inscribir_asistente(cedula, nombre, categoria))
            pausa()
        elif opcion == "2":
            cedula = leer_cedula()
            asistente = control.buscar_asistente(cedula)
            if asistente is None:
                print("[ERROR] No hay ningún asistente con la cédula " + cedula + ".")
            else:
                print("Encontrado: " + str(asistente))
                if control.esta_en_fila(cedula):
                    print("  (Está esperando en la fila del torniquete.)")
            pausa()
        elif opcion == "3":
            control.mostrar_padron()
            pausa()
        elif opcion == "4":
            cedula = leer_cedula()
            mostrar_resultado(control.eliminar_asistente(cedula))
            pausa()
        elif opcion == "0":
            return
        else:
            print("Opción no válida.")


# ======================================================================
# Submenu 2: Torniquete (Cola + Pila)
# ======================================================================
def menu_torniquete(control):
    while True:
        titulo("TORNIQUETE  ·  Fila (Cola) y Bitácora (Pila)")
        print("  1. Llegada a la fila (validar credencial)")
        print("  2. Ver quién sigue en la fila")
        print("  3. Dar ingreso al siguiente")
        print("  4. Ver fila de espera")
        print("  5. Ver bitácora de ingresos")
        print("  6. Deshacer último ingreso")
        print("  0. Volver al menú principal")
        linea()
        opcion = input("Opción: ").strip()

        if opcion == "1":
            cedula = leer_cedula("Cédula de quien llega: ")
            mostrar_resultado(control.llegar_a_fila(cedula))
            pausa()
        elif opcion == "2":
            siguiente = control.ver_siguiente()
            if siguiente is None:
                print("La fila de espera está vacía.")
            else:
                print("Sigue: " + str(siguiente))
            pausa()
        elif opcion == "3":
            mostrar_resultado(control.dar_ingreso())
            pausa()
        elif opcion == "4":
            control.mostrar_fila()
            pausa()
        elif opcion == "5":
            control.mostrar_bitacora()
            pausa()
        elif opcion == "6":
            mostrar_resultado(control.deshacer_ultimo_ingreso())
            pausa()
        elif opcion == "0":
            return
        else:
            print("Opción no válida.")


# ======================================================================
# Submenu 3: Eventos (Arbol BST + Lista Doblemente Enlazada)
# ======================================================================
def menu_eventos(control):
    while True:
        titulo("EVENTOS  ·  Catálogo (Árbol BST) y Agenda (Lista Doble)")
        print("  1. Registrar evento")
        print("  2. Buscar evento por ID")
        print("  3. Ver catálogo ordenado por ID")
        print("  4. Ver agenda (inicio -> fin)")
        print("  5. Ver agenda en reversa (fin -> inicio)")
        print("  6. Retirar evento de la agenda")
        print("  7. Volver a programar un evento en la agenda")
        print("  0. Volver al menú principal")
        linea()
        opcion = input("Opción: ").strip()

        if opcion == "1":
            id_evento = leer_entero("ID del evento: ")
            nombre = leer_texto("Nombre del evento: ")
            capacidad = leer_entero("Capacidad (aforo): ")
            escenario = leer_texto("Escenario: ")
            mostrar_resultado(control.registrar_evento(id_evento, nombre, capacidad, escenario))
            pausa()
        elif opcion == "2":
            id_evento = leer_entero("ID del evento: ")
            evento = control.buscar_evento(id_evento)
            if evento is None:
                print("[ERROR] No existe un evento con el ID " + str(id_evento) + ".")
            else:
                print("Encontrado: " + str(evento))
                if control.esta_en_agenda(id_evento):
                    print("  (Está programado en la agenda.)")
                else:
                    print("  (No está en la agenda.)")
            pausa()
        elif opcion == "3":
            control.mostrar_catalogo()
            pausa()
        elif opcion == "4":
            control.mostrar_agenda_adelante()
            pausa()
        elif opcion == "5":
            control.mostrar_agenda_atras()
            pausa()
        elif opcion == "6":
            id_evento = leer_entero("ID del evento a retirar: ")
            mostrar_resultado(control.retirar_de_agenda(id_evento))
            pausa()
        elif opcion == "7":
            id_evento = leer_entero("ID del evento a programar: ")
            mostrar_resultado(control.programar_en_agenda(id_evento))
            pausa()
        elif opcion == "0":
            return
        else:
            print("Opción no válida.")


# ======================================================================
# Menu principal
# ======================================================================
def main():
    control = ControlEvento()

    while True:
        titulo("EVENTOSCONNECT  ·  Menú principal")
        print("  1. Asistentes (padrón)")
        print("  2. Torniquete de acceso (fila y bitácora)")
        print("  3. Eventos (catálogo y agenda)")
        print("  4. Resumen del sistema")
        print("  5. Cargar datos de demostración")
        print("  0. Salir")
        linea()
        opcion = input("Opción: ").strip()

        if opcion == "1":
            menu_asistentes(control)
        elif opcion == "2":
            menu_torniquete(control)
        elif opcion == "3":
            menu_eventos(control)
        elif opcion == "4":
            control.mostrar_resumen()
            pausa()
        elif opcion == "5":
            mostrar_resultado(control.cargar_datos_demo())
            pausa()
        elif opcion == "0":
            print("Gracias por usar EventosConnect. ¡Hasta pronto!")
            return
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido. ¡Hasta pronto!")
    except EOFError:
        print("\nEntrada finalizada. ¡Hasta pronto!")
