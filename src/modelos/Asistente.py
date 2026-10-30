class Asistente:
    """
    Clase que representa a un participante registrado en el sistema EventosConnect.
    Esta entidad será almacenada en la Lista Enlazada, encolada en la Cola
    y registrada en la Pila de bitácora del torniquete.
    """
    def __init__(self, cedula, nombre, categoria="General"):
        """
        Constructor de la clase Asistente.
        
        :param cedula: Documento de identidad único (str o int).
        :param nombre: Nombre completo del participante (str).
        :param categoria: Tipo de acreditación, ej. 'General', 'VIP', 'Organizador' (str).
        """
        self.cedula = str(cedula)           # Identificador único principal
        self.nombre = nombre                 # Nombre del usuario
        self.categoria = categoria           # Categoría o tipo de boleto
        self.estado_ingreso = False          # False = fuera del recinto, True = dentro

    def cambiar_estado_ingreso(self, estado: bool):
        """
        Actualiza el estado de presencia del participante al cruzar el torniquete.
        """
        self.estado_ingreso = estado

    def __eq__(self, otro):
        """
        Sobrecarga del operador de igualdad (==).
        Permite comparar si dos objetos Asistente son la misma persona
        evaluando únicamente su cédula.
        Útil para métodos de búsqueda y eliminación en la Lista Enlazada.
        """
        if isinstance(otro, Asistente):
            return self.cedula == otro.cedula
        elif isinstance(otro, (str, int)):
            return self.cedula == str(otro)
        return False

    def __str__(self):
        """
        Representación en texto del asistente para mostrar en la consola.
        """
        estado_str = "DENTRO" if self.estado_ingreso else "FUERA"
        return f"[Cédula: {self.cedula} | Nombre: {self.nombre} | Cat: {self.categoria} | Estado: {estado_str}]"