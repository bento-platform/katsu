from chord_lib.schemas.chord import CHORD_DATA_USE_SCHEMA
from rest_framework import serializers
from .models import *
from jsonschema import Draft7Validator, FormatChecker
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
	type = serializers.JSONField(source='pftype',
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

	class Meta:
		model = PhenotypicFeature
		# fields = '__all__'
		exclude = ['pftype']

	# def to_representation(self, obj):
	# 	output = super().to_representation(obj)
	# 	output['type'] = output.pop('pftype')
	# 	return output

	# def to_internal_value(self, data):
	# 	if 'type' in data.keys():
	# 		data['pftype'] = data.pop('type')
	# 	return super(PhenotypicFeatureSerializer, self).to_internal_value(data=data)

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

	def create(self, validated_data):
		instance, _ = Procedure.objects.get_or_create(**validated_data)
		return instance

	# def validate(self, data):
	# 	"""
	# 	Check if body_site is not empty
	# 	if not bind 'code' and 'body_site' to be unique together
	# 	"""

	# 	if data.get('body_site'):
	# 		check = Procedure.objects.filter(
	# 			code=data.get('code'), body_site=data.get('body_site')).exists()
	# 		if check:
	# 			raise serializers.ValidationError(
	# 				"This procedure is already exists."
	# 				)
	# 	return data


class HtsFileSerializer(GenericSerializer):

	class Meta:
		model = HtsFile
		fields = '__all__'


class GeneSerializer(GenericSerializer):
	alternate_id = serializers.ListField(
		child=serializers.CharField(allow_blank=True),
		allow_empty=True, required=False)

	class Meta:
		model = Gene
		fields = '__all__'


class VariantSerializer(GenericSerializer):
	allele = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ALLELE_SCHEMA)])
	zygosity = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
		allow_null=True, required=False)

	class Meta:
		model = Variant
		fields = '__all__'

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
		return super(VariantSerializer, self).to_internal_value(data=data)


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
	# procedure = ProcedureSerializer(exclude_when_nested=['id'])
	procedure = ProcedureSerializer()

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

	def create(self, validated_data):
		procedure_data = validated_data.pop('procedure')
		procedure_model, _ = Procedure.objects.get_or_create(**procedure_data)
		biosample = Biosample.objects.create(procedure=procedure_model, **validated_data)
		return biosample

	def update(self, instance, validated_data):
		instance.sampled_tissue = validated_data.get('sampled_tissue',
			instance.sampled_tissue)
		instance.taxonomy = validated_data.get('taxonomy',
			instance.taxonomy)
		instance.histological_diagnosis = validated_data.get('histological_diagnosis',
			instance.histological_diagnosis)
		instance.tumor_progression = validated_data.get('tumor_progression',
			instance.tumor_progression)
		instance.tumor_grade = validated_data.get('tumor_grade',
			instance.tumor_grade)
		instance.diagnostic_markers = validated_data.get('diagnostic_markers',
			instance.diagnostic_markers)
		instance.save()
		procedure_data = validated_data.pop('procedure', None)
		if procedure_data:
			instance.procedure, _ = Procedure.objects.get_or_create(**procedure_data)
		instance.save()
		return instance


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
