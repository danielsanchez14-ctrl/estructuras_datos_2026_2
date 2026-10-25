from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntEnum

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
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    points: list[Point] = field(default_factory=list)
    children: list[QuadNode] | None = None

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

        # Caso base (Hoja alcanzada)
        if len(points) <= capacity or depth == max_depth:
            return QuadNode(x_min, y_min, x_max, y_max, points, None)
        else:
            # Caso recursivo

            # Operaciones sobre los datos
            x_mid = (x_min + x_max) / 2
            y_mid = (y_min + y_max) / 2

            # Distribución de los puntos en cuadrantes
            buckets = ([], [], [], [])
            for px, py in points:
                buckets[Region.assign_region(px, py, x_mid, y_mid)].append((px, py))

            # Creamos un nodo interno y llamamos recursivamente a build para sus hijos
            parent = QuadNode(x_min, y_min, x_max, y_max)
            parent.children = [None, None, None, None]
            parent.children[Region.SW] = Quadtree._build(buckets[Region.SW], x_min, y_min, x_mid, y_mid, capacity, max_depth, depth + 1)
            parent.children[Region.SE] = Quadtree._build(buckets[Region.SE], x_mid, y_min, x_max, y_mid, capacity, max_depth, depth + 1)
            parent.children[Region.NW] = Quadtree._build(buckets[Region.NW], x_min, y_mid, x_mid, y_max, capacity, max_depth, depth + 1)
            parent.children[Region.NE] = Quadtree._build(buckets[Region.NE], x_mid, y_mid, x_max, y_max, capacity, max_depth, depth + 1) 

            return parent

    def range_search(self, central_point: Point, radius: float) -> list[Point]:
        pass

    def nearest_neighbor_search(self, query_point: Point) -> Point:
        pass

    def k_nearest_neighbors_search(self, query_point: Point, k : int = 2) -> list[Point]:
        pass


