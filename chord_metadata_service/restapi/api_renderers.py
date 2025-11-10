import json
import csv
from abc import ABCMeta, abstractmethod
from uuid import UUID
from typing import Dict, Optional, Any, Type

from pydantic import BaseModel
from rdflib import Graph
from rdflib.plugin import register
from rdflib.serializer import Serializer
from django.http import HttpResponse
from rest_framework import status
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer, BaseRenderer
from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from chord_metadata_service.experiments import serializers as exp_s
from chord_metadata_service.patients import serializers as pa_s
from chord_metadata_service.phenopackets import serializers as phe_s
from chord_metadata_service.phenopackets.utils import time_element_to_str
from .jsonld_utils import dataset_to_jsonld
from .serializers import GenericSerializer

__all__ = [
    "PhenopacketsRenderer",
    "JSONLDDatasetRenderer",
    "RDFDatasetRenderer",
    "render_age",
    "PassThruCSVRenderer",
    "KatsuCSVRenderer",
    "IndividualCSVRenderer",
    "BiosamplesCSVRenderer",
    "ExperimentCSVRenderer",
    "IndividualBentoSearchRenderer",
    "PydanticJSONRenderer",
    "PydanticBrowsableAPIRenderer",
]

OUTPUT_FORMAT_BENTO_SEARCH_RESULT = "bento_search_result"

register('json-ld', Serializer, 'rdflib_jsonld.serializer', 'JsonLDSerializer')


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


class PhenopacketsRenderer(CamelCaseJSONRenderer):
    media_type = 'application/json'
    format = 'phenopackets'

    def render(self, data, media_type=None, renderer_context=None):
        return super().render(data, media_type, renderer_context)


class JSONLDDatasetRenderer(PhenopacketsRenderer):
    media_type = 'application/ld+json'
    format = 'json-ld'

    def render(self, data, media_type=None, renderer_context=None):
        if 'results' in data:
            json_obj = {'results': [dataset_to_jsonld(item) for item in data['results']]}
        else:
            json_obj = dataset_to_jsonld(data)

        return super().render(json_obj, media_type, renderer_context)


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


def render_age(item: Dict[str, Any], time_key: str) -> Optional[str]:
    if time_key not in item:
        return None
    time_to_render = item[time_key]

    if "age_range" in time_to_render:
        age_range = time_to_render["age_range"]
        start = age_range["start"]["iso8601duration"]
        end = age_range["end"]["iso8601duration"]
        return f"{start} - {end}"
    if "age" in time_to_render:
        return time_to_render["age"]["iso8601duration"]
    return None


class PassThruCSVRenderer(BaseRenderer):
    """
    A sort-of skeleton CSV renderer, which assumes data are already CSV bytes and just handles negotiation and response
    content type.
    """

    media_type = "text/csv"
    format = "csv"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return HttpResponse(data, content_type="text/csv")  # CSV should already be rendered as bytes here


class KatsuCSVRenderer(JSONRenderer, metaclass=ABCMeta):
    media_type = "text/csv"
    format = "csv"

    file_name: str = "data.csv"

    @staticmethod
    @abstractmethod
    def get_model_serializer() -> Type[GenericSerializer]:
        pass

    @abstractmethod
    def get_columns(self) -> list[str]:  # pragma: no cover
        raise NotImplementedError("get_columns() not implemented")

    @abstractmethod
    def get_dicts(self, data, renderer_context) -> list[dict[str, str]]:  # pragma: no cover
        raise NotImplementedError("get_dicts() not implemented")

    def _generate_csv_response(self, data: list[dict[str, str]]):
        columns = self.get_columns()

        # remove underscore and capitalize column names
        headers = {key: key.replace("_", " ").capitalize() for key in columns}

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename='{self.file_name}'"

        dict_writer = csv.DictWriter(response, fieldnames=columns)
        dict_writer.writerow(headers)
        dict_writer.writerows(data)

        return response

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not data:
            return self._generate_csv_response([])

        if renderer_context and (res_status := renderer_context["response"].status_code) != status.HTTP_200_OK:
            # error response as JSON instead of CSV
            return HttpResponse(
                json.dumps(data).encode("utf-8"),
                status=res_status,
                content_type="application/json; charset=utf-8",
            )

        return self._generate_csv_response(self.get_dicts(data, renderer_context))


