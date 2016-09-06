from contextlib import closing

import requests
import io
import os

url = 'http://overpass-api.de/api/interpreter'


def download(out_file, query):

    print 'Downloading "%s" to "%s"' % (query, out_file)

    with closing(requests.get(url, data={'data': query}, stream=True)) as r:

        with open(out_file, 'wb') as f:
            for line in r.iter_content(io.DEFAULT_BUFFER_SIZE):
                f.write(line)

        print 'Downloaded size: %.2f MB' % (os.path.getsize(out_file) / 1024.0 / 1024.0)


# download osm data for a bounding box
def main():

    min_lat = 46
    max_lat = 47.2
    min_lng = -122
    max_lng = -121

    query = '(node(%f,%f,%f,%f);<;);out meta;' % (min_lat, min_lng, max_lat, max_lng)
    out_file = 'data.osm'
    download(out_file, query)


if __name__ == '__main__':
    main()
