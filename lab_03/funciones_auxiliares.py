import random
import gc
import time
from faker import Faker

_POOL_NOMBRES = None  # se llena la primera vez que se necesita

def _obtener_pool_nombres(tamano: int = 10000) -> list:
    """
    Crea o expande una lista global de nombres falsos para reutilización eficiente.
    """
    global _POOL_NOMBRES
    if _POOL_NOMBRES is None or len(_POOL_NOMBRES) < tamano:
        Faker.seed(0)
        faker = Faker()
        _POOL_NOMBRES = [faker.name() for _ in range(tamano)]
    return _POOL_NOMBRES

def generar_estudiantes(cantidad: int, ordenados: bool = False, semilla: int = None) -> list:
    """
    Genera una lista de diccionarios que representan estudiantes.
    IDs únicos aleatorios o secuenciales según el parámetro 'ordenados'.
    """
    rng = random.Random(semilla) # Instancia de random con la semilla dada

    if ordenados:
        ids = list(range(1, cantidad + 1)) # Lista de enteros [1, cantidad]
    else:
        # Generamos los ID de forma no secuencial
        # tomando del rango [1, 10*cantidad]
        # Así, aseguramos dos elementos:
        # Que los ids sean dispersos
        # Facilitar la generación de búsquedas fallidas (ID no existe)
        # la función sample asegura que no haya duplicados
        ids = rng.sample(range(1, 10*cantidad + 1), cantidad)

    # Elegimos k nombres al azar del pool de nombres, permite repeticiones
    nombres = rng.choices(_obtener_pool_nombres(cantidad), k=cantidad)

    # Construimos una lista de diccionarios, cada diccionario representa al estudiante
    return [
        {
            "id" : i,
            "nombre": n,
            "edad": rng.randint(17, 30),
            "promedio": round(rng.uniform(0.0, 10.0), 1)
        } for i, n in zip(ids, nombres)
    ]

def generar_ids_busqueda(estudiantes: list, cantidad_m: int, proporcion_existentes: float = 0.8, semilla: int = None) -> list:
    """
        Esta función genera una lista que contiene M números de ID para pasárselos como entrada al método
        buscar(id) de cada estructura (Lista, ABB, B+).

        La lista resultante contiene ids existentes (hay estudiantes con ese id) y
        también ids no existentes (para medir búsquedas fallidas).
        Por defecto, usamos la proporción 80% exitosas y 20% fallidas.
    """

    rng = random.Random(semilla) #Instanciamos el motor aleatorio

    # Extraemos los id de la lista de estudiantes en otra lista
    ids_existentes = [e["id"] for e in estudiantes]

    # Obtenemos el id mayor
    max_id = max(ids_existentes) if ids_existentes else 100

    # Calculamos la cantidad de ids exitosos (existentes)
    # con base en un porcentaje, por defecto tomamos
    # que el 80% de los ids se encuentren presentes.
    cant_exitos = int(cantidad_m*proporcion_existentes)

    # Calculamos la cantidad de fallos: Fallos = M - éxitos
    cant_fallos = cantidad_m - cant_exitos

    # De los id existentes, tomamos un total dado por la cant_exitos
    # de forma aleatoria, admite repetidos (simulando varias búsquedas a
    # un mismo estudiante)
    busquedas_exito = rng.choices(ids_existentes, k=cant_exitos)

    # Generar IDs que no pertenecen al conjunto actual para simular fallos
    conjunto_existentes = set(ids_existentes)
    busquedas_fallo = []
    while len(busquedas_fallo) < cant_fallos:
        # Generamos un id candidato como un número entre
        # [1, max_id + 2M], de manera tal que podamos tener
        # fallos internos (ids que son menores al máximo posible pero que no existen en la lista)
        # fallos externos (ids superiores a cualquier registro)
        candidato = rng.randint(1, max_id + cantidad_m*2)
        if candidato not in conjunto_existentes:
            busquedas_fallo.append(candidato)

    # Concatenamos las dos listas
    total_busquedas = busquedas_exito + busquedas_fallo
    # La desordenamos y retornamos
    rng.shuffle(total_busquedas)
    return total_busquedas

def generar_rangos_busqueda(estudiantes: list, cantidad_m: int, amplitud_promedio: int = 50, semilla: int = None) -> list:
    """
        Esta función se encarga de construir una lista de M pares de rangos [lb, ub]
        para evaluar experimentalmente el rendimiento de las consultas por rango en las tres estructuras de datos
        (Lista, ABB, Árbol B+)

        Dado el conjunto de ids, ubica el id máximo y el id mínimo. 
        Posteriormente, elige un entero aleatorio dentro de ese rango
        y determina la amplitud o radio para calcular los limtes superior
        e inferior del intervalo de búsqueda.

        Los rangos por ende son de longitud variable.
    """
    rng = random.Random(semilla)
    ids_existentes = [e["id"] for e in estudiantes]
    min_id = min(ids_existentes) if ids_existentes else 1
    max_id = max(ids_existentes) if ids_existentes else 100

    rangos = []
    for _ in range(cantidad_m):
        centro = rng.randint(min_id, max_id)
        radio = rng.randint(1, amplitud_promedio)
        lb = max(1, centro - radio)
        ub = centro + radio
        rangos.append((lb, ub))

    return rangos

