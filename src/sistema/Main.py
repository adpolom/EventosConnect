# ======================================================================
# Main.py  ·  Menú interactivo por consola
# ----------------------------------------------------------------------
# Este archivo es la "cara" del programa: muestra los menús, pide los
# datos al usuario, los valida y llama a ControlEvento para que haga el
# trabajo. Main.py nunca toca las estructuras de datos directamente.
#
# Cómo ejecutarlo (desde la carpeta principal del proyecto):
#     python -m src.sistema.Main
#
# Organización del menú:
#     Menú principal
#       1. Asistentes  -> menu_asistentes()  (Lista Enlazada)
#       2. Torniquete  -> menu_torniquete()  (Cola + Pila)
#       3. Eventos     -> menu_eventos()     (Árbol BST + Lista Doble)
#       4. Resumen
#       5. Datos de demostración
#       0. Salir
# ======================================================================

import os
import sys

# Permite ejecutar este archivo directamente (botón "Run" de VS Code o
# "python src/sistema/Main.py"), además de "python -m src.sistema.Main".
# Solo agrega la carpeta raíz del proyecto a la ruta de importación para
# que funcionen los imports "from src...."; no guarda datos del programa.
# Se sube tres carpetas desde este archivo: Main.py -> sistema -> src -> raíz.
RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if RAIZ_PROYECTO not in sys.path:
    sys.path.insert(0, RAIZ_PROYECTO)

# ControlEvento tiene toda la lógica; a_entero se reutiliza para validar números.
from src.sistema.ControlEvento import ControlEvento, a_entero


# ======================================================================
# Utilidades de entrada y salida
# ----------------------------------------------------------------------
# Funciones pequeñas que se usan en todos los menús, para no repetir código.
# ======================================================================
def linea():
    # Imprime una línea separadora de 60 guiones.
    print("-" * 60)


def titulo(texto):
    # Imprime un encabezado enmarcado con signos "=".
    print()
    print("=" * 60)
    print("  " + texto)
    print("=" * 60)


def pausa():
    # Espera a que el usuario presione Enter, para que alcance a leer el
    # resultado antes de que se vuelva a dibujar el menú.
    input("\nPresione Enter para continuar...")


def mostrar_resultado(resultado):
    # Recibe un objeto Resultado (ver ControlEvento.py) y lo muestra con
    # [OK] si la operación funcionó o [ERROR] si fue rechazada.
    if resultado.exito:
        print("[OK] " + resultado.mensaje)
    else:
        print("[ERROR] " + resultado.mensaje)


# ----------------------------------------------------------------------
# Funciones de lectura con validación.
# Todas usan un ciclo "while True" que se repite hasta que el usuario
# escribe un dato válido; el "return" es lo que rompe el ciclo.
# ----------------------------------------------------------------------
def leer_texto(mensaje):
    """Pide un texto hasta que no venga vacío."""
    while True:
        texto = input(mensaje).strip()     # strip() quita espacios sobrantes
        if texto != "":
            return texto
        print("  Este campo no puede quedar vacío.")


def leer_entero(mensaje, minimo=1):
    """Pide un número entero mayor o igual a 'minimo'."""
    while True:
        # a_entero devuelve None si lo escrito no es un número (por ejemplo "abc").
        numero = a_entero(input(mensaje))
        if numero is not None and numero >= minimo:
            return numero
        print("  Ingrese un número entero mayor o igual a " + str(minimo) + ".")


def leer_cedula(mensaje="Cédula: "):
    """Pide una cédula formada solo por dígitos (entre 5 y 12)."""
    while True:
        cedula = input(mensaje).strip()
        # isdigit() es True solo si todos los caracteres son números.
        if cedula.isdigit() and len(cedula) >= 5 and len(cedula) <= 12:
            return cedula
        print("  La cédula debe tener solo números (entre 5 y 12 dígitos).")


def leer_categoria():
    # Muestra las 3 categorías posibles y devuelve el texto de la elegida.
    print("Categoría:  1. General   2. VIP   3. Organizador")
    while True:
        opcion = input("Seleccione (Enter = General): ").strip()
        # Si el usuario solo presiona Enter, se toma "General" por defecto.
        if opcion == "" or opcion == "1":
            return "General"
        elif opcion == "2":
            return "VIP"
        elif opcion == "3":
            return "Organizador"
        print("  Opción no válida.")


# ======================================================================
# Submenú 1: Asistentes (Lista Enlazada)
# ----------------------------------------------------------------------
# Todos los submenús siguen el mismo patrón:
#   1. Mostrar las opciones.
#   2. Leer la opción elegida.
#   3. Con if/elif, pedir los datos necesarios y llamar a ControlEvento.
#   4. Repetir hasta que el usuario elija 0 (el "return" vuelve al menú principal).
# Se usa if/elif porque el proyecto no permite diccionarios para mapear opciones.
# ======================================================================
def menu_asistentes(control):
    # "control" es el mismo objeto ControlEvento creado en main(); así todos
    # los menús trabajan sobre las mismas estructuras y los datos se conservan.
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
            # Inscribir: se piden los 3 datos y ControlEvento decide si se acepta.
            cedula = leer_cedula()
            nombre = leer_texto("Nombre completo: ")
            categoria = leer_categoria()
            mostrar_resultado(control.inscribir_asistente(cedula, nombre, categoria))
            pausa()
        elif opcion == "2":
            # Buscar: recorre la Lista Enlazada hasta encontrar la cédula.
            cedula = leer_cedula()
            asistente = control.buscar_asistente(cedula)
            if asistente is None:
                print("[ERROR] No hay ningún asistente con la cédula " + cedula + ".")
            else:
                # str(asistente) usa el método __str__ de la clase Asistente.
                print("Encontrado: " + str(asistente))
                if control.esta_en_fila(cedula):
                    print("  (Está esperando en la fila del torniquete.)")
            pausa()
        elif opcion == "3":
            control.mostrar_padron()
            pausa()
        elif opcion == "4":
            # Eliminar: ControlEvento revisa que no esté dentro ni en la fila.
            cedula = leer_cedula()
            mostrar_resultado(control.eliminar_asistente(cedula))
            pausa()
        elif opcion == "0":
            return
        else:
            print("Opción no válida.")


