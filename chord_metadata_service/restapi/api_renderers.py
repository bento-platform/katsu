import json
import csv
import io
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from uuid import UUID
from typing import Callable, ClassVar, Dict, Optional, Any, Type

from bento_lib.responses import errors
from openpyxl import Workbook
from pydantic import BaseModel
from rdflib import Graph
from rdflib.plugin import register
from rdflib.serializer import Serializer
from django.http import HttpResponse
from rest_framework import status
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer, BaseRenderer
from rest_framework.response import Response
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
    "PassThruXLSXRenderer",
    "KatsuCSVRenderer",
    "KatsuXLSXRenderer",
    "IndividualCSVRenderer",
    "IndividualXLSXRenderer",
    "BiosamplesCSVRenderer",
    "BiosamplesXLSXRenderer",
    "ExperimentCSVRenderer",
    "ExperimentXLSXRenderer",
    "IndividualBentoSearchRenderer",
    "PydanticJSONRenderer",
    "PydanticBrowsableAPIRenderer",
    "csv_fields_error_response",
]

OUTPUT_FORMAT_BENTO_SEARCH_RESULT = "bento_search_result"

register("json-ld", Serializer, "rdflib_jsonld.serializer", "JsonLDSerializer")


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


class PhenopacketsRenderer(CamelCaseJSONRenderer):
    media_type = "application/json"
    format = "phenopackets"

    def render(self, data, media_type=None, renderer_context=None):
        return super().render(data, media_type, renderer_context)


class JSONLDDatasetRenderer(PhenopacketsRenderer):
    media_type = "application/ld+json"
    format = "json-ld"

    def render(self, data, media_type=None, renderer_context=None):
        if "results" in data:
            json_obj = {"results": [dataset_to_jsonld(item) for item in data["results"]]}
        else:
            json_obj = dataset_to_jsonld(data)

        return super().render(json_obj, media_type, renderer_context)


class RDFDatasetRenderer(PhenopacketsRenderer):
    # change for 'application/rdf+xml'
    media_type = "application/rdf+xml"
    render_style = "binary"
    charset = "utf-8"
    format = "rdf"

    def render(self, data, media_type=None, renderer_context=None):
        if "results" in data:
            g = Graph()
            for item in data["results"]:
                ld_context_item = dataset_to_jsonld(item)
                small_g = Graph().parse(data=json.dumps(ld_context_item, cls=UUIDEncoder), format="json-ld")
                # join graphs
                g = g + small_g
        else:
            ld_context_data = dataset_to_jsonld(data)
            g = Graph().parse(data=json.dumps(ld_context_data, cls=UUIDEncoder), format="json-ld")
        rdf_data = g.serialize(format="pretty-xml")
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


XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class PassThruXLSXRenderer(BaseRenderer):
    """
    A sort-of skeleton XLSX renderer, which assumes data are already a rendered XLSX response and just handles
    negotiation and response content type.
    """

    media_type = XLSX_MEDIA_TYPE
    format = "xlsx"
    charset = None  # binary format - avoid DRF appending "; charset=utf-8" to the Content-Type header

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return HttpResponse(data, content_type=XLSX_MEDIA_TYPE)  # XLSX should already be rendered as bytes here


@dataclass(frozen=True)
class FieldSpec:
    """Declares how to pull one exportable column's value out of a serialized row (a dict, from a DRF serializer)."""

    getter: Callable[[dict], Any]


def get_path(row: dict, *path: str, default: Any = None) -> Any:
    """
    Walk a chain of dict keys, short-circuiting to `default` if a step is missing/None. Raises TypeError if a step
    resolves to a non-None, non-dict value while path segments remain - that means the field registry's path
    doesn't match the actual row shape, which is a bug, not a normal absent-value case.
    """
    val: Any = row
    for key in path:
        if val is None:
            return default
        if not isinstance(val, dict):
            raise TypeError(f"get_path: expected dict while resolving {key!r}, got {type(val).__name__}")
        val = val.get(key)
    return default if val is None else val


def simple_field(*path: str, default: Any = None) -> FieldSpec:
    """A FieldSpec that just reads a (possibly nested) path out of the row, e.g. simple_field("taxonomy", "label")."""
    return FieldSpec(lambda row: get_path(row, *path, default=default))


def _column_label(key: str) -> str:
    return key.replace("_", " ").capitalize()


