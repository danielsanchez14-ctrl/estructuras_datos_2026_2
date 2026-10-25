from Quadtree import Point, Quadtree, QuadNode
import random
import unittest
import heapq
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.axes import Axes


class BruteForceAlgorithm:
    """
        La siguiente clase agrupa los algoritmos de:
        1. Range Search.
        2. Nearest Neighbor Search.
        3. Nearest Neighbor Search (Versión para K vecinos)

        La diferencia con la implementación de Quadtree.py es que estos algoritmos son de "fuerza bruta",
        es decir, hacen solo uso de listas nativas de Python para ejecutar cada tarea.
    """

    @staticmethod
    def range_search(points_list: list[Point], central_point: Point, radius: float) -> list[Point]:

        if radius < 0:
            return []
        
        return [
            point for point in points_list 
            if BruteForceAlgorithm.distance_squared(point, central_point) <= radius**2]

    @staticmethod
    def nearest_neighbor_search(points_list: list[Point], query_point: Point) -> Point | None:
        # Menor distancia al cuadrado encontrada hasta el momento (inicialmente es infinito)
        best_distance = float("inf")
        # El punto que alcanza esa distancia, al inicio es nulo
        best_solution = None
        for point in points_list:
            distance_squared_point_to_query_point = BruteForceAlgorithm.distance_squared(point, query_point)
            if distance_squared_point_to_query_point < best_distance:
                best_distance = distance_squared_point_to_query_point
                best_solution = point

        return best_solution

    @staticmethod
    def k_nearest_neighbor_search(points_list: list[Point], query_point: Point, k : int = 2) -> list[Point]:
        if k <= 0:
            return []
        priority_queue = []
        for point in points_list:
            distance_squared_to_query_point = BruteForceAlgorithm.distance_squared(point, query_point)
            if len(priority_queue) < k:
                heapq.heappush(priority_queue, (-distance_squared_to_query_point, point))
            else:
                best_distance = abs(priority_queue[0][0])
                if distance_squared_to_query_point < best_distance:
                    heapq.heapreplace(priority_queue, (-distance_squared_to_query_point, point))

        return [point for _, point in sorted(priority_queue, reverse=True)]


    @staticmethod
    def distance_squared(point1: Point, point2: Point):
        """
            Método auxiliar, calcula la distancia euclidiana cuadrada entre dos puntos.
        """
        px, py = point1
        qx, qy = point2
        return (px - qx)**2 + (py - qy)**2



##### Pruebas unitarias y tests #####
# Parámetros del problema: la ciudad es un cuadrado de 10 km x 10 km,
# con coordenadas en metros.
NUM_POINTS = 10_000
CITY_SIZE = 10_000
SEED = 42 # Semilla de aleatorización utilizada.
RADIUS = 500          # metros (enunciado)
NUM_QUERIES = 200 # Total de consultas a realizar
CAPACITIES = (1, 4, 8) # Capacidades por hoja (cuántos puntos guarda una hoja)
IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imagenes")

