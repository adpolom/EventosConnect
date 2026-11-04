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
from src.estructuras.ListaDoblementeEnlazada import ListaDoblementeEnlazada, NodoDoble


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


def normalizar_hora(texto):
    """
    Valida una hora en formato 24 horas y la devuelve siempre como "HH:MM".
    Devuelve None si no es una hora válida.

    Ejemplos:
        normalizar_hora("8:00")  -> "08:00"
        normalizar_hora("14:30") -> "14:30"
        normalizar_hora("25:00") -> None

    Se devuelve con dos dígitos a propósito: así las horas se pueden
    comparar como texto ("08:00" < "14:00") y la agenda queda en orden.
    """
    texto = str(texto).strip()
    # Se ubica el ":" y se corta el texto en dos partes (sin usar split,
    # que crearía una lista; el proyecto no permite listas de Python).
    pos = texto.find(":")
    if pos == -1 or texto.find(":", pos + 1) != -1:
        return None                    # no tiene ":" o tiene más de uno
    texto_horas = texto[:pos]
    texto_minutos = texto[pos + 1:]
    horas = a_entero(texto_horas)
    minutos = a_entero(texto_minutos)
    if horas is None or minutos is None or len(texto_minutos.strip()) != 2:
        return None
    if horas < 0 or horas > 23 or minutos < 0 or minutos > 59:
        return None
    return str(horas).zfill(2) + ":" + str(minutos).zfill(2)


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


class Turno:
    """
    Lo que se guarda en la fila (Cola) y en la bitácora (Pila):
    QUIÉN entra (el Asistente) y A QUÉ EVENTO entra.

    Hace falta guardar los dos juntos para el control de aforo: al dar
    ingreso hay que saber a qué evento se le descuenta un cupo, y al
    deshacer hay que saber a qué evento se le devuelve.
    """
    def __init__(self, asistente, evento):
        self.asistente = asistente
        self.evento = evento

    def __str__(self):
        # Así se ve cada turno cuando se imprime la fila o la bitácora.
        return (self.asistente.nombre + " (" + self.asistente.cedula + ") -> evento "
                + str(self.evento.id_evento) + " " + self.evento.nombre
                + " a las " + self.evento.hora)


