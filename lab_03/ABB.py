from .Estructura import Estructura

class ABB(Estructura):
    """
        Esta clase representa una implementación básica de un árbol binario de búsqueda (ABB),
        hereda de la clase abstracta Estrucrura, para mantener los métodos de forma consistente con las
        otras estructuras de datos.

        Las operaciones de inserción, búsqueda y mostrar los datos son implementaciones basadas en los algoritmos
        del libro Introduction to Algorithms de Cormen.
    """

    class Nodo:
        """
            Esta clase representa un nodo de árbol binario de búsqueda.
            Para este reto, se decidió implementar el árbol a modo de lista ligada,
            es decir, el nodo guarda referencias hacia sus hijos.
        """
        def __init__(self, estudiante :dict, hijo_izquierdo : "ABB.Nodo" = None, hijo_derecho : "ABB.Nodo" = None):
            self.hijo_izquierdo = hijo_izquierdo
            self.hijo_derecho = hijo_derecho
            self.estudiante = estudiante

    def __init__(self):
        self.raiz = None #Raíz inicia siendo nula

    def insertar(self, estudiante :dict) -> dict:
        """
            Dado un diccionario que representa un estudiante, se inserta el nodo correspondiente en el árbol.
            Este es el algoritmo estándar (versión iterativa) de inserción en un árbol binario, adaptado del libro Introduction
            To Algorithms de Cormen.

            El procedimiento es el que sigue:
                1. nodo_actual se utiliza para recorrer el árbol y nodo_previo se utiliza para almacenar el nodo inmediatamente anterior
                    al nodo actual.
                2. Siempre que nodo_actual no sea nulo, desde él se decide si la inserción continúa por la izquierda (valor <=) o la derecha.
                3. Se actualiza el nodo_actual a su hijo izquierdo o derecho y se guarda en nodo_previo la referencia a él.
                4. Una vez que se llegue a una hoja, nodo_actual será nulo y nodo_previo será el padre del valor a insertar.
                5. Finalmente, se decide si el valor se inserta a la izquierda o a la derecha del nodo_previo.

        """
        nodo_actual = self.raiz
        nodo_previo = None
        while nodo_actual is not None:
            nodo_previo = nodo_actual
            if estudiante["id"] <= nodo_actual.estudiante["id"]:
                nodo_actual = nodo_actual.hijo_izquierdo
            else:
                nodo_actual = nodo_actual.hijo_derecho

        if nodo_previo is None:
            self.raiz = self.Nodo(estudiante=estudiante) # Caso especial: árbol totalmente vacío.
        elif estudiante["id"] <= nodo_previo.estudiante["id"]:
            nodo_previo.hijo_izquierdo = self.Nodo(estudiante=estudiante)
        else:
            nodo_previo.hijo_derecho = self.Nodo(estudiante=estudiante)
        
        return estudiante

    def buscar(self, id_estudiante : int) -> str:
        """
            Dado un id de estudiante, recorre el árbol para encontrar el nodo correspondiente.
            Este es el algoritmo estándar (versión iterativa) de búsqueda en un árbol binario, adaptado del libro
            Introduction To Algorithms de Cormen.

            El procedimiento es el que sigue:
                1. nodo_actual se utiliza para recorrer el árbol, comenzando desde la raíz.
                2. En cada iteración, si el id buscado coincide con el del nodo_actual, el ciclo termina (encontrado).
                3. Si no coincide, se decide si continuar por la izquierda (id buscado <=) o por la derecha,
                    aprovechando la propiedad de orden del ABB para descartar la mitad del subárbol en cada paso.
                4. El ciclo también termina si nodo_actual llega a ser nulo, lo que significa que el id
                    no existe en el árbol.
                5. Finalmente, se construye el string de resultado según si el nodo fue encontrado o no.

        """
        nodo_actual = self.raiz
        while nodo_actual is not None and id_estudiante != nodo_actual.estudiante["id"]:
            if id_estudiante <= nodo_actual.estudiante["id"]:
                nodo_actual = nodo_actual.hijo_izquierdo
            else:
                nodo_actual = nodo_actual.hijo_derecho

        resultado = ""
        if nodo_actual is not None:
            resultado += "Encontrado :\n"
            for clave, valor in nodo_actual.estudiante.items():
                resultado += f"{clave} : {valor} | "
        else:
            resultado = f"Estudiante con id: {id_estudiante} no fue encontrado."
    
        return resultado

    def buscar_rango_id(self, lb: int, ub: int) -> str:
        """
        Busca todos los estudiantes cuyo id se encuentre dentro del rango inclusivo [lb, ub].

        Realiza un recorrido in-orden iterativo optimizado mediante una pila explícita,
        descartando subárboles completos cuyas claves estén fuera de los límites del rango.
        
        Procedimiento paso a paso:
            1. Se inicia el recorrido desde la raíz del árbol utilizando una pila explícita
               para gestionar los nodos pendientes y una lista auxiliar para almacenar los 
               registros coincidentes.

            2. Desde el nodo actual se evalúa el ID del estudiante:
               - Si id >= lb: El nodo actual o su subárbol izquierdo contienen claves dentro del rango.
                 Se apila el nodo y se continúa descendiendo hacia el hijo izquierdo.
               - Si id < lb: Se descarta por completo el subárbol izquierdo (sus descendientes son < lb)
                 y se salta directamente a explorar el hijo derecho.

            3. Al no poder descender más hacia la izquierda, se extrae el último nodo de la pila,
               lo que garantiza procesar las claves en secuencia estrictamente ascendente (in-orden).

            4. Evaluación del id:
               - Si lb <= id <= ub: El registro pertenece al rango y se agrega al resultado.
               - Si id > ub: Se interrumpe la búsqueda inmediatamente (break), pues los nodos 
                 pendientes por visitar tendrán un ID mayor al límite superior.

            5. Exploración del subárbol derecho y repetición:
               Se avanza hacia el hijo derecho del nodo desapilado y se repite el proceso desde 
               el paso 2 hasta agotar la pila o alcanzar el límite superior.
        """
        if self.raiz is None:
            return "El árbol está vacío."

        coincidencias = []
        pila = []
        nodo_actual = self.raiz

        while nodo_actual is not None or len(pila) > 0:
            # 1. Descender por la izquierda solo si el id puede ser >= lb
            while nodo_actual is not None:
                if nodo_actual.estudiante["id"] >= lb:
                    pila.append(nodo_actual)
                    nodo_actual = nodo_actual.hijo_izquierdo
                else:
                    # Si el id del nodo es menor que lb, sus hijos izquierdos también lo serán
                    # se pasa directamente a explorar el hijo derecho.
                    nodo_actual = nodo_actual.hijo_derecho

            if not pila:
                break

            # 2. Desapilar el nodo siguiente en secuencia in-orden
            nodo_actual = pila.pop()

            # 3. Guardar el registro si cae dentro del rango
            if lb <= nodo_actual.estudiante["id"] <= ub:
                coincidencias.append(nodo_actual.estudiante)

            # 4. Si la clave supera el límite superior, se detiene la búsqueda
            # (las claves posteriores en in-orden serán mayores)
            if nodo_actual.estudiante["id"] > ub:
                break

            # 5. Explorar el subárbol derecho
            nodo_actual = nodo_actual.hijo_derecho

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
        """
            Retorna un string con todos los estudiantes del árbol, ordenados de forma ascendente por id.

            Este método es un simple punto de entrada que delega el trabajo real en _inorden, el cual
            realiza un recorrido in-order (izquierda, nodo, derecha) sobre el árbol. Gracias a la propiedad
            de orden del ABB, este tipo de recorrido garantiza que los estudiantes se visiten en orden
            ascendente por id, sin necesidad de un paso adicional de ordenamiento (a diferencia de la
            lista, donde listar en orden requiere un sort completo).

            Se usa una lista auxiliar mutable (resultado) para ir acumulando los fragmentos de texto y luego
            unirlos con "".join(), ya que la concatenación repetida de strings es 
            más costosa en tiempo (cada concatenación crea
            un nuevo string en memoria).
        """
        resultado = []
        self._inorden(self.raiz, resultado)
        return "".join(resultado)

    def _inorden(self, nodo: Nodo, resultado: list):
        """
            Recorrido in-orden iterativo sobre el árbol, usado como método auxiliar de listar().

            Reemplaza la pila de llamadas recursivas del sistema por una pila explícita (pila).
            
            El procedimiento es el siguiente:
                1. Se recorre todo el subárbol izquierdo apilando cada nodo alcanzado.
                2. Cuando no existen más nodos a la izquierda (nodo_actual es None), se desapila 
                el último nodo guardado.
                3. Se procesa la información del estudiante del nodo recién desapilado.
                4. Se mueve la referencia al hijo derecho del nodo desapilado y se repite el proceso.
        """
        pila = []
        nodo_actual = nodo

        while nodo_actual is not None or len(pila) > 0:
            # 1. Ir lo más a la izquierda posible en la rama actual, apilando el camino
            while nodo_actual is not None:
                pila.append(nodo_actual)
                nodo_actual = nodo_actual.hijo_izquierdo

            # 2. Desapilar el último nodo procesable
            nodo_actual = pila.pop()

            # 3. Procesar/visitar el nodo desapilado
            resultado.append("Estudiante:\n")
            datos = "["
            for clave, valor in nodo_actual.estudiante.items():
                datos += f"{clave} : {valor} | "
            datos += "]\n"
            resultado.append(datos)

            # 4. Pasar a explorar el hijo derecho
            nodo_actual = nodo_actual.hijo_derecho

    def construir_arbol(self, datos : list) -> None:
        """
            Construye el árbol completo a partir de una lista de estudiantes, insertándolos uno por uno
            en el orden en que aparecen en la lista.
        """
        for estudiante in datos:
            self.insertar(estudiante)

    def altura(self) -> int:
        """
        Número de niveles del árbol (vacío = 0, solo la raíz = 1).

        Recorre el árbol nivel por nivel. La lista `nivel` contiene todos los nodos
        de un mismo nivel. En cada vuelta se cuenta un nivel y se reemplaza `nivel`
        por la lista de los hijos de esos nodos, es decir, el nivel de abajo.
        Cuando ya no hay hijos, la lista queda vacía y el ciclo termina.
        Es iterativo (sin recursión), para que funcione con árboles degenerados.

        Origen: generada con asistencia de IA (Claude, Anthropic, octubre 2026),
        autorizado por el enunciado del Laboratorio 3.
        """
        if self.raiz is None:
            return 0

        nivel = [self.raiz]   # nivel 1: solo la raíz
        altura = 0

        while len(nivel) > 0:
            altura += 1                    # contamos el nivel actual

            siguiente_nivel = []           # aquí se juntan los nodos del nivel de abajo
            for nodo in nivel:
                if nodo.hijo_izquierdo is not None:
                    siguiente_nivel.append(nodo.hijo_izquierdo)
                if nodo.hijo_derecho is not None:
                    siguiente_nivel.append(nodo.hijo_derecho)

            nivel = siguiente_nivel        # bajamos un nivel

        return altura