class TestQuadtree(unittest.TestCase):

    def setUp(self) -> None:
        """
            Se ejecuta antes de CADA prueba. Genera los puntos de entrega
            y construye el árbol. La semilla fija hace que los datos sean
            idénticos en cada ejecución (pruebas reproducibles).

            Método cocreado con Claude AI, Anthropic (25/10/2026)
        """
        random.seed(SEED)
        self.points: list[Point] = [
            (random.uniform(0, CITY_SIZE), random.uniform(0, CITY_SIZE))
            for _ in range(NUM_POINTS)
        ]
        self.tree = Quadtree.build(self.points, 0, 0, CITY_SIZE, CITY_SIZE) # Árbol sobre el que se realizan las pruebas

    @staticmethod
    def collect_leaf_points(node: QuadNode) -> list[Point]:
        """
            Auxiliar: recorre el árbol y devuelve los puntos de todas las hojas.
            Una hoja es un nodo sin hijos; los nodos internos no guardan puntos.

            Método cocreado con Claude AI, Anthropic (25/10/2026)
        """
        # Caso base: nodo hoja alcanzado
        if not node.children:
            return list(node.points)

        # Caso recursivo: si es un nodo interno, se sigue a través de sus descendientes hasta alcanzar las hojas
        points: list[Point] = []
        for child in node.children:
            points.extend(TestQuadtree.collect_leaf_points(child))
        return points

    def test_build_keeps_all_points(self) -> None:
        """
            Prueba 1: la construcción no pierde ni duplica puntos.

            Se recolectan los puntos de todas las hojas y se comparan con los
            de entrada. Si el reparto en cuadrantes fallara en un borde,
            faltaría un punto o aparecería repetido.

            Método cocreado con Claude AI, Anthropic (25/10/2026)
        """
        leaf_points = self.collect_leaf_points(self.tree.root)

        # 1. La cantidad total coincide.
        # falla si a != b y muestra msg.
        self.assertEqual(
            len(leaf_points), NUM_POINTS,
            msg="La cantidad de puntos en las hojas no coincide con la entrada"
        )

        # 2. Son los mismos puntos, cada uno exactamente las mismas veces.
        # compara dos listas ignorando el orden pero respetando cuántas veces aparece cada elemento.
        self.assertCountEqual(leaf_points, self.points)

    def test_range_search_matches_brute_force(self) -> None:
        """
            Prueba 2: range_search del quadtree equivalente a range_search de fuerza bruta.

            Para cada capacidad de hoja (1, 4 y 8) se construye un árbol y se
            lanzan NUM_QUERIES consultas aleatorias con radio de 500 m.
            El resultado del quadtree debe contener los mismos puntos que el
            de fuerza bruta: ni uno de más (falso positivo) ni uno de menos
            (poda incorrecta).

            Método cocreado con Claude AI, Anthropic (25/10/2026)
        """
        # Generador propio: las consultas no dependen de lo hecho en setUp.
        rng = random.Random(SEED)
        found_total = 0
        for capacity in CAPACITIES:
            tree = Quadtree.build(
                self.points, 0, 0, CITY_SIZE, CITY_SIZE, capacity=capacity
            )

            for _ in range(NUM_QUERIES):
                query: Point = (rng.uniform(0, CITY_SIZE), rng.uniform(0, CITY_SIZE))

                # subTest: si falla, indica la capacidad y la consulta exactas.
                # permite identificar la consulta concreta que falla sin detener todas las comprobaciones posteriores.
                with self.subTest(capacity=capacity, query=query):
                    expected = BruteForceAlgorithm.range_search(self.points, query, RADIUS)
                    result = tree.range_search(query, RADIUS)
                    # comprueba que el quadtree y la fuerza bruta devuelvan exactamente los mismos puntos, sin exigir el mismo orden.
                    self.assertCountEqual(result, expected)
                    found_total += len(expected)

        # comprueba que las consultas hayan encontrado al menos un punto en total, 
        # evitando que una comparación de listas vacías haga pasar la prueba sin una búsqueda efectiva.
        self.assertGreater(found_total, 0, msg="Ninguna consulta encontró puntos")

    def test_nearest_neighbor_matches_brute_force(self) -> None:
        """
            Prueba 3: nearest_neighbor_search del quadtree equivalente al de fuerza bruta.

            Para cada capacidad de hoja (1, 4 y 8) se lanzan NUM_QUERIES consultas
            aleatorias. Se compara la DISTANCIA al cuadrado del punto encontrado,
            no el punto: si hay empate, ambos métodos pueden devolver puntos
            distintos y los dos serían correctos.

            Además, se consulta sobre un punto que ya existe en el dataset:
            su vecino más cercano es él mismo, a distancia 0.

            Método cocreado con Claude AI, Anthropic (25/10/2026)

        """
        rng = random.Random(SEED)

        for capacity in CAPACITIES:
            tree = Quadtree.build(self.points, 0, 0, CITY_SIZE, CITY_SIZE, capacity=capacity)

            # 1. Consultas aleatorias contra fuerza bruta
            for _ in range(NUM_QUERIES):
                query : Point = (rng.uniform(0, CITY_SIZE), rng.uniform(0, CITY_SIZE))

                # subTest: si falla, indica la capacidad y la consulta exactas.
                # permite identificar la consulta concreta que falla sin detener todas las comprobaciones posteriores.
                with self.subTest(capacity = capacity, query = query):
                    expected = BruteForceAlgorithm.nearest_neighbor_search(self.points, query)
                    result = tree.nearest_neighbor_search(query)

                    # Comnprobamos que los resultados no sean nulos
                    self.assertIsNotNone(expected)
                    self.assertIsNotNone(result)
                    assert expected is not None and result is not None

                    # Comnprobar si las distancias de los vecinos más cercanos son las mismas
                    # Para ambos métodos
                    self.assertEqual(
                        BruteForceAlgorithm.distance_squared(result, query),
                        BruteForceAlgorithm.distance_squared(expected, query)
                    )
            
            # 2. Consulta sobre un punto existente: distancia 0.
            existing = self.points[0]
            with self.subTest(capacity=capacity, query=existing):
                result = tree.nearest_neighbor_search(existing)
                self.assertEqual(result, existing)

    def test_range_search_circle_border(self) -> None:
        """
            Prueba 4: range search sobre 
            puntos exactamente sobre en el 
            borde del círculo incluidos.

            Con consulta (0, 0) y radio 500:
            - (0, 0), (500, 0) y (300, 400) están a distancia <= 500 -> deben salir.
              (300, 400): su distancia es exactamente 500.
            - (500.001, 0) y (0, 501) están apenas por fuera -> no deben salir.
            - (5000, 5000) está lejos y sobre una línea de corte del árbol.

            Se repite para cada capacidad de hoja.

            Método cocreado con Claude AI, Anthropic (25/10/2026)
        """
        points: list[Point] = [
            (0, 0), (500, 0), (300, 400),      # dentro (dos justo en el borde)
            (500.001, 0), (0, 501),            # apenas fuera
            (5000, 5000),                      # lejos, sobre una línea de corte
        ]

        query: Point = (0, 0)
        expected: list[Point] = [(0, 0), (500, 0), (300, 400)]

        for capacity in CAPACITIES:
            with self.subTest(capacity=capacity):
                tree = Quadtree.build(
                    points, 0, 0, CITY_SIZE, CITY_SIZE, capacity=capacity
                )
                result = tree.range_search(query, RADIUS)

                self.assertCountEqual(result, expected)
    
    def test_duplicated_and_no_results(self) -> None:
        """
            Prueba 5: casos extremos de range_search y construcción del árbol.

            1. Duplicados: se construye un quadtree con cinco copias del mismo
            punto y capacity=1. Como los puntos no pueden separarse en
            cuadrantes diferentes, la construcción debe terminar al alcanzar
            max_depth. Se comprueba que se alcanza dicha profundidad y que
            la búsqueda devuelve todas las copias.

            2. Sin resultados: se consulta una región sin puntos dentro del
            radio y se comprueba que range_search devuelva una lista vacía.

            Método cocreado con Claude AI, Anthropic (25/10/2026)
        """
        duplicated_point: Point = (1000, 1000)
        points: list[Point] = [duplicated_point] * 5
        
        max_depth = 20
        tree = Quadtree.build(
                        points,
                        0, 0, CITY_SIZE, CITY_SIZE,
                        capacity=1,
                        max_depth=max_depth
                    )

        with self.subTest(case="duplicados y max_depth"):

            self.assertEqual(TestQuadtree.tree_depth(tree.root), max_depth)

            # Comprobamos que se conservaron todas las copias.
            result = tree.range_search(duplicated_point, RADIUS)

            self.assertEqual(len(result), len(points))
            self.assertCountEqual(result, points)

        with self.subTest(case="sin resultados"):
            query: Point = (9000, 9000)
            result = tree.range_search(query, RADIUS)

            self.assertEqual(result, [])

    @staticmethod
    def tree_depth(node: QuadNode, depth: int = 0) -> int:
        """Auxiliar: profundidad del nivel más profundo del árbol."""
        if not node.children:
            return depth
        return max(TestQuadtree.tree_depth(child, depth + 1) for child in node.children)


    def test_k_nearest_matches_brute_force(self) -> None:
        """
            Prueba 6: k_nearest_neighbors_search equivalente al de fuerza bruta.

            Se comparan las DISTANCIAS al cuadrado de los k puntos devueltos
            (en orden), no los puntos, para que un empate no dé un falso fallo.
            También se verifican los casos extremos de k.

            Método cocreado con Claude AI, Anthropic (25/10/2026)
        """
        rng = random.Random(SEED)
        k = 5
        dist2 = BruteForceAlgorithm.distance_squared

        for capacity in CAPACITIES:
            tree = Quadtree.build(
                self.points, 0, 0, CITY_SIZE, CITY_SIZE, capacity=capacity
            )

            for _ in range(NUM_QUERIES):
                query: Point = (rng.uniform(0, CITY_SIZE), rng.uniform(0, CITY_SIZE))

                with self.subTest(capacity=capacity, query=query):
                    expected = BruteForceAlgorithm.k_nearest_neighbor_search(self.points, query, k)
                    result = tree.k_nearest_neighbors_search(query, k)

                    self.assertEqual(len(result), k)
                    self.assertEqual(
                        [dist2(p, query) for p in result],
                        [dist2(p, query) for p in expected],
                    )

        # Casos extremos de k (con el árbol de capacity=1 de setUp).
        with self.subTest(case="k <= 0"):
            self.assertEqual(self.tree.k_nearest_neighbors_search((0, 0), 0), [])

        with self.subTest(case="k mayor que n"):
            small = [(1.0, 1.0), (2.0, 2.0), (3.0, 3.0)]
            small_tree = Quadtree.build(small, 0, 0, CITY_SIZE, CITY_SIZE)
            result = small_tree.k_nearest_neighbors_search((0, 0), 10)
            self.assertCountEqual(result, small)



