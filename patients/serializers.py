from rest_framework import serializers
from .models import *


class VariantSerializer(serializers.ModelSerializer):

	class Meta:
		model = Variant
		fields = '__all__'


##### Allele classes have to be serialized in VarianSerializer #####


class PhenotypicFeatureSerializer(serializers.ModelSerializer):

	class Meta:
		model = PhenotypicFeature
		fields = '__all__'


class ProcedureSerializer(serializers.ModelSerializer):

	class Meta:
		model = Procedure
		fields = '__all__'


class HtsFileSerializer(serializers.ModelSerializer):

	class Meta:
		model = HtsFile
		fields = '__all__'


class GeneSerializer(serializers.ModelSerializer):

	class Meta:
		model = Gene
		fields = '__all__'


class DiseaseSerializer(serializers.ModelSerializer):

	class Meta:
		model = Disease
		fields = '__all__'


class ResourceSerializer(serializers.ModelSerializer):

	class Meta:
		model = Resource
		fields = '__all__'


class UpdateSerializer(serializers.ModelSerializer):

	class Meta:
		model = Update
		fields = '__all__'


class ExternalReferenceSerializer(serializers.ModelSerializer):

	class Meta:
		model = ExternalReference
		fields = '__all__'


class MetaDataSerializer(serializers.ModelSerializer):

	class Meta:
		model = MetaData
		fields = '__all__'


class IndividualSerializer(serializers.ModelSerializer):

	class Meta:
		model = Individual
		fields = '__all__'


class BiosampleSerializer(serializers.ModelSerializer):

	class Meta:
		model = Biosample
		fields = '__all__'


class PhenopacketSerializer(serializers.ModelSerializer):

	class Meta:
		model = Phenopacket
		fields = '__all__'
