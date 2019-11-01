from chord_lib.schemas.chord import CHORD_DATA_USE_SCHEMA
from rest_framework import serializers, validators
from .models import *
from jsonschema import validate, ValidationError, Draft7Validator, FormatChecker
from chord_metadata_service.restapi.schemas import *
from chord_metadata_service.restapi.validators import JsonSchemaValidator
from chord_metadata_service.restapi.serializers import GenericSerializer


#############################################################
#                                                           #
#                  Metadata  Serializers                    #
#                                                           #
#############################################################

class ResourceSerializer(GenericSerializer):

	class Meta:
		model = Resource
		fields = '__all__'


class MetaDataSerializer(GenericSerializer):

	class Meta:
		model = MetaData
		fields = '__all__'

	def validate_updates(self, value):
		"""
		Check updates against schema.
		Timestamp must follow ISO8601 UTC standard
		e.g. 2018-06-10T10:59:06Z

		"""

		if isinstance(value, list):
			for item in value:
				validation = Draft7Validator(
					UPDATE_SCHEMA, format_checker=FormatChecker(formats=['date-time'])
					).is_valid(item)
				if not validation:
					raise serializers.ValidationError("Update is not valid")
		return value

	def validate_external_references(self, value):
		if isinstance(value, list):
			for item in value:
				validation = Draft7Validator(EXTERNAL_REFERENCE).is_valid(item)
				if not validation:
					raise serializers.ValidationError("Not valid JSON schema for this field.")
		return value


#############################################################
#                                                           #
#              Phenotypic Data  Serializers                 #
#                                                           #
#############################################################

class PhenotypicFeatureSerializer(GenericSerializer):
	_type = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)])
	severity = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
		allow_null=True, required=False)
	onset = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
		allow_null=True, required=False)
	evidence = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=EVIDENCE)],
		allow_null=True, required=False)

	def __init__(self, *args, **kwargs):
		exclude_when_nested = kwargs.pop('exclude_when_nested', None)
		super(PhenotypicFeatureSerializer, self).__init__(*args, **kwargs)

		if exclude_when_nested:
			for field_name in exclude_when_nested:
				self.fields.pop(field_name)
	
	class Meta:
		model = PhenotypicFeature
		fields = '__all__'
		# exclude = ['biosample']

	def validate_modifier(self, value):
		if isinstance(value, list):
			for item in value:
				validation = Draft7Validator(ONTOLOGY_CLASS).is_valid(item)
				if not validation:
					raise serializers.ValidationError("Not valid JSON schema for this field.")
		return value


class ProcedureSerializer(GenericSerializer):
	code = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)])
	body_site = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
		allow_null=True, required=False)

	class Meta:
		model = Procedure
		fields = '__all__'

	def validate(self, data):
		"""
		Check if body_site is not empty
		if not bind 'code' and 'body_site' to be unique together
		"""

		if data.get('body_site'):
			check = Procedure.objects.filter(
				code=data.get('code'), body_site=data.get('body_site')).exists()
			if check:
				raise serializers.ValidationError(
					"This procedure is already exists."
					)
		return data


class HtsFileSerializer(GenericSerializer):

	class Meta:
		model = HtsFile
		fields = '__all__'


class GeneSerializer(GenericSerializer):

	class Meta:
		model = Gene
		fields = '__all__'


class VariantSerializer(GenericSerializer):
	# allele_type = serializers.CharField()
	allele = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ALLELE_SCHEMA)])
	# allele = serializers.JSONField()
	zygosity = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
		allow_null=True, required=False)
	# zygosity = serializers.JSONField(required=False, allow_null=True)

	class Meta:
		model = Variant
		fields = '__all__'


class DiseaseSerializer(GenericSerializer):
	term = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)])

	class Meta:
		model = Disease
		fields = '__all__'

	def validate_tumor_stage(self, value):
		if isinstance(value, list):
			for item in value:
				validation = Draft7Validator(ONTOLOGY_CLASS).is_valid(item)
				if not validation:
					raise serializers.ValidationError(
						"Not valid JSON schema for this field."
						)
		return value


class BiosampleSerializer(GenericSerializer):
	sampled_tissue = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)])
	taxonomy = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
		allow_null=True, required=False)
	histological_diagnosis = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
		allow_null=True, required=False)
	tumor_progression = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
		allow_null=True, required=False)
	tumor_grade = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
		allow_null=True, required=False)
	phenotypic_features = PhenotypicFeatureSerializer(read_only=True,
		many=True, exclude_when_nested=['id', 'biosample'])

	class Meta:
		model = Biosample
		fields = '__all__'

	def validate_diagnostic_markers(self, value):
		if isinstance(value, list):
			for item in value:
				validation = Draft7Validator(ONTOLOGY_CLASS).is_valid(item)
				if not validation:
					raise serializers.ValidationError(
						"Not valid JSON schema for this field."
						)
		return value


class PhenopacketSerializer(GenericSerializer):
	phenotypic_features = PhenotypicFeatureSerializer(read_only=True,
		many=True, exclude_when_nested=['id', 'biosample'])

	class Meta:
		model = Phenopacket
		fields = '__all__'


#############################################################
#                                                           #
#                Interpretation Serializers                 #
#                                                           #
#############################################################

class GenomicInterpretationSerializer(GenericSerializer):

	class Meta:
		model = GenomicInterpretation
		fields = '__all__'


class DiagnosisSerializer(GenericSerializer):

	class Meta:
		model = Diagnosis
		fields = '__all__'


class InterpretationSerializer(GenericSerializer):

	class Meta:
		model = Interpretation
		fields = '__all__'


#############################################################
#                                                           #
#              Project Management  Serializers              #
#                                                           #
#############################################################

class ProjectSerializer(GenericSerializer):
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


class DatasetSerializer(GenericSerializer):
	# noinspection PyMethodMayBeStatic
	def validate_name(self, value):
		if len(value.strip()) < 3:
			raise serializers.ValidationError("Name must be at least 3 characters")
		return value.strip()

	class Meta:
		model = Dataset
		fields = '__all__'


class TableOwnershipSerializer(GenericSerializer):
	class Meta:
		model = TableOwnership
		fields = '__all__'
