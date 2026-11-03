class NodoCola:
    """Un nodo de la cola: guarda un dato y apunta al nodo que sigue."""

    def __init__(self, dato):
        self.dato = dato          # Lo que guarda el nodo (ej: un Asistente)
        self.siguiente = None     # Referencia al siguiente nodo (o None)


class Cola:
    """Cola FIFO construida solo con nodos y referencias."""

    def __init__(self):
        self.frente = None   # Primer nodo de la fila (el proximo a salir)
        self.final = None    # Ultimo nodo de la fila (el ultimo en llegar)
        self.tamano = 0      # Cuantas personas hay en la fila

    def esta_vacia(self):
        """Devuelve True si no hay nadie en la fila."""
        return self.frente is None

    def encolar(self, dato):
        """Agrega una persona AL FINAL de la fila (llega a la puerta)."""
        nuevo = NodoCola(dato)

        if self.esta_vacia():
            # Fila vacia: el nuevo nodo es a la vez el frente y el final
            self.frente = nuevo
            self.final = nuevo
        else:
            # El que era el ultimo ahora apunta al nuevo...
            self.final.siguiente = nuevo
            # ...y el nuevo pasa a ser el ultimo
            self.final = nuevo

        self.tamano += 1

    def desencolar(self):
        """Saca y devuelve a la persona del FRENTE (la que va a entrar).
        Si la fila esta vacia devuelve None."""
        if self.esta_vacia():
            return None

        nodo_atendido = self.frente           # Guardamos el que sale
        self.frente = self.frente.siguiente   # El frente avanza al siguiente

        # Si ya no queda nadie, tambien hay que limpiar el final
        if self.frente is None:
            self.final = None

        self.tamano -= 1
        return nodo_atendido.dato

    def ver_frente(self):
        """Devuelve quien sigue en la fila SIN sacarlo. None si esta vacia."""
        if self.esta_vacia():
            return None
        return self.frente.dato

    def obtener_tamano(self):
        """Devuelve cuantas personas hay esperando."""
        return self.tamano

    def mostrar(self):
        """Imprime la fila completa, de la primera a la ultima persona."""
        if self.esta_vacia():
            print("La fila de espera esta vacia.")
            return

        print("Fila de espera (" + str(self.tamano) + " personas):")
        actual = self.frente
        posicion = 1
        while actual is not None:
            print("  " + str(posicion) + ". " + str(actual.dato))
            actual = actual.siguiente
            posicion += 1


