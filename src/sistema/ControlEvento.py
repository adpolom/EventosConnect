# ======================================================================
# ControlEvento.py  ·  Módulo de Sistema (Integración)
# ----------------------------------------------------------------------
# Este archivo es el "cerebro" del programa. Aquí se crean las 5
# estructuras de datos del proyecto y se aplican las reglas del negocio
# (quién puede hacer la fila, quién puede entrar, qué se puede borrar...).
#
# Main.py NO toca las estructuras directamente: solo pide datos al usuario
# y llama a los métodos de esta clase. Así cada archivo tiene una sola
# responsabilidad:
#     Main.py          -> pedir datos y mostrar resultados (interfaz)
#     ControlEvento.py -> decidir qué se hace con los datos (lógica)
# ======================================================================

# --- Importaciones ---------------------------------------------------
# Las rutas empiezan por "src." porque el programa se ejecuta desde la
# carpeta principal del proyecto (python -m src.sistema.Main).

# Modelos: las "cosas" que guardamos dentro de las estructuras.
from src.modelos.Asistente import Asistente
from src.modelos.Evento import Evento

# Estructuras de datos hechas por el equipo (todas con nodos y referencias).
from src.estructuras.ListaEnlazada import ListaEnlazada
from src.estructuras.Cola import Cola
from src.estructuras.Pila import Pila
from src.estructuras.ArbolBST import ArbolBST
from src.estructuras.ListaDoblementeEnlazada import ListaDoblementeEnlazada


def a_entero(valor):
    """
    Convierte un valor a número entero (int).
    Si el valor no es un número válido (por ejemplo "abc"), devuelve None
    en lugar de hacer que el programa se caiga.

    Ejemplos:
        a_entero("105")  -> 105
        a_entero(" 7 ")  -> 7
        a_entero("abc")  -> None

    Solo se captura ValueError (y no una tupla de excepciones como
    (ValueError, TypeError)) porque el proyecto no permite tuplas.
    Como primero se hace str(valor), nunca llega un TypeError.
    """
    try:
        # str() convierte cualquier cosa a texto, strip() quita espacios
        # al inicio y al final, e int() intenta convertir ese texto a número.
        return int(str(valor).strip())
    except ValueError:
        # int() lanza ValueError cuando el texto no es un número.
        return None