def parse_requested_fields(request) -> Optional[list[str]]:
    """
    The caller's selected-fields list, if any: a comma-separated `fields` query param, or a `fields` list in a
    POST body (batch export endpoints negotiate format from the body, so fields can travel the same way).
    Returns None if the caller didn't ask for a subset (i.e. every registered column should be returned).
    """
    if request is None:
        return None

    # discovery_matches namespaces its query params (anything not starting with "_" is read as a discovery filter
    # field), so it needs the "_fields" spelling; other endpoints accept plain "fields".
    requested = request.query_params.get("fields") or request.query_params.get("_fields")
    if requested is None and isinstance(getattr(request, "data", None), dict):
        requested = request.data.get("fields")

    if not requested:
        return None

    return [f.strip() for f in requested.split(",")] if isinstance(requested, str) else list(requested)


class FieldRegistryRenderer(metaclass=ABCMeta):
    """
    Shared plumbing for renderers that export a serialized queryset via a declarative field_registry: dict[str,
    FieldSpec]. Subclasses (one per output format, e.g. KatsuCSVRenderer/KatsuXLSXRenderer) supply the actual
    serialization to bytes; concrete per-entity renderers just set field_registry and get_model_serializer().
    """

    # Ordered registry of every column this renderer can produce, column key -> FieldSpec. The dict key IS the
    # export column key everywhere (get_columns() and get_dicts() both derive from it), so there's exactly one
    # place a column is named.
    field_registry: ClassVar[dict[str, FieldSpec]]

    @staticmethod
    @abstractmethod
    def get_model_serializer() -> Type[GenericSerializer]:
        pass

    @classmethod
    def field_choices(cls) -> list[dict[str, str]]:
        """Every column this renderer can produce, as {key, label} pairs - for a UI column picker."""
        return [{"key": key, "label": _column_label(key)} for key in cls.field_registry]

    @classmethod
    def unknown_requested_fields(cls, request) -> list[str]:
        """Any `fields` the caller asked for that aren't in this renderer's registry - [] if none/not applicable."""
        requested = parse_requested_fields(request)
        if requested is None:
            return []
        return [f for f in requested if f not in cls.field_registry]

    def get_columns(self, renderer_context) -> list[str]:
        request = renderer_context.get("request") if renderer_context else None
        requested = parse_requested_fields(request)
        if requested is None:
            return list(self.field_registry.keys())
        # keep registry order regardless of the order fields were requested in; drop unrecognized keys
        selected = set(requested)
        return [key for key in self.field_registry if key in selected]

    def get_dicts(self, data, columns: list[str]) -> list[dict[str, str]]:
        return [{key: self.field_registry[key].getter(row) for key in columns} for row in data]

    def _build_response(self, rows: list[dict[str, str]], columns: list[str]):
        """Subclasses turn selected rows/columns into the actual format-specific response body."""
        raise NotImplementedError

    def render(self, data, accepted_media_type=None, renderer_context=None):
        columns = self.get_columns(renderer_context)

        if not data:
            return self._build_response([], columns)

        response_obj = renderer_context.get("response") if renderer_context else None
        if response_obj is not None and response_obj.status_code != status.HTTP_200_OK:
            # Error response: render as JSON instead of CSV/XLSX. This is invoked either directly (renderer_context
            # has no "response" - see discovery_matches, which never hits this branch: it only reaches render() on
            # the success path, errors having already been returned earlier) or via a DRF Response's own rendering
            # (renderer_context["response"] is that same Response, headers already fixed to the export content type
            # by finalize_response before render() runs) - so we mutate its Content-Type in place and hand back raw
            # bytes for DRF to assign as the body, rather than building a whole separate HttpResponse that DRF
            # would just discard the headers of.
            response_obj["Content-Type"] = "application/json; charset=utf-8"
            return json.dumps(data).encode("utf-8")

        # paginated DRF responses arrive as {"count": ..., "results": [...]}; batch/discovery endpoints already
        # pass a plain list.
        if isinstance(data, dict):
            data = data["results"]

        return self._build_response(self.get_dicts(data, columns), columns)


class KatsuCSVRenderer(FieldRegistryRenderer, JSONRenderer, metaclass=ABCMeta):
    media_type = "text/csv"
    format = "csv"

    file_name: str = "data.csv"

    def _build_response(self, rows: list[dict[str, str]], columns: list[str]):
        headers = {key: _column_label(key) for key in columns}

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename='{self.file_name}'"

        dict_writer = csv.DictWriter(response, fieldnames=columns)
        dict_writer.writerow(headers)
        dict_writer.writerows(rows)

        return response


