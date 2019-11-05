from rest_framework.renderers import JSONRenderer
from .utils import convert_to_fhir, camel_case_field_names


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


class PhenopacketsRenderer(JSONRenderer):
	media_type = 'application/json'
	format = 'phenopackets'

	def render(self, data, media_type=None, renderer_context=None):
		return super(PhenopacketsRenderer, self).render(data, media_type, renderer_context)