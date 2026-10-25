from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntEnum
import heapq
# Tipo encargado de representar un punto, que será una tupla de coordenadas reales
Point = tuple[float, float]

class Region(IntEnum):
    """
    Esta clase representa la convención estándar para nombrar los cuadrantes
    en un Quadtree. Corresponde a un enum de enteros donde cada punto cardinal
    se asocia a un valor entero, que sirve como índice para la lista de nodos
    hijos de un nodo interno.

    A continuación, cada valor representa el siguiente cuadrante:
    SW (Suroeste) : abajo-izquierda
    SE (Sureste) : abajo-derecha
    NW (Noroeste) : arriba-izquierda
    NE (Noreste) : arriba-derecha
    """
    SW = 0
    SE = 1
    NW = 2
    NE = 3

    @classmethod
    def assign_region(cls, px: float, py: float, x_mid: float, y_mid: float) -> Region:
        """
            Este método codifica las reglas de distribución de un punto (px, py) hacia uno 
            de los cuatro cuadrantes.
        """
        if px > x_mid and py > y_mid:
            return cls.NE
        elif px <= x_mid and py > y_mid:
            return cls.NW
        elif px <= x_mid and py <= y_mid:
            return cls.SW
        elif px > x_mid and py <= y_mid:
            return cls.SE

@dataclass(slots=True, eq=False, repr=False)
class QuadNode:
    """
        Representación de un nodo del árbol Quadtree. Almacena los límites verticales y horizontales de la región cuadrada
        que representa, la lista de puntos (si es hoja) y la lista de punteros hacia sus nodos hijos.
    """
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    points: list[Point] = field(default_factory=list)
    children: list[QuadNode | None] | None = None

