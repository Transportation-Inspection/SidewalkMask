from rasterio.features import rasterize
from shapely.geometry import Polygon, mapping
from rasterio.transform import Affine


def transform_from_corner(ulx, uly, dx, dy):
    return Affine.translation(ulx, uly)*Affine.scale(dx, -dy)
# image transform
bounds = (119.52, -21.6, 120.90, -20.5)
transform = transform_from_corner(bounds[0], bounds[3], 1.0/3600, 1.0/3600)

# Make raster image, burn in vector data which lies completely inside the bounding box
poly = Polygon(((120, -21), (120.5, -21), (120.5, -21.2), (120, -21.2)))
output = rasterize([poly], transform=transform, out_shape=(3961, 4969))

import matplotlib.pyplot as plt
plt.imshow(output)
print(output)