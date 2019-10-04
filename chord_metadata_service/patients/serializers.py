from rest_framework import serializers, validators
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


class OntologySerializer(serializers.ModelSerializer):
	# this will create problems
	id = serializers.CharField(source='ontology_id')
	primary_key = serializers.CharField(source='id', read_only=True)

	class Meta:
		model = Ontology
		fields = ['id', 'label', 'primary_key']

	# def run_validators(self, value):
	# 	for validator in self.validators:
	# 		if isinstance(validator, validators.UniqueTogetherValidator):
	# 			self.validators.remove(validator)
	# 	super(OntologySerializer, self).run_validators(value)

	def create(self, validated_data):
		instance, _ = Ontology.objects.get_or_create(**validated_data)
		return instance


class VariantSerializer(serializers.ModelSerializer):
	#allele_type = serializers.CharField()
	allele = JSONField()
	zygosity = OntologySerializer()

	class Meta:
		model = Variant
		fields = ['id', 'allele_type', 'allele', 'zygosity']

	def validate_allele(self, value):
		""" Check that allele json data is valid """

		validation = Draft7Validator(ALLELE_SCHEMA).is_valid(value)
		if not validation:
			raise serializers.ValidationError("Allele is not valid")
		return value

	# TODO uncomment when update() added
	# def to_representation(self, obj):
	# 	""" Change 'allele_type' field name to allele type value. """

	# 	output = super().to_representation(obj)
	# 	output[obj.allele_type] = output.pop('allele')
	# 	return output

	def create(self, validated_data):
		zygosity_data = validated_data.pop('zygosity')
		ontology_model, _ = Ontology.objects.get_or_create(**zygosity_data)
		variant = Variant.objects.create(zygosity=ontology_model, **validated_data)
		return variant


class PhenotypicFeatureSerializer(serializers.ModelSerializer):
	#phenotype = JSONField(validators=[ontology_validator])
	type = OntologySerializer(source='_type')
	severity = OntologySerializer()
	modifier = OntologySerializer()
	onset = OntologySerializer()

	class Meta:
		model = PhenotypicFeature
		exclude = ['_type']
		#extra_kwargs = {'phenotype': {'required': True}}

	# def validate(self, data):
	# 	""" Validate all OntologyClass JSONFields against OntologyClass schema """

	# 	ontology_fields = ['_type', 'severity', 'onset', 'evidence']
	# 	errors = {}
	# 	for field in ontology_fields:
	# 		if data.get(field):
	# 			v = Draft7Validator(ONTOLOGY_CLASS)
	# 			validation = v.is_valid(data.get(field))
	# 			if not validation:
	# 				errors[field] = [str(error.message) for error in sorted(v.iter_errors(data.get(field)))]
	# 	if errors:
	# 		raise serializers.ValidationError(
	# 			errors)
	# 	else:
	# 		return data


class ProcedureSerializer(serializers.ModelSerializer):
	code = OntologySerializer()
	body_site = OntologySerializer()

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
	term = OntologySerializer()
	age_of_onset_ontology = OntologySerializer()
	tumor_stage = OntologySerializer()

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
	taxonomy = OntologySerializer()

	class Meta:
		model = Individual
		fields = '__all__'


class BiosampleSerializer(serializers.ModelSerializer):
	sampled_tissue = OntologySerializer()
	taxonomy = OntologySerializer()
	historical_diagnosis = OntologySerializer()
	tumor_progression = OntologySerializer()
	tumor_grade = OntologySerializer()
	diagnostic_markers = OntologySerializer()

	class Meta:
		model = Biosample
		fields = '__all__'


class PhenopacketSerializer(serializers.ModelSerializer):

	class Meta:
		model = Phenopacket
		fields = '__all__'


class GenomicInterpretationSerializer(serializers.ModelSerializer):

	class Meta:
		model = GenomicInterpretation
		fields = '__all__'


class DiagnosisSerializer(serializers.ModelSerializer):

	class Meta:
		model = Diagnosis
		fields = '__all__'


class InterpretationSerializer(serializers.ModelSerializer):

	class Meta:
		model = Interpretation
		fields = '__all__'
