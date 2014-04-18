import argparse
import json
import os
import requests
import sys

BING_API_KEY = os.environ.get('BING_API_KEY', '')
BING_GEOCODER_URL = 'http://dev.virtualearth.net/REST/v1/Locations/'
# User location is set to Chicago, since this is an Illinois-centric (and particularly
# Chicago-centric) tool
BING_USER_LOCATION = '41.8903465270996,-87.6233291625977'
BOUNDARY_BASE_URL = 'http://boundaries.tribapps.com/1.0/boundary/%s'

# Searchable fields from the Boundary Service
BOUNDARY_META = [
    'census-places', 'census-tracts', 'community-areas',
    'cook-county-board-of-commissioners-districts', 'cook-county-board-of-review-districts',
    'cook-county-park-tax-districts', 'cook-judicial-subcircuits', 'counties',
    'county-subdivisions', 'judicial-circuits', 'judicial-districts', 'neighborhoods',
    'planning-districts', 'planning-regions', 'police-areas', '2010-police-areas', 'police-beats',
    '2010-police-beats', 'police-districts', '2010-police-districts']


def get_boundaries_for(lat, lng, boundary):
    """
    Given geo coordinates and a boundary type, return what boundary service
    believes to be the relevant containing geometry. For instance, police
    district encompassing a given point.
    """
    query_str = '?format=json&contains=%s,%s&sets=%s' % (lat, lng, boundary)
    r = requests.get(BOUNDARY_BASE_URL % query_str)
    return json.loads(r.text)


def geocode_address(address):
    """
    Attempt to search for matching addresses for address, using the Bing geocoder directly.
    """
    results = []
    query = {
        'query': address,
        'key': BING_API_KEY,
        'maxResults': 10,
        'userLocation': BING_USER_LOCATION
    }
    response = requests.get(BING_GEOCODER_URL, params=query)
    try:
        geocodes = response.json()["resourceSets"].pop()["resources"]
    except IndexError:
        return []
    for match in geocodes:
        # This is an Illinois-centric tool, so if the address isn't in IL we didn't get what we need
        if (not match['address'].get('adminDistrict')
                or match['address']['adminDistrict'] != 'IL'):
            continue
        try:
            results.append({
                'location': match['name'],
                'confidence': match['confidence'],
                'matchCodes': match['matchCodes'],
                'locality': match['address']['locality'],
                'lat': match['point']['coordinates'][0],
                'lng': match['point']['coordinates'][1]
            })
        except KeyError:
            # We need all of those fields to be present in order to be confident we got a valid
            # result
            continue
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get boundary information for addresses')
    parser.add_argument('address', metavar='address', type=str, help='Address to look up')
    parser.add_argument(
        'boundary',
        metavar='boundary',
        type=str,
        help='Boundary to return; permitted values include: %s' % ','.join(BOUNDARY_META)
    )
    args = parser.parse_args()
    if args.boundary not in BOUNDARY_META:
        print 'Error: need to specify boundary from %s' % ','.join(BOUNDARY_META)
        sys.exit(0)
    if not BING_API_KEY:
        print 'Error: you need to set the BING_API_KEY environment variable'
        sys.exit(0)
    addr = geocode_address(args.address)
    if not addr:
        print 'Error: unable to geocode address %s' % args.address
        sys.exit(0)
    boundary = get_boundaries_for(addr[0]['lat'], addr[0]['lng'], args.boundary)
    if not boundary or not boundary['objects']:
        print 'Error: unable to get boundary %s for address %s' % (args.boundary, args.address)
        sys.exit(0)
    print boundary['objects'][0]['name']
