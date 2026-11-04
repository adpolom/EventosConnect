class Evento:
    """
    Clase que representa un evento o actividad dentro de la agenda.
    Esta entidad sera indexada en el Arbol Binario de Busqueda (BST) segun su id_evento,
    y organizada cronologicamente en la Lista Doblemente Enlazada.
    """
    def __init__(self, id_evento: int, nombre: str, capacidad: int, escenario: str, hora: str = "09:00"):
        """
        Constructor de la clase Evento.
        
        :param id_evento: Identificador numerico unico del evento (int).
        :param nombre: Titulo o nombre de la actividad (str).
        :param capacidad: Aforo maximo permitido (int).
        :param escenario: Ubicacion fisica o tarima asignada (str).
        :param hora: Hora programada del evento (str, opcional). Por defecto "09:00".
        """
        self.id_evento = int(id_evento)     # Clave principal para el Arbol BST
        self.nombre = nombre                 # Nombre del taller o concierto
        self.capacidad = int(capacidad)      # Aforo total
        self.escenario = escenario           # Lugar donde se realiza
        self.hora = hora                     # Hora del evento

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
        Permite al Arbol BST ubicar este evento a la izquierda si su ID es menor.
        """
        if isinstance(otro, Evento):
            return self.id_evento < otro.id_evento
        elif isinstance(otro, int):
            return self.id_evento < otro
        return False

    def __gt__(self, otro):
        """
        Sobrecarga del operador 'mayor que' (>).
        Permite al Arbol BST ubicar este evento a la derecha si su ID es mayor.
        """
        if isinstance(otro, Evento):
            return self.id_evento > otro.id_evento
        elif isinstance(otro, int):
            return self.id_evento > otro
        return False

    def __str__(self):
        """
        Representacion en texto para impresion en el menu interactivo.
        """
        return f"[ID: {self.id_evento} | Hora: {self.hora} | Evento: {self.nombre} | Capacidad: {self.capacidad} | Escenario: {self.escenario}]"