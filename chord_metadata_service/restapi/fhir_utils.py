from fhirclient.models.fhirdate import FHIRDate
from chord_metadata_service.restapi.ga4gh_fhir_profiles import GA4GH_FHIR_PROFILES
from fhirclient.models import (observation as obs, patient as p, extension, age, coding as c,
							   codeableconcept, specimen as s, identifier as fhir_indentifier,
							   annotation as a, range, quantity, fhirreference
							   )


# Utils for converting data between formats

# TODO move to a separate file
def camel_case_field_names(string):
	""" Function to convert snake_case field names to camelCase """

	if '_' in string:
		splitted = string.split('_')
		capitilized = []
		capitilized.append(splitted[0])
		for each in splitted[1:]:
			capitilized.append(each.title())
		return ''.join(capitilized)
	return string


def transform_keys(obj):
	"""
	This function is needed for validation against DATS schemas that use camelCase.
	Iterates over a dict and  changes all keys in nested objects to cameCase.
	"""
	if isinstance(obj, dict):
		transformed_obj = {}
		for key, value in obj.items():
			if isinstance(value, dict):
				value = transform_keys(value)
			transformed_obj[camel_case_field_names(key)] = value
		return transformed_obj


def fhir_patient(obj):
	patient = p.Patient()
	patient.id = obj.get('id', None)
	patient.birthDate = FHIRDate(obj.get('date_of_birth', None))
	patient.gender = obj.get('sex', None)
	patient.active = obj.get('active', None)
	patient.deceasedBoolean = obj.get('deceased', None)
	patient.extension = list()
	# age
	age_extension = extension.Extension()
	# TODO move phenopackets-fhir mappings in a separate file
	age_extension.url = GA4GH_FHIR_PROFILES['individual-age']
	age_extension.valueAge = age.Age()
	age_extension.valueAge.unit = obj.get('age', None).get('age', None)
	patient.extension.append(age_extension)
	# karyotypic_sex
	karyotypic_sex_extension = extension.Extension()
	karyotypic_sex_extension.url = GA4GH_FHIR_PROFILES['individual-karyotypic-sex']['url']
	karyotypic_sex_extension.valueCodeableConcept = codeableconcept.CodeableConcept()
	karyotypic_sex_extension.valueCodeableConcept.coding = list()
	coding = c.Coding()
	coding.display = obj.get('karyotypic_sex', None)
	coding.code = obj.get('karyotypic_sex', None)
	coding.system = GA4GH_FHIR_PROFILES['individual-karyotypic-sex']['coding_system']
	karyotypic_sex_extension.valueCodeableConcept.coding.append(coding)
	patient.extension.append(karyotypic_sex_extension)
	# taxonomy
	taxonomy_extension = extension.Extension()
	taxonomy_extension.url = GA4GH_FHIR_PROFILES['individual-taxonomy']
	taxonomy_extension.valueCodeableConcept = codeableconcept.CodeableConcept()
	taxonomy_extension.valueCodeableConcept.coding = list()
	coding = c.Coding()
	coding.display = obj.get('taxonomy', None).get('label', None)
	coding.code = obj.get('taxonomy', None).get('id', None)
	taxonomy_extension.valueCodeableConcept.coding.append(coding)
	patient.extension.append(taxonomy_extension)
	return patient.as_json()


def individual_to_fhir(obj):
	""" Transform individual data to Patient FHIR record. """

	fhir_record = {}
	fhir_record['resourceType'] = 'Patient'
	# mapping for basic Patient attributes
	mapping = {
	'id': 'identifier',
	'date_of_birth': 'birthDate',
	'sex': 'gender',
	'active': 'active',
	'deceased': 'deceased',
	'race': 'race',
	'ethnicity': 'ethnicity'
	}
	for field in mapping.keys():
		if field in obj.keys():
			fhir_record[mapping.get(field)] = obj.get(field, None)
	# mapping for biosamples assosiated with this patient
	if 'biosamples' in obj.keys():
		fhir_record['biosamples'] = []
		for sample in obj.get('biosamples', None):
			biosample_record = biosample_to_fhir(sample)
			fhir_record['biosamples'].append(biosample_record)
	return fhir_record


def fhir_coding(obj, value=None):
	""" Generic function to convert to FHIR coding element. """

	coding = {}
	if value:
		coding['code'] = obj.get(value).get('id', None)
		coding['display'] = obj.get(value).get('label', None)
	else:
		coding['code'] = obj.get('id', None)
		coding['display'] = obj.get('label', None)
	return coding


