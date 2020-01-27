from rest_framework.renderers import JSONRenderer
from djangorestframework_camel_case.render import CamelCaseJSONRenderer


class FHIRRenderer(JSONRenderer):
    media_type = 'application/json'
    format = 'fhir'

    def render(self, data, media_type=None, renderer_context=None):
        fhir_datatype_plural = getattr(
                renderer_context.get('view').get_serializer().Meta,
                'fhir_datatype_plural', 'objects'
                )
        class_converter = getattr(
                renderer_context.get('view').get_serializer().Meta,
                'class_converter', 'objects'
                )
        if 'results' in data:
            final_data = {}
            final_data[fhir_datatype_plural] = []
            for item in data.get('results'):
                item_data = class_converter(item)
                final_data[fhir_datatype_plural].append(item_data)
        else:
            final_data = class_converter(data)
        return super(FHIRRenderer, self).render(final_data, media_type, renderer_context)


class PhenopacketsRenderer(CamelCaseJSONRenderer):
    media_type = 'application/json'
    format = 'phenopackets'

    def render(self, data, media_type=None, renderer_context=None):
        return super(PhenopacketsRenderer, self).render(data, media_type, renderer_context)
