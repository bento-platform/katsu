import json
from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from rdflib import Graph
from rdflib.plugin import register, Serializer
from rest_framework.renderers import JSONRenderer
from uuid import UUID

from .jsonld_utils import dataset_to_jsonld

register('json-ld', Serializer, 'rdflib_jsonld.serializer', 'JsonLDSerializer')


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


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
            final_data = {fhir_datatype_plural: [class_converter(item) for item in data['results']]}
        else:
            final_data = class_converter(data)
        return super(FHIRRenderer, self).render(final_data, media_type, renderer_context)


class PhenopacketsRenderer(CamelCaseJSONRenderer):
    media_type = 'application/json'
    format = 'phenopackets'

    def render(self, data, media_type=None, renderer_context=None):
        return super(PhenopacketsRenderer, self).render(data, media_type, renderer_context)


class JSONLDDatasetRenderer(PhenopacketsRenderer):
    media_type = 'application/ld+json'
    format = 'json-ld'

    def render(self, data, media_type=None, renderer_context=None):
        if 'results' in data:
            json_obj = {'results': [dataset_to_jsonld(item) for item in data['results']]}
        else:
            json_obj = dataset_to_jsonld(data)

        return super(JSONLDDatasetRenderer, self).render(json_obj, media_type, renderer_context)


class RDFDatasetRenderer(PhenopacketsRenderer):
    # change for 'application/rdf+xml'
    media_type = 'application/rdf+xml'
    render_style = 'binary'
    charset = 'utf-8'
    format = 'rdf'

    def render(self, data, media_type=None, renderer_context=None):
        if 'results' in data:
            g = Graph()
            for item in data['results']:
                ld_context_item = dataset_to_jsonld(item)
                small_g = Graph().parse(data=json.dumps(ld_context_item, cls=UUIDEncoder), format='json-ld')
                # join graphs
                g = g + small_g
        else:
            ld_context_data = dataset_to_jsonld(data)
            g = Graph().parse(data=json.dumps(ld_context_data, cls=UUIDEncoder), format='json-ld')
        rdf_data = g.serialize(format='pretty-xml')
        return rdf_data
