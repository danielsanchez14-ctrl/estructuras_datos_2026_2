from Estructura import Estructura
import math

class ArbolBPlus(Estructura):
    class Nodo:
        """
            Nodo del árbol B+ de orden n (n es el número total de punteros del nodo)
            Se sigue la estructura conceptual de este tipo de nodos:

            nodo = [Puntero 1, Clave 1, Puntero 2, Clave 2, ..., Puntero n-1, Clave n-1, Puntero n]

            Donde Puntero n representa al puntero que enlaza las hojas como lista ligada.
        """
        def __init__(self, orden_n : int, es_hoja : bool = True):
            self.orden_n = orden_n # Guardamos cúal es el órden n (número total de punteros que puede tener el nodo)
            self.es_hoja = es_hoja # Bandera booleana que diferencia a un nodo hoja de un nodo interno

            # A continuación, la estructura conceptual del nodo será representada mediante dos listas paralelas
            # Una lista guarda punteros, la otra guarda las claves.

            self.claves = [] # Guardamos las claves que van desde 1 hasta n-1
            self.punteros = [] # Guardamos solo los punteros que llevan hacia nodos hijos/datos

            self.puntero_siguiente = None # Atributo reservado para las HOJAS, apunta hacia la siguiente hoja de la lista enlazada.

            self.padre = None # Atributo útil para los algoritmos de inserción

        def tiene_espacio(self) -> bool:
            """
                Método interno diseñado para verificar si un nodo tiene espacio disponible o no.
                Si el nodo es hoja, validamos si su cantidad de claves es menor que n - 1.
                Si el nodo es interno, validamos si su cantidad de punteros es menor que n.
            """

            if self.es_hoja:
                return len(self.claves) < self.orden_n - 1
            else:
                return len(self.punteros) < self.orden_n



    def __init__(self, orden_n):
        self.raiz : "ArbolBPlus.Nodo" = None
        self.orden_n : int = orden_n


    def insertar(self, estudiante):
        clave_busqueda = estudiante["id"]
        puntero_dato = estudiante

        if self.raiz == None:
            nuevo_nodo = self.Nodo(orden_n=self.orden_n)
            self._insertar_en_hoja(nuevo_nodo, clave_busqueda, puntero_dato)
            self.raiz = nuevo_nodo
        else:
            hoja_objetivo = self._buscar_hoja(clave_busqueda)

            if hoja_objetivo.tiene_espacio():
                self._insertar_en_hoja(hoja_objetivo, clave_busqueda, puntero_dato)
            else:
                nodo_division = self.Nodo(orden_n=self.orden_n)

                punteros_hoja_objetivo = hoja_objetivo.punteros.copy()
                claves_hoja_objetivo = hoja_objetivo.claves.copy()

                nodo_temp = self.Nodo(self.orden_n)
                nodo_temp.claves = claves_hoja_objetivo
                nodo_temp.punteros = punteros_hoja_objetivo

                self._insertar_en_hoja(nodo_temp, clave_busqueda, puntero_dato)

                nodo_division.puntero_siguiente = hoja_objetivo.puntero_siguiente
                hoja_objetivo.puntero_siguiente = nodo_division

                limite = math.ceil(self.orden_n/2)

                hoja_objetivo.punteros = nodo_temp.punteros[:limite]
                hoja_objetivo.claves = nodo_temp.claves[:limite]

                nodo_division.punteros = nodo_temp.punteros[limite:]
                nodo_division.claves = nodo_temp.claves[limite:]

                clave_intermedia = nodo_division.claves[0]

                self._insertar_en_padre(hoja_objetivo, clave_intermedia, nodo_division)

        return estudiante

    def buscar(self, id_estudiante: int) -> str:
        """
            Busca un estudiante por su id, descendiendo hasta la hoja correspondiente
            y revisando si la clave existe ahí.
        """
        hoja = self._buscar_hoja(id_estudiante)

        if hoja is not None:
            for i, clave in enumerate(hoja.claves):
                if clave == id_estudiante:
                    resultado = "Encontrado :\n"
                    for k, v in hoja.punteros[i].items():
                        resultado += f"{k} : {v} | "
                    return resultado

        return f"Estudiante con id: {id_estudiante} no fue encontrado."

    def buscar_rango_id(self, lb :int, ub:int) -> str:
        """
            Busca todos los registros cuya clave (id) se encuentre dentro del rango
            inclusivo [lb, ub].

            Este algoritmo es una traducción a Python del seudocódigo findRange(lb, ub) de Database System Concepts (Silberschatz et al.).

        """
        if self.raiz is None:
            return "El árbol está vacío."

        conjunto_resultado = []
        c = self.raiz

        #Primero: bajar desde la raíz hasta la hoja adecuada para el límite inferior (lb)
        while not c.es_hoja:
            # Menor índice i tal que lb <= c.claves[i]
            i = next((idx for idx, clave in enumerate(c.claves) if lb <= clave), None)

            if i is None:
                # Si no existe tal índice, se desciende por el último puntero
                c = c.punteros[-1]
            elif lb == c.claves[i]:
                c = c.punteros[i + 1]
            else: # lb < c.claves[i]
                c = c.punteros[i]

        #Segundo: en la hoja C, hallar el menor índice tal que c.claves[i] >= lb
        i = next((idx for idx, clave in enumerate(c.claves) if clave >= lb), None)
        if i is None:
            i = len(c.claves) # Forzar el paso a la siguiente hoja

        #Tercero: recorrer las hojas secuencialmente reuniendo los registros entre [lb, ub]
        terminado = False
        while not terminado:
            n = len(c.claves)
            if i < n and c.claves[i] <= ub:
                conjunto_resultado.append(c.punteros[i])
                i += 1
            elif i < n and c.claves[i] > ub:
                terminado = True
            elif i >= n and c.puntero_siguiente is not None:
                c = c.puntero_siguiente
                i = 0 #Avanzar al inicio de la siguiente hoja
            else:
                terminado = True # No hay más hojas a la derecha

        # Formatear la respuesta
        if not conjunto_resultado:
            return f"No se encontraron estudiantes en el rango [{lb}, {ub}]."

        resultado = [f"Estudiantes encontrados en el rango [{lb}, {ub}]:\n"]
        for estudiante in conjunto_resultado:
            resultado.append("Estudiante:\n[")
            for k, v in estudiante.items():
                resultado.append(f"{k} : {v} | ")
            resultado.append("]\n")

        return "".join(resultado)

    def listar(self) -> str:
        """
            Recorre todas las hojas del árbol de izquierda a derecha, aprovechando
            el enlace puntero_siguiente entre ellas, y devuelve los estudiantes
            en orden ascendente por id.
        """
        resultado = []
        hoja = self.raiz

        # Bajamos hasta la hoja más a la izquierda del árbol
        while hoja is not None and not hoja.es_hoja:
            hoja = hoja.punteros[0]

        # Recorremos las hojas enlazadas hacia adelante
        while hoja is not None:
            for estudiante in hoja.punteros:
                resultado.append("Estudiante:\n[")
                for k, v in estudiante.items():
                    resultado.append(f"{k} : {v} | ")
                resultado.append("]\n")
            hoja = hoja.puntero_siguiente

        return "".join(resultado)

    def construir_arbol(self, datos: list) -> None:
        """
            Inserta, uno por uno y en el orden dado, todos los estudiantes de la lista.
        """
        for estudiante in datos:
            self.insertar(estudiante)

            
    ## Métodos base (algoritmos de búsqueda e inserción), obtenidos de Database System Concepts (Silberschatz, Korth, Sudarshan)

    def _buscar_hoja(self, clave_busqueda : int):
        """
            Algoritmo estándar de búsqueda en un árbol B+.
            Desciende desde la raíz hasta encontrar la hoja que
            se espera contenga la clave de búsqueda indicada por el 
            parámetro clave_busqueda.
        """
        if self.raiz is None:
            return None
        
        nodo_actual = self.raiz

        while not nodo_actual.es_hoja:
            # Encontramos el índice i más pequeño tal que clave_busqueda <= nodo_actual.claves[i]
            i = next((i for i, clave in enumerate(nodo_actual.claves) if clave_busqueda <= clave), None)

            if i is None:
                # Si la clave objetivo es mayor a todas las de este nodo, descendemos hacia el hijo más grande.
                nodo_actual = nodo_actual.punteros[-1]

            elif clave_busqueda == nodo_actual.claves[i]:
                # Si la clave objetivo coincide con una clave en este nodo, entonces descendemos hacia la derecha, ya que
                # los valores mayores o iguales van al subárbol derecho.
                nodo_actual = nodo_actual.punteros[i + 1]
            else:
                # Si la clave objetivo es menor a la clave encontrada en i, descendemos por su puntero correspondiente.
                nodo_actual = nodo_actual.punteros[i]

        # Tras finalizar el ciclo, nos encontramos en la hoja donde se espera que se encuentre el valor
        return nodo_actual

    def _insertar_en_hoja(self, hoja : "ArbolBPlus.Nodo", clave : int, puntero : dict) -> None:

        # La hoja está completamente vacía
        if not hoja.claves:
            hoja.claves.append(clave)
            hoja.punteros.append(puntero)
            return

        # Buscamos la primera clave tal que sea mayor a la clave que se desea insertar
        for i in range(len(hoja.claves)):
            if hoja.claves[i] > clave:
                hoja.claves.insert(i, clave)
                hoja.punteros.insert(i, puntero)
                return

        # Si la clave es mayor que todas las demás, la insertamos al final
        hoja.claves.append(clave)
        hoja.punteros.append(puntero)
            

    def _insertar_en_padre(self, nodo_original : "ArbolBPlus.Nodo", clave_separadora : int, nodo_nuevo : "ArbolBPlus.Nodo") -> None:
        if nodo_original == self.raiz:
            nueva_raiz = self.Nodo(nodo_original.orden_n, es_hoja=False)
            nueva_raiz.claves = [clave_separadora]
            nueva_raiz.punteros = [nodo_original, nodo_nuevo]
            nodo_original.padre = nueva_raiz
            nodo_nuevo.padre = nueva_raiz
            self.raiz = nueva_raiz
            return

        padre = nodo_original.padre

        if padre.tiene_espacio():
            for i in range(len(padre.claves)):
                if padre.claves[i] > clave_separadora:
                    padre.claves.insert(i, clave_separadora)
                    padre.punteros.insert(i + 1, nodo_nuevo)
                    break
            else:
                # Si la clave resulta ser la mayor existente y el for nunca se detuvo
                padre.claves.append(clave_separadora)
                padre.punteros.append(nodo_nuevo)

            # Como ahora hay nuevos punteros en este padre
            nodo_nuevo.padre = padre
        else:
            # Se extraen copias de los punteros y claves del padre
            punteros_padre = padre.punteros.copy()
            claves_padre = padre.claves.copy()

            # Insertamos clave_separadora y el nuevo nodo en las copias
            for i in range(len(claves_padre)):
                if claves_padre[i] > clave_separadora:
                    claves_padre.insert(i, clave_separadora)
                    punteros_padre.insert(i + 1, nodo_nuevo)
                    break
            else:
                # Si la clave resulta ser la mayor existente y el for nunca se detuvo
                claves_padre.append(clave_separadora)
                punteros_padre.append(nodo_nuevo)

            # Ahora, procedemos a dividir al padre, creando un nuevo nodo
            nodo_division_padre = self.Nodo(orden_n=padre.orden_n, es_hoja=False)

            limite = math.ceil((nodo_division_padre.orden_n + 1) / 2)

            padre.punteros = punteros_padre[:limite]
            padre.claves = claves_padre[:limite - 1]

            nueva_clave_intermedia = claves_padre[limite - 1]

            nodo_division_padre.punteros = punteros_padre[limite:]
            nodo_division_padre.claves = claves_padre[limite:]

            # Los hijos que quedaron en el nuevo padre de la división deben actualizar sus punteros
            for nodo_hijo in nodo_division_padre.punteros:
                nodo_hijo.padre = nodo_division_padre

            # En caso de que el nodo nuevo se encuentre en el nodo padre original, se actualiza su puntero padre
            if nodo_nuevo in padre.punteros:
                nodo_nuevo.padre = padre
            else:
                nodo_nuevo.padre = nodo_division_padre

            self._insertar_en_padre(padre, nueva_clave_intermedia, nodo_division_padre)

    def altura(self) -> int:
        """
        Número de niveles del árbol B+ (vacío = 0, solo una hoja = 1).
        En un B+ todas las hojas están a la misma profundidad, así que basta
        bajar siempre por el primer puntero hasta llegar a una hoja, contando niveles.

        Origen: generada con asistencia de IA (Claude, Anthropic, octubre 2026),
        autorizado por el enunciado del Laboratorio 3.
        """
        altura = 0
        nodo = self.raiz
        while nodo is not None:
            altura += 1
            nodo = None if nodo.es_hoja else nodo.punteros[0]
        return altura

