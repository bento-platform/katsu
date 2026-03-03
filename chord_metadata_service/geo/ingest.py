from django.contrib.gis.geos import Point
from . import constants as gc, models as gm, serializers as gs


__all__ = [
    "get_or_create_geo_location",
]


def get_or_create_geo_location(geoloc_json: dict) -> gm.GeoLocation:
    """
    Given a GeoJSON-based representation of a location, return an existing (re-used) or new GeoLocation object, now
    saved in the database. The provided dictionary should be compatible with the Katsu GeoLocation format, based on the
    GA4GH schema block / Progenetix GeoLocation schema< https://schemablocks.org/schema_pages/Progenetix/GeoLocation/>.
    """
    gs.GeoLocationSerializer(data=geoloc_json).is_valid(raise_exception=True)
    geoloc_json_props = geoloc_json.get("properties", {})
    geoloc, _ = gm.GeoLocation.objects.get_or_create(
        # GeoJSON uses WGS 84 (SRID: 4326); https://www.rfc-editor.org/rfc/rfc7946#page-12
        point=Point(geoloc_json["geometry"]["coordinates"], srid=4326),
        **{
            gc.MODEL_PREDEF_PROPS_TO_ATTRS[gk]: gv
            for gk, gv in geoloc_json_props.items()
            if gk in gc.MODEL_PREDEF_PROPS_TO_ATTRS
        },
        extra_properties={gk: gv for gk, gv in geoloc_json_props.items() if gk not in gc.MODEL_PREDEF_PROPS_TO_ATTRS},
    )
    return geoloc
