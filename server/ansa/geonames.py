
from superdesk.places.places_autocomplete import geonames_request, format_geoname_item


def get_place_by_id(geoname_id):
    return format_geoname_item(
        geonames_request('getJSON', [('geonameId', geoname_id), ('lang', 'it')])
    )
