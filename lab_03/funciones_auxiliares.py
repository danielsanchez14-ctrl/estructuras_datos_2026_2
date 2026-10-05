import random
import gc
import time
from faker import Faker

_POOL_NOMBRES = None  # se llena la primera vez que se necesita

def _obtener_pool_nombres(tamano: int = 1000) -> list:
    """
        Crea (una sola vez) una lista de nombres falsos para reutilizarlos.
        Origen: generada con asistencia de IA (Claude, Anthropic, octubre 2026)
    """
    global _POOL_NOMBRES
    if _POOL_NOMBRES is None:
        faker = Faker()
        _POOL_NOMBRES = [faker.name() for _ in range(tamano)]
    return _POOL_NOMBRES


def generar_estudiantes(cantidad: int, ordenados: bool = False, semilla: int = None) -> list:
    """
    Devuelve una lista de `cantidad` estudiantes (diccionarios con id, nombre, edad, promedio).
    - ordenados=True  -> IDs 1, 2, 3, ..., N en orden creciente.
    - ordenados=False -> IDs únicos y aleatorios, tomados entre 1 y 10*N, sin orden.
    - semilla: si se da, los datos son siempre los mismos.

    Origen: generada con asistencia de IA (Claude, Anthropic, octubre 2026)
    """
    rng = random.Random(semilla)

    if ordenados:
        ids = range(1, cantidad + 1)
    else:
        ids = rng.sample(range(1, 10 * cantidad + 1), cantidad)

    nombres = rng.choices(_obtener_pool_nombres(), k=cantidad)

    return [
        {"id": i, "nombre": n, "edad": rng.randint(17, 30), "promedio": round(rng.uniform(0, 10), 1)}
        for i, n in zip(ids, nombres)
    ]


def medir_ns(funcion) -> int:
    """
    Mide cuántos nanosegundos tarda en ejecutarse `funcion` (una función sin argumentos).
    Desactiva el recolector de basura durante la medición y lo restaura al terminar.

    Origen: generada con asistencia de IA (Claude, Anthropic, octubre 2026)
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


def medir_busquedas(estructura, ids_busqueda: list) -> int:
    """
        Tiempo (ns) total de buscar todos los IDs de la lista en la estructura.
        Origen: generada con asistencia de IA (Claude, Anthropic, octubre 2026)
    """
    buscar = estructura.buscar

    def tarea():
        for id_objetivo in ids_busqueda:
            buscar(id_objetivo)

    return medir_ns(tarea)


def medir_construccion(crear_estructura, estudiantes: list):
    """
    Construye una estructura vacía e inserta los estudiantes uno por uno.
    `crear_estructura` es una función sin argumentos que devuelve la estructura vacía.
    Devuelve (tiempo_ns, estructura_construida) para poder reutilizarla en otras pruebas.

    Origen: generada con asistencia de IA (Claude, Anthropic, octubre 2026)
    """
    estructura = crear_estructura()
    insertar = estructura.insertar

    def tarea():
        for estudiante in estudiantes:
            insertar(estudiante)

    tiempo = medir_ns(tarea)
    return tiempo, estructura


def medir_listado(estructura) -> int:
    """
    Tiempo (ns) de listar todos los estudiantes en orden por ID.
    Origen: generada con asistencia de IA (Claude, Anthropic, octubre 2026)
    """
    return medir_ns(estructura.listar)


def repetir_medicion(medicion, repeticiones: int = 30, calentamiento: int = 2) -> list:
    """
    Ejecuta `medicion` (función sin argumentos que devuelve un tiempo en ns).
    Las primeras `calentamiento` ejecuciones se descartan; devuelve la lista de tiempos restantes.
    Origen: generada con asistencia de IA (Claude, Anthropic, octubre 2026)
    """
    for _ in range(calentamiento):
        medicion()
    return [medicion() for _ in range(repeticiones)]