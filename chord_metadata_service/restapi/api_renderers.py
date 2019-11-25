from rest_framework.renderers import JSONRenderer
from .utils import *
from djangorestframework_camel_case.render import CamelCaseJSONRenderer


class FHIRRenderer(JSONRenderer):
	media_type = 'application/json'
	format = 'fhir'

	def render(self, data, media_type=None, renderer_context=None):
		if 'results' in data:
			final_data = {}
			final_data['patients'] = []
			for item in data.get('results'):
				item_data = convert_to_fhir(item)
				final_data['patients'].append(item_data)
		else:
			final_data = convert_to_fhir(data)

		return super(FHIRRenderer, self).render(final_data, media_type, renderer_context)


class BiosampleFHIRRenderer(JSONRenderer):
	media_type = 'application/json'
	format = 'fhir'

	def render(self, data, media_type=None, renderer_context=None):
		if 'results' in data:
			final_data = {}
			final_data['specimens'] = []
			for item in data.get('results'):
				item_data = biosample_to_fhir(item)
				final_data['specimens'].append(item_data)
		else:
			final_data = biosample_to_fhir(data)

		return super(BiosampleFHIRRenderer, self).render(final_data, media_type, renderer_context)


class PhenotypicFeatureFHIRRenderer(JSONRenderer):
	media_type = 'application/json'
	format = 'fhir'

	def render(self, data, media_type=None, renderer_context=None):
		if 'results' in data:
			final_data = {}
			final_data['observations'] = []
			for item in data.get('results'):
				item_data = phenotypic_feature_to_fhir(item)
				final_data['observations'].append(item_data)
		else:
			final_data = phenotypic_feature_to_fhir(data)

		return super(PhenotypicFeatureFHIRRenderer, self).render(final_data, media_type, renderer_context)


class ProcedureFHIRRenderer(JSONRenderer):
	media_type = 'application/json'
	format = 'fhir'

	def render(self, data, media_type=None, renderer_context=None):
		if 'results' in data:
			final_data = {}
			final_data['procedures'] = []
			for item in data.get('results'):
				item_data = procedure_to_fhir(item)
				final_data['procedures'].append(item_data)
		else:
			final_data = procedure_to_fhir(data)

		return super(ProcedureFHIRRenderer, self).render(final_data, media_type, renderer_context)


class HstFileFHIRRenderer(JSONRenderer):
	media_type = 'application/json'
	format = 'fhir'

	def render(self, data, media_type=None, renderer_context=None):
		if 'results' in data:
			final_data = {}
			final_data['document_references'] = []
			for item in data.get('results'):
				item_data = hts_file_to_fhir(item)
				final_data['document_references'].append(item_data)
		else:
			final_data = hts_file_to_fhir(data)

		return super(HstFileFHIRRenderer, self).render(final_data, media_type, renderer_context)


class GeneFHIRRenderer(JSONRenderer):
	media_type = 'application/json'
	format = 'fhir'

	def render(self, data, media_type=None, renderer_context=None):
		if 'results' in data:
			final_data = {}
			final_data['codeable_concepts'] = []
			for item in data.get('results'):
				item_data = gene_to_fhir(item)
				final_data['codeable_concepts'].append(item_data)
		else:
			final_data = gene_to_fhir(data)

		return super(GeneFHIRRenderer, self).render(final_data, media_type, renderer_context)


class PhenopacketsRenderer(CamelCaseJSONRenderer):
	media_type = 'application/json'
	format = 'phenopackets'

	def render(self, data, media_type=None, renderer_context=None):
		return super(PhenopacketsRenderer, self).render(data, media_type, renderer_context)