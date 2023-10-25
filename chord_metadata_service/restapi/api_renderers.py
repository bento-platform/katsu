import json
import csv
from uuid import UUID
from rdflib import Graph
from rdflib.plugin import register, Serializer
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from .jsonld_utils import dataset_to_jsonld
from .utils import parse_onset

OUTPUT_FORMAT_BENTO_SEARCH_RESULT = "bento_search_result"

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


class ARGORenderer(JSONRenderer):
    media_type = 'application/json'
    format = 'argo'

    def render(self, data, media_type=None, renderer_context=None):
        argo_profile_plural = getattr(
            renderer_context.get('view').get_serializer().Meta,
            'argo_profile_plural', 'objects'
        )
        class_converter = getattr(
            renderer_context.get('view').get_serializer().Meta,
            'argo_converter', 'objects'
        )
        if 'results' in data:
            final_data = {argo_profile_plural: [class_converter(item) for item in data['results']]}
        else:
            final_data = class_converter(data)
        return super(ARGORenderer, self).render(final_data, media_type, renderer_context)


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


def generate_csv_response(data, filename, columns):
    headers = {key: key.replace('_', ' ').capitalize() for key in columns}
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f"attachment; filename='{filename}'"
    dict_writer = csv.DictWriter(response, fieldnames=columns)
    dict_writer.writerow(headers)
    dict_writer.writerows(data)
    return response


class IndividualCSVRenderer(JSONRenderer):
    media_type = 'text/csv'
    format = 'csv'

    def render(self, data, media_type=None, renderer_context=None):
        if 'results' not in data or not data['results']:
            return

        individuals = []
        for individual in data['results']:
            ind_obj = {
                'id': individual['id'],
                'sex': individual.get('sex', None),
                'date_of_birth': individual.get('date_of_birth', None),
                'taxonomy': None,
                'karyotypic_sex': individual['karyotypic_sex'],
                'age': None,
                'diseases': None,
                'created': individual['created'],
                'updated': individual['updated']
            }
            if 'taxonomy' in individual:
                ind_obj['taxonomy'] = individual['taxonomy'].get('label', None)
            if 'age' in individual:
                if 'age' in individual['age']:
                    ind_obj['age'] = individual['age'].get('age', None)
                elif 'start' and 'end' in individual['age']:
                    ind_obj['age'] = str(
                        individual['age']['start'].get('age', "NA")
                        + ' - ' +
                        individual['age']['end'].get('age', "NA")
                    )
                else:
                    ind_obj['age'] = None
            if 'phenopackets' in individual:
                all_diseases = []
                for phenopacket in individual['phenopackets']:
                    if 'diseases' in phenopacket:
                        # use ; because some disease terms might contain , in their label
                        single_phenopacket_diseases = '; '.join(
                            [
                                f"{d['term']['label']} ({parse_onset(d['onset'])})"
                                if 'onset' in d else d['term']['label'] for d in phenopacket['diseases']
                            ]
                        )
                        all_diseases.append(single_phenopacket_diseases)
                if all_diseases:
                    ind_obj['diseases'] = '; '.join(all_diseases)
            individuals.append(ind_obj)
        columns = individuals[0].keys()
        # remove underscore and capitalize column names
        return generate_csv_response(individuals, 'data.csv', columns)


class BiosamplesCSVRenderer(JSONRenderer):
    media_type = 'text/csv'
    format = 'csv'

    def render(self, data, media_type=None, renderer_context=None):
        if not data:
            return

        biosamples = []
        for biosample in data:
            bio_obj = {
                'id': biosample['id'],
                'description': biosample.get('description', 'NA'),
                'sampled_tissue': biosample.get('sampled_tissue', {}).get('label', 'NA'),
                'individual_age_at_collection': biosample.get('individual_age_at_collection', {}).get('age', 'NA'),
                'histological_diagnosis': biosample.get('histological_diagnosis', {}).get('label', 'NA'),
                'extra_properties': f"Material: {biosample.get('extra_properties', {}).get('material', 'NA')}",
                'created': biosample['created'],
                'updated': biosample['updated'],
                'individual': biosample['individual']
            }
            biosamples.append(bio_obj)

        columns = biosamples[0].keys()
        return generate_csv_response(biosamples, 'biosamples.csv', columns)


class ExperimentCSVRenderer(JSONRenderer):
    media_type = 'text/csv'
    format = 'csv'

    def render(self, data, media_type=None, renderer_context=None):
        if not data:
            return

        experiments = []
        for experiment in data:
            exp_obj = {
                'id': experiment.get('id'),
                'study_type': experiment.get('study_type'),
                'experiment_type': experiment.get('experiment_type', 'NA'),
                'molecule': experiment.get('molecule'),
                'library_strategy': experiment.get('library_strategy'),
                'library_source': experiment.get('library_source', 'NA'),
                'library_selection': experiment.get('library_selection'),
                'library_layout': experiment.get('library_layout'),
                'created': experiment.get('created'),
                'updated': experiment.get('updated'),
                'biosample': experiment.get('biosample'),
                'individual_id': experiment.get('biosample_individual', {}).get('id', 'NA'),
            }
            experiments.append(exp_obj)

        columns = experiments[0].keys()
        return generate_csv_response(experiments, 'experiments.csv', columns)


class IndividualBentoSearchRenderer(JSONRenderer):
    """
    This renderer directly maps bento_search_result to the JSON Renderer
    Note: this seems necessary to be able to use the format parameter
    "bento_search_result" in the Individual ViewSet.
    """
    media_type = 'application/json'
    format = OUTPUT_FORMAT_BENTO_SEARCH_RESULT
