class Evento:
    """
    Clase que representa un evento o actividad dentro de la agenda.
    Esta entidad será indexada en el Árbol Binario de Búsqueda (BST) según su id_evento,
    y organizada cronológicamente en la Lista Doblemente Enlazada.
    """
    def __init__(self, id_evento: int, nombre: str, capacidad: int, escenario: str):
        """
        Constructor de la clase Evento.
        
        :param id_evento: Identificador numérico único del evento (int).
        :param nombre: Título o nombre de la actividad (str).
        :param capacidad: Aforo máximo permitido (int).
        :param escenario: Ubicación física o tarima asignada (str).
        """
        self.id_evento = int(id_evento)     # Clave principal para el Árbol BST
        self.nombre = nombre                 # Nombre del taller o concierto
        self.capacidad = capacidad           # Aforo total
        self.escenario = escenario           # Lugar donde se realiza

    def __eq__(self, otro):
        """
        Sobrecarga del operador == para comparar eventos por su ID.
        """
        if isinstance(otro, Evento):
            return self.id_evento == otro.id_evento
        elif isinstance(otro, int):
            return self.id_evento == otro
        return False

    def __lt__(self, otro):
        """
        Sobrecarga del operador 'menor que' (<).
        Permite al Árbol BST ubicar este evento a la izquierda si su ID es menor.
        """
        if isinstance(otro, Evento):
            return self.id_evento < otro.id_evento
        elif isinstance(otro, int):
            return self.id_evento < otro
        return False

    def __gt__(self, otro):
        """
        Sobrecarga del operador 'mayor que' (>).
        Permite al Árbol BST ubicar este evento a la derecha si su ID es mayor.
        """
        if isinstance(otro, Evento):
            return self.id_evento > otro.id_evento
        elif isinstance(otro, int):
            return self.id_evento > otro
        return False

    def __str__(self):
        """
        Representación en texto para impresión en el menú interactivo.
        """
        return f"[ID: {self.id_evento} | Evento: {self.nombre} | Capacidad: {self.capacidad} | Escenario: {self.escenario}]"