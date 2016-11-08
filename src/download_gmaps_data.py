from GoogleStaticMaps import GoogleStaticMaps
from GoogleStaticMapsMask import GoogleStaticMapsMask

def test():
    gsm = GoogleStaticMaps(38.910779, -77.046662)
    gsmm = GoogleStaticMapsMask(gsm)

    gsm.fetch_google_static_maps_image()
    gsm.save_meta_data()
    gsmm.save_google_static_maps_mask_image()

if __name__ == '__main__':
    test()
