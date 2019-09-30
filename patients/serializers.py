from rest_framework import serializers
from .models import *
from jsonschema import validate, ValidationError, Draft7Validator
from .allele import ALLELE_SCHEMA


##### Allele classes have to be serialized in VarianSerializer #####
# TODO move
ONTOLOGY_CLASS = {
"$schema": "http://json-schema.org/draft-07/schema#",
	"$id": "todo",
	"title": "Ontology class schema",
	"description": "todo",
	"type": "object",
	"properties": {
		"id": {"type": "string", "description": "CURIE style identifier"},
		"label": {"type": "string", "description": "Human-readable class name"}
	},
	"required": ["id", "label"]
	
}

class VariantSerializer(serializers.ModelSerializer):
	#allele_type = serializers.CharField()
	allele = JSONField()
	zygosity = JSONField()

	class Meta:
		model = Variant
		fields = ['id', 'allele_type', 'allele', 'zygosity']

	def validate_allele(self, value):
		""" Check that allele json data is valid """

		validation = Draft7Validator(ALLELE_SCHEMA).is_valid(value)
		if not validation:
			raise serializers.ValidationError("Allele is not valid")
		return value

	def to_representation(self, obj):
		""" Change 'allele_type' field name to allele type value. """

		output = super().to_representation(obj)
		output[obj.allele_type] = output.pop('allele')
		return output


class PhenotypicFeatureSerializer(serializers.ModelSerializer):

	class Meta:
		model = PhenotypicFeature
		fields = '__all__'


	def validate_phenotype(self, value):
		validation = Draft7Validator(ONTOLOGY_CLASS).is_valid(value)
		if not validation:
			raise serializers.ValidationError("Phenotype must have id and label of an ontology class.")
		return value


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
