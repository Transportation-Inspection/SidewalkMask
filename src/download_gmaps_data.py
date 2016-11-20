from BoundingBox import BoundingBox
from GoogleStaticMaps import GoogleStaticMaps
from GoogleStaticMapsMask import GoogleStaticMapsMask
from RTreeIndex import RTreeIndex
from StreetEdge import StreetEdge

import logging
from tqdm import tqdm
logging.basicConfig(level=logging.INFO)

from geoalchemy2.shape import to_shape


from shapely.geometry import LineString
from shapely.ops import transform
from functools import partial
import pyproj

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
        gsmm.save_google_static_maps_mask_image()

def get_latlngs(name):
    if name == "data_1000":
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
        query = StreetEdge.fetch_street_edges_within(bounding_box)

        # Split each segment queried into a set of points that are reasonably far away from each other.
        rtidx = RTreeIndex()
        segments = [to_shape(segment.geom) for segment in query]
        for segment in segments:
            projected_segment = transform(project_4326_to_26917, segment)
            length_m = projected_segment.length
            num_split = math.ceil(length_m / distance_threshold_m)

            piece_length_m = length_m / num_split

            for idx in range(num_split + 1):
                p = projected_segment.interpolate(idx * piece_length_m)

                # check if there are nearby points
                result = rtidx.query_points_within(p, distance_threshold_m / 2)
                if len(result) == 0:
                    logging.debug("Insert a point")
                    rtidx.insert(p)
                else:
                    logging.debug("There are nearby points already in the data")

        points = rtidx.get_all()
        latlngs = [transform(project_26917_to_4326, p) for p in points]
        return latlngs
    else:
        return []

def data_1000():
    latlngs = get_latlngs("data_1000")
    len(latlngs)
    for latlng in tqdm(latlngs):
        gsm = GoogleStaticMaps(latlng.y, latlng.x)
        gsmm = GoogleStaticMapsMask(gsm)

        gsm.fetch_google_static_maps_image()
        gsm.save_meta_data()
        gsmm.save_google_static_maps_mask_image()

    return


if __name__ == '__main__':
    data_1000()