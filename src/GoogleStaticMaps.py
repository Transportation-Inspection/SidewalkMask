"""
Google Statisc Maps Conversion code from:
    http://gis.stackexchange.com/questions/46729/corner-coordinates-of-google-static-map-tile
"""

from BoundingBox import BoundingBox

import math
import urllib.request
from collections import namedtuple

BoundingCoordinates = namedtuple('BoundingCoordinates', ['nw', 'ne', 'sw', 'se'])
LatLng = namedtuple('LatLng', ['lat', 'lng'])

tile_size = 256
earth_radius = 6378137  # meters
initial_resolution = 2 * math.pi * earth_radius / tile_size
origin_shift = 2 * math.pi * earth_radius / 2.0


class GoogleStaticMaps(object):

    def __init__(self, center_lat: float, center_lng: float, image_w: int=640, image_h: int=640, zoom: int=20) -> None:
        self.center_lat, self.center_lng = center_lat, center_lng
        self.image_w, self.image_h, self.zoom = image_w, image_h, zoom
        return

    def _get_google_static_maps_url(self) -> str:
        """Prepares and returns a Google Maps static image url
        URL Example: https://maps.googleapis.com/maps/api/staticmap?center=38.910779,%20-77.046662&zoom=20&size=1000x1000&maptype=satellite&key=YOUR_KEY

        Reference:
        https://developers.google.com/maps/documentation/static-maps/intro
        """
        url = "https://maps.googleapis.com/maps/api/staticmap?"
        latlng_center = "center=%f,%f" % (self.center_lat, self.center_lng)
        zoom = "zoom=%d" % self.zoom
        size = "size=%dx%d" % (self.image_h, self.image_w)
        map_type = "maptype=satellite"
        key = "AIzaSyAErrAIxL1j5_h3AMjWCuaHdAiy3Em5Erg"
        parameters = [latlng_center, zoom, size, map_type, key]

        url += "&".join(parameters)
        return url

    def save_google_static_maps_image(self, url: str, output_dir="../data/output/google_static_maps/images/") -> None:
        identifier = self.get_identifier()
        output_filename = output_dir + identifier + ".png"
        urllib.request.urlretrieve(url, output_filename)
        return

    def _pixels_to_meters(self, px: int, zoom: int) -> float:
        res = get_resolution(zoom)
        return px * res - origin_shift

    def _meters_to_lat_lon(self, mx: float, my: float) -> (float, float):
        lon = (mx / origin_shift) * 180.0
        lat = (my / origin_shift) * 180.0

        lat = 180 / math.pi * (2 * math.atan(math.exp(lat * math.pi / 180.0)) - math.pi / 2.0)
        return lat, lon

    def _meters_to_pixels(self, mx, my):
        res = get_resolution(self.zoom)
        px = (mx + origin_shift) / res
        py = (my + origin_shift) / res
        return px, py

    def _lat_lon_to_meters(self, lat, lon):
        mx = lon * origin_shift / 180.0
        my = math.log(math.tan((90 + lat) * math.pi / 360.0)) / (math.pi / 180.0)
        my = my * origin_shift / 180.0
        return mx, my

    def get_image_bounding_box(self) -> BoundingBox:
        mx, my = self._lat_lon_to_meters(self.center_lat, self.center_lng)
        pixel_x, pixel_y = self._meters_to_pixels(mx, my)
        w_pixel_x, e_pixel_x = pixel_x - self.image_w / 2, pixel_x + self.image_w / 2
        s_pixel_y, n_pixel_y = pixel_y - self.image_h / 2, pixel_y + self.image_h / 2

        w_meter_x = self._pixels_to_meters(w_pixel_x, self.zoom)
        e_meter_x = self._pixels_to_meters(e_pixel_x, self.zoom)
        s_meter_y = self._pixels_to_meters(s_pixel_y, self.zoom)
        n_meter_y = self._pixels_to_meters(n_pixel_y, self.zoom)

        s_lat, w_lng = self._meters_to_lat_lon(w_meter_x, s_meter_y)
        n_lat, e_lng = self._meters_to_lat_lon(e_meter_x, n_meter_y)

        return BoundingBox(s_lat, w_lng, n_lat, e_lng)

    def get_identifier(self):
        return "gsm_ll%f,%f_z%d_wh%dx%d" % (self.center_lat, self.center_lng, self.zoom, self.image_w, self.image_h)

    def describe(self) -> str:
        bounding_box = self.get_image_bounding_box()
        identifier = self.get_identifier()
        description = "id:%s\n" % identifier
        description += "center:%f,%f\n" % (self.center_lat, self.center_lng)
        description += "south_west:%f,%f\n" % (bounding_box.south, bounding_box.west)
        description += "north_east:%f,%f\n" % (bounding_box.north, bounding_box.east)
        description += "image_w:%d\n" % (self.image_w,)
        description += "image_h:%d\n" % (self.image_h,)
        description += "zoom:%d\n" % (self.zoom,)
        description += "url:%s" % self._get_google_static_maps_url()
        return description

    def save_meta_data(self, output_dir="../data/output/google_static_maps/info/") -> None:
        description = self.describe()
        identifier = self.get_identifier()
        filename = output_dir + identifier + ".txt"
        with open(filename, 'w') as f:
            f.write(description)
        return

    def fetch_google_static_maps_image(self) -> None:
        """Fetch Google Static Maps Image
        """
        url = self._get_google_static_maps_url()
        #self.save_google_static_maps_image(url)
        #self.save_meta_data()
        return