def _render_csv_diseases(diseases: list[dict]) -> str:
    # use ; because some disease terms might contain , in their label
    return "; ".join(
        [
            f"{d['term']['label']} ({time_element_to_str(d['onset'])})"
            if d.get("onset") else d["term"]["label"] for d in diseases
        ]
    )


class IndividualCSVRenderer(KatsuCSVRenderer):
    file_name = "individuals.csv"

    @staticmethod
    def get_model_serializer() -> Type[GenericSerializer]:
        return pa_s.IndividualSerializer

    def get_columns(self) -> list[str]:
        return ["id", "sex", "date_of_birth", "taxonomy", "karyotypic_sex", "age", "diseases", "created", "updated"]

    def get_dicts(self, data, _renderer_context) -> list[dict[str, str]]:
        individuals = []

        if isinstance(data, dict):
            data = data["results"]

        for individual in data:
            ind_obj = {
                "id": individual["id"],
                "sex": individual.get("sex", None),
                "date_of_birth": individual.get("date_of_birth", None),
                "taxonomy": individual.get("taxonomy", {}).get("label", None),
                "karyotypic_sex": individual["karyotypic_sex"],
                "age": render_age(individual, "time_at_last_encounter"),
                "diseases": None,
                "created": individual["created"],
                "updated": individual["updated"]
            }
            if "phenopackets" in individual:
                all_diseases = []
                for phenopacket in individual["phenopackets"]:
                    if "diseases" in phenopacket:
                        single_phenopacket_diseases = _render_csv_diseases(phenopacket["diseases"])
                        all_diseases.append(single_phenopacket_diseases)
                if all_diseases:
                    ind_obj["diseases"] = "; ".join(all_diseases)
            individuals.append(ind_obj)

        return individuals


class PhenopacketCSVRenderer(KatsuCSVRenderer):
    file_name = "phenopackets.csv"

    @staticmethod
    def get_model_serializer() -> Type[GenericSerializer]:
        return phe_s.PhenopacketSerializer

    def get_columns(self) -> list[str]:
        return [
            "id",
            "subject_id",
            "subject_sex",
            "subject_taxonomy",
            "biosamples",
            "diseases",
            "created_by",
            "submitted_by",
            "dataset",
        ]

    def get_dicts(self, data, _renderer_context) -> list[dict[str, str]]:
        return [
            {
                "id": phe["id"],
                "subject_id": phe["subject"]["id"] if phe.get("subject") else None,
                "subject_sex": phe["subject"]["sex"] if phe.get("subject") else None,
                "subject_taxonomy": phe["subject"]["taxonomy"]["label"] if phe.get("subject") else None,
                "biosamples": "; ".join(
                    (
                        f"{b['id']} [{b['sampled_tissue']['label']}]"
                        if b.get("sampled_tissue")
                        else b["id"]
                    )
                    for b in phe["biosamples"]
                ) if phe.get("biosamples") else None,
                "diseases": _render_csv_diseases(phe["diseases"]) if phe.get("diseases") else None,
                "created_by": phe["meta_data"].get("created_by"),
                "submitted_by": phe["meta_data"].get("submitted_by"),
                "dataset": phe.get("dataset"),
            }
            for phe in data
        ]


