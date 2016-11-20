import math
from rtree import index

from BoundingBox import BoundingBox

from collections import namedtuple
Point = namedtuple("Point", ["x", 'y'])

class RTreeIndex(object):
    def __init__(self):
        self.idx = index.Index()
        self.counter = 1

    def insert(self, point):
        bounds = (point.x, point.y, point.x, point.y)
        self.idx.insert(self.counter, bounds, obj=point)
        self.counter += 1

    def query_points_within(self, point_arg, distance_m=40):
        x_min = point_arg.x - distance_m / 2
        x_max = point_arg.x + distance_m / 2
        y_min = point_arg.y - distance_m / 2
        y_max = point_arg.y + distance_m / 2
        bounds = (x_min, y_min, x_max, y_max)
        result = self.idx.intersection(bounds, objects=True)

        def dist(point):
            return math.sqrt((point_arg.x - point.x) ** 2 + (point_arg.y - point.y) ** 2)

        result = filter(lambda item: dist(item.object) < distance_m, result)
        return [item.object for item in result]

    def intersection(self, bounding_box: BoundingBox, object: bool=True):
        """Return points within the bounding box"""
        result = self.idx.intersection(bounding_box.to_tuple(), object)
        return [item.object for item in result]

    def get_all(self):
        """Return all the points stored"""
        bound = self.get_bounds()
        return self.intersection(bound)

    def get_bounds(self, coordinate_interleaved=None):
        bound = self.idx.get_bounds()
        x_min, y_min, x_max, y_max = bound
        return BoundingBox(y_min, x_min, y_max, x_max)

def test_query_points_within():
    ridx = RTreeIndex()
    ridx.insert(Point(10, 10))
    ridx.insert(Point(100, 100))

    q = ridx.query_points_within(Point(90, 90))
    print(q)

def test_intersection():
    ridx = RTreeIndex()
    ridx.insert(Point(10, 10))
    ridx.insert(Point(100, 100))

    q = ridx.intersection(BoundingBox(0, 0, 100, 100))
    print(q)

    q = ridx.intersection(BoundingBox(0, 0, 90, 90))
    print(q)

if __name__ == '__main__':
    test_intersection()

