class NodoPila:
    """Un nodo de la pila: guarda un dato y apunta al nodo de abajo."""

    def __init__(self, dato):
        self.dato = dato          # Lo que guarda el nodo (ej: un Asistente)
        self.siguiente = None     # Referencia al nodo que esta debajo


class Pila:
    """Pila LIFO construida solo con nodos y referencias."""

    def __init__(self):
        self.tope = None    # Nodo de arriba (el ultimo que ingreso)
        self.tamano = 0     # Cuantos ingresos hay registrados

    def esta_vacia(self):
        """Devuelve True si la bitacora no tiene ingresos."""
        return self.tope is None

    def apilar(self, dato):
        """Registra un nuevo ingreso poniendolo ARRIBA de la pila."""
        nuevo = NodoPila(dato)
        nuevo.siguiente = self.tope   # El nuevo apunta al que era el tope
        self.tope = nuevo             # Ahora el nuevo es el tope
        self.tamano += 1

    def desapilar(self):
        """Quita y devuelve el ULTIMO ingreso (sirve para 'Deshacer').
        Si la pila esta vacia devuelve None."""
        if self.esta_vacia():
            return None

        nodo_quitado = self.tope        # Guardamos el que sale
        self.tope = self.tope.siguiente # El tope baja al nodo de abajo
        self.tamano -= 1
        return nodo_quitado.dato

    def ver_tope(self):
        """Devuelve el ultimo ingreso SIN quitarlo. None si esta vacia."""
        if self.esta_vacia():
            return None
        return self.tope.dato

    def obtener_tamano(self):
        """Devuelve cuantos ingresos hay en la bitacora."""
        return self.tamano

    def mostrar(self):
        """Imprime la bitacora, del ingreso mas reciente al mas antiguo."""
        if self.esta_vacia():
            print("La bitacora de accesos esta vacia.")
            return

        print("Bitacora de accesos (" + str(self.tamano) + " ingresos):")
        actual = self.tope
        posicion = 1
        while actual is not None:
            print("  " + str(posicion) + ". " + str(actual.dato))
            actual = actual.siguiente
            posicion += 1


