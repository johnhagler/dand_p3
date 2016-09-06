#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import re
import codecs
import json
import cleaning

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = ["version", "changeset", "timestamp", "user", "uid"]


def extract_info(node, attrib):

    if 'id' in attrib:
        node['id'] = attrib['id']
    if 'visible' in attrib:
        node['visible'] = attrib['visible']


def extract_created(node, attrib):

    created = dict()
    for key in attrib.keys():
        if key in CREATED:
            created[key] = attrib[key]

    if len(created.keys()) > 0:
        node['created'] = created


def extract_pos(node, attrib):

    if 'lat' in attrib and 'lon' in attrib:
        lat = float(attrib['lat'])
        lon = float(attrib['lon'])
        node['pos'] = [lat, lon]


def valid_key(tag_key):
    if problemchars.match(tag_key):
        return False
    else:
        return True


def shape_tags(node, tags):

    for tag in tags:
        key = tag.attrib['k']
        value = tag.attrib['v']

        if lower.match(key):
            node[key] = value
        elif lower_colon.match(key):
            split = key.split(':')

            prefix = split[0]
            subkey = split[1]

            # convert addr => address
            if prefix == 'addr':
                prefix = 'address'

            if prefix not in node:
                node[prefix] = dict()

            if type(node[prefix]) is dict:
                node[prefix][subkey] = value
            elif type(node[prefix]) is str:
                node[key] = value


def shape_node_refs(node, element):

    refs = list()
    for nd in element.iter('nd'):
        refs.append(nd.attrib['ref'])

    if len(refs) > 0:
        node['node_refs'] = refs


def shape_element(element):
    node = dict()
    if element.tag == "node" or element.tag == "way":

        a = element.attrib
        extract_info(node, a)
        extract_created(node, a)
        extract_pos(node, a)

        shape_tags(node, element.iter('tag'))

        shape_node_refs(node, element)

        cleaning.clean_elevation(node)
        cleaning.clean_missing_elevation(node)
        cleaning.clean_water_classification(node)

        node['type'] = element.tag

        return node
    else:
        return None


def process_map(file_in, pretty=False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in, events=('start',)):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2) + "\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


def main():

    process_map('data.osm', False)


if __name__ == "__main__":
    main()