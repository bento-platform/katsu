from django.conf import settings
from chord_metadata_service.metadata.elastic import es
from chord_metadata_service.phenopackets.serializers import (
    ProcedureSerializer,
    BiosampleSerializer,
    PhenotypicFeatureSerializer
)
from chord_metadata_service.phenopackets.models import (
    Procedure,
    Biosample,
    PhenotypicFeature
)
from chord_metadata_service.restapi.fhir_utils import (
    fhir_specimen_collection,
    fhir_specimen,
    fhir_observation
)


def build_procedure_index(procedure: Procedure) -> str:
    if es:
        procedure_json = ProcedureSerializer(procedure)
        fhir_procedure_json = fhir_specimen_collection(procedure_json.data)

        res = es.index(index=settings.FHIR_INDEX_NAME, id=procedure.id, body=fhir_procedure_json)
        return res['result']


def remove_procedure_index(procedure: Procedure) -> str:
    if es:
        res = es.delete(index=settings.FHIR_INDEX_NAME, id=procedure.id)
        return res['result']


def build_biosample_index(biosample: Biosample) -> str:
    if es:
        biosample_json = BiosampleSerializer(biosample)
        fhir_biosample_json = fhir_specimen(biosample_json.data)

        res = es.index(index=settings.FHIR_INDEX_NAME, id=biosample.id, body=fhir_biosample_json)
        return res['result']


def remove_biosample_index(biosample: Biosample) -> str:
    if es:
        res = es.delete(index=settings.FHIR_INDEX_NAME, id=biosample.id)
        return res['result']


def build_phenotypicfeature_index(feature: PhenotypicFeature) -> str:
    if es:
        feature_json = PhenotypicFeatureSerializer(feature)
        fhir_feature_json = fhir_observation(feature_json.data)

        res = es.index(index=settings.FHIR_INDEX_NAME, id=feature.id, body=fhir_feature_json)
        return res['result']


def remove_phenotypicfeature_index(feature: PhenotypicFeature) -> str:
    if es:
        res = es.delete(index=settings.FHIR_INDEX_NAME, id=feature.id)
        return res['result']
