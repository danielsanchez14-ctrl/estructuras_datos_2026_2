import gc
import math
import os
import random
import time
import statistics
import pandas as pd

import matplotlib.pyplot as plt

from Quadtree import Point, Quadtree
from test import BruteForceAlgorithm # misma referencia usada en las pruebas

##### Parámetros del análisis #####
SIZES = (100, 500, 1_000, 5_000, 10_000, 50_000)  # cantidades de puntos (n)
CITY_SIZE = 10_000      # la ciudad siempre es de 10 km x 10 km (metros)
NUM_QUERIES = 200       # consultas aleatorias por cada n
RADIUS = 500            # metros (enunciado)
K = 5                   # vecinos para k-NN
REPEATS = 10             # repeticiones de cada medición; se reporta el promedio
SEED = 42
VERIFY_SIZE = 1_000     # tamaño del conjunto usado para verificar resultados
IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imagenes")

# Operaciones medidas: la clave produce el título para gráficas y reporte
OPERATIONS = {
    "range": f"Range search ({RADIUS} m)",
    "nn": "Vecino más cercano (1-NN)",
    "knn": f"{K} vecinos más cercanos (k-NN)",
}


class Benchmark:
    """
        Mide el rendimiento del Quadtree frente a fuerza bruta.

        Reglas de medición:
        1. Ambos métodos reciben exactamente las mismas consultas.
        2. La construcción del árbol se cronometra aparte, nunca dentro de las consultas.
        3. Se usa perf_counter_ns con el recolector de basura desactivado, para que
           una limpieza de memoria no distorsione un tiempo.
        4. Cada medición se repite REPEATS veces y se promedia.

        Todos los tiempos se guardan en nanosegundos (ns).

        Métodos cocreados con Claude AI, Anthropic (26/10/2026)
    """

    @staticmethod
    def generate_points(n: int, rng: random.Random) -> list[Point]:
        """Genera n puntos aleatorios dentro de la ciudad."""
        return [(rng.uniform(0, CITY_SIZE), rng.uniform(0, CITY_SIZE)) for _ in range(n)]

    @staticmethod
    def operations(tree: Quadtree, points: list[Point]) -> dict:
        """
            Para cada operación (range search, K-NN, 1-NN) se devuelve el par función
            del quadtree - función de fuerza bruta. Ambas reciben solo el punto de consulta, así
            el cronometraje las trata igual.
        """
        return {
            "range" : (lambda query: tree.range_search(query, RADIUS), lambda query: BruteForceAlgorithm.range_search(points, query, RADIUS)),
            "nn": (lambda query: tree.nearest_neighbor_search(query), lambda query: BruteForceAlgorithm.nearest_neighbor_search(points, query)),
            "knn": (lambda query: tree.k_nearest_neighbors_search(query, K), lambda query: BruteForceAlgorithm.k_nearest_neighbor_search(points, query, K)),
        }

    @staticmethod
    def verify_same_results() -> None:
        """
            Antes de medir, comprueba que ambos métodos devuelven lo mismo.
            No tiene sentido comparar tiempos de algoritmos que dan respuestas
            distintas. Range se compara como listas ordenadas; NN y k-NN por
            distancia al cuadrado (para que un empate no cuente como fallo).
        """

        rng = random.Random(SEED)
        points = Benchmark.generate_points(VERIFY_SIZE, rng)
        tree = Quadtree.build(points, 0, 0, CITY_SIZE, CITY_SIZE)
        distance_squared = BruteForceAlgorithm.distance_squared

        for _ in range(50):
            query: Point = (rng.uniform(0, CITY_SIZE), rng.uniform(0, CITY_SIZE))

            assert sorted(tree.range_search(query, RADIUS)) == sorted(BruteForceAlgorithm.range_search(points, query, RADIUS)), f"range_search difiere en {query}"

            quad_nn = tree.nearest_neighbor_search(query)
            brute_nn = BruteForceAlgorithm.nearest_neighbor_search(points, query)
            assert quad_nn is not None and brute_nn is not None
            assert distance_squared(quad_nn, query) == distance_squared(brute_nn, query), f"1-NN difiere en {query}"

            quad_knn = tree.k_nearest_neighbors_search(query, K)
            brute_knn = BruteForceAlgorithm.k_nearest_neighbor_search(points, query, K)

            assert [distance_squared(p, query) for p in quad_knn] == [distance_squared(p, query) for p in brute_knn], f"k-NN difiere en {query}"

        print("Verificación previa: el quadtree y la fuerza bruta devuelven lo mismo.\n")

    @staticmethod
    def time_queries(search, queries: list[Point]) -> list[float]:
        """
            Tiempo promedio por consulta (ns) de la función "search".
            Ejecuta todas las consultas REPEATS veces y promedia los resultados.
        """
        samples: list[float] = []
        for _ in range(REPEATS):
            gc.collect() # Limpiar antes de medir
            gc.disable() # Apagar recolector de basura durante la medición
            try:
                start = time.perf_counter_ns()
                for query in queries:
                    search(query)
                time_elapsed = time.perf_counter_ns() - start
            finally:
                gc.enable()
            samples.append(time_elapsed/len(queries))

        return samples

    @staticmethod
    def calculate_average_time(values: list[float]):
        """
            Auxiliar, calcula el promedio de la lista de tiempos de cada repetición.
            Para el cronometraje del tiempo de ejecución de un algoritmo.
        """
        return statistics.mean(values)

    @staticmethod
    def time_build(points: list[Point]) -> list[float]:
        """Devuelve los tiempos (ns) de construir el árbol en cada repetición."""
        samples: list[float] = []
        for _ in range(REPEATS):
            gc.collect()
            gc.disable()
            try:
                start = time.perf_counter_ns()
                tree = Quadtree.build(points, 0, 0, CITY_SIZE, CITY_SIZE)
                elapsed = time.perf_counter_ns() - start
                del tree
            finally:
                gc.enable()
            samples.append(elapsed)
        return samples

    @staticmethod
    def run() -> pd.DataFrame:
        """
            Recorre todos los n y devuelve un DataFrame indexado por n, con los
            tiempos en ns: build, range_quad, range_brute, nn_quad, nn_brute, ...
        """
        rng = random.Random(SEED)
        rows = []

        for n in SIZES:
            print(f"Midiendo n = {n} ...")
            points = Benchmark.generate_points(n, rng)
            queries = [(rng.uniform(0, CITY_SIZE), rng.uniform(0, CITY_SIZE))
                       for _ in range(NUM_QUERIES)]

            row = {"n": n, "build": Benchmark.calculate_average_time(Benchmark.time_build(points))}
            tree = Quadtree.build(points, 0, 0, CITY_SIZE, CITY_SIZE)

            for key, (quad_search, brute_search) in Benchmark.operations(tree, points).items():
                row[f"{key}_quad"] = Benchmark.calculate_average_time(Benchmark.time_queries(quad_search, queries))
                row[f"{key}_brute"] = Benchmark.calculate_average_time(Benchmark.time_queries(brute_search, queries))
            rows.append(row)

        print()
        return pd.DataFrame(rows).set_index("n")

    @staticmethod
    def find_crossover(sizes: list[int], quad: list[float], brute: list[float]) -> int | None:
        """
            Menor n desde el cual el quadtree es más rápido Y lo sigue siendo en
            todos los n mayores (un cruce aislado podría ser ruido).
            Devuelve None si el quadtree no gana en el n más grande.
        """
        crossover = None
        for n, q, b in reversed(list(zip(sizes, quad, brute))):
            if q < b:
                crossover = n
            else:
                break
        return crossover

    @staticmethod
    def estimate_exponent(sizes: list[int], times: list[float]) -> float:
        """
            Estima el exponente p de T(n) ≈ c · n^p.
            Ajusta una recta por mínimos cuadrados a (log n, log T); su pendiente es p.
            Ej.: p ≈ 1 -> crecimiento lineal O(n); p ≈ 0 -> casi constante o logarítmico.
        """
        log_n = [math.log(n) for n in sizes]
        log_t = [math.log(t) for t in times]
        return statistics.linear_regression(log_n, log_t).slope
    
