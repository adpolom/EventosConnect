from src.modelos.Evento import Evento  # Importa la clase modelo Evento


class NodoArbol:
    """
    Nodo manual para el Árbol Binario de Búsqueda (BST).
    Almacena un objeto Evento y mantiene referencias a sus hijos izquierdo y derecho.
    """
    def __init__(self, evento: Evento):
        self.evento = evento
        self.izquierda = None
        self.derecha = None


class ArbolBST:
    """
    Implementación manual de un Árbol Binario de Búsqueda (BST) para el catálogo de eventos.
    Indexa y organiza los eventos según su id_evento utilizando las sobrecargas de comparación (<, >).
    """
    def __init__(self):
        self.raiz = None

    def esta_vacio(self) -> bool:
        """Verifica si el árbol no contiene ningún evento."""
        return self.raiz is None

    def insertar(self, evento: Evento) -> bool:
        """
        Inserta un objeto Evento en el árbol respetando la regla BST (Izq < Raíz < Der).
        Retorna True si se insertó con éxito, o False si el id_evento ya existía (no duplicados).
        """
        if self.esta_vacio():
            self.raiz = NodoArbol(evento)
            return True
        return self._insertar_recursivo(self.raiz, evento)

    def _insertar_recursivo(self, nodo_actual: NodoArbol, evento: Evento) -> bool:
        # Si el ID del evento es menor que el del nodo actual, va a la izquierda
        if evento < nodo_actual.evento:
            if nodo_actual.izquierda is None:
                nodo_actual.izquierda = NodoArbol(evento)
                return True
            return self._insertar_recursivo(nodo_actual.izquierda, evento)
        
        # Si el ID del evento es mayor que el del nodo actual, va a la derecha
        elif evento > nodo_actual.evento:
            if nodo_actual.derecha is None:
                nodo_actual.derecha = NodoArbol(evento)
                return True
            return self._insertar_recursivo(nodo_actual.derecha, evento)
        
        # Si el ID ya existe en el árbol, se ignora el duplicado
        return False

    def buscar(self, id_evento: int):
        """
        Busca un evento por su id_evento en complejidad promedio O(log n).
        Retorna el objeto Evento si lo encuentra, o None si no existe.
        """
        return self._buscar_recursivo(self.raiz, id_evento)

    def _buscar_recursivo(self, nodo_actual: NodoArbol, id_evento: int):
        if nodo_actual is None:
            return None
        
        if id_evento == nodo_actual.evento.id_evento:
            return nodo_actual.evento
        elif id_evento < nodo_actual.evento.id_evento:
            return self._buscar_recursivo(nodo_actual.izquierda, id_evento)
        else:
            return self._buscar_recursivo(nodo_actual.derecha, id_evento)

    def recorrido_inorden(self):
        """
        Recorre el árbol en In-orden (Izquierda -> Raíz -> Derecha).
        Muestra en consola el catálogo ordenado de menor a mayor por id_evento.
        """
        if self.esta_vacio():
            print("El catálogo de eventos está vacío.")
        else:
            self._inorden_recursivo(self.raiz)

    def _inorden_recursivo(self, nodo_actual: NodoArbol):
        if nodo_actual is not None:
            self._inorden_recursivo(nodo_actual.izquierda)
            print(f"  -> {nodo_actual.evento}")
            self._inorden_recursivo(nodo_actual.derecha)