# ======================================================================
# Submenú 2: Torniquete (Cola + Pila)
# ----------------------------------------------------------------------
# Simula la puerta del evento:
#   Llegada (encolar) -> Dar ingreso (desencolar + apilar) -> Deshacer (desapilar)
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
            # Solo entra a la Cola si está inscrito, no está dentro y no está ya en la fila.
            cedula = leer_cedula("Cédula de quien llega: ")
            mostrar_resultado(control.llegar_a_fila(cedula))
            pausa()
        elif opcion == "2":
            # Mira el frente de la Cola sin sacar a nadie.
            siguiente = control.ver_siguiente()
            if siguiente is None:
                print("La fila de espera está vacía.")
            else:
                print("Sigue: " + str(siguiente))
            pausa()
        elif opcion == "3":
            # Atiende al primero de la Cola (FIFO) y lo registra en la Pila.
            mostrar_resultado(control.dar_ingreso())
            pausa()
        elif opcion == "4":
            control.mostrar_fila()
            pausa()
        elif opcion == "5":
            control.mostrar_bitacora()
            pausa()
        elif opcion == "6":
            # Saca el tope de la Pila (LIFO): siempre se deshace el último ingreso.
            mostrar_resultado(control.deshacer_ultimo_ingreso())
            pausa()
        elif opcion == "0":
            return
        else:
            print("Opción no válida.")


# ======================================================================
# Submenú 3: Eventos (Árbol BST + Lista Doblemente Enlazada)
# ----------------------------------------------------------------------
# Catálogo (BST): buscar por ID y listar ordenado.
# Agenda (Lista Doble): ver adelante/atrás, retirar y volver a programar.
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
            # Registrar: se guarda en el BST y al final de la agenda.
            id_evento = leer_entero("ID del evento: ")
            nombre = leer_texto("Nombre del evento: ")
            capacidad = leer_entero("Capacidad (aforo): ")
            escenario = leer_texto("Escenario: ")
            mostrar_resultado(control.registrar_evento(id_evento, nombre, capacidad, escenario))
            pausa()
        elif opcion == "2":
            # Buscar: el BST baja por la izquierda o la derecha según el ID.
            id_evento = leer_entero("ID del evento: ")
            evento = control.buscar_evento(id_evento)
            if evento is None:
                print("[ERROR] No existe un evento con el ID " + str(id_evento) + ".")
            else:
                print("Encontrado: " + str(evento))
                # Un evento puede estar en el catálogo pero no en la agenda.
                if control.esta_en_agenda(id_evento):
                    print("  (Está programado en la agenda.)")
                else:
                    print("  (No está en la agenda.)")
            pausa()
        elif opcion == "3":
            # Recorrido in-orden del BST: sale ordenado de menor a mayor ID.
            control.mostrar_catalogo()
            pausa()
        elif opcion == "4":
            # Lista Doble recorrida con el puntero "siguiente".
            control.mostrar_agenda_adelante()
            pausa()
        elif opcion == "5":
            # Lista Doble recorrida con el puntero "anterior".
            control.mostrar_agenda_atras()
            pausa()
        elif opcion == "6":
            # Lo quita de la agenda, pero sigue en el catálogo.
            id_evento = leer_entero("ID del evento a retirar: ")
            mostrar_resultado(control.retirar_de_agenda(id_evento))
            pausa()
        elif opcion == "7":
            # Lo vuelve a poner al final de la agenda.
            id_evento = leer_entero("ID del evento a programar: ")
            mostrar_resultado(control.programar_en_agenda(id_evento))
            pausa()
        elif opcion == "0":
            return
        else:
            print("Opción no válida.")


# ======================================================================
# Menú principal
# ======================================================================
def main():
    # Se crea UN solo controlador para todo el programa. Dentro de él viven
    # las 5 estructuras; se le pasa a cada submenú para compartir los datos.
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
            return       # Sale de main() y el programa termina.
        else:
            print("Opción no válida.")


# Este bloque solo se ejecuta cuando se corre el archivo como programa
# (y no cuando otro archivo lo importa).
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # El usuario presionó Ctrl+C: se cierra con un mensaje en vez de un error.
        print("\nPrograma interrumpido. ¡Hasta pronto!")
    except EOFError:
        # La entrada se cerró (por ejemplo, Ctrl+Z en Windows): cierre limpio.
        print("\nEntrada finalizada. ¡Hasta pronto!")
