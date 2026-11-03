from src.modelos.Asistente import Asistente
from src.modelos.Evento import Evento
from src.estructuras.ListaEnlazada import ListaEnlazada
from src.estructuras.Cola import Cola
from src.estructuras.Pila import Pila
from src.estructuras.ArbolBST import ArbolBST
from src.estructuras.ListaDoblementeEnlazada import ListaDoblementeEnlazada


def a_entero(valor):
    """
    Convierte un valor a int. Devuelve None si no es un numero entero valido.
    (Se captura solo ValueError: str() nunca falla, y asi se evita usar
    una tupla de excepciones, que el proyecto no permite.)
    """
    try:
        return int(str(valor).strip())
    except ValueError:
        return None


class Resultado:
    """
    Respuesta de una operacion del sistema.
    Se usa en lugar de devolver varios valores a la vez (eso seria una tupla,
    que el proyecto no permite). Main.py lee 'exito' y muestra 'mensaje'.
    """
    def __init__(self, exito: bool, mensaje: str, dato=None):
        self.exito = exito        # True si la operacion se completo
        self.mensaje = mensaje    # Texto para mostrar en la consola
        self.dato = dato          # Objeto involucrado (Asistente o Evento), si aplica


class ControlEvento:
    """
    Controlador central de EventosConnect.
    Une las 5 estructuras del proyecto y aplica las reglas del negocio,
    de modo que Main.py solo se encarga de pedir datos y mostrar resultados.

      - padron    (ListaEnlazada)           : asistentes inscritos
      - fila      (Cola)                    : personas esperando en el torniquete (FIFO)
      - bitacora  (Pila)                    : ingresos registrados, permite deshacer (LIFO)
      - catalogo  (ArbolBST)                : todos los eventos, indexados por id_evento
      - agenda    (ListaDoblementeEnlazada) : eventos programados, navegable en ambos sentidos
    """
    def __init__(self):
        self.padron = ListaEnlazada()
        self.fila = Cola()
        self.bitacora = Pila()
        self.catalogo = ArbolBST()
        self.agenda = ListaDoblementeEnlazada()
        self.total_eventos = 0           # El ArbolBST no lleva un contador propio
        self.datos_demo_cargados = False

    # ==================================================================
    # ASISTENTES (Lista Enlazada)
    # ==================================================================
    def inscribir_asistente(self, cedula, nombre, categoria="General") -> Resultado:
        """Agrega un asistente al padron si su cedula no esta repetida."""
        cedula = str(cedula).strip()
        nombre = str(nombre).strip()

        if cedula == "" or nombre == "":
            return Resultado(False, "La cédula y el nombre son obligatorios.")
        if self.padron.existe(cedula):
            existente = self.padron.buscar(cedula)
            return Resultado(False, "Ya existe un asistente con la cédula " + cedula
                             + ": " + existente.nombre + ".")

        nuevo = Asistente(cedula, nombre, categoria)
        self.padron.insertar_al_final(nuevo)
        return Resultado(True, "Asistente inscrito: " + str(nuevo), nuevo)

    def buscar_asistente(self, cedula):
        """Devuelve el Asistente con esa cedula, o None si no esta inscrito."""
        return self.padron.buscar(str(cedula).strip())

    def esta_en_fila(self, cedula) -> bool:
        """
        Indica si la persona ya esta esperando en la fila.
        La Cola no tiene un metodo de busqueda, asi que se recorre nodo por
        nodo (solo lectura, sin sacar a nadie). La comparacion usa la
        sobrecarga Asistente.__eq__, que acepta la cedula como texto.
        """
        cedula = str(cedula).strip()
        actual = self.fila.frente
        while actual is not None:
            if actual.dato == cedula:
                return True
            actual = actual.siguiente
        return False

    def eliminar_asistente(self, cedula) -> Resultado:
        """Quita del padron a un asistente que no este dentro ni en la fila."""
        cedula = str(cedula).strip()
        asistente = self.padron.buscar(cedula)

        if asistente is None:
            return Resultado(False, "No hay ningún asistente con la cédula " + cedula + ".")
        if asistente.estado_ingreso:
            return Resultado(False, asistente.nombre + " está DENTRO del recinto; "
                             "no se puede eliminar del padrón.")
        if self.esta_en_fila(cedula):
            return Resultado(False, asistente.nombre + " está esperando en la fila; "
                             "no se puede eliminar del padrón.")

        self.padron.eliminar(cedula)
        return Resultado(True, "Asistente eliminado del padrón: " + asistente.nombre + ".", asistente)

    def mostrar_padron(self):
        self.padron.mostrar()

    # ==================================================================
    # TORNIQUETE (Cola = fila de espera, Pila = bitacora de ingresos)
    # ==================================================================
    def llegar_a_fila(self, cedula) -> Resultado:
        """La persona llega a la puerta: se valida su credencial y se encola."""
        cedula = str(cedula).strip()
        asistente = self.padron.buscar(cedula)

        if asistente is None:
            return Resultado(False, "Credencial rechazada: la cédula " + cedula
                             + " no está inscrita en el padrón.")
        if asistente.estado_ingreso:
            return Resultado(False, asistente.nombre + " ya está DENTRO del recinto.")
        if self.esta_en_fila(cedula):
            return Resultado(False, asistente.nombre + " ya está esperando en la fila.")

        self.fila.encolar(asistente)
        return Resultado(True, asistente.nombre + " entró a la fila. Posición: "
                         + str(self.fila.obtener_tamano()) + ".", asistente)

    def ver_siguiente(self):
        """Devuelve quien sigue en la fila sin sacarlo (o None)."""
        return self.fila.ver_frente()

    def dar_ingreso(self) -> Resultado:
        """Atiende al primero de la fila: entra al recinto y queda en la bitacora."""
        if self.fila.esta_vacia():
            return Resultado(False, "No hay nadie esperando en la fila.")

        asistente = self.fila.desencolar()
        asistente.cambiar_estado_ingreso(True)
        self.bitacora.apilar(asistente)
        return Resultado(True, "Ingreso registrado: " + asistente.nombre
                         + " (" + asistente.categoria + ").", asistente)

    def deshacer_ultimo_ingreso(self) -> Resultado:
        """Revierte el ingreso mas reciente (tope de la pila): la persona queda FUERA."""
        if self.bitacora.esta_vacia():
            return Resultado(False, "No hay ingresos para deshacer.")

        asistente = self.bitacora.desapilar()
        asistente.cambiar_estado_ingreso(False)
        return Resultado(True, "Se deshizo el ingreso de " + asistente.nombre
                         + ". Queda FUERA y puede volver a hacer la fila.", asistente)

    def mostrar_fila(self):
        self.fila.mostrar()

    def mostrar_bitacora(self):
        self.bitacora.mostrar()

    # ==================================================================
    # EVENTOS (Arbol BST = catalogo, Lista Doble = agenda)
    # ==================================================================
    def registrar_evento(self, id_evento, nombre, capacidad, escenario) -> Resultado:
        """Crea el evento en el catalogo (BST) y lo programa al final de la agenda."""
        id_evento = a_entero(id_evento)
        capacidad = a_entero(capacidad)
        if id_evento is None or capacidad is None:
            return Resultado(False, "El ID y la capacidad deben ser números enteros.")

        nombre = str(nombre).strip()
        escenario = str(escenario).strip()

        if id_evento <= 0:
            return Resultado(False, "El ID del evento debe ser mayor que 0.")
        if capacidad <= 0:
            return Resultado(False, "La capacidad debe ser mayor que 0.")
        if nombre == "" or escenario == "":
            return Resultado(False, "El nombre y el escenario son obligatorios.")

        evento = Evento(id_evento, nombre, capacidad, escenario)
        if not self.catalogo.insertar(evento):
            existente = self.catalogo.buscar(id_evento)
            return Resultado(False, "Ya existe un evento con el ID " + str(id_evento)
                             + ": " + existente.nombre + ".")

        self.total_eventos += 1
        self.agenda.insertar_final(evento)
        return Resultado(True, "Evento registrado y programado en la agenda: " + str(evento), evento)

    def buscar_evento(self, id_evento):
        """Busca en el BST. Devuelve el Evento o None (tambien si el ID no es numerico)."""
        id_evento = a_entero(id_evento)   # El BST compara con <, asi que debe ser int
        if id_evento is None:
            return None
        return self.catalogo.buscar(id_evento)

    def esta_en_agenda(self, id_evento) -> bool:
        id_evento = a_entero(id_evento)
        if id_evento is None:
            return False
        return self.agenda.buscar_por_id(id_evento) is not None

    def retirar_de_agenda(self, id_evento) -> Resultado:
        """
        Quita un evento de la agenda (Lista Doble). El evento sigue en el
        catalogo (BST) y se puede volver a programar despues.
        """
        evento = self.buscar_evento(id_evento)
        if evento is None:
            return Resultado(False, "No existe un evento con el ID " + str(id_evento) + ".")
        if not self.agenda.eliminar_por_id(evento.id_evento):
            return Resultado(False, "El evento '" + evento.nombre + "' no está en la agenda.")
        return Resultado(True, "Evento retirado de la agenda: " + evento.nombre
                         + ". Sigue en el catálogo.", evento)

    def programar_en_agenda(self, id_evento) -> Resultado:
        """Vuelve a poner al final de la agenda un evento que ya existe en el catalogo."""
        evento = self.buscar_evento(id_evento)
        if evento is None:
            return Resultado(False, "No existe un evento con el ID " + str(id_evento)
                             + ". Primero regístrelo.")
        if self.esta_en_agenda(evento.id_evento):
            return Resultado(False, "El evento '" + evento.nombre + "' ya está en la agenda.")
        self.agenda.insertar_final(evento)
        return Resultado(True, "Evento programado al final de la agenda: " + evento.nombre + ".", evento)

    def mostrar_catalogo(self):
        print("=== CATÁLOGO DE EVENTOS (ordenado por ID) ===")
        self.catalogo.recorrido_inorden()

    def mostrar_agenda_adelante(self):
        self.agenda.mostrar_adelante()

    def mostrar_agenda_atras(self):
        self.agenda.mostrar_atras()

    # ==================================================================
    # RESUMEN Y DATOS DE DEMOSTRACION
    # ==================================================================
    def mostrar_resumen(self):
        print("=== RESUMEN DE EVENTOSCONNECT ===")
        print("  Asistentes inscritos (padrón) : " + str(self.padron.obtener_tamano()))
        print("  Personas en la fila           : " + str(self.fila.obtener_tamano()))
        # Cada ingreso queda en la bitacora y "deshacer" lo saca, asi que el
        # tamano de la pila es exactamente la cantidad de personas dentro.
        print("  Personas dentro del recinto   : " + str(self.bitacora.obtener_tamano()))
        siguiente = self.fila.ver_frente()
        if siguiente is not None:
            print("  Siguiente en la fila          : " + siguiente.nombre)
        ultimo = self.bitacora.ver_tope()
        if ultimo is not None:
            print("  Último ingreso                : " + ultimo.nombre)
        print("  Eventos en el catálogo        : " + str(self.total_eventos))
        print("  Eventos en la agenda          : " + str(self.agenda.tamanio))

    def cargar_datos_demo(self) -> Resultado:
        """Carga asistentes y eventos de ejemplo para probar o sustentar el proyecto."""
        if self.datos_demo_cargados:
            return Resultado(False, "Los datos de demostración ya fueron cargados.")

        asistentes = 0   # Cuantos se insertaron (si ya existian, se omiten)
        if self.inscribir_asistente("11111", "Ana Gómez", "VIP").exito:
            asistentes += 1
        if self.inscribir_asistente("22222", "Carlos Pérez", "General").exito:
            asistentes += 1
        if self.inscribir_asistente("33333", "Laura Martínez", "Organizador").exito:
            asistentes += 1
        if self.inscribir_asistente("44444", "Diego Rodríguez", "General").exito:
            asistentes += 1
        if self.inscribir_asistente("55555", "Sofía Herrera", "VIP").exito:
            asistentes += 1

        # Se registran desordenados a proposito: la agenda conserva el orden
        # de programacion y el catalogo (BST) los muestra ordenados por ID.
        eventos = 0
        if self.registrar_evento(105, "Apertura y Registro", 300, "Auditorio Principal").exito:
            eventos += 1
        if self.registrar_evento(102, "Taller de Python", 40, "Sala 2").exito:
            eventos += 1
        if self.registrar_evento(108, "Ponencia de IA", 150, "Sala 1").exito:
            eventos += 1
        if self.registrar_evento(101, "Feria de Proyectos", 200, "Plaza Central").exito:
            eventos += 1
        if self.registrar_evento(110, "Cierre y Premiación", 300, "Auditorio Principal").exito:
            eventos += 1

        self.datos_demo_cargados = True
        mensaje = ("Datos cargados: " + str(asistentes) + " de 5 asistentes "
                   "(cédulas 11111, 22222, 33333, 44444, 55555) y "
                   + str(eventos) + " de 5 eventos (IDs 101, 102, 105, 108, 110).")
        if asistentes < 5 or eventos < 5:
            mensaje += " Los que ya existían se omitieron."
        return Resultado(True, mensaje)
