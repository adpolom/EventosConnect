from src.modelos.Evento import Evento  # Importa la clase modelo Evento


class NodoDoble:
    """
    Nodo manual para la Lista Doblemente Enlazada.
    Almacena un objeto Evento y mantiene punteros tanto al nodo siguiente como al anterior.
    """
    def __init__(self, evento: Evento):
        self.evento = evento
        self.siguiente = None
        self.anterior = None


class ListaDoblementeEnlazada:
    """
    Implementación manual de una Lista Doblemente Enlazada.
    Permite la navegación bidireccional (anterior/siguiente) por la agenda del día.
    """
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self.tamanio = 0

    def esta_vacia(self) -> bool:
        """Verifica si la lista no contiene ningún evento."""
        return self.cabeza is None

    def insertar_final(self, evento: Evento):
        """
        Agrega un nuevo evento al final de la agenda cronológica.
        """
        nuevo_nodo = NodoDoble(evento)
        if self.esta_vacia():
            self.cabeza = nuevo_nodo
            self.cola = nuevo_nodo
        else:
            nuevo_nodo.anterior = self.cola
            self.cola.siguiente = nuevo_nodo
            self.cola = nuevo_nodo
        self.tamanio += 1

    def buscar_por_id(self, id_evento: int):
        """
        Busca secuencialmente un evento por su id_evento.
        Retorna el objeto Evento si existe, o None si no se encuentra.
        """
        actual = self.cabeza
        while actual is not None:
            if actual.evento.id_evento == id_evento:
                return actual.evento
            actual = actual.siguiente
        return None

    def eliminar_por_id(self, id_evento: int) -> bool:
        """
        Elimina un evento de la agenda ajustando los punteros anterior y siguiente.
        Retorna True si fue eliminado, o False si el evento no existía.
        """
        actual = self.cabeza
        while actual is not None:
            if actual.evento.id_evento == id_evento:
                # Caso 1: Es el único nodo en la lista
                if actual == self.cabeza and actual == self.cola:
                    self.cabeza = None
                    self.cola = None
                # Caso 2: Es el primer nodo (cabeza)
                elif actual == self.cabeza:
                    self.cabeza = actual.siguiente
                    self.cabeza.anterior = None
                # Caso 3: Es el último nodo (cola)
                elif actual == self.cola:
                    self.cola = actual.anterior
                    self.cola.siguiente = None
                # Caso 4: Nodo intermedio
                else:
                    actual.anterior.siguiente = actual.siguiente
                    actual.siguiente.anterior = actual.anterior
                
                self.tamanio -= 1
                return True
            actual = actual.siguiente
        return False

    def mostrar_adelante(self):
        """
        Navega e imprime la agenda desde el primer evento hasta el último (Cabeza -> Cola).
        """
        if self.esta_vacia():
            print("La agenda de eventos está vacía.")
            return
        actual = self.cabeza
        print("=== AGENDA CRONOLÓGICA (Inicio -> Fin) ===")
        while actual is not None:
            print(f"  [<-] {actual.evento} [->]")
            actual = actual.siguiente

    def mostrar_atras(self):
        """
        Navega e imprime la agenda en orden inverso (Cola -> Cabeza).
        Demuestra el uso funcional del puntero anterior en la lista doble.
        """
        if self.esta_vacia():
            print("La agenda de eventos está vacía.")
            return
        actual = self.cola
        print("=== AGENDA INVERSA (Fin -> Inicio) ===")
        while actual is not None:
            print(f"  [<-] {actual.evento} [->]")
            actual = actual.anterior


# Bloque de prueba individual para Luis
if __name__ == "__main__":
    lista = ListaDoblementeEnlazada()
    e1 = Evento(101, "Apertura y Registro", 100, "Auditorio Principal")
    e2 = Evento(102, "Ponencia IA", 150, "Sala 1")
    e3 = Evento(103, "Cierre y Premiación", 200, "Auditorio Principal")

    lista.insertar_final(e1)
    lista.insertar_final(e2)
    lista.insertar_final(e3)

    lista.mostrar_adelante()
    print()
    lista.mostrar_atras()