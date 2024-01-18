from chord_metadata_service.chord.workflows import metadata as wm

from .experiments import ingest_experiments_workflow, ingest_maf_derived_from_vcf_workflow
from .fhir import ingest_fhir_workflow
from .phenopackets import ingest_phenopacket_workflow
from .readsets import ingest_readset_workflow

from typing import Callable, Dict

__all__ = [
    "WORKFLOW_INGEST_FUNCTION_MAP",
]

WORKFLOW_INGEST_FUNCTION_MAP: Dict[str, Callable] = {
    wm.WORKFLOW_EXPERIMENTS_JSON: ingest_experiments_workflow,
    wm.WORKFLOW_PHENOPACKETS_JSON: ingest_phenopacket_workflow,
    wm.WORKFLOW_FHIR_JSON: ingest_fhir_workflow,
    wm.WORKFLOW_READSET: ingest_readset_workflow,
    wm.WORKFLOW_MAF_DERIVED_FROM_VCF_JSON: ingest_maf_derived_from_vcf_workflow,
}