def procedure_to_fhir(obj):
	""" Convert procedure to FHIR Procedure. """

	procedure = {}
	procedure['resourceType'] = 'Procedure'
	if 'id' in obj.keys():
		procedure['identifier'] = obj.get('id', None)
	procedure['code'] = {}
	procedure['code']['coding'] = []
	coding = fhir_coding(obj, 'code')
	procedure['code']['coding'].append(coding)
	if obj.get('body_site'):
		procedure['bodySite'] = {}
		procedure['bodySite']['coding'] = []
		body_site_coding = fhir_coding(obj, 'body_site')
		procedure['bodySite']['coding'].append(body_site_coding)
	return procedure

def codeable_concepts_fields(field_list, obj):
	concept_extensions = []
	for field in field_list:
		if field in obj.keys():
			codeable_concepts_extension = extension.Extension()
			codeable_concepts_extension.url = GA4GH_FHIR_PROFILES[field]
			codeable_concepts_extension.valueCodeableConcept = fhir_codeable_concept(obj[field])
			concept_extensions.append(codeable_concepts_extension)
	return concept_extensions
		

def fhir_observation(obj):
	observation = obs.Observation()
	if 'description' in obj.keys():
		observation.note = []
		annotation = a.Annotation()
		annotation.text = obj.get('description', None)
		observation.note.append(annotation)
	observation.code = fhir_codeable_concept(obj['type'])
	# required by FHIR specs but omitted by phenopackets, for now set for unknown
	observation.status = 'unknown'
	if 'negated' in obj.keys():
		observation.interpretation = fhir_codeable_concept(
			{"label": "Positive", "id": "POS"}
		)
	else:
		observation.interpretation = fhir_codeable_concept(
			{"label": "Negative", "id": "NEG"}
		)
	observation.extension = []
	concept_extensions = codeable_concepts_fields(['severity', 'modifier', 'onset'], obj)
	for c in concept_extensions:
		observation.extension.append(c)

	return observation.as_json()


def phenotypic_feature_to_fhir(obj):
	""" Convert phenotypic feature to FHIR Observation. """
	feature_record = {}
	feature_record['resourceType'] = 'Observation'
	if 'id' in obj.keys():
		feature_record['identifier'] = obj.get('id', None)
	if 'description' in obj.keys():
		feature_record['note'] = obj.get('description', None)
	if 'type' in obj.keys():
		feature_record['code'] = {}
		feature_record['code']['coding'] = []
		ftype = fhir_coding(obj, 'type')
		feature_record['code']['coding'].append(ftype)
	if 'onset' in obj.keys():
		feature_record['onsetAge'] = {}
		feature_record['onsetAge']['value'] = obj.get('onset').get('label', None)
		feature_record['onsetAge']['code'] = obj.get('onset').get('id', None)
	if 'modifier' in obj.keys():
		feature_record['modifier'] = {}
		# TODO store all profile references in separate dict, should be treated as a context
		feature_record['modifier']['url'] = 'http://ga4gh.org/fhir/phenopackets/StructureDefinition/phenotypic-feature-modifier'
		feature_record['modifier']['coding'] = []
		for item in obj.get('modifier'):
			mod = {}
			mod['code'] = item.get('id')
			mod['display'] = item.get('label')
			feature_record['modifier']['coding'].append(mod)
	if 'evidence' in obj.keys():
		evidence = obj.get('evidence')
		feature_record['evidence'] = []
		evidence_code = {}
		evidence_code['code'] = []
		code = {}
		code['coding'] = []
		coding = fhir_coding(evidence, 'evidence_code')
		code['coding'].append(coding)
		evidence_code['code'].append(code)
		feature_record['evidence'].append(evidence_code)
		if 'reference' in evidence.keys():
			evidence_detail = {}
			evidence_detail['detail'] = []
			detail = {}
			detail['reference'] = evidence.get('reference').get('id')
			detail['display'] = evidence.get('reference').get('description', None)
			evidence_detail['detail'].append(detail)
			feature_record['evidence'].append(evidence_detail)
	return feature_record


