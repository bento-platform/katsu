from rest_framework import serializers
from chord_metadata_service.restapi.serializers import GenericSerializer
from .models import GeoLocation

__all__ = [
    "GeoLocationPropertiesSerializer",
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


class GeoLocationPropertiesSerializer(serializers.Serializer):
    label: serializers.CharField(required=False, allow_blank=True)
    city: serializers.CharField(required=False, allow_blank=True)
    country: serializers.CharField(required=False, allow_blank=True)
    ISO3166alpha3: serializers.CharField(required=False, allow_blank=True)
    precision: serializers.CharField(required=False, allow_blank=True)


class GeoLocationSerializer(GenericSerializer):

    type = serializers.CharField(validators=[type_is_feature])
    geometry = PointSerializer()
    properties = GeoLocationPropertiesSerializer()

    def to_representation(self, instance: GeoLocation):
        """
        Completely custom override of to_representation to generate proper nested GeoJSON-compatible dictionary.
        """

        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": instance.point.coords,
            },
            "properties": {
                k: getattr(instance, k)
                for k in ("label", "city", "country", "ISO3166alpha3", "precision")
                if getattr(instance, k)
            },
        }

    class Meta:
        model = GeoLocation
        fields = "__all__"
