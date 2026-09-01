from rest_framework import serializers

from .constants import MODEL_ATTRS_TO_PREDEF_PROPS
from .models import GeoLocation

__all__ = [
    "GeoLocationSerializer",
]


def type_is_feature(value):
    if value != "Feature":
        raise serializers.ValidationError('GeoLocation type must be "Feature"')


def type_is_point(value):
    if value != "Point":
        raise serializers.ValidationError('GeoLocation geometry type must be "Point"')


class PointSerializer(serializers.Serializer):
    type = serializers.CharField(validators=[type_is_point])
    coordinates = serializers.ListSerializer(
        child=serializers.FloatField(), allow_empty=False, min_length=2, max_length=3
    )


GEO_LOCATION_PREDEF_ATTRS = ("label", "city", "country", "iso_a3_code", "precision")


class GeoLocationSerializer(serializers.Serializer):
    type = serializers.CharField(validators=[type_is_feature])
    geometry = PointSerializer()
    properties = serializers.DictField(required=False, write_only=True)

    def to_representation(self, instance: GeoLocation):
        """
        Completely custom override of to_representation to generate proper nested GeoJSON-compatible dictionary.
        """

        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": list(instance.point.coords),
            },
            "properties": {
                **({k: v for k, v in instance.extra_properties.items() if k not in GEO_LOCATION_PREDEF_ATTRS}),
                **(
                    {
                        MODEL_ATTRS_TO_PREDEF_PROPS[k]: getattr(instance, k)
                        for k in GEO_LOCATION_PREDEF_ATTRS
                        if getattr(instance, k)
                    }
                ),
            },
        }