@dataclass(slots=True, eq=False, repr=False)
class Quadtree:
    root: QuadNode
    capacity: int = 1
    max_depth: int = 20

    @classmethod
    def build(
        cls,
        points: list[Point],
        x_min: float,
        y_min: float,
        x_max: float,
        y_max: float,
        capacity: int = 1,
        max_depth: int = 20
    ) -> Quadtree:
        root : QuadNode = Quadtree._build(points, x_min, y_min, x_max, y_max, capacity, max_depth)
        return cls(root, capacity, max_depth)

    @staticmethod
    def _build(points : list[Point], x_min : float, y_min : float, x_max : float, y_max : float, capacity : int, max_depth : int, depth : int = 0) -> QuadNode:
        """
            Método estático que construye recursivamente el árbol Quadtree.
            Recibe la lista de puntos (x, y) y los límites horizontales y verticales de la región que los contiene.
            También, recibe la capacidad (cantidad de puntos por nodo hoja); la profundidad máxima (para evitar recursión indefinida)
            y la profundidad (contador que indica en que nivel del árbol se encuentra la recursión).
        """

        # Caso base: la región tiene la cantidad de puntos indicados por la capacidad o se superó el límite de recursión.
        if len(points) <= capacity or depth == max_depth:
            return QuadNode(x_min, y_min, x_max, y_max, points, None)
        else:
            # Caso recursivo: subdividir una región en cuatro cuadrantes y distribuir los puntos.

            # Operaciones sobre los datos (divdir la zona en cuatro).
            x_mid = (x_min + x_max) / 2
            y_mid = (y_min + y_max) / 2

            # Distribución de los puntos en cuadrantes.
            buckets = ([], [], [], [])
            for px, py in points:
                buckets[Region.assign_region(px, py, x_mid, y_mid)].append((px, py))

            # Creamos un nodo interno y llamamos recursivamente a build para sus hijos.
            parent = QuadNode(x_min, y_min, x_max, y_max)
            parent.children = [None, None, None, None]
            parent.children[Region.SW] = Quadtree._build(buckets[Region.SW], x_min, y_min, x_mid, y_mid, capacity, max_depth, depth + 1)
            parent.children[Region.SE] = Quadtree._build(buckets[Region.SE], x_mid, y_min, x_max, y_mid, capacity, max_depth, depth + 1)
            parent.children[Region.NW] = Quadtree._build(buckets[Region.NW], x_min, y_mid, x_mid, y_max, capacity, max_depth, depth + 1)
            parent.children[Region.NE] = Quadtree._build(buckets[Region.NE], x_mid, y_mid, x_max, y_max, capacity, max_depth, depth + 1) 

            return parent

    def range_search(self, central_point: Point, radius: float) -> list[Point]:
        """
            Implementación de la búsqueda por rango.
            Recibe un punto central para realizar la búsqueda y un radio.
            retorna la lista de tuplas que se encuentran dentro de ese radio.
        """
        if self.root is None or radius < 0:
            return []

        solution = [] #Aquí se almacenan los puntos de la solución.

        self._range_search_visit(self.root, central_point, radius, solution) #Recorremos recursivamente al árbol.

        return solution

    def _range_search_visit(self, node: QuadNode, central_point : Point, radius : float, sol : list[Point]) -> None:
        """
            Algoritmo recursivo para visitar los nodos del árbol para range search.
        """
        if node is None:
            return

        if self._distance_squared_to_region(central_point, node) > radius**2:
            return # Escenario de poda, si un nodo/región cuadrada no está intersectada/solapada con el círculo, se descarta pot completo.

        if not node.children: # Si el nodo no tiene hijos (es hoja), analizamos la distancia de cada punto respecto al centro y el radio.
            for point in node.points:
                if self._distance_squared(point, central_point) <= radius**2:
                    sol.append(point)

            return

        for region in Region: # Continuamos visitando recursivamente los hijos del nodo interno.
            self._range_search_visit(node.children[region], central_point, radius, sol)

    def _distance_squared(self, point1: Point, point2: Point):
        """
            Método auxiliar, calcula la distancia euclidiana cuadrada entre dos puntos.
        """
        px, py = point1
        qx, qy = point2
        return (px - qx)**2 + (py - qy)**2
    
    def _distance_squared_to_region(self, point: Point, region: QuadNode) -> float:
        """
            Método auxiliar, calcula la distancia entre un punto y una región cuadrada.
        """
        px, py = point
        distance_squared_x = max(region.x_min - px, 0, px - region.x_max)
        distance_squared_y = max(region.y_min - py, 0, py - region.y_max)
        return distance_squared_x**2 + distance_squared_y**2 

    def nearest_neighbor_search(self, query_point: Point) -> Point | None:
        """
            Implementación de la búsqueda del vecino más cercano.
            Encuentra el punto almacenado cuya distancia a un punto de consulta (query_point)
            sea mínima.
        """
        if self.root is None:
            return None
        
        # Menor distancia al cuadrado encontrada hasta el momento (inicialmente es infinito)
        best_distance = [float("inf")]
        # El punto que alcanza esa distancia, al inicio es nulo
        best_solution = [None]

        self._visit_nearest_neighbor_search(self.root, query_point, best_distance, best_solution)

        return best_solution[0]

    def _visit_nearest_neighbor_search(self, node: QuadNode, query_point: Point, best_distance: list[float], best_solution: list[Point | None]) -> None:
        """
            Algoritmo recursivo que visita los nodos del árbol para la búsqueda del vecino más cercano.
        """
        if node is None:
            return

        distance_squared_to_region = self._distance_squared_to_region(query_point, node)
        if distance_squared_to_region >= best_distance[0]:
            return # Caso de poda: si la distancia entre el punto de consulta y una región es mayor a la mejor almacenada, se descarta toda esa región.

        if not node.children: # Si el nodo es una hoja, analizamos la distancia de cada punto con la mejor almacenada
            for point in node.points:
                distance_squared_point_to_query_point = self._distance_squared(point, query_point)
                if distance_squared_point_to_query_point < best_distance[0]:
                    best_distance[0] = distance_squared_point_to_query_point
                    best_solution[0] = point

            return

        for region in Region: # Continuamos visitando recursivamente los hijos del nodo interno.
            self._visit_nearest_neighbor_search(node.children[region], query_point, best_distance, best_solution)
        

    def k_nearest_neighbors_search(self, query_point: Point, k : int = 2) -> list[Point]:
        if self.root is None or k <= 0:
            return []

        # Lista auxiliar que será utilizada como cola de prioridad, almacena tuplas de la forma (distancia, punto)
        priority_queue = []

        self._visit_k_nearest_neighbor_search(self.root, query_point, k, priority_queue)

        return [point for _, point in sorted(priority_queue, reverse=True)]

    def _visit_k_nearest_neighbor_search(self, node: QuadNode, query_point: Point, k: int, priority_queue: list) -> None:

        if node is None:
            return

        if len(priority_queue) == k:
            # Tomamos la distancia del punto más lejano que hay entre los k más cercanos.
            best_distance = abs(priority_queue[0][0])

            distance_squared_to_region = self._distance_squared_to_region(query_point, node)

            """
                Poda: si la distancia cuadrada del punto de consulta a la región del nodo a visitar
                es mayor que la distancia más lejana almacenada en la cola de prioridad, entonces se descarta
                dicho nodo y sus descendientes (toda la rama).
            """
            if distance_squared_to_region >= best_distance:
                return

        if not node.children: #Si el nodo es hoja, analizamos los nuevos puntos para determinar si van en la cola de prioridad
            for point in node.points:
                distance_squared_to_query_point = self._distance_squared(point, query_point)
                if len(priority_queue) == k:
                    if distance_squared_to_query_point < abs(priority_queue[0][0]):
                        heapq.heapreplace(priority_queue, (-distance_squared_to_query_point, point))
                else:
                    heapq.heappush(priority_queue, (-distance_squared_to_query_point, point))

            return

        for region in Region: # Continuamos visitando recursivamente los hijos del nodo interno.
            self._visit_k_nearest_neighbor_search(node.children[region], query_point, k, priority_queue)