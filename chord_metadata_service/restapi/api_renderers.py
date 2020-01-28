from rest_framework.renderers import JSONRenderer
from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from chord_metadata_service.restapi.jsonld_utils import dataset_to_jsonld, CONTEXT
from rdflib import Graph
import json
from rdflib.plugin import register, Serializer

register('json-ld', Serializer, 'rdflib_jsonld.serializer', 'JsonLDSerializer')
from uuid import UUID
from rest_framework.response import Response


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


class JSONLDDatasetRenderer(PhenopacketsRenderer):
    media_type = 'application/ld+json'
    format = 'json-ld'

    def render(self, data, media_type=None, renderer_context=None):
        if 'results' in data:
            json_obj = {}
            json_obj['results'] = []
            for item in data['results']:
                dataset_jsonld = dataset_to_jsonld(item)
                json_obj['results'].append(dataset_jsonld)
        else:
            json_obj = dataset_to_jsonld(data)

        return super(JSONLDDatasetRenderer, self).render(json_obj, media_type, renderer_context)


class RDFDatasetRenderer(PhenopacketsRenderer):
    # change for 'application/rdf+xml'
    media_type = 'text/html'
    format = 'rdf'

    def render(self, data, media_type=None, renderer_context=None):
        if 'results' in data:
            g = Graph()
            for item in data['results']:
                context = CONTEXT
                small_g = Graph().parse(data=json.dumps(item, cls=UUIDEncoder), context=context, format='json-ld')
                # join graphs
                g = g + small_g
        else:
            context = CONTEXT
            g = Graph().parse(data=json.dumps(data, cls=UUIDEncoder), context=context, format='json-ld')
            # If destination is None serialize method returns the serialization as a string.
        rdf_data = g.serialize(format='pretty-xml').decode('utf-8')

        return super(RDFDatasetRenderer, self).render(rdf_data, media_type, renderer_context)
