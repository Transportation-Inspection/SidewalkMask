from BoundingBox import BoundingBox
from GoogleStaticMaps import GoogleStaticMaps
from GoogleStaticMapsMask import GoogleStaticMapsMask
from StreetEdge import StreetEdge

from geoalchemy2.shape import to_shape


from shapely.geometry import LineString
from shapely.ops import transform
from functools import partial
import pyproj

from scipy.spatial import KDTree

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
    project = partial(
        pyproj.transform,
        pyproj.Proj(init='EPSG:4326'),
        pyproj.Proj(init='EPSG:26917')
    )

    bounding_box = BoundingBox(38.890, -77.040, 38.911, -77.005)
    query = StreetEdge.fetch_street_edges_intersecting(bounding_box)

    segments = [to_shape(segment.geom) for segment in query]
    # to_shape(poly.geom)
    for segment in segments:
        transformed_segment = transform(project, segment)
        print(transformed_segment.length)


if __name__ == '__main__':
    data_1000()
