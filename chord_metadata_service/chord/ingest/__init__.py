from chord_metadata_service.chord.workflows import metadata as wm

from .experiments import ingest_experiments_workflow, ingest_maf_derived_from_vcf_workflow
from .fhir import ingest_fhir_workflow
from .mcode import ingest_mcode_fhir_workflow, ingest_mcode_workflow
from .phenopackets import ingest_phenopacket_workflow
from .readsets import ingest_readset_workflow

__all__ = [
    "WORKFLOW_INGEST_FUNCTION_MAP",
]

WORKFLOW_INGEST_FUNCTION_MAP = {
    wm.WORKFLOW_EXPERIMENTS_JSON: ingest_experiments_workflow,
    wm.WORKFLOW_PHENOPACKETS_JSON: ingest_phenopacket_workflow,
    wm.WORKFLOW_FHIR_JSON: ingest_fhir_workflow,
    wm.WORKFLOW_MCODE_FHIR_JSON: ingest_mcode_fhir_workflow,
    wm.WORKFLOW_MCODE_JSON: ingest_mcode_workflow,
    wm.WORKFLOW_READSET: ingest_readset_workflow,
    wm.WORKFLOW_MAF_DERIVED_FROM_VCF_JSON: ingest_maf_derived_from_vcf_workflow,
}
