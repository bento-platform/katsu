# Utils for converting data between formats


def convert_to_fhir(individual_data):
	""" Transform individual data to Patient FHIR record """
	fhir_record = {}
	fhir_record['resourceType'] = 'Patient'
	# mapping for basic Patient attributes
	mapping = {
	'individual_id': 'identifier',
	'date_of_birth': 'birthDate',
	'sex': 'gender',
	'active': 'active',
	'deceased': 'deceased',
	'address_postal_code': 'addresPostalCode',
	'race': 'race',
	'ethnicity': 'ethnicity'
	}
	for field in mapping.keys():
		if field in individual_data.keys():
			fhir_record[mapping.get(field)] = individual_data.get(field, None)
	# mapping for biosamples assosiated with this patient
	if 'biosamples' in individual_data.keys():
		fhir_record['biosamples'] = []
		for sample in individual_data.get('biosamples'):
			biosample_record = {}
			biosample_record['resourceType'] = 'Specimen'
			biosample_record['identifier'] = sample.get('biosample_id')
			biosample_record['parent'] = {}
			biosample_record['parent']['reference'] = {}
			biosample_record['parent']['reference']['reference'] = sample.get('sampled_tissue').get('id')
			biosample_record['parent']['reference']['display'] = sample.get('sampled_tissue').get('label')
			# mapping for phenotypic_features related to each biosample
			if 'phenotypic_features' in sample.keys():
				biosample_record['phenotypic_features'] = []
				for feature in sample.get('phenotypic_features'):
					feature_record = {}
					feature_record['resourceType'] = 'Condition'
					if 'id' in feature.keys():
						feature_record['identifier'] = feature.get('id')
					if 'description' in feature.keys():
						feature_record['text'] = feature.get('description')
					if 'type' in feature.keys():
						feature_record['code'] = {}
						feature_record['code']['coding'] = []
						ftype = {}
						ftype['code'] = feature.get('type').get('id')
						ftype['display'] = feature.get('type').get('label')
						feature_record['code']['coding'].append(ftype)
					biosample_record['phenotypic_features'].append(feature_record)
			fhir_record['biosamples'].append(biosample_record)

	return fhir_record