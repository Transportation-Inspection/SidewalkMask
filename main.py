import fiona
import math
import pyproj
import rasterio
import urllib.request

from functools import partial
from pyproj import Proj, transform
from rasterio import features
from rasterio.features import rasterize
from shapely.geometry import shape
from shapely.geometry.polygon import Polygon
from shapely import ops

from google_static_maps import get_image_bounding_coordinates


def get_google_static_maps_url(lat, lng, zoom=20, height=640, width=640):
    """Prepare a GMaps static image url

    URL Example: https://maps.googleapis.com/maps/api/staticmap?center=38.910779,%20-77.046662&zoom=20&size=1000x1000&maptype=satellite&key=YOUR_KEY

    Reference:
    https://developers.google.com/maps/documentation/static-maps/intro

    :param lat:
    :param lng:
    :param zoom:
    :param height:
    :param width:
    :return:
    """
    url = "https://maps.googleapis.com/maps/api/staticmap?"
    latlng_center = "center=%s,%s" % (str(lat), str(lng))
    zoom = "zoom=%s" % str(zoom)
    size = "size=%sx%s" % (str(height), str(width))
    map_type = "maptype=satellite"
    key = "AIzaSyAErrAIxL1j5_h3AMjWCuaHdAiy3Em5Erg"
    parameters = [latlng_center, zoom, size, map_type, key]

    print(parameters)
    url += "&".join(parameters)
    return url


def save_google_static_maps_image(url, output_dir="./data/output/"):
    """Save Google Static Maps image

    :param url:
    :return:
    """

    parameters = url.split("&")
    center_parameter = next(filter(lambda parameter: "center" in parameter, parameters))
    latlng = center_parameter.split("=")[1].replace(",", "_")

    output_filename = output_dir + "coord_" + latlng + ".png"
    print(output_filename)
    urllib.request.urlretrieve(url, output_filename)


def fetch_google_static_maps_image():
    """Fetch Google Static Maps Image
    """
    url = get_google_static_maps_url(38.910779, -77.046662)
    save_google_static_maps_image(url)



# def rasterize_sidewalk_polygons(sidewalk_polygons, center_lat, center_lng, image_w=640, image_h=640, zoom=20):
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

    out = rasterize(sidewalk_polygons, transform=affine, out_shape=(image_w, image_h))

    with rasterio.open('./data/output/test.tif', 'w', driver='GTiff', dtype=rasterio.uint8, count=1, width=640, height=640) as dst:
        dst.write(out, indexes=1)
    return out


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

    sidewalk_layer_filename = "./data/sidewalk_vector_files/dc/SidewalkPly.shp"
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



from rasterio import Affine
def main():
    center_lat, center_lng = 38.910779, -77.046662
    image_w, image_h = 640, 640
    zoom = 20
    image_bound = get_image_bounding_coordinates(center_lat, center_lng, image_w=image_w, image_h=image_h, zoom=zoom)

    # Prepare an affine transformation matrix to map latlng points to pixel coordinates
    x0 = image_bound.sw.lng
    y0 = image_bound.sw.lat
    x_scale = image_w / (image_bound.ne.lng - x0)
    y_scale = - (image_h / (image_bound.ne.lat - y0))  # flip y-coordinate
    affine_translate = Affine.translation(-x0, -y0)
    affine_scale = Affine.scale(x_scale, y_scale) * affine_translate
    affine_transform = Affine.translation(0, image_h) * affine_scale

    # Todo. Fix the bounding box
    sidewalk_polygons = get_intersecting_sidewalk_polygons(center_lat, center_lng)
    rasterize_sidewalk_polygons(sidewalk_polygons, affine_transform, image_w, image_h)


if __name__ == '__main__':
    main()