class Plotter:
    """
        Agrupa las verificaciones visuales pedidas en el enunciado:
        1. Range search: radio y puntos encontrados dentro del radio.
        2. Vecinos más cercanos: consulta, 1-NN y k vecinos.
        3. (Opcional) Divisiones del quadtree.

        Todas las figuras tienen dos paneles: vista global (dónde cae la consulta
        en la ciudad) y zoom (para poder ver los puntos individuales, porque un
        círculo de 500 m es muy pequeño en una ciudad de 10 km).
    """

    @staticmethod
    def plot_range_search(
        points: list[Point],
        query: Point,
        radius: float,
        found: list[Point],
        filename: str = "range_search.png",
        show: bool = False,
    ) -> None:
        """
            Verificación visual del range search.
            Dibuja todos los puntos (gris), el círculo de búsqueda, la consulta
            y los puntos encontrados (resaltados). A simple vista, todos los
            resaltados deben estar dentro del círculo y ningún gris debe estarlo.
        """
        fig, (ax_global, ax_zoom) = plt.subplots(1, 2, figsize=(14, 7))

        for ax in (ax_global, ax_zoom):
            Plotter._draw_points(ax, points)
            ax.add_patch(patches.Circle(
                query, radius, fill=False, color="tab:red", linewidth=2,
                label=f"Radio de {radius:g} m",
            ))
            ax.scatter(*zip(*found), color="tab:blue", s=25, zorder=3,
                       label=f"Encontrados ({len(found)})") if found else None
            ax.scatter(*query, color="black", marker="X", s=100, zorder=4,
                       label="Consulta")
            ax.set_aspect("equal")
            ax.set_xlabel("x (m)")
            ax.set_ylabel("y (m)")

        ax_global.set_title(f"Vista global ({len(points)} puntos de entrega)")
        ax_zoom.set_title("Zoom sobre el círculo")
        Plotter._zoom(ax_zoom, query, radius * 1.3)
        ax_zoom.legend(loc="upper right", fontsize=8)

        Plotter._save(fig, filename, show)

    @staticmethod
    def plot_nearest_neighbors(
        points: list[Point],
        query: Point,
        nearest: Point,
        k_nearest: list[Point],
        filename: str = "nearest_neighbors.png",
        show: bool = False,
    ) -> None:
        """
            Verificación visual de los vecinos más cercanos.
            Dibuja todos los puntos (gris), la consulta, los k vecinos con una
            línea hasta la consulta, y el vecino más cercano (1-NN) destacado.
            El zoom se ajusta al vecino más lejano de los k.
        """
        fig, (ax_global, ax_zoom) = plt.subplots(1, 2, figsize=(14, 7))

        for ax in (ax_global, ax_zoom):
            Plotter._draw_points(ax, points)

            # Líneas de la consulta a cada uno de los k vecinos.
            for neighbor in k_nearest:
                ax.plot([query[0], neighbor[0]], [query[1], neighbor[1]],
                        color="tab:orange", linestyle="--", linewidth=1, zorder=2)
            ax.scatter(*zip(*k_nearest), color="tab:orange", s=40, zorder=3,
                       label=f"{len(k_nearest)} vecinos más cercanos")

            # El vecino más cercano, más grande y con borde.
            ax.scatter(*nearest, color="gold", edgecolor="black", s=120, zorder=4,
                       label="Vecino más cercano (1-NN)")
            ax.scatter(*query, color="black", marker="X", s=100, zorder=5,
                       label="Consulta")
            ax.set_aspect("equal")
            ax.set_xlabel("x (m)")
            ax.set_ylabel("y (m)")

        # Zoom: distancia al vecino más lejano de los k, con margen.
        farthest = max(
            ((p[0] - query[0]) ** 2 + (p[1] - query[1]) ** 2) ** 0.5
            for p in k_nearest
        )
        ax_global.set_title(f"Vista global ({len(points)} puntos de entrega)")
        ax_zoom.set_title("Zoom sobre los vecinos")
        Plotter._zoom(ax_zoom, query, farthest * 1.3)
        ax_zoom.legend(loc="upper right", fontsize=8)

        Plotter._save(fig, filename, show)

    @staticmethod
    def plot_tree_divisions(
        points: list[Point],
        tree: Quadtree,
        filename: str = "quadtree_divisions.png",
        show: bool = False,
    ) -> None:
        """
            (Opcional) Dibuja el rectángulo de cada hoja del quadtree sobre los
            puntos. Se ven las zonas densas más subdivididas que las vacías.
        """
        fig, ax = plt.subplots(figsize=(8, 8))
        Plotter._draw_points(ax, points)
        Plotter._draw_leaves(ax, tree.root)
        ax.set_aspect("equal")
        ax.set_title("Divisiones del Quadtree (hojas)")
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")

        Plotter._save(fig, filename, show)

    # ---------- Auxiliares ----------

    @staticmethod
    def _draw_points(ax: Axes, points: list[Point]) -> None:
        """Dibuja todos los puntos del dataset en gris claro (fondo)."""
        xs, ys = zip(*points)
        ax.scatter(xs, ys, color="dimgray", s=6, alpha=0.6, zorder=1, label="Puntos de entrega")

    @staticmethod
    def _draw_leaves(ax: Axes, node: QuadNode) -> None:
        """Recorre el árbol y dibuja el rectángulo de cada hoja."""
        if not node.children:
            ax.add_patch(patches.Rectangle(
                (node.x_min, node.y_min),
                node.x_max - node.x_min,
                node.y_max - node.y_min,
                fill=False, edgecolor="tab:green", linewidth=0.4,
            ))
            return
        for child in node.children:
            Plotter._draw_leaves(ax, child)

    @staticmethod
    def _zoom(ax: Axes, center: Point, margin: float) -> None:
        """Limita los ejes a un cuadrado de lado 2*margin centrado en `center`."""
        ax.set_xlim(center[0] - margin, center[0] + margin)
        ax.set_ylim(center[1] - margin, center[1] + margin)

    @staticmethod
    def _save(fig, filename: str, show: bool) -> None:
        """Guarda la figura en la carpeta de imágenes y opcionalmente la muestra."""
        os.makedirs(IMAGES_DIR, exist_ok=True)
        fig.tight_layout()
        fig.savefig(os.path.join(IMAGES_DIR, filename), dpi=150)
        if show:
            plt.show()
        plt.close(fig)

if __name__ == "__main__":
    unittest.main(exit=False)

    rng = random.Random(SEED)
    points = [(rng.uniform(0, CITY_SIZE), rng.uniform(0, CITY_SIZE))
              for _ in range(NUM_POINTS)]
    tree = Quadtree.build(points, 0, 0, CITY_SIZE, CITY_SIZE)
    query: Point = (rng.uniform(0, CITY_SIZE), rng.uniform(0, CITY_SIZE))

    found = tree.range_search(query, RADIUS)
    nearest = tree.nearest_neighbor_search(query)
    k_nearest = tree.k_nearest_neighbors_search(query, 5)
    assert nearest is not None

    Plotter.plot_range_search(points, query, RADIUS, found)
    Plotter.plot_nearest_neighbors(points, query, nearest, k_nearest)
    Plotter.plot_tree_divisions(points, tree)