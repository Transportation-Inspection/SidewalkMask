from BoundingBox import BoundingBox
from GoogleStaticMaps import GoogleStaticMaps
from GoogleStaticMapsMask import GoogleStaticMapsMask
from StreetEdge import StreetEdge

from geoalchemy2.shape import to_shape


from shapely.geometry import LineString
from shapely.ops import transform
from functools import partial
import pyproj

from rtree import index
import math

def test():
    gsm = GoogleStaticMaps(38.910779, -77.046662)
    gsmm = GoogleStaticMapsMask(gsm)

    gsm.fetch_google_static_maps_image()
    gsm.save_meta_data()
    gsmm.save_google_static_maps_mask_image()


def test():
    latlngs = [
        (38.905236, -77.053984),
        (38.905261, -77.053319),
        (38.905269, -77.052332),
        (38.905277, -77.051388),
        (38.905252, -77.050734),
        (38.905252, -77.050122),
        (38.905285, -77.049425),
        (38.905268, -77.048813),
        (38.905260, -77.048116),
        (38.905302, -77.047494),
        (38.903691, -77.053297),
        (38.903741, -77.052331),
        (38.903749, -77.051398),
        (38.903741, -77.050744),
        (38.903716, -77.050090),
        (38.903741, -77.049017),
        (38.904459, -77.053276),
        (38.904417, -77.051388),
        (38.904459, -77.050101),
        (38.904509, -77.048792)
    ]

    for latlng in latlngs:
        print("%f,%f" % (latlng[0], latlng[1]))
        gsm = GoogleStaticMaps(latlng[0], latlng[1])
        gsmm = GoogleStaticMapsMask(gsm)

        gsm.fetch_google_static_maps_image()
        gsm.save_meta_data()
        # gsmm.save_google_static_maps_mask_image()

def data_1000():
    # Latlngs from ST_MakeEnvelope(-77.040, 38.890, -77.005, 38.911, 4326)
    distance_threshold_m = 80  # meters
    project_4326_to_26917 = partial(
        pyproj.transform,
        pyproj.Proj(init='EPSG:4326'),
        pyproj.Proj(init='EPSG:26917')
    )

    project_26917_to_4326 = partial(
        pyproj.transform,
        pyproj.Proj(init='EPSG:26917'),
        pyproj.Proj(init='EPSG:4326')
    )

    bounding_box = BoundingBox(38.890, -77.040, 38.911, -77.005)
    query = StreetEdge.fetch_street_edges_intersecting(bounding_box)

    # rtree index
    # rt_idx = RTreeIndex()

    segments = [to_shape(segment.geom) for segment in query]
    for segment in segments:
        projected_segment = transform(project_4326_to_26917, segment)
        length_m = projected_segment.length
        num_split = math.ceil(length_m / distance_threshold_m)


        piece_length_m = length_m / num_split
        print(length_m, piece_length_m)

        for idx in range(num_split + 1):
            p = projected_segment.interpolate(idx * piece_length_m)

            print(p)

        print()

        # num_split = math.ceil(transformed_segment.length / distance_threshold_m) + 1

class RTreeIndex(object):
    def __init__(self):
        self.idx = index.Index()
        self.counter = 1

    def insert(self, point):
        bounds = (point.x, point.y, point.x, point.y)
        self.idx.insert(self.counter, bounds=bounds, obj=point)
        self.counter += 1

    def query_points_within(self, point, distance_m=40):
        x_min = point.x - distance_m / 2
        x_max = point.x + distance_m / 2
        y_min = point.y - distance_m / 2
        y_max = point.y + distance_m / 2
        bounds = (x_min, y_min, x_max, y_max)
        result = self.idx.intersection(bounds, object=True)

        def dist(x, y):
            return math.sqrt((point.x - x) ** 2 + (point.y - y) ** 2)

        []


if __name__ == '__main__':
    data_1000()
