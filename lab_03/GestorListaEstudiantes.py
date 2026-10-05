from .Estructura import Estructura

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

        Ordena los datos por id y filtra los registros que cumplen con la condición del rango.
        """
        datos_ordenados = sorted(self.datos, key=lambda estudiante: estudiante["id"])
        coincidencias = [e for e in datos_ordenados if lb <= e["id"] <= ub]

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
        datos = sorted(self.datos, key= lambda estudiante : estudiante["id"])
        listado = ""
        for estudiante in datos:
            listado += "Estudiante:\n"
            listado += "["
            for clave, valor in estudiante.items():
                listado += f"{clave} : {valor} | "
            listado += "]\n"

        return listado      