def fhir_specimen(obj):
	specimen = s.Specimen()
	specimen.identifier = []
	# id
	identifier = fhir_indentifier.Identifier()
	identifier.value = obj.get('id', None)
	specimen.identifier.append(identifier)
	# individual - subject property in FHIR is mandatory for a specimen
	specimen.subject = fhirreference.FHIRReference()
	specimen.subject.reference = obj.get('individual', 'unknown')
	# sampled_tissue
	specimen.type = codeableconcept.CodeableConcept()
	specimen.type.coding = []
	coding = c.Coding()
	coding.code = obj.get('sampled_tissue', None).get('id', None)
	coding.display = obj.get('sampled_tissue', None).get('label', None)
	specimen.type.coding.append(coding)
	# description
	if 'description' in obj.keys():
		specimen.note = []
		annotation = a.Annotation()
		annotation.text = obj.get('description', None)
		specimen.note.append(annotation)
	# procedure
	specimen.collection = s.SpecimenCollection()
	specimen.collection.method = fhir_codeable_concept(obj['procedure']['code'])
	if 'body_site' in obj['procedure'].keys():
		specimen.collection.bodySite = fhir_codeable_concept(obj['procedure']['body_site'])
	# Note on taxonomy from phenopackets specs:
	# Individuals already contain a taxonomy attribute so this attribute is not needed.
	# extensions
	specimen.extension = []
	# individual_age_at_collection
	if 'individual_age_at_collection' in obj.keys():
		ind_age_at_collection_extension = extension.Extension()
		ind_age_at_collection_extension.url = GA4GH_FHIR_PROFILES['biosample-individual-age-at-collection']
		if isinstance(obj['individual_age_at_collection']['age'], dict):
			ind_age_at_collection_extension.valueRange = range.Range()
			ind_age_at_collection_extension.valueRange.low = quantity.Quantity()
			ind_age_at_collection_extension.valueRange.low.unit = obj['individual_age_at_collection']['age']\
				['start']['age']
			ind_age_at_collection_extension.valueRange.high = quantity.Quantity()
			ind_age_at_collection_extension.valueRange.high.unit = obj['individual_age_at_collection']['age']\
				['end']['age']
			specimen.extension.append(ind_age_at_collection_extension)
		else:
			ind_age_at_collection_extension.valueAge = age.Age()
			ind_age_at_collection_extension.valueAge.unit = obj['individual_age_at_collection']['age']
			specimen.extension.append(ind_age_at_collection_extension)
	codeable_concepts_fields = [
		'histological_diagnosis', 'tumor_progression',
		'tumor_grade', 'diagnostic_markers'
	]
	for field in codeable_concepts_fields:
		if field in obj.keys():
			codeable_concepts_extension = extension.Extension()
			codeable_concepts_extension.url = GA4GH_FHIR_PROFILES[field]
			codeable_concepts_extension.valueCodeableConcept = fhir_codeable_concept(obj[field])
			specimen.extension.append(codeable_concepts_extension)
	if 'is_control_sample' in obj.keys():
		control_extension = extension.Extension()
		control_extension.url = GA4GH_FHIR_PROFILES['is_control_sample']
		control_extension.valueBoolean = obj['is_control_sample']
		specimen.extension.append(control_extension)
	# TODO 2m extensions - references
	return specimen.as_json()


def fhir_coding_util(obj):
	coding = c.Coding()
	coding.display = obj['label']
	coding.code = obj['id']
	return  coding


def fhir_codeable_concept(obj):
	codeable_concept = codeableconcept.CodeableConcept()
	codeable_concept.coding = []
	if isinstance(obj, list):
		for item in obj:
			coding = fhir_coding_util(item)
			codeable_concept.coding.append(coding)
	else:
		coding = fhir_coding_util(obj)
		codeable_concept.coding.append(coding)
	return codeable_concept


def biosample_to_fhir(obj):
	""" Convert biosample to FHIR Specimen. """

	biosample_record = {}
	biosample_record['resourceType'] = 'Specimen'
	biosample_record['identifier'] = obj.get('id', None)
	biosample_record['parent'] = {}
	biosample_record['parent']['reference'] = {}
	biosample_record['parent']['reference']['reference'] = obj.get('sampled_tissue').get('id', None)
	biosample_record['parent']['reference']['display'] = obj.get('sampled_tissue').get('label', None)
	# mapping for phenotypic_features related to each biosample
	if 'phenotypic_features' in obj.keys():
		biosample_record['phenotypicFeatures'] = []
		for feature in obj.get('phenotypic_features'):
			feature_record = phenotypic_feature_to_fhir(feature)
			biosample_record['phenotypicFeatures'].append(feature_record)
	# mapping for procedure related to each biosample
	if 'procedure' in obj.keys():
		procedure = obj.get('procedure')
		biosample_record['collection'] = {}
		biosample_record['collection']['method'] = procedure_to_fhir(procedure).get('code')
		biosample_record['collection']['bodySite'] = procedure_to_fhir(procedure).get('bodySite')
	# all these elements are represented by FHIR Class CodeableConcept
	# and have the same schema
	codeable_concepts = [
		'taxonomy', 'histological_diagnosis',
		'tumor_progression', 'tumor_grade',
		'diagnostic_markers'
		]
	for concept in codeable_concepts:
		if concept in obj.keys():
			concept_data = obj.get(concept)
			concept_field_name = camel_case_field_names(concept)
			biosample_record[concept_field_name] = fhir_codeable_concept(concept_data)
	return biosample_record


