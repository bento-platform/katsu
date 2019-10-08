from chord_lib.schemas.chord import CHORD_DATA_USE_SCHEMA
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
	#id = serializers.CharField(source='ontology_id')

	class Meta:
		model = Ontology
		fields = ['ontology_id', 'label', 'id']

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
	zygosity = OntologySerializer(required=False)

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

	def to_internal_value(self, data):
		""" When writing back to db change field name back to 'allele'. """

		if not 'allele' in data.keys():
			allele_type = data.get('allele_type')
			data['allele'] = data.pop(allele_type)
		return data

	def create(self, validated_data):
		if 'zygosity' in validated_data.keys():
			zygosity_data = validated_data.pop('zygosity')
			ontology_model, _ = Ontology.objects.get_or_create(**zygosity_data)
			variant = Variant.objects.create(zygosity=ontology_model, **validated_data)
		variant = Variant.objects.create(**validated_data)
		return variant

	def update(self, instance, validated_data):
		instance.allele = validated_data.get('allele', instance.allele)
		instance.allele_type = validated_data.get('allele_type', instance.allele_type)
		instance.save()
		zygosity_data = validated_data.pop('zygosity', None)
		if zygosity_data:
			instance.zygosity, _ = Ontology.objects.get_or_create(**zygosity_data)
		return instance


class PhenotypicFeatureSerializer(serializers.ModelSerializer):
	#phenotype = JSONField(validators=[ontology_validator])
	type = OntologySerializer(source='_type')
	severity = OntologySerializer()
	modifier = OntologySerializer(required=False, many=True)
	onset = OntologySerializer()

	class Meta:
		model = PhenotypicFeature
		exclude = ['_type']
		#extra_kwargs = {'phenotype': {'required': True}}

	def create(self, validated_data):
		type_data = validated_data.pop('_type')
		severity = validated_data.pop('severity')
		onset = validated_data.pop('onset')
		# M2M field
		modifier = validated_data.pop('modifier', [])
		# TODO refactor
		type_ontology, _ = Ontology.objects.get_or_create(**type_data)
		severity_ontology, _ = Ontology.objects.get_or_create(**severity)
		onset_ntology, _ = Ontology.objects.get_or_create(**onset)

		phenotypic_feature = PhenotypicFeature.objects.create(
			 _type=type_ontology,
			severity=severity_ontology, onset=onset_ntology,
			**validated_data
			)
		# for M2M
		for mod in modifier:
			modifier_ontology, _ = Ontology.objects.get_or_create(**mod)
			phenotypic_feature.modifier.add(modifier_ontology)

		return phenotypic_feature

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


class ProjectSerializer(serializers.ModelSerializer):
	# noinspection PyMethodMayBeStatic
	def validate_data_use(self, value):
		validation = Draft7Validator(CHORD_DATA_USE_SCHEMA).is_valid(value)
		if not validation:
			raise serializers.ValidationError("Data use is not valid")
		return value

	# noinspection PyMethodMayBeStatic
	def validate_name(self, value):
		if len(value.strip()) < 3:
			raise serializers.ValidationError("Name must be at least 3 characters")
		return value.strip()

	class Meta:
		model = Project
		fields = '__all__'


class DatasetSerializer(serializers.ModelSerializer):
	# noinspection PyMethodMayBeStatic
	def validate_name(self, value):
		if len(value.strip()) < 3:
			raise serializers.ValidationError("Name must be at least 3 characters")
		return value.strip()

	class Meta:
		model = Dataset
		fields = '__all__'