class KatsuXLSXRenderer(FieldRegistryRenderer, BaseRenderer, metaclass=ABCMeta):
    """
    Renders a serialized queryset (via field_registry) as a single-sheet XLSX workbook - same columns/values/
    ordering as the equivalent KatsuCSVRenderer.
    """

    media_type = XLSX_MEDIA_TYPE
    format = "xlsx"
    charset = None  # binary format - avoid DRF appending "; charset=utf-8" to the Content-Type header

    file_name: str = "data.xlsx"
    sheet_name: str = "Export"

    def _build_response(self, rows: list[dict[str, str]], columns: list[str]):
        wb = Workbook()
        ws = wb.active
        ws.title = self.sheet_name
        ws.append([_column_label(key) for key in columns])
        for row in rows:
            ws.append([row.get(key) for key in columns])

        buf = io.BytesIO()
        wb.save(buf)

        response = HttpResponse(buf.getvalue(), content_type=XLSX_MEDIA_TYPE)
        response["Content-Disposition"] = f"attachment; filename='{self.file_name}'"
        return response


def csv_fields_error_response(request, renderer_cls: Type["KatsuCSVRenderer"]) -> Optional[Response]:
    """
    If the request's `fields` selection names a column not in renderer_cls's registry, return a 400 in the standard
    katsu/bento_lib error format; otherwise None (no `fields` param, or all requested keys are valid).
    """
    unknown = renderer_cls.unknown_requested_fields(request)
    if not unknown:
        return None
    return Response(
        errors.bad_request_error(f"unknown export field(s): {', '.join(unknown)}"),
        status=status.HTTP_400_BAD_REQUEST,
    )


def _render_csv_diseases(diseases: list[dict]) -> str:
    # use ; because some disease terms might contain , in their label
    return "; ".join(
        [
            f"{d['term']['label']} ({time_element_to_str(d['onset'])})" if d.get("onset") else d["term"]["label"]
            for d in diseases
        ]
    )


def _individual_diseases(individual: dict) -> Optional[str]:
    if "phenopackets" not in individual:
        return None
    all_diseases = [
        _render_csv_diseases(phenopacket["diseases"])
        for phenopacket in individual["phenopackets"]
        if "diseases" in phenopacket
    ]
    return "; ".join(all_diseases) if all_diseases else None


INDIVIDUAL_FIELDS: dict[str, FieldSpec] = {
    "id": simple_field("id"),
    "sex": simple_field("sex"),
    "date_of_birth": simple_field("date_of_birth"),
    "taxonomy": simple_field("taxonomy", "label"),
    "karyotypic_sex": FieldSpec(lambda row: row["karyotypic_sex"]),
    "age": FieldSpec(lambda row: render_age(row, "time_at_last_encounter")),
    "diseases": FieldSpec(_individual_diseases),
    "created": FieldSpec(lambda row: row["created"]),
    "updated": FieldSpec(lambda row: row["updated"]),
}


class IndividualCSVRenderer(KatsuCSVRenderer):
    file_name = "individuals.csv"
    field_registry = INDIVIDUAL_FIELDS

    @staticmethod
    def get_model_serializer() -> Type[GenericSerializer]:
        return pa_s.IndividualSerializer


class IndividualXLSXRenderer(KatsuXLSXRenderer):
    file_name = "individuals.xlsx"
    sheet_name = "Individuals"
    field_registry = INDIVIDUAL_FIELDS

    @staticmethod
    def get_model_serializer() -> Type[GenericSerializer]:
        return pa_s.IndividualSerializer


def _phenopacket_biosamples(phe: dict) -> Optional[str]:
    if not phe.get("biosamples"):
        return None
    return "; ".join(
        (f"{b['id']} [{b['sampled_tissue']['label']}]" if b.get("sampled_tissue") else b["id"])
        for b in phe["biosamples"]
    )


PHENOPACKET_FIELDS: dict[str, FieldSpec] = {
    "id": FieldSpec(lambda row: row["id"]),
    "subject_id": simple_field("subject", "id"),
    "subject_sex": simple_field("subject", "sex"),
    "subject_taxonomy": simple_field("subject", "taxonomy", "label"),
    "biosamples": FieldSpec(_phenopacket_biosamples),
    "diseases": FieldSpec(lambda row: _render_csv_diseases(row["diseases"]) if row.get("diseases") else None),
    "created_by": FieldSpec(lambda row: row["meta_data"].get("created_by")),
    "submitted_by": FieldSpec(lambda row: row["meta_data"].get("submitted_by")),
    "dataset": simple_field("dataset"),
}


class PhenopacketCSVRenderer(KatsuCSVRenderer):
    file_name = "phenopackets.csv"
    field_registry = PHENOPACKET_FIELDS

    @staticmethod
    def get_model_serializer() -> Type[GenericSerializer]:
        return phe_s.PhenopacketSerializer


