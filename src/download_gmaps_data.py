from GoogleStaticMaps import GoogleStaticMaps
from GoogleStaticMapsMask import GoogleStaticMapsMask


def test():
    gsm = GoogleStaticMaps(38.910779, -77.046662)
    gsmm = GoogleStaticMapsMask(gsm)

    gsm.fetch_google_static_maps_image()
    gsm.save_meta_data()
    gsmm.save_google_static_maps_mask_image()


def main():
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

if __name__ == '__main__':
    main()