class Resultado:
    """
    Objeto que devuelve cada operación del sistema para decir cómo le fue.

    ¿Por qué existe? Una operación necesita devolver varias cosas a la vez:
    si funcionó, un mensaje para el usuario y, a veces, el objeto afectado.
    En Python lo normal sería devolver una tupla (True, "mensaje"), pero el
    proyecto no permite tuplas, así que agrupamos esos datos en un objeto.

    Main.py lo usa así:
        resultado = control.dar_ingreso()
        if resultado.exito: ...      # ¿funcionó?
        print(resultado.mensaje)     # ¿qué le digo al usuario?
    """
    def __init__(self, exito: bool, mensaje: str, dato=None):
        self.exito = exito        # True si la operación se completó, False si se rechazó
        self.mensaje = mensaje    # Texto que se mostrará en la consola
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
        # Al crear el controlador se crean las 5 estructuras, todas vacías.

        # Lista Enlazada: el "padrón", la lista de todos los inscritos.
        # Se usa una lista porque hay que recorrerla para buscar cédulas
        # y poder eliminar a alguien de cualquier posición.
        self.padron = ListaEnlazada()

        # Cola (FIFO = First In, First Out): la fila en la puerta.
        # El primero que llega es el primero que entra, como en una fila real.
        self.fila = Cola()

        # Pila (LIFO = Last In, First Out): la bitácora de ingresos.
        # El último que entró queda arriba, por eso "deshacer" siempre
        # revierte el ingreso más reciente.
        self.bitacora = Pila()

        # Árbol Binario de Búsqueda: el catálogo de eventos.
        # Ordena los eventos por ID: los menores a la izquierda y los mayores
        # a la derecha, así buscar un evento es rápido (O(log n) en promedio).
        self.catalogo = ArbolBST()

        # Lista Doblemente Enlazada: la agenda del día.
        # Cada nodo apunta al siguiente y al anterior, así se puede recorrer
        # de inicio a fin y también de fin a inicio.
        self.agenda = ListaDoblementeEnlazada()

        # El ArbolBST no tiene un contador de elementos, así que lo llevamos aquí.
        self.total_eventos = 0

        # Bandera para no cargar los datos de demostración dos veces.
        self.datos_demo_cargados = False

    # ==================================================================
    # ASISTENTES (Lista Enlazada)
    # ==================================================================
    def inscribir_asistente(self, cedula, nombre, categoria="General") -> Resultado:
        """Agrega un asistente al padrón si su cédula no está repetida."""
        # Se normalizan los datos: todo a texto y sin espacios sobrantes.
        # Así "12345" y " 12345 " se consideran la misma cédula.
        cedula = str(cedula).strip()
        nombre = str(nombre).strip()

        # Regla 1: la cédula y el nombre no pueden estar vacíos.
        if cedula == "" or nombre == "":
            return Resultado(False, "La cédula y el nombre son obligatorios.")

        # Regla 2: no puede haber dos asistentes con la misma cédula.
        # existe() recorre la Lista Enlazada nodo por nodo buscando la cédula.
        if self.padron.existe(cedula):
            existente = self.padron.buscar(cedula)
            return Resultado(False, "Ya existe un asistente con la cédula " + cedula
                             + ": " + existente.nombre + ".")

        # Si pasó las reglas: se crea el objeto Asistente y se agrega al final.
        nuevo = Asistente(cedula, nombre, categoria)
        self.padron.insertar_al_final(nuevo)
        return Resultado(True, "Asistente inscrito: " + str(nuevo), nuevo)

    def buscar_asistente(self, cedula):
        """Devuelve el Asistente con esa cédula, o None si no está inscrito."""
        # La búsqueda la hace la Lista Enlazada (recorrido secuencial, O(n)).
        return self.padron.buscar(str(cedula).strip())

    def esta_en_fila(self, cedula) -> bool:
        """
        Indica si la persona ya está esperando en la fila.
        La Cola no tiene un método de búsqueda, así que se recorre nodo por
        nodo (solo lectura, sin sacar a nadie). La comparación usa la
        sobrecarga Asistente.__eq__, que acepta la cédula como texto.
        """
        cedula = str(cedula).strip()

        # Empezamos en el primer nodo de la fila (el frente).
        actual = self.fila.frente
        while actual is not None:
            # actual.dato es un Asistente. Gracias a __eq__ (sobrecarga del
            # operador ==), comparar un Asistente con un texto compara su cédula.
            if actual.dato == cedula:
                return True
            # Avanzamos al siguiente nodo siguiendo la referencia.
            actual = actual.siguiente

        # Recorrimos toda la fila y no apareció.
        return False

    def eliminar_asistente(self, cedula) -> Resultado:
        """Quita del padrón a un asistente que no esté dentro ni en la fila."""
        cedula = str(cedula).strip()
        asistente = self.padron.buscar(cedula)

        # Regla 1: solo se puede eliminar a alguien que esté inscrito.
        if asistente is None:
            return Resultado(False, "No hay ningún asistente con la cédula " + cedula + ".")

        # Regla 2: no se puede borrar a alguien que está dentro del recinto,
        # porque la bitácora (Pila) quedaría apuntando a alguien que no existe.
        if asistente.estado_ingreso:
            return Resultado(False, asistente.nombre + " está DENTRO del recinto; "
                             "no se puede eliminar del padrón.")

        # Regla 3: tampoco si está en la fila; si no, al llegar su turno
        # entraría alguien que ya no está inscrito.
        if self.esta_en_fila(cedula):
            return Resultado(False, asistente.nombre + " está esperando en la fila; "
                             "no se puede eliminar del padrón.")

        # La Lista Enlazada lo quita reconectando el nodo anterior con el siguiente.
        self.padron.eliminar(cedula)
        return Resultado(True, "Asistente eliminado del padrón: " + asistente.nombre + ".", asistente)

    def mostrar_padron(self):
        # Delegamos la impresión al método mostrar() de la Lista Enlazada.
        self.padron.mostrar()

    # ==================================================================
    # TORNIQUETE (Cola = fila de espera, Pila = bitácora de ingresos)
    # ==================================================================
    # Flujo de una persona en la puerta:
    #   1. llegar_a_fila()            -> se valida la cédula y entra a la Cola
    #   2. dar_ingreso()              -> sale de la Cola, queda DENTRO y se apila
    #   3. deshacer_ultimo_ingreso()  -> (si fue un error) sale de la Pila y queda FUERA
    def llegar_a_fila(self, cedula) -> Resultado:
        """La persona llega a la puerta: se valida su credencial y se encola."""
        cedula = str(cedula).strip()
        asistente = self.padron.buscar(cedula)

        # Validación de credencial: si no está en el padrón, no puede hacer la fila.
        if asistente is None:
            return Resultado(False, "Credencial rechazada: la cédula " + cedula
                             + " no está inscrita en el padrón.")

        # Si ya entró, no tiene sentido que vuelva a hacer la fila.
        if asistente.estado_ingreso:
            return Resultado(False, asistente.nombre + " ya está DENTRO del recinto.")

        # Evita que la misma persona aparezca dos veces en la fila.
        if self.esta_en_fila(cedula):
            return Resultado(False, asistente.nombre + " ya está esperando en la fila.")

        # encolar() lo agrega al FINAL de la Cola (el último en llegar).
        self.fila.encolar(asistente)
        return Resultado(True, asistente.nombre + " entró a la fila. Posición: "
                         + str(self.fila.obtener_tamano()) + ".", asistente)

    def ver_siguiente(self):
        """Devuelve quién sigue en la fila sin sacarlo (o None)."""
        # ver_frente() solo mira el primer nodo; no lo saca de la Cola.
        return self.fila.ver_frente()

    def dar_ingreso(self) -> Resultado:
        """Atiende al primero de la fila: entra al recinto y queda en la bitácora."""
        if self.fila.esta_vacia():
            return Resultado(False, "No hay nadie esperando en la fila.")

        # 1. desencolar() saca a la persona del FRENTE de la Cola (FIFO).
        asistente = self.fila.desencolar()
        # 2. Se marca como DENTRO del recinto.
        asistente.cambiar_estado_ingreso(True)
        # 3. Se registra en la bitácora: apilar() lo pone en el TOPE de la Pila.
        self.bitacora.apilar(asistente)
        return Resultado(True, "Ingreso registrado: " + asistente.nombre
                         + " (" + asistente.categoria + ").", asistente)

    def deshacer_ultimo_ingreso(self) -> Resultado:
        """Revierte el ingreso más reciente (tope de la pila): la persona queda FUERA."""
        if self.bitacora.esta_vacia():
            return Resultado(False, "No hay ingresos para deshacer.")

        # desapilar() saca el elemento del TOPE: el último que entró (LIFO).
        # Por eso la Pila es la estructura ideal para "deshacer".
        asistente = self.bitacora.desapilar()
        # Se revierte su estado: vuelve a quedar FUERA del recinto.
        asistente.cambiar_estado_ingreso(False)
        return Resultado(True, "Se deshizo el ingreso de " + asistente.nombre
                         + ". Queda FUERA y puede volver a hacer la fila.", asistente)

    def mostrar_fila(self):
        # Muestra la Cola del frente hacia el final.
        self.fila.mostrar()

    def mostrar_bitacora(self):
        # Muestra la Pila del tope hacia abajo (del ingreso más reciente al más antiguo).
        self.bitacora.mostrar()

    # ==================================================================
    # EVENTOS (Árbol BST = catálogo, Lista Doble = agenda)
    # ==================================================================
    # Un mismo objeto Evento se guarda en DOS estructuras a la vez:
    #   - Catálogo (BST): registro permanente de todos los eventos, para
    #     buscarlos rápido por ID y listarlos ordenados.
    #   - Agenda (Lista Doble): los eventos programados, en el orden en que
    #     se programaron, para recorrerlos adelante y atrás.
    def registrar_evento(self, id_evento, nombre, capacidad, escenario) -> Resultado:
        """Crea el evento en el catálogo (BST) y lo programa al final de la agenda."""
        # El ID y la capacidad deben ser números; a_entero devuelve None si no lo son.
        id_evento = a_entero(id_evento)
        capacidad = a_entero(capacidad)
        if id_evento is None or capacidad is None:
            return Resultado(False, "El ID y la capacidad deben ser números enteros.")

        nombre = str(nombre).strip()
        escenario = str(escenario).strip()

        # Validaciones de datos.
        if id_evento <= 0:
            return Resultado(False, "El ID del evento debe ser mayor que 0.")
        if capacidad <= 0:
            return Resultado(False, "La capacidad debe ser mayor que 0.")
        if nombre == "" or escenario == "":
            return Resultado(False, "El nombre y el escenario son obligatorios.")

        evento = Evento(id_evento, nombre, capacidad, escenario)

        # insertar() del BST devuelve False si el ID ya existe (no hay duplicados).
        # Para ubicar el evento, el árbol usa las sobrecargas < y > de Evento.
        if not self.catalogo.insertar(evento):
            existente = self.catalogo.buscar(id_evento)
            return Resultado(False, "Ya existe un evento con el ID " + str(id_evento)
                             + ": " + existente.nombre + ".")

        # Si se insertó en el catálogo, también se programa al final de la agenda.
        self.total_eventos += 1
        self.agenda.insertar_final(evento)
        return Resultado(True, "Evento registrado y programado en la agenda: " + str(evento), evento)

    def buscar_evento(self, id_evento):
        """Busca en el BST. Devuelve el Evento o None (también si el ID no es numérico)."""
        # El BST compara con < y >, así que el ID debe ser int: si llegara un
        # texto como "105", el árbol lanzaría un error al comparar texto con número.
        id_evento = a_entero(id_evento)
        if id_evento is None:
            return None
        # El árbol va a la izquierda o a la derecha según el ID hasta encontrarlo.
        return self.catalogo.buscar(id_evento)

    def esta_en_agenda(self, id_evento) -> bool:
        # Indica si el evento está programado en la agenda (Lista Doble).
        id_evento = a_entero(id_evento)
        if id_evento is None:
            return False
        return self.agenda.buscar_por_id(id_evento) is not None

    def retirar_de_agenda(self, id_evento) -> Resultado:
        """
        Quita un evento de la agenda (Lista Doble). El evento sigue en el
        catálogo (BST) y se puede volver a programar después.
        """
        # Primero se confirma que el evento exista en el catálogo.
        evento = self.buscar_evento(id_evento)
        if evento is None:
            return Resultado(False, "No existe un evento con el ID " + str(id_evento) + ".")

        # eliminar_por_id() de la Lista Doble reconecta los punteros anterior
        # y siguiente de los vecinos. Devuelve False si no estaba en la agenda.
        if not self.agenda.eliminar_por_id(evento.id_evento):
            return Resultado(False, "El evento '" + evento.nombre + "' no está en la agenda.")

        # Nota: el ArbolBST no tiene método eliminar, por eso el evento se
        # queda en el catálogo (y así se puede volver a programar).
        return Resultado(True, "Evento retirado de la agenda: " + evento.nombre
                         + ". Sigue en el catálogo.", evento)

    def programar_en_agenda(self, id_evento) -> Resultado:
        """Vuelve a poner al final de la agenda un evento que ya existe en el catálogo."""
        evento = self.buscar_evento(id_evento)
        if evento is None:
            return Resultado(False, "No existe un evento con el ID " + str(id_evento)
                             + ". Primero regístrelo.")

        # Evita que el mismo evento aparezca dos veces en la agenda.
        if self.esta_en_agenda(evento.id_evento):
            return Resultado(False, "El evento '" + evento.nombre + "' ya está en la agenda.")

        self.agenda.insertar_final(evento)
        return Resultado(True, "Evento programado al final de la agenda: " + evento.nombre + ".", evento)

    def mostrar_catalogo(self):
        print("=== CATÁLOGO DE EVENTOS (ordenado por ID) ===")
        # El recorrido in-orden (izquierda -> raíz -> derecha) de un BST
        # siempre muestra los elementos ordenados de menor a mayor.
        self.catalogo.recorrido_inorden()

    def mostrar_agenda_adelante(self):
        # Recorre la Lista Doble desde la cabeza usando el puntero "siguiente".
        self.agenda.mostrar_adelante()

    def mostrar_agenda_atras(self):
        # Recorre la Lista Doble desde el último nodo usando el puntero "anterior".
        self.agenda.mostrar_atras()

    # ==================================================================
    # RESUMEN Y DATOS DE DEMOSTRACIÓN
    # ==================================================================
    def mostrar_resumen(self):
        # Muestra el estado de todas las estructuras de un vistazo.
        print("=== RESUMEN DE EVENTOSCONNECT ===")
        print("  Asistentes inscritos (padrón) : " + str(self.padron.obtener_tamano()))
        print("  Personas en la fila           : " + str(self.fila.obtener_tamano()))
        # Cada ingreso queda en la bitácora y "deshacer" lo saca, así que el
        # tamaño de la pila es exactamente la cantidad de personas dentro.
        print("  Personas dentro del recinto   : " + str(self.bitacora.obtener_tamano()))

        # Estos dos datos solo se muestran si hay alguien en la fila o en la bitácora.
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

        # Se usan los mismos métodos que usaría el usuario, así los datos de
        # prueba también pasan por todas las validaciones.
        asistentes = 0   # Cuántos se insertaron (si ya existían, se omiten)
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

        # Se registran desordenados a propósito: la agenda conserva el orden
        # de programación y el catálogo (BST) los muestra ordenados por ID.
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