class PhenopacketXLSXRenderer(KatsuXLSXRenderer):
    file_name = "phenopackets.xlsx"
    sheet_name = "Phenopackets"
    field_registry = PHENOPACKET_FIELDS

    @staticmethod
    def get_model_serializer() -> Type[GenericSerializer]:
        return phe_s.PhenopacketSerializer


BIOSAMPLE_FIELDS: dict[str, FieldSpec] = {
    "id": FieldSpec(lambda row: row["id"]),
    "description": simple_field("description", default="NA"),
    "sampled_tissue": simple_field("sampled_tissue", "label", default="NA"),
    "time_of_collection": FieldSpec(lambda row: render_age(row, "time_of_collection")),
    "histological_diagnosis": simple_field("histological_diagnosis", "label", default="NA"),
    "extra_properties": FieldSpec(
        lambda row: f"Material: {get_path(row, 'extra_properties', 'material', default='NA')}",
    ),
    "created": FieldSpec(lambda row: row["created"]),
    "updated": FieldSpec(lambda row: row["updated"]),
    "individual": simple_field("individual"),
}


class BiosamplesCSVRenderer(KatsuCSVRenderer):
    file_name = "biosamples.csv"
    field_registry = BIOSAMPLE_FIELDS

    @staticmethod
    def get_model_serializer() -> Type[GenericSerializer]:
        return phe_s.BiosampleSerializer


class BiosamplesXLSXRenderer(KatsuXLSXRenderer):
    file_name = "biosamples.xlsx"
    sheet_name = "Biosamples"
    field_registry = BIOSAMPLE_FIELDS

    @staticmethod
    def get_model_serializer() -> Type[GenericSerializer]:
        return phe_s.BiosampleSerializer


EXPERIMENT_FIELDS: dict[str, FieldSpec] = {
    "id": simple_field("id"),
    "study_type": simple_field("study_type"),
    "experiment_type": simple_field("experiment_type", default="NA"),
    "molecule": simple_field("molecule"),
    "library_strategy": simple_field("library_strategy"),
    "library_source": simple_field("library_source", default="NA"),
    "library_selection": simple_field("library_selection"),
    "library_layout": simple_field("library_layout"),
    "created": simple_field("created"),
    "updated": simple_field("updated"),
    "biosample": simple_field("biosample"),
    "individual": simple_field("biosample_individual", "id", default="NA"),
}


class ExperimentCSVRenderer(KatsuCSVRenderer):
    file_name = "experiments.csv"
    field_registry = EXPERIMENT_FIELDS

    @staticmethod
    def get_model_serializer() -> Type[GenericSerializer]:
        return exp_s.ExperimentSerializer


class ExperimentXLSXRenderer(KatsuXLSXRenderer):
    file_name = "experiments.xlsx"
    sheet_name = "Experiments"
    field_registry = EXPERIMENT_FIELDS

    @staticmethod
    def get_model_serializer() -> Type[GenericSerializer]:
        return exp_s.ExperimentSerializer


EXPERIMENT_RESULT_FIELDS: dict[str, FieldSpec] = {
    "id": simple_field("id"),
    "description": simple_field("description"),
    "filename": simple_field("filename"),
    "url": simple_field("url"),
    "genome_assembly_id": simple_field("genome_assembly_id"),
    "file_format": simple_field("file_format"),
    "data_output_type": simple_field("data_output_type"),
    "usage": simple_field("usage"),
    "creation_date": simple_field("creation_date"),
    "created_by": simple_field("created_by"),
}


class ExperimentResultCSVRenderer(KatsuCSVRenderer):
    file_name = "experiment_results.csv"
    field_registry = EXPERIMENT_RESULT_FIELDS

    @staticmethod
    def get_model_serializer() -> Type[GenericSerializer]:
        return exp_s.ExperimentResultSerializer


class ExperimentResultXLSXRenderer(KatsuXLSXRenderer):
    file_name = "experiment_results.xlsx"
    sheet_name = "Experiment Results"
    field_registry = EXPERIMENT_RESULT_FIELDS

    @staticmethod
    def get_model_serializer() -> Type[GenericSerializer]:
        return exp_s.ExperimentResultSerializer


class IndividualBentoSearchRenderer(JSONRenderer):
    """
    This renderer directly maps bento_search_result to the JSON Renderer
    Note: this seems necessary to be able to use the format parameter
    "bento_search_result" in the Individual ViewSet.
    """

    media_type = "application/json"
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