class BenchmarkPlotter:
    """
        Gráficas del análisis. Todas son log-log y muestran los tiempos en
        segundos (se convierten desde ns aquí).

        Métodos cocreados con Claude AI, Anthropic (26/10/2026)
    """
    NS_TO_S = 1e-9 # Para conversión de tiempo

    @staticmethod
    def plot_queries(df: pd.DataFrame) -> None:
        """Genera una gráfica independiente por cada operación."""

        for key, title in OPERATIONS.items():
            fig, ax = plt.subplots(figsize=(7, 5))

            quad = df[f"{key}_quad"] * BenchmarkPlotter.NS_TO_S
            brute = df[f"{key}_brute"] * BenchmarkPlotter.NS_TO_S

            ax.loglog(df.index, quad, "o-", color="tab:blue", label="Quadtree")
            ax.loglog(df.index, brute, "s--", color="tab:red", label="Fuerza bruta")

            ax.set_title(title)
            ax.set_xlabel("Cantidad de puntos (n)")
            ax.set_ylabel("Tiempo por consulta (s)")
            ax.grid(True, which="both", alpha=0.3)
            ax.legend()

            BenchmarkPlotter._save(fig, f"analisis_{key}.png")
    @staticmethod
    def plot_build(df: pd.DataFrame, filename: str = "analisis_construccion.png") -> None:
        """Tiempo de construcción del árbol vs. n."""
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.loglog(df.index, df["build"] * BenchmarkPlotter.NS_TO_S, "o-", color="tab:green")
        ax.set_title("Construcción del Quadtree")
        ax.set_xlabel("Cantidad de puntos (n)")
        ax.set_ylabel("Tiempo de construcción (s)")
        ax.grid(True, which="both", alpha=0.3)

        BenchmarkPlotter._save(fig, filename)

    @staticmethod
    def _save(fig, filename: str) -> None:
        os.makedirs(IMAGES_DIR, exist_ok=True)
        fig.tight_layout()
        fig.savefig(os.path.join(IMAGES_DIR, filename), dpi=150)
        plt.close(fig)