def get_resolution(zoom: int) -> float:
    return initial_resolution / (2 ** zoom)


def lat_lon_to_meters(lat, lon):
    """
    """
    mx = lon * origin_shift / 180.0
    my = math.log( math.tan((90 + lat) * math.pi / 360.0 )) / (math.pi / 180.0)
    my = my * origin_shift / 180.0
    return mx, my


def meters_to_pixels(mx, my, zoom):
    """
    """
    res = get_resolution(zoom)
    px = (mx + origin_shift) / res
    py = (my + origin_shift) / res
    return px, py




def pixels_to_meters(px, py, zoom):
    res = get_resolution(zoom)
    mx = px * res - origin_shift
    my = py * res - origin_shift
    return mx, my


def meters_to_lat_lon(mx, my):
    lon = (mx / origin_shift) * 180.0
    lat = (my / origin_shift) * 180.0

    lat = 180 / math.pi * (2 * math.atan(math.exp(lat * math.pi / 180.0)) - math.pi / 2.0)
    return lat, lon


def get_image_bounding_coordinates(center_lat, center_lng, image_h, image_w, zoom):
    mx, my = lat_lon_to_meters(center_lat, center_lng)
    pixel_x, pixel_y = meters_to_pixels(mx, my, zoom)
    nw_pixel_x, nw_pixel_y = pixel_x - image_w / 2, pixel_y + image_h / 2
    ne_pixel_x, ne_pixel_y = pixel_x + image_w / 2, pixel_y + image_h / 2
    sw_pixel_x, sw_pixel_y = pixel_x - image_w / 2, pixel_y - image_h / 2
    se_pixel_x, se_pixel_y = pixel_x + image_w / 2, pixel_y - image_h / 2

    nw_meter_x, nw_meter_y = pixels_to_meters(nw_pixel_x, nw_pixel_y, zoom)
    ne_meter_x, ne_meter_y = pixels_to_meters(ne_pixel_x, ne_pixel_y, zoom)
    sw_meter_x, sw_meter_y = pixels_to_meters(sw_pixel_x, sw_pixel_y, zoom)
    se_meter_x, se_meter_y = pixels_to_meters(se_pixel_x, se_pixel_y, zoom)

    nw_lat, nw_lng = meters_to_lat_lon(nw_meter_x, nw_meter_y)
    ne_lat, ne_lng = meters_to_lat_lon(ne_meter_x, ne_meter_y)
    sw_lat, sw_lng = meters_to_lat_lon(sw_meter_x, sw_meter_y)
    se_lat, se_lng = meters_to_lat_lon(se_meter_x, se_meter_y)

    nw = LatLng(nw_lat, nw_lng)
    ne = LatLng(ne_lat, ne_lng)
    sw = LatLng(sw_lat, sw_lng)
    se = LatLng(se_lat, se_lng)

    return BoundingCoordinates(nw, ne, sw, se)

if __name__ == '__main__':
    gsm = GoogleStaticMaps(38.910779, -77.046662)
    # gsm.fetch_google_static_maps_image()
    gsmm = GoogleStaticMapsMask(gsm)
    gsmm.save_google_static_maps_mask_image()