def hts_file_to_fhir(obj):
	""" Convert HTSFile record to FHIR Document Reference. """

	htsfile_record = {}
	htsfile_record['resourceType'] = 'DocumentReference'
	htsfile_record['content'] = []
	content_data = {}
	content_data['attachment'] = {}
	content_data['attachment']['url'] = obj.get('uri', None)
	if 'description' in obj.keys():
		content_data['attachment']['title'] = obj.get('description', None)
	htsfile_record['content'].append(content_data)
	htsfile_record['type'] = {}
	htsfile_record['type']['coding'] = []
	coding = {}
	coding['code'] = obj.get('hts_format', None)
	coding['display'] = obj.get('hts_format', None)
	htsfile_record['type']['coding'].append(coding)
	htsfile_record['extension'] = {}
	htsfile_record['extension']['url'] = 'http://ga4gh.org/fhir/phenopackets/StructureDefinition/htsfile-genome-assembly'
	htsfile_record['extension']['valueCode'] = obj.get('genome_assembly', None)
	return htsfile_record


def gene_to_fhir(obj):
	""" Gene to FHIR CodeableConcept. """

	gene_record = {}
	gene_record['resourceType'] = 'CodeableConcept'
	gene_record['coding'] = []
	coding = {}
	coding['code'] = obj.get('id', None)
	coding['display'] = obj.get('symbol', None)
	gene_record['coding'].append(coding)
	return gene_record


def variant_to_fhir(obj):
	""" Variant to FHIR """
	# TODO check this example
	# http://build.fhir.org/ig/HL7/genomics-reporting/SNVexample.json.html

	variant_record = {}
	variant_record['resourceType'] = 'Observation'
	variant_record['identifier'] = obj.get('id', None)
	variant_record['meta'] = {}
	variant_record['meta']['profile'] = [
		'http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/variant'
		]

	return variant_record


def disease_to_fhir(obj):
	""" Disease to FHIR Condition. """

	disease_record = {}
	disease_record['resourceType'] = 'Condition'
	disease_record['code'] = []
	coding = {}
	coding['coding'] = []
	coding['coding'].append(fhir_coding(obj, 'term'))
	disease_record['code'].append(coding)
	if obj.get('onset'):
		disease_record['onsetAge'] = {}
		disease_record['onsetAge']['code'] = obj.get('onset', {}).get('age', None)
	disease_stages = obj.get('disease_stage', None)
	if disease_stages:
		disease_record['stage'] = []
		stage_type = {}
		stage_type['type'] = {}
		stage_type['type']['coding'] = []
		for coding in disease_stages:
			coding = fhir_coding(coding)
			stage_type['type']['coding'].append(coding)
		disease_record['stage'].append(stage_type)
	return disease_record


def phenopacket_to_fhir(obj):
	""" Phenopacket to FHIR Composition. """

	phenopacket_record = {}
	phenopacket_record['resourceType'] = "Composition"
	phenopacket_record['id'] = obj.get('id', None)
	phenopacket_record['meta'] = {}
	metadata = obj.get('meta_data')
	if metadata.get('phenopacket_schema_version'):
		phenopacket_record['meta']['versionId'] = metadata.get(
			'phenopacket_schema_version'
			)
		phenopacket_record['meta']['lastUpdated'] = metadata.get(
			'created'
			)
	if metadata.get('external_references'):
		phenopacket_record['meta']['source'] = metadata.get(
			'external_references'
			)
	phenopacket_record['meta']['tag'] = metadata.get('resources')
	phenopacket_record['subject'] = {}
	phenopacket_record['subject']['reference'] = obj.get('subject')
	phenopacket_record['section'] = []
	def _get_section_object(inner_obj, title):
		""" Internal function to parse phenopacket m2m objects. """
		section_object = {}
		section_object['title'] = title
		section_object['entry'] =[]
		if isinstance(inner_obj, list):
			for each in inner_obj:
				if each.get('id'):
					section_object['entry'].append(each.get('id', None))
				else:
					section_object['entry'].append(each.get('uri', None))

		else:
			section_object['entry'].append(inner_obj)
		return section_object

	sections = ['biosamples', 'genes', 'variants', 'diseases', 'hts_files']
	for section in sections:
		if section in obj.keys():
			entry_value = _get_section_object(obj.get(section, None), section)
			phenopacket_record['section'].append(entry_value)
	return phenopacket_record
