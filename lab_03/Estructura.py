from abc import ABC, abstractmethod

class Estructura(ABC):
    """
        Clase abstracta, sirve para mantener la coherencia de las clases concretas de árbol binario, gestor de lista y árbol B+
        Todas deben mantener el contrato definido por los métodos de esta clase.
    """
    @abstractmethod
    def insertar(self, estudiante:dict) -> dict:
        pass

    @abstractmethod
    def buscar(self, id_estudiante:int) -> str:
        pass

    @abstractmethod
    def listar(self) -> str:
        pass

    @abstractmethod
    def buscar_rango_id(lb:int, ub:int) -> str:
        pass