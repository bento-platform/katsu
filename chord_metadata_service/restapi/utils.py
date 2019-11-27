# Utils for converting data between formats


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
		coding['code'] = obj.get(value, None).get('id', None)
		coding['display'] = obj.get(value, None).get('label', None)
	else:
		coding['code'] = obj.get('id', None)
		coding['display'] = obj.get('label', None)
	return coding


def fhir_codeable_concept(obj):
	""" Convert  different data types to FHIR Codeable concept. """

	codeable_concept = {}
	codeable_concept['resourceType'] = 'CodeableConcept'
	codeable_concept['coding'] = []
	if isinstance(obj, list):
		for item in obj:
			coding = fhir_coding(item)
			codeable_concept['coding'].append(coding)
	else:
		coding = fhir_coding(obj)
		codeable_concept['coding'].append(coding)
	return codeable_concept


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
	procedure['bodySite'] = {}
	procedure['bodySite']['coding'] = []
	body_site_coding = fhir_coding(obj, 'body_site')
	procedure['bodySite']['coding'].append(body_site_coding)
	return procedure


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
	if obj.get('age_of_onset'):
		disease_record['onsetAge'] = {}
		disease_record['onsetAge']['code'] = obj.get('age_of_onset', None).get('age', None)
	tumor_stage_list = obj.get('tumor_stage', None)
	if tumor_stage_list:
		disease_record['stage'] = []
		stage_type = {}
		stage_type['type'] = {}
		stage_type['type']['coding'] = []
		for coding in tumor_stage_list:
			coding = fhir_coding(coding)
			stage_type['type']['coding'].append(coding)
		disease_record['stage'].append(stage_type)
	return disease_record
