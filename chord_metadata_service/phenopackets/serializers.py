from chord_lib.schemas.chord import CHORD_DATA_USE_SCHEMA
from rest_framework import serializers, validators
from .models import *
from jsonschema import validate, ValidationError, Draft7Validator, FormatChecker
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS, ALLELE_SCHEMA
from chord_metadata_service.restapi.validators import JsonSchemaValidator


# class OntologySerializer(serializers.ModelSerializer):
# 	# this will create problems
# 	#id = serializers.CharField(source='ontology_id')

# 	class Meta:
# 		model = Ontology
# 		fields = ['ontology_id', 'label', 'id']

# 	# def run_validators(self, value):
# 	# 	for validator in self.validators:
# 	# 		if isinstance(validator, validators.UniqueTogetherValidator):
# 	# 			self.validators.remove(validator)
# 	# 	super(OntologySerializer, self).run_validators(value)

# 	def create(self, validated_data):
# 		instance, _ = Ontology.objects.get_or_create(**validated_data)
# 		return instance

class ResourceSerializer(serializers.ModelSerializer):

	class Meta:
		model = Resource
		fields = '__all__'


# class ExternalReferenceSerializer(serializers.ModelSerializer):

# 	class Meta:
# 		model = ExternalReference
# 		fields = '__all__'


class MetaDataSerializer(serializers.ModelSerializer):

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


class PhenotypicFeatureSerializer(serializers.ModelSerializer):
	_type = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)])
	severity = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
		allow_null=True)
	onset = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
		allow_null=True)
	
	class Meta:
		model = PhenotypicFeature
		fields = '__all__'

	def validate_modifier(self, value):
		if isinstance(value, list):
			for item in value:
				validation = Draft7Validator(ONTOLOGY_CLASS).is_valid(item)
				if not validation:
					raise serializers.ValidationError("Not valid JSON schema for this field.")
		return value

	# def create(self, validated_data):
	# 	modifiers = []
	# 	if 'modifier' in validated_data.keys():
	# 		modifier = validated_data.pop('modifier', None)
	# 		if isinstance(modifier, list):
	# 			for mod in modifier:
	# 				modifier_ontology, _ = Ontology.objects.get_or_create(**mod)
	# 				modifiers.append(modifier_ontology)
	# 	all_ontologies = {}
	# 	ontology_fields = ['_type', 'severity', 'onset']
	# 	for field in ontology_fields:
	# 		field_data = validated_data.pop(field, None)
	# 		if field_data:
	# 			field_ontology, _ = Ontology.objects.get_or_create(**field_data)
	# 			all_ontologies[field] = field_ontology

	# 	phenotypic_feature = PhenotypicFeature.objects.create(_type=all_ontologies.get('_type', None),
	# 		severity=all_ontologies.get('severity', None), onset=all_ontologies.get('onset', None),
	# 		**validated_data
	# 		)
	# 	# add ManyToMany related objects
	# 	phenotypic_feature.modifier.add(*set(modifiers))
	# 	return phenotypic_feature

	# def update(self, instance, validated_data):
	# 	instance.description = validated_data.get('description', instance.description)
	# 	instance.negated = validated_data.get('negated', instance.negated)
	# 	instance.evidence = validated_data.get('evidence', instance.evidence)
	# 	instance.save()
	# 	ontology_fields = ['_type', 'severity', 'onset']
	# 	# TODO if field was removed entirely, clean this field in db too
	# 	for field in ontology_fields:
	# 		if field in validated_data.keys():
	# 			field_data = validated_data.pop(field, None)
	# 			# if field_data:
	# 			instance.field, _ = Ontology.objects.get_or_create(**field_data)
	# 			instance.save()
	# 	modifiers = []
	# 	if 'modifier' in validated_data.keys():
	# 		modifier = validated_data.pop('modifier', None)
	# 		for mod in modifier:
	# 			modifier_ontology, _ = Ontology.objects.get_or_create(**mod)
	# 			modifiers.append(modifier_ontology)
	# 	instance.modifier.clear()
	# 	instance.modifier.add(*set(modifiers))
	# 	instance.save()
	# 	return instance


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
	code = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)])
	body_site = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
		allow_null=True)

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


class VariantSerializer(serializers.ModelSerializer):
	# allele_type = serializers.CharField()
	allele = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ALLELE_SCHEMA)])
	# allele = serializers.JSONField()
	zygosity = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
		allow_null=True)
	# zygosity = serializers.JSONField(required=False, allow_null=True)

	class Meta:
		model = Variant
		fields = '__all__'


	# def to_representation(self, obj):
	# 	""" Change 'allele_type' field name to allele type value. """

	# 	output = super().to_representation(obj)
	# 	output[obj.allele_type] = output.pop('allele')
	# 	return output

	# def to_internal_value(self, data):
	# 	""" When writing back to db change field name back to 'allele'. """

	# 	if not 'allele' in data.keys():
	# 		allele_type = data.get('allele_type')
	# 		data['allele'] = data.pop(allele_type)
	# 	return data

	# def validate_allele(self, value):
	# 	""" Check that allele json data is valid """

	# 	validation = Draft7Validator(ALLELE_SCHEMA).is_valid(value)
	# 	if not validation:
	# 		raise serializers.ValidationError("Allele is not valid")
	# 	return value

	# def validate_zygosity(self, value):
	# 	""" Check that zygosity json data is valid """

	# 	validation = Draft7Validator(ONTOLOGY_CLASS).is_valid(value)
	# 	if not validation:
	# 		raise serializers.ValidationError("Zygosity is not valid")
	# 	return value


	# def create(self, validated_data):
	# 	if 'zygosity' in validated_data.keys():
	# 		zygosity_data = validated_data.pop('zygosity')
	# 		ontology_model, _ = Ontology.objects.get_or_create(**zygosity_data)
	# 		variant = Variant.objects.create(zygosity=ontology_model, **validated_data)
	# 	variant = Variant.objects.create(**validated_data)
	# 	return variant

	# def update(self, instance, validated_data):
	# 	instance.allele = validated_data.get('allele', instance.allele)
	# 	instance.allele_type = validated_data.get('allele_type', instance.allele_type)
	# 	instance.save()
	# 	zygosity_data = validated_data.pop('zygosity', None)
	# 	if zygosity_data:
	# 		instance.zygosity, _ = Ontology.objects.get_or_create(**zygosity_data)
	# 		# TODO Save instance?
	# 	return instance


class DiseaseSerializer(serializers.ModelSerializer):
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


class BiosampleSerializer(serializers.ModelSerializer):
	sampled_tissue = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)])
	taxonomy = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
		allow_null=True)
	histological_diagnosis = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
		allow_null=True)
	tumor_progression = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
		allow_null=True)
	tumor_grade = serializers.JSONField(
		validators=[JsonSchemaValidator(schema=ONTOLOGY_CLASS)],
		allow_null=True)

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


class TableOwnershipSerializer(serializers.ModelSerializer):
	class Meta:
		model = TableOwnership
		fields = '__all__'