def generar_rangos_por_tamano(estudiantes: list, cantidad_m: int, k: int = 50, semilla: int = None) -> list:
    """
    Genera M rangos [lb, ub] para probar buscar_rango_id, de forma que cada rango
    contenga exactamente k estudiantes, sin importar cómo estén distribuidos los IDs.

    Idea: en vez de elegir el ancho del rango en IDs (que da más o menos resultados
    según la densidad de los IDs), se ordenan los IDs existentes, se elige una
    posición de inicio al azar y se toman k IDs seguidos. El primero es lb y el
    último es ub. Como lb y ub son IDs que existen y los IDs son únicos, el rango
    [lb, ub] contiene justo esos k estudiantes.

    Origen: generada con asistencia de IA (Claude, Anthropic, octubre 2026),
    autorizado por el enunciado del Laboratorio 3.
    """
    rng = random.Random(semilla)  # generador propio: no altera el random global

    # Los IDs en orden ascendente; sus posiciones 0, 1, 2, ... son las que se sortean
    ids = sorted(e["id"] for e in estudiantes)

    # Sin estudiantes no hay rangos posibles (evita errores de índice más abajo)
    if not ids:
        return []

    # Si piden más estudiantes de los que existen, se devuelven todos
    k = min(k, len(ids))

    rangos = []
    for _ in range(cantidad_m):
        # Posición de inicio. El último inicio válido es len(ids) - k, porque desde
        # ahí se toman k IDs justo hasta el final de la lista. randint incluye ambos extremos.
        inicio = rng.randint(0, len(ids) - k)

        # ids[inicio] es el primer ID del grupo y ids[inicio + k - 1] es el k-ésimo
        rangos.append((ids[inicio], ids[inicio + k - 1]))

    return rangos

### FUNCIONES PARA MEDIR TIEMPOS

def medir_ns(funcion) -> int:
    """
    Ejecuta una función desactivando el Garbage Collector para evitar sesgos en el tiempo en ns.
    """
    gc_estaba_activo = gc.isenabled()
    gc.disable()
    try:
        inicio = time.perf_counter_ns()
        funcion()
        fin = time.perf_counter_ns()
    finally:
        if gc_estaba_activo:
            gc.enable()
    return fin - inicio

def medir_construccion(crear_estructura, estudiantes: list):
    """
    Mide el tiempo de construcción de una estructura insertando 'estudiantes' uno a uno.
    Devuelve (tiempo_ns, estructura_construida).
    """
    # Instanciamos la estructura, por parámetro se pasa el constructor
    estructura = crear_estructura()

    # Extraemos la referencia del método insertar
    insertar = estructura.insertar

    # Definimos la tarea interna sin argumentos
    # Como las estructuras usan métodos de construcción basados en
    # Llamar repetidamente al método insertar para cada estudiante
    # Aquí emulamos la misma tarea.
    def tarea():
        for estudiante in estudiantes:
            insertar(estudiante)

    # Medimos el tiempo de esa tarea
    tiempo = medir_ns(tarea)

    # Retornar tanto el tiempo como la estructura llena
    return tiempo, estructura

def medir_busquedas(estructura, ids_busqueda: list) -> int:
    """
    Mide el tiempo total acumulado (ns) al ejecutar M búsquedas puntuales.
    """
    buscar = estructura.buscar

    def tarea():
        for id_objetivo in ids_busqueda:
            buscar(id_objetivo)

    return medir_ns(tarea)

def medir_busquedas_rango(estructura, rangos_busqueda: list) -> int:
    """
    Mide el tiempo total acumulado (ns) al ejecutar M búsquedas por rango.
    """
    buscar_rango = estructura.buscar_rango_id

    def tarea():
        for lb, ub in rangos_busqueda:
            buscar_rango(lb, ub)

    return medir_ns(tarea)

def medir_listado(estructura) -> int:
    """
    Mide el tiempo (ns) de listar todos los elementos ordenados por ID.
    """
    return medir_ns(estructura.listar)

def repetir_medicion(medicion, repeticiones: int = 30, calentamiento: int = 3) -> list:
    """
    Ejecuta un protocolo de calentamiento y realiza K repeticiones de una función de medición.
    """
    for _ in range(calentamiento):
        medicion()
    return [medicion() for _ in range(repeticiones)]