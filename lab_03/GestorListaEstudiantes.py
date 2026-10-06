from Estructura import Estructura

class GestorListaEstudiantes(Estructura):
    """
        Esta clase se encarga de gestionar las operaciones de inserción, búsqueda y listado de los estudiantes
        cuando la estructura de datos en cuestión es una lista nativa de Python.
    """
    def __init__(self, datos : list):
        self.datos = datos

    def insertar(self, estudiante:dict) -> dict:
        self.datos.append(estudiante)
        return estudiante

    def buscar(self, id_estudiante:int) -> str:
        for estudiante in self.datos:
            if estudiante["id"] == id_estudiante:
                resultado = ""
                resultado += "Encontrado :\n"
                for clave, valor in estudiante.items():
                    resultado += f"{clave} : {valor} | "
                return resultado

        return f"Estudiante con id: {id_estudiante} no fue encontrado."

    def buscar_rango_id(self, lb: int, ub: int) -> str:
        """
        Busca todos los estudiantes cuyo id se encuentre dentro del rango inclusivo [lb, ub].

        Filtra los registros que cumplen con la condición del rango y luego los ordena por id.
        """
        
        coincidencias = sorted((e for e in self.datos if lb <= e["id"] <= ub), key=lambda e: e["id"])

        if not coincidencias:
            return f"No se encontraron estudiantes en el rango [{lb}, {ub}]."

        resultado = [f"Estudiantes encontrados en el rango [{lb}, {ub}]:\n"]
        for estudiante in coincidencias:
            resultado.append("Estudiante:\n[")
            for clave, valor in estudiante.items():
                resultado.append(f"{clave} : {valor} | ")
            resultado.append("]\n")

        return "".join(resultado)

    def listar(self) -> str:
        datos = sorted(self.datos, key=lambda estudiante: estudiante["id"])
        resultado = []
        for estudiante in datos:
            resultado.append("Estudiante:\n[")
            for clave, valor in estudiante.items():
                resultado.append(f"{clave} : {valor} | ")
            resultado.append("]\n")

        return "".join(resultado)