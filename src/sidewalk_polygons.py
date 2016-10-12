import fiona
import os
import pyproj
import rtree
from functools import partial
from rtree import index
from shapely.geometry import shape
from shapely import ops

from shapely.geometry.polygon import Polygon


def get_intersecting_sidewalk_polygons(lat, lng):
    """
    Reference
    http://gis.stackexchange.com/questions/121441/convert-shapely-polygon-coordinates
    http://gis.stackexchange.com/questions/90553/fiona-get-each-feature-extent-bounds
    http://stackoverflow.com/questions/30457089/python-shapely-how-to-create-a-polygon-given-its-point-vertices

    :return:
    """

    delta = 0.001

    target_area = Polygon([
        (lng - delta, lat - delta),
        (lng - delta, lat + delta),
        (lng + delta, lat + delta),
        (lng + delta, lat + delta)
    ])

    sidewalk_layer_filename = "../data/sidewalk_vector_files/dc/Polygon.shp"
    sidewalks = fiona.open(sidewalk_layer_filename)

    project = partial(
        pyproj.transform,
        pyproj.Proj(sidewalks.crs),  # source coordinate system
        pyproj.Proj(init='EPSG:4326'))  # destination coordinate system


    intersecting_sidewalk_polygons = []
    for feature in sidewalks:
        geom = shape(feature['geometry'])
        projected_geom = ops.transform(project, geom)

        if projected_geom.intersects(target_area):
            intersecting_sidewalk_polygons.append(projected_geom)

    return intersecting_sidewalk_polygons

# class SidewalkPolygons(object):
#     """Slow...
#
#     """
#
#     def __init__(self, index_name="rtree"):
#         """
#
#         References:
#             - Rtree tutorial. http://toblerity.org/rtree/tutorial.html
#             - Transform Shapely Polygon. http://gis.stackexchange.com/questions/127427/transforming-shapely-polygon-and-multipolygon-objects
#         """
#         properties = rtree.index.Property()
#         properties.dat_extension = 'data'
#         properties.idx_extension = 'index'
#
#         if not os.path.isfile(index_name):
#             self._index = index.Index(index_name, properties=properties)  # Create a file
#             self.initialize_polygons()
#         else:
#             self._index = index.Index(index_name, properties=properties)  # Load a file
#
#     def intersection(self, geom):
#         return self._index.intersection(geom.bounds, objects=True)
#
#     def initialize_polygons(self):
#         filename = "./data/sidewalk_vector_files/dc/SidewalkPly.shp"
#         sidewalks = fiona.open(filename)
#
#         project = partial(
#             pyproj.transform,
#             pyproj.Proj(sidewalks.crs),  # source coordinate system
#             pyproj.Proj(init='EPSG:4326'))  # destination coordinate system
#
#         for i, feature in enumerate(sidewalks):
#             geom = shape(feature['geometry'])
#             projected_geom = ops.transform(project, geom)
#             self._index.insert(i, projected_geom.bounds, projected_geom)

