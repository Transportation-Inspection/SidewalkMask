import fiona
import math
import pyproj
import rasterio
import urllib.request

from functools import partial
from pyproj import Proj, transform
from rasterio import features, Affine
from shapely.geometry import shape
from shapely.geometry.polygon import Polygon
from shapely import ops

from google_static_maps import get_image_bounding_coordinates
from sidewalk_polygons import get_intersecting_sidewalk_polygons


def rasterize_sidewalk_polygons(sidewalk_polygons, affine, image_w, image_h):
    """
    References:
    https://github.com/mapbox/rasterio
    https://github.com/mapbox/rasterio/blob/51c6e6294dc6a246b0a6b6e60e4a6ec3b3765c43/examples/features.ipynb

    Google Maps coordinate system. http://gis.stackexchange.com/questions/40538/what-is-the-difference-between-epsg900913-and-epsg3857
    Static Maps coordinates. http://gis.stackexchange.com/questions/46729/corner-coordinates-of-google-static-map-tile

    :param sidewalk_polygons: Shapely polygons
    :return:
    """

    out = features.rasterize(sidewalk_polygons, transform=affine, out_shape=(image_w, image_h))
    with rasterio.open(
            '../data/output/test.tif',
            'w',
            driver='GTiff',
            dtype=rasterio.uint8,
            count=1,
            width=image_w,
            height=image_h,
            transform=affine) as dst:
        dst.write(out, indexes=1)
    return out




def main():
    center_lat, center_lng = 38.910779, -77.046662
    image_w, image_h = 640, 640
    zoom = 20
    image_bound = get_image_bounding_coordinates(center_lat, center_lng, image_w=image_w, image_h=image_h, zoom=zoom)

    sidewalk_polygons = get_intersecting_sidewalk_polygons(center_lat, center_lng)

    # Prepare an affine transformation matrix to map latlng points to pixel coordinates
    lng1, lng2 = image_bound.sw.lng, image_bound.ne.lng
    lat1, lat2 = image_bound.sw.lat, image_bound.ne.lat
    x_scale = image_w / (lng2 - lng1)
    y_scale = - (image_h / (lat2 - lat1))  # flip y-coordinate

    affine_translate = Affine.translation(-lng1, -lat2)
    affine_scale = Affine.scale(x_scale, y_scale)
    affine_mirror = Affine(1, 0, 0, 0, -1, image_h)
    affine_transform = affine_mirror * affine_scale * affine_translate

    def transform_from_corner(ulx, uly, dx, dy):
        return Affine.translation(ulx, uly) * Affine.scale(dx, -dy)
    trans = transform_from_corner(lng1, lat2, 1.0/3600, 1.0/3600)
    output = rasterio.features.rasterize(sidewalk_polygons, transform=trans, out_shape=(3961, 4969))


    # Todo. Maybe all the polygons need to be inside the bound?
    rasterize_sidewalk_polygons(sidewalk_polygons, affine_transform, image_w, image_h)

    # for polygon in sidewalk_polygons:
    #
    #     for point in polygon.exterior.coords:
    #         print("%s,%s" % (str(point[1]), str(point[0])))





def test():
    a_scale = Affine.scale(10, -10)
    a_translate = Affine.translation(-10, -10)
    a_transform = a_scale * a_translate

    item = [[15, 15]]
    a_transform.itransform(item)

    pass


if __name__ == '__main__':
    main()