class ControlEvento:
    """
    Controlador central de EventosConnect.
    Une las 5 estructuras del proyecto y aplica las reglas del negocio,
    de modo que Main.py solo se encarga de pedir datos y mostrar resultados.

      - padron    (ListaEnlazada)           : asistentes inscritos
      - fila      (Cola)                    : turnos esperando en el torniquete (FIFO)
      - bitacora  (Pila)                    : turnos que ya ingresaron, permite deshacer (LIFO)
      - catalogo  (ArbolBST)                : todos los eventos, indexados por id_evento
      - agenda    (ListaDoblementeEnlazada) : eventos programados, ordenados por hora
    """
    def __init__(self):
        # Al crear el controlador se crean las 5 estructuras, todas vacías.

        # Lista Enlazada: el "padrón", la lista de todos los inscritos.
        # Se usa una lista porque hay que recorrerla para buscar cédulas
        # y poder eliminar a alguien de cualquier posición.
        self.padron = ListaEnlazada()

        # Cola (FIFO = First In, First Out): la fila en la puerta.
        # El primero que llega es el primero que entra, como en una fila real.
        # Cada elemento es un Turno (asistente + evento al que va).
        self.fila = Cola()

        # Pila (LIFO = Last In, First Out): la bitácora de ingresos.
        # El último que entró queda arriba, por eso "deshacer" siempre
        # revierte el ingreso más reciente.
        self.bitacora = Pila()

        # Árbol Binario de Búsqueda: el catálogo de eventos.
        # Ordena los eventos por ID: los menores a la izquierda y los mayores
        # a la derecha, así buscar un evento es rápido (O(log n) en promedio).
        self.catalogo = ArbolBST()

        # Lista Doblemente Enlazada: la agenda del día, en orden de hora.
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

    def turno_en_fila(self, cedula):
        """
        Devuelve el Turno de esa persona si está esperando en la fila, o None.
        La Cola no tiene un método de búsqueda, así que se recorre nodo por
        nodo (solo lectura, sin sacar a nadie). La comparación usa la
        sobrecarga Asistente.__eq__, que acepta la cédula como texto.
        """
        cedula = str(cedula).strip()

        # Empezamos en el primer nodo de la fila (el frente).
        actual = self.fila.frente
        while actual is not None:
            # actual.dato es un Turno; su asistente se compara con la cédula
            # gracias a __eq__ (sobrecarga del operador ==).
            if actual.dato.asistente == cedula:
                return actual.dato
            # Avanzamos al siguiente nodo siguiendo la referencia.
            actual = actual.siguiente

        # Recorrimos toda la fila y no apareció.
        return None

    def esta_en_fila(self, cedula) -> bool:
        return self.turno_en_fila(cedula) is not None

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
    # CONTROL DE AFORO
    # ==================================================================
    # Cada Evento tiene una 'capacidad' (aforo máximo). Para saber cuántos
    # cupos quedan se cuentan los turnos de ese evento en la bitácora
    # (personas que ya entraron) y en la fila (personas que ya tienen su
    # cupo apartado). Se cuenta recorriendo los nodos, sin estructuras extra.
    def ingresados_a(self, evento) -> int:
        """Cuántas personas han entrado a ese evento (turnos en la Pila)."""
        cuenta = 0
        actual = self.bitacora.tope
        while actual is not None:
            if actual.dato.evento == evento:
                cuenta += 1
            actual = actual.siguiente
        return cuenta

    def en_fila_para(self, evento) -> int:
        """Cuántas personas esperan en la fila para ese evento (turnos en la Cola)."""
        cuenta = 0
        actual = self.fila.frente
        while actual is not None:
            if actual.dato.evento == evento:
                cuenta += 1
            actual = actual.siguiente
        return cuenta

    def cupos_disponibles(self, evento) -> int:
        """Capacidad menos los que ya entraron y los que esperan en la fila."""
        return evento.capacidad - self.ingresados_a(evento) - self.en_fila_para(evento)

    # ==================================================================
    # TORNIQUETE (Cola = fila de espera, Pila = bitácora de ingresos)
    # ==================================================================
    # Flujo de una persona en la puerta:
    #   1. llegar_a_fila()            -> se valida la cédula, el evento y el cupo; entra a la Cola
    #   2. dar_ingreso()              -> sale de la Cola, se vuelve a revisar el aforo,
    #                                    queda DENTRO y se apila en la bitácora
    #   3. deshacer_ultimo_ingreso()  -> (si fue un error) sale de la Pila, queda FUERA
    #                                    y su cupo vuelve a estar libre
    def llegar_a_fila(self, cedula, id_evento) -> Resultado:
        """La persona llega a la puerta para un evento: se valida y se encola."""
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

        # El evento debe existir en el catálogo y estar programado en la agenda.
        evento = self.buscar_evento(id_evento)
        if evento is None:
            return Resultado(False, "No existe un evento con el ID " + str(id_evento) + ".")
        if not self.esta_en_agenda(evento.id_evento):
            return Resultado(False, "El evento '" + evento.nombre + "' no está programado en la agenda.")

        # Control de aforo: no se aparta un cupo que ya no existe.
        if self.cupos_disponibles(evento) <= 0:
            return Resultado(False, "Aforo completo: el evento '" + evento.nombre
                             + "' ya tiene sus " + str(evento.capacidad) + " cupos ocupados o apartados.")

        # encolar() agrega el turno al FINAL de la Cola (el último en llegar).
        self.fila.encolar(Turno(asistente, evento))
        return Resultado(True, asistente.nombre + " entró a la fila para '" + evento.nombre
                         + "'. Posición: " + str(self.fila.obtener_tamano())
                         + ". Cupos que quedan: " + str(self.cupos_disponibles(evento)) + ".", asistente)

    def ver_siguiente(self):
        """Devuelve el Turno que sigue en la fila sin sacarlo (o None)."""
        # ver_frente() solo mira el primer nodo; no lo saca de la Cola.
        return self.fila.ver_frente()

    def dar_ingreso(self) -> Resultado:
        """Atiende al primero de la fila: entra al evento y queda en la bitácora."""
        if self.fila.esta_vacia():
            return Resultado(False, "No hay nadie esperando en la fila.")

        # 1. desencolar() saca el turno del FRENTE de la Cola (FIFO).
        turno = self.fila.desencolar()
        asistente = turno.asistente
        evento = turno.evento

        # 2. Segunda revisión del aforo, ya en el torniquete. Normalmente
        #    siempre hay cupo porque se apartó al hacer la fila, pero se
        #    revisa otra vez por seguridad.
        if self.ingresados_a(evento) >= evento.capacidad:
            return Resultado(False, "Aforo completo en '" + evento.nombre + "' ("
                             + str(evento.capacidad) + " personas). " + asistente.nombre
                             + " no puede entrar.", asistente)

        # 3. Se marca como DENTRO y se registra en la bitácora (tope de la Pila).
        asistente.cambiar_estado_ingreso(True)
        self.bitacora.apilar(turno)
        return Resultado(True, "Ingreso registrado: " + asistente.nombre + " (" + asistente.categoria
                         + ") a '" + evento.nombre + "'. Aforo: " + str(self.ingresados_a(evento))
                         + "/" + str(evento.capacidad) + ".", asistente)

    def deshacer_ultimo_ingreso(self) -> Resultado:
        """Revierte el ingreso más reciente (tope de la pila): la persona queda FUERA."""
        if self.bitacora.esta_vacia():
            return Resultado(False, "No hay ingresos para deshacer.")

        # desapilar() saca el turno del TOPE: el último que entró (LIFO).
        # Por eso la Pila es la estructura ideal para "deshacer".
        turno = self.bitacora.desapilar()
        asistente = turno.asistente
        # Se revierte su estado: vuelve a quedar FUERA, y como ya no está en la
        # bitácora, su cupo en el evento queda libre otra vez.
        asistente.cambiar_estado_ingreso(False)
        return Resultado(True, "Se deshizo el ingreso de " + asistente.nombre + " a '"
                         + turno.evento.nombre + "'. Queda FUERA y su cupo se libera.", asistente)

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
    #   - Catálogo (BST): registro de todos los eventos, para buscarlos
    #     rápido por ID y listarlos ordenados.
    #   - Agenda (Lista Doble): los eventos programados, ordenados por hora,
    #     para recorrerlos adelante y atrás.
    def _programar_en_orden(self, evento):
        """
        Inserta el evento en la agenda en su lugar según la hora, para que la
        agenda quede siempre en orden cronológico.

        La Lista Doble trae insertar_final(); como aquí hay que insertar en
        medio, se recorre la lista hasta el primer evento con una hora mayor
        y el nodo nuevo se enlaza ANTES de él, ajustando los punteros
        'anterior' y 'siguiente' de sus dos vecinos.
        """
        actual = self.agenda.cabeza
        while actual is not None and actual.evento.hora <= evento.hora:
            actual = actual.siguiente

        # Si no hay ningún evento más tarde, va al final.
        if actual is None:
            self.agenda.insertar_final(evento)
            return

        nuevo = NodoDoble(evento)
        nuevo.siguiente = actual
        nuevo.anterior = actual.anterior
        if actual.anterior is None:          # va de primero
            self.agenda.cabeza = nuevo
        else:
            actual.anterior.siguiente = nuevo
        actual.anterior = nuevo
        self.agenda.tamanio += 1

    def registrar_evento(self, id_evento, nombre, capacidad, escenario, hora) -> Resultado:
        """Crea el evento en el catálogo (BST) y lo programa en la agenda según su hora."""
        # El ID y la capacidad deben ser números; a_entero devuelve None si no lo son.
        id_evento = a_entero(id_evento)
        capacidad = a_entero(capacidad)
        if id_evento is None or capacidad is None:
            return Resultado(False, "El ID y la capacidad deben ser números enteros.")

        nombre = str(nombre).strip()
        escenario = str(escenario).strip()
        hora_valida = normalizar_hora(hora)

        # Validaciones de datos.
        if id_evento <= 0:
            return Resultado(False, "El ID del evento debe ser mayor que 0.")
        if capacidad <= 0:
            return Resultado(False, "La capacidad debe ser mayor que 0.")
        if nombre == "" or escenario == "":
            return Resultado(False, "El nombre y el escenario son obligatorios.")
        if hora_valida is None:
            return Resultado(False, "La hora debe tener el formato HH:MM de 24 horas (por ejemplo 14:00).")

        evento = Evento(id_evento, nombre, capacidad, escenario, hora_valida)

        # insertar() del BST devuelve False si el ID ya existe (no hay duplicados).
        # Para ubicar el evento, el árbol usa las sobrecargas < y > de Evento.
        if not self.catalogo.insertar(evento):
            existente = self.catalogo.buscar(id_evento)
            return Resultado(False, "Ya existe un evento con el ID " + str(id_evento)
                             + ": " + existente.nombre + ".")

        # Si se insertó en el catálogo, también se programa en la agenda.
        self.total_eventos += 1
        self._programar_en_orden(evento)
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

    def _tiene_personas(self, evento):
        """Mensaje de error si alguien está dentro o en la fila para ese evento; '' si no."""
        if self.ingresados_a(evento) > 0:
            return "hay personas dentro de ese evento"
        if self.en_fila_para(evento) > 0:
            return "hay personas en la fila para ese evento"
        return ""

    def retirar_de_agenda(self, id_evento) -> Resultado:
        """
        Quita un evento de la agenda (Lista Doble). El evento sigue en el
        catálogo (BST) y se puede volver a programar después.
        """
        # Primero se confirma que el evento exista en el catálogo.
        evento = self.buscar_evento(id_evento)
        if evento is None:
            return Resultado(False, "No existe un evento con el ID " + str(id_evento) + ".")

        # No se retira un evento al que todavía le esperan personas en la fila.
        if self.en_fila_para(evento) > 0:
            return Resultado(False, "No se puede retirar '" + evento.nombre
                             + "': hay personas en la fila para ese evento.")

        # eliminar_por_id() de la Lista Doble reconecta los punteros anterior
        # y siguiente de los vecinos. Devuelve False si no estaba en la agenda.
        if not self.agenda.eliminar_por_id(evento.id_evento):
            return Resultado(False, "El evento '" + evento.nombre + "' no está en la agenda.")

        return Resultado(True, "Evento retirado de la agenda: " + evento.nombre
                         + ". Sigue en el catálogo.", evento)

    def programar_en_agenda(self, id_evento) -> Resultado:
        """Vuelve a poner en la agenda (en su hora) un evento que ya existe en el catálogo."""
        evento = self.buscar_evento(id_evento)
        if evento is None:
            return Resultado(False, "No existe un evento con el ID " + str(id_evento)
                             + ". Primero regístrelo.")

        # Evita que el mismo evento aparezca dos veces en la agenda.
        if self.esta_en_agenda(evento.id_evento):
            return Resultado(False, "El evento '" + evento.nombre + "' ya está en la agenda.")

        self._programar_en_orden(evento)
        return Resultado(True, "Evento programado en la agenda a las " + evento.hora
                         + ": " + evento.nombre + ".", evento)

    def eliminar_evento(self, id_evento) -> Resultado:
        """
        Borra un evento del todo: del catálogo (BST) y de la agenda (Lista Doble).
        El BST resuelve los tres casos de eliminación (hoja, un hijo y dos
        hijos con el sucesor inorden).
        """
        evento = self.buscar_evento(id_evento)
        if evento is None:
            return Resultado(False, "No existe un evento con el ID " + str(id_evento) + ".")

        # No se borra un evento con personas dentro o esperando en la fila,
        # porque sus turnos quedarían apuntando a un evento que no existe.
        motivo = self._tiene_personas(evento)
        if motivo != "":
            return Resultado(False, "No se puede eliminar '" + evento.nombre + "': " + motivo + ".")

        self.agenda.eliminar_por_id(evento.id_evento)   # puede que ya no estuviera en la agenda
        self.catalogo.eliminar(evento.id_evento)
        self.total_eventos -= 1
        return Resultado(True, "Evento eliminado del catálogo y de la agenda: " + evento.nombre + ".", evento)

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
        print("  Personas dentro               : " + str(self.bitacora.obtener_tamano()))

        # Estos dos datos solo se muestran si hay alguien en la fila o en la bitácora.
        siguiente = self.fila.ver_frente()
        if siguiente is not None:
            print("  Siguiente en la fila          : " + siguiente.asistente.nombre)
        ultimo = self.bitacora.ver_tope()
        if ultimo is not None:
            print("  Último ingreso                : " + ultimo.asistente.nombre)

        print("  Eventos en el catálogo        : " + str(self.total_eventos))
        print("  Eventos en la agenda          : " + str(self.agenda.tamanio))

        # Aforo de cada evento programado, en el orden de la agenda.
        if not self.agenda.esta_vacia():
            print("  Aforo por evento (dentro / capacidad, en fila):")
            actual = self.agenda.cabeza
            while actual is not None:
                e = actual.evento
                print("    " + e.hora + "  " + str(e.id_evento) + " " + e.nombre.ljust(22)
                      + str(self.ingresados_a(e)).rjust(3) + " / " + str(e.capacidad).ljust(4)
                      + " en fila: " + str(self.en_fila_para(e)))
                actual = actual.siguiente

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

        # Se registran desordenados a propósito (por ID y por hora): el
        # catálogo (BST) los muestra ordenados por ID y la agenda los ubica
        # sola en orden de hora. El Taller de Python tiene solo 3 cupos para
        # poder mostrar el control de aforo con los 5 asistentes de prueba.
        eventos = 0
        if self.registrar_evento(110, "Cierre y Premiación", 300, "Auditorio Principal", "17:00").exito:
            eventos += 1
        if self.registrar_evento(102, "Taller de Python", 3, "Sala 2", "10:00").exito:
            eventos += 1
        if self.registrar_evento(101, "Feria de Proyectos", 200, "Plaza Central", "14:00").exito:
            eventos += 1
        if self.registrar_evento(105, "Apertura y Registro", 300, "Auditorio Principal", "08:00").exito:
            eventos += 1
        if self.registrar_evento(108, "Ponencia de IA", 150, "Sala 1", "11:30").exito:
            eventos += 1

        self.datos_demo_cargados = True
        mensaje = ("Datos cargados: " + str(asistentes) + " de 5 asistentes "
                   "(cédulas 11111, 22222, 33333, 44444, 55555) y "
                   + str(eventos) + " de 5 eventos (105 a las 08:00, 102 a las 10:00, "
                   "108 a las 11:30, 101 a las 14:00 y 110 a las 17:00).")
        if asistentes < 5 or eventos < 5:
            mensaje += " Los que ya existían se omitieron."
        return Resultado(True, mensaje)