class BenchmarkReport:
    """
        Genera un reporte de texto con los tiempos de búsqueda y el tamaño
        a partir del cual el Quadtree supera a la fuerza bruta.

        Métodos cocreados con Claude AI, Anthropic (26/10/2026)
    """
    @staticmethod
    def operation_table(df: pd.DataFrame, key: str) -> pd.DataFrame:
        """Construye la tabla de tiempos promedio por consulta, 
        en microsegundos."""
        return pd.DataFrame({
            "Quadtree (µs)": df[f"{key}_quad"] / 1e3,
            "Fuerza bruta (µs)": df[f"{key}_brute"] / 1e3,
        })

    @staticmethod
    def crossover_message(df: pd.DataFrame, key: str) -> str:
        """Indica desde qué tamaño medido el Quadtree gana de forma sostenida."""
        crossover = Benchmark.find_crossover(list(df.index), df[f"{key}_quad"].tolist(), df[f"{key}_brute"].tolist())

        if crossover is None:
            return (
                "Cruce sostenido no identificado: el Quadtree no es más "
                f"rápido para el mayor tamaño medido (n = {df.index[-1]})."
            )

        if crossover == df.index[0]:
            return (
                "El Quadtree es más rápido desde el menor tamaño "
                f"medido (n = {crossover})."
            )

        return f"El Quadtree es más rápido de forma sostenida desde n = {crossover}."

    @staticmethod
    def build_lines(df: pd.DataFrame) -> list[str]:
        """Prepara las secciones del reporte de rendimiento."""

        lines = [
            "=" * 60,
            "ANÁLISIS DE RENDIMIENTO",
            "=" * 60,
            "",
            f"Consultas por tamaño de entrada: {NUM_QUERIES}",
            f"Radio de búsqueda: {RADIUS} m",
            f"Número de vecinos: {K}",
            f"Repeticiones por medición: {REPEATS} (se reporta el promedio)",
            "",
        ]

        fmt = "{:.2f}".format

        for key, title in OPERATIONS.items():
            lines.append(f"{title}: tiempo promedio por consulta")
            lines.append(
                BenchmarkReport.operation_table(df, key).to_string(float_format=fmt)
            )
            lines.append(BenchmarkReport.crossover_message(df, key))
            lines.append("")

        # La construcción se informa por separado
        lines.append("Construcción del Quadtree (ms)")
        lines.append(
            (df[["build"]] / 1e6)
            .rename(columns={"build": "Tiempo promedio (ms)"})
            .to_string(float_format=fmt)
        )
        lines.append("")

        # Pendiente estimada de la construcción
        build_slope = Benchmark.estimate_exponent(
            list(df.index),
            df["build"].tolist()
        )

        lines.append("Pendiente estimada de la construcción")
        lines.append(f"  Quadtree: {build_slope:.2f}")
        lines.append("")

        
        # Estimación de la pendiente de crecimiento
        lines.append("Pendiente estimada en escala log-log")

        for key, title in OPERATIONS.items():
            slope_quad = Benchmark.estimate_exponent(
                list(df.index),
                df[f"{key}_quad"].tolist()
            )

            slope_brute = Benchmark.estimate_exponent(
                list(df.index),
                df[f"{key}_brute"].tolist()
            )

            lines.append(title)
            lines.append(f"  Quadtree: {slope_quad:.2f}")
            lines.append(f"  Fuerza bruta: {slope_brute:.2f}")
            lines.append("")

        return lines

    @staticmethod
    def save(lines: list[str], filename: str = "analisis_rendimiento.txt") -> None:
        """Imprime el reporte y lo guarda en un archivo de texto."""

        report = "\n".join(lines)
        print(report)

        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            filename
        )

        with open(path, "w", encoding="utf-8") as file:
            file.write(report)


if __name__ == "__main__":
    Benchmark.verify_same_results()
    df = Benchmark.run()
    BenchmarkPlotter.plot_queries(df)
    BenchmarkPlotter.plot_build(df)
    BenchmarkReport.save(BenchmarkReport.build_lines(df))