ATRIBUTO_CREDENCIAL = "cedula"


class NodoLista:
    """Un nodo de la lista: guarda un dato y apunta al nodo siguiente."""

    def __init__(self, dato):
        self.dato = dato          # Lo que guarda el nodo (ej: un Asistente)
        self.siguiente = None     # Referencia al siguiente nodo (o None)


class ListaEnlazada:
    """Lista enlazada simple construida solo con nodos y referencias."""

    def __init__(self):
        self.cabeza = None   # Primer nodo de la lista
        self.tamano = 0      # Cuantos asistentes hay inscritos

    def esta_vacia(self):
        """Devuelve True si el padron no tiene asistentes."""
        return self.cabeza is None

    def _credencial_de(self, dato):
        """Metodo auxiliar: obtiene la credencial de un dato como TEXTO.
        Si el dato tiene el atributo definido arriba (la cedula) lo usa;
        si no, usa el dato completo. Se convierte a texto porque la
        cedula del Asistente se guarda como str, y asi la busqueda
        funciona igual si nos llega 123 o "123"."""
        return str(getattr(dato, ATRIBUTO_CREDENCIAL, dato))

    def insertar_al_inicio(self, dato):
        """Agrega un asistente al INICIO del padron (muy rapido)."""
        nuevo = NodoLista(dato)
        nuevo.siguiente = self.cabeza   # El nuevo apunta a la antigua cabeza
        self.cabeza = nuevo             # Y ahora el nuevo es la cabeza
        self.tamano += 1

    def insertar_al_final(self, dato):
        """Agrega un asistente al FINAL del padron."""
        nuevo = NodoLista(dato)

        if self.esta_vacia():
            # Lista vacia: el nuevo nodo es la cabeza
            self.cabeza = nuevo
        else:
            # Recorremos hasta el ultimo nodo (el que apunta a None)
            actual = self.cabeza
            while actual.siguiente is not None:
                actual = actual.siguiente
            actual.siguiente = nuevo    # El ultimo ahora apunta al nuevo

        self.tamano += 1

    def buscar(self, credencial):
        """Valida una credencial: recorre el padron y devuelve el
        asistente que la tenga, o None si no esta inscrito."""
        credencial = str(credencial)    # Misma forma que la cedula guardada
        actual = self.cabeza
        while actual is not None:
            if self._credencial_de(actual.dato) == credencial:
                return actual.dato      # Encontrado
            actual = actual.siguiente   # Pasamos al siguiente nodo
        return None                     # Recorrimos todo y no aparecio

    def existe(self, credencial):
        """Devuelve True si la credencial esta en el padron."""
        return self.buscar(credencial) is not None

    def eliminar(self, credencial):
        """Quita del padron al asistente con esa credencial.
        Devuelve True si lo elimino, False si no lo encontro."""
        credencial = str(credencial)    # Misma forma que la cedula guardada
        anterior = None
        actual = self.cabeza

        while actual is not None:
            if self._credencial_de(actual.dato) == credencial:
                if anterior is None:
                    # Era la cabeza: la cabeza pasa al siguiente
                    self.cabeza = actual.siguiente
                else:
                    # Saltamos el nodo: el anterior apunta al siguiente
                    anterior.siguiente = actual.siguiente
                self.tamano -= 1
                return True
            anterior = actual
            actual = actual.siguiente

        return False

    def obtener_tamano(self):
        """Devuelve cuantos asistentes hay en el padron."""
        return self.tamano

    def mostrar(self):
        """Imprime todo el padron, de la cabeza hasta el final."""
        if self.esta_vacia():
            print("El padron de asistentes esta vacio.")
            return

        print("Padron de asistentes (" + str(self.tamano) + " inscritos):")
        actual = self.cabeza
        posicion = 1
        while actual is not None:
            print("  " + str(posicion) + ". " + str(actual.dato))
            actual = actual.siguiente
            posicion += 1


