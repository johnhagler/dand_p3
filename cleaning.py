import re
import requests

ele_re = re.compile('((?:\d*\.)?\d+)(.*)')


def clean_elevation(node):
    if 'ele' in node:
        ele_str = node['ele']
        elevation = None
        try:
            elevation = float(ele_str)
        except:
            m = ele_re.match(ele_str)
            elevation = float(m.group(1))
            unit = m.group(2).strip().lower()

            if unit == 'm':
                pass
            elif unit == 'ft':
                elevation *= .3048

        if elevation is not None:
            node['ele'] = int(round(elevation, 0))


def get_elevation(pos):
    elevation = None
    url = 'http://elevation.mapzen.com/height?json={"shape":[{"lat":%s, "lon": %s}]}&api_key=elevation-xzsLksZ' \
          % (pos[0], pos[1])

    r = requests.get(url)
    if r.status_code == 200:
        elevation = r.json()['height'][0]

    return elevation


def is_mountain(node):
    return 'natural' in node and \
        (node['natural'] == 'peak' or node['natural'] == 'volcano')


def missing_elevation(node):
    return 'ele' not in node or node['ele'] is not None


def clean_missing_elevation(node):
    if is_mountain(node) and missing_elevation(node) and 'pos' in node:
        elevation = get_elevation(node['pos'])
        if elevation:
            node['ele'] = elevation


def is_water(node):
    return 'natural' in node and node['natural'] == 'water'


def missing_water(node):
    return 'water' not in node or node['water'] is not None


def clean_water_classification(node):
    if is_water(node) and missing_water(node) and 'name' in node:
        name = node['name'].lower()
        if 'lake' in name:
            node['water'] = 'lake'
        elif 'pond' in name:
            node['water'] = 'pond'
        elif 'hole' in name:
            node['water'] = 'hole'