class BiosamplesCSVRenderer(KatsuCSVRenderer):
    file_name = "biosamples.csv"

    @staticmethod
    def get_model_serializer() -> Type[GenericSerializer]:
        return phe_s.BiosampleSerializer

    def get_columns(self) -> list[str]:
        return [
            "id",
            "description",
            "sampled_tissue",
            "time_of_collection",
            "histological_diagnosis",
            "extra_properties",
            "created",
            "updated",
            "individual",
        ]

    def get_dicts(self, data, _renderer_context) -> list[dict[str, str]]:
        return [
            {
                "id": biosample["id"],
                "description": biosample.get("description", "NA"),
                "sampled_tissue": biosample.get("sampled_tissue", {}).get("label", "NA"),
                "time_of_collection": render_age(biosample, "time_of_collection"),
                "histological_diagnosis": biosample.get("histological_diagnosis", {}).get("label", "NA"),
                "extra_properties": f"Material: {biosample.get('extra_properties', {}).get('material', 'NA')}",
                "created": biosample["created"],
                "updated": biosample["updated"],
                "individual": biosample.get("individual")
            }
            for biosample in data
        ]


class ExperimentCSVRenderer(KatsuCSVRenderer):
    file_name = "experiments.csv"

    @staticmethod
    def get_model_serializer() -> Type[GenericSerializer]:
        return exp_s.ExperimentSerializer

    def get_columns(self) -> list[str]:
        return [
            "id",
            "study_type",
            "experiment_type",
            "molecule",
            "library_strategy",
            "library_source",
            "library_selection",
            "library_layout",
            "created",
            "updated",
            "biosample",
            "individual",
        ]

    def get_dicts(self, data, _renderer_context) -> list[dict[str, str]]:
        return [
            {
                "id": experiment.get("id"),
                "study_type": experiment.get("study_type"),
                "experiment_type": experiment.get("experiment_type", "NA"),
                "molecule": experiment.get("molecule"),
                "library_strategy": experiment.get("library_strategy"),
                "library_source": experiment.get("library_source", "NA"),
                "library_selection": experiment.get("library_selection"),
                "library_layout": experiment.get("library_layout"),
                "created": experiment.get("created"),
                "updated": experiment.get("updated"),
                "biosample": experiment.get("biosample"),
                "individual": experiment.get("biosample_individual", {}).get("id", "NA"),
            }
            for experiment in data
        ]


class ExperimentResultCSVRenderer(KatsuCSVRenderer):
    file_name = "experiment_results.csv"

    @staticmethod
    def get_model_serializer() -> Type[GenericSerializer]:
        return exp_s.ExperimentResultSerializer

    def get_columns(self) -> list[str]:
        return [
            "id",
            "description",
            "filename",
            "url",
            "genome_assembly_id",
            "file_format",
            "data_output_type",
            "usage",
            "creation_date",
            "created_by",
        ]

    def get_dicts(self, data, _renderer_context) -> list[dict[str, str]]:
        return [
            {
                "id": er.get("id"),
                "description": er.get("description"),
                "filename": er.get("filename"),
                "url": er.get("url"),
                "genome_assembly_id": er.get("genome_assembly_id"),
                "file_format": er.get("file_format"),
                "data_output_type": er.get("data_output_type"),
                "usage": er.get("usage"),
                "creation_date": er.get("creation_date"),
                "created_by": er.get("created_by"),
            }
            for er in data
        ]


class IndividualBentoSearchRenderer(JSONRenderer):
    """
    This renderer directly maps bento_search_result to the JSON Renderer
    Note: this seems necessary to be able to use the format parameter
    "bento_search_result" in the Individual ViewSet.
    """
    media_type = 'application/json'
    format = OUTPUT_FORMAT_BENTO_SEARCH_RESULT


def _json_dump_if_pyd(data):
    return data.model_dump(mode="json") if isinstance(data, BaseModel) else data


class PydanticJSONRenderer(JSONRenderer):
    """
    An extended version of the default DRF JSONRenderer class, which handles Pydantic model instances if passed. If the
    data passed is not a Pydantic model instance, this simply falls back to the superclass behaviour.
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return super().render(_json_dump_if_pyd(data), accepted_media_type, renderer_context)


class PydanticBrowsableAPIRenderer(BrowsableAPIRenderer):
    """
    An extended version of the default DRF BrowsableAPIRenderer class, which handles Pydantic model instances if passed.
    If the data passed is not a Pydantic model instance, this simply falls back to the superclass behaviour.
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        return super().render(_json_dump_if_pyd(data), accepted_media_type, renderer_context)
