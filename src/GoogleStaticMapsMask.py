import rasterio
from geoalchemy2.shape import to_shape
from rasterio import features, Affine
from GoogleStaticMaps import GoogleStaticMaps
from SidewalkPolygon import SidewalkPolygon

class GoogleStaticMapsMask(object):

    def __init__(self, google_static_maps: GoogleStaticMaps) -> None:
        self.google_static_maps = google_static_maps
        return

    def save_google_static_maps_mask_image(self):
        bounding_box = self.google_static_maps.get_image_bounding_box()

        query = SidewalkPolygon.fetch_polygons_intersecting(bounding_box)
        sidewalk_polygons = [to_shape(poly.geom) for poly in query]

        from functools import partial
        import pyproj
        from shapely.ops import transform


        proj4 = '+proj=lcc +lat_1=38.3 +lat_2=39.45 +lat_0=37.66666666666666 +lon_0=-77 +x_0=400000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs'
        project = partial(
            pyproj.transform,
            pyproj.Proj(proj4),  # source coordinate system
            pyproj.Proj(init='epsg:4326')
        )  # destination coordinate system

        sidewalk_polygons = [transform(project, polygon) for polygon in sidewalk_polygons]

        lng1, lng2 = bounding_box.west, bounding_box.east
        lat1, lat2 = bounding_box.south, bounding_box.north
        x_scale = self.google_static_maps.image_w / (lng2 - lng1)
        y_scale = - self.google_static_maps.image_h / (lat2 - lat1)

        affine_translate = Affine.translation(-lng1, -lat2)
        affine_scale = Affine.scale(x_scale, y_scale)
        # affine_mirror = Affine(1, 0, 0, 0, -1, image_h)
        affine_transform = affine_scale * affine_translate

        self._rasterize_sidewalk_polygons(
            sidewalk_polygons,
            affine_transform.__invert__()
        )

    def _rasterize_sidewalk_polygons(self, sidewalk_polygons, affine,
                                     output_dir="../data/output/google_static_maps/masks/"):
        out = features.rasterize(
            sidewalk_polygons,
            transform=affine,
            out_shape=(
                self.google_static_maps.image_w,
                self.google_static_maps.image_h
            )
        )
        out *= 255

        identifier = self.google_static_maps.get_identifier()
        filename = output_dir + identifier + '.png'
        with rasterio.open(
                filename,
                'w',
                driver='PNG',
                dtype=rasterio.uint8,
                count=1,
                width=self.google_static_maps.image_w,
                height=self.google_static_maps.image_h,
                transform=affine) as dst:
            dst.write(out, indexes=1)
        return

if __name__ == '__main__':
    gsm = GoogleStaticMaps(38.910779, -77.046662)
    # gsm.fetch_google_static_maps_image()
    gsmm = GoogleStaticMapsMask(gsm)
    gsmm.save_google_static_maps_mask_image()