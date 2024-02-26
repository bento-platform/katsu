from pathlib import Path
from bento_lib.workflows import models as wm
from bento_lib.workflows.workflow_set import WorkflowSet

__all__ = [
    "WORKFLOW_PHENOPACKETS_JSON",
    "WORKFLOW_EXPERIMENTS_JSON",
    "WORKFLOW_EXPERIMENTS_EXTENDED_JSON",
    "WORKFLOW_FHIR_JSON",
    "WORKFLOW_READSET",
    "WORKFLOW_DOCUMENT",
    "WORKFLOW_MAF_DERIVED_FROM_VCF_JSON",
    "WORKFLOW_VCF2MAF",
    "WORKFLOW_CBIOPORTAL",

    "workflow_set",
]

from chord_metadata_service.chord.data_types import DATA_TYPE_EXPERIMENT, DATA_TYPE_PHENOPACKET

WORKFLOW_PHENOPACKETS_JSON = "phenopackets_json"
WORKFLOW_EXPERIMENTS_JSON = "experiments_json"
WORKFLOW_EXPERIMENTS_EXTENDED_JSON = "experiments_extended_json"

WORKFLOW_FHIR_JSON = "fhir_json"
WORKFLOW_READSET = "readset"
WORKFLOW_DOCUMENT = "document"
WORKFLOW_MAF_DERIVED_FROM_VCF_JSON = "maf_derived_from_vcf_json"
WORKFLOW_VCF2MAF = "vcf2maf"
WORKFLOW_CBIOPORTAL = "cbioportal"

WORKFLOW_TAG_CBIOPORTAL = "cbioportal"


def json_file_input(id_: str, required: bool = True):
    return wm.WorkflowFileInput(id=id_, required=required, pattern=r"^.*\.json$")


DRS_URL_INPUT = wm.WorkflowServiceUrlInput(id="drs_url", service_kind="drs")
DIRECTORY_PATH_INPUT = wm.WorkflowDirectoryInput(id="directory")
KATSU_URL_INPUT = wm.WorkflowServiceUrlInput(id="katsu_url", service_kind="metadata")
PROJECT_DATASET_INPUT = wm.WorkflowProjectDatasetInput(id="project_dataset")
ACCESS_TOKEN_INPUT = wm.WorkflowSecretInput(id="access_token", key="access_token")
VALIDATE_SSL_INPUT = wm.WorkflowConfigInput(id="validate_ssl", key="validate_ssl")


workflow_set = WorkflowSet(Path(__file__).parent / "wdls")

# Ingestion workflows --------------------------------------------------------------------------------------------------

workflow_set.add_workflow(WORKFLOW_PHENOPACKETS_JSON, wm.WorkflowDefinition(
    type="ingestion",
    name="Bento Phenopackets-Compatible JSON",
    description="This ingestion workflow will validate and import a Phenopackets schema-compatible JSON document.",
    data_type=DATA_TYPE_PHENOPACKET,  # for permissions
    tags=[DATA_TYPE_PHENOPACKET],
    file="phenopackets_json.wdl",
    inputs=[
        # injected
        ACCESS_TOKEN_INPUT,
        KATSU_URL_INPUT,
        VALIDATE_SSL_INPUT,
        # user
        PROJECT_DATASET_INPUT,
        json_file_input("json_document"),
    ],
))

workflow_set.add_workflow(WORKFLOW_EXPERIMENTS_JSON, wm.WorkflowDefinition(
    type="ingestion",
    name="Bento Experiments JSON",
    description="This ingestion workflow will validate and import a Bento Experiments schema-compatible JSON document.",
    data_type=DATA_TYPE_EXPERIMENT,  # for permissions
    tags=[DATA_TYPE_EXPERIMENT],
    file="experiments_json.wdl",
    inputs=[
        # injected
        ACCESS_TOKEN_INPUT,
        KATSU_URL_INPUT,
        VALIDATE_SSL_INPUT,
        # user
        PROJECT_DATASET_INPUT,
        json_file_input("json_document"),
    ],
))

workflow_set.add_workflow(WORKFLOW_EXPERIMENTS_EXTENDED_JSON, wm.WorkflowDefinition(
    type="ingestion",
    name="Bento Experiments JSON-extended",
    description="This workflow ingests experiments and related files into DRS.",
    data_type=DATA_TYPE_EXPERIMENT,
    tags=[DATA_TYPE_EXPERIMENT, "experiment_result"],
    file="experiments_extended_json.wdl",
    inputs=[
        # injected
        ACCESS_TOKEN_INPUT,
        DRS_URL_INPUT,
        KATSU_URL_INPUT,
        VALIDATE_SSL_INPUT,
        # user
        PROJECT_DATASET_INPUT,
        DIRECTORY_PATH_INPUT,
        json_file_input("json_document"),
    ],
))

workflow_set.add_workflow(WORKFLOW_READSET, wm.WorkflowDefinition(
    type="ingestion",
    name="Readset",
    description="This workflow will copy readset files over to DRS.",
    data_type=DATA_TYPE_EXPERIMENT,  # for permissions
    tags=[DATA_TYPE_EXPERIMENT, "readset"],
    file="readset.wdl",
    inputs=[
        # injected
        ACCESS_TOKEN_INPUT,
        DRS_URL_INPUT,
        VALIDATE_SSL_INPUT,
        # user
        PROJECT_DATASET_INPUT,
        wm.WorkflowFileArrayInput(
            id="readset_files",
            required=True,
            pattern=r"^.*\.(cram|bam|bigWig|bigBed|bw|bb)$",
        ),
    ],
))

workflow_set.add_workflow(WORKFLOW_DOCUMENT, wm.WorkflowDefinition(
    type="ingestion",
    name="Document",
    description="This workflow ingests into DRS documents which have been already listed as experiment results.",
    data_type=DATA_TYPE_EXPERIMENT,  # for permissions
    tags=[DATA_TYPE_EXPERIMENT, "experiment_result"],
    file="document.wdl",
    inputs=[
        # injected
        ACCESS_TOKEN_INPUT,
        DRS_URL_INPUT,
        VALIDATE_SSL_INPUT,
        # user
        PROJECT_DATASET_INPUT,
        wm.WorkflowFileArrayInput(
            id="document_files",
            required=True,
            pattern=r"^.*\.(pdf|csv|tsv|txt|docx|xlsx|jpeg|jpg|png|gif|md|markdown|mp3|m4a|mp4)$",
        ),
    ],
))

workflow_set.add_workflow(WORKFLOW_MAF_DERIVED_FROM_VCF_JSON, wm.WorkflowDefinition(
    type="ingestion",
    name="MAF files derived from VCF files as a JSON",
    description="This ingestion workflow will add to the current experiment results MAF files that were generated from "
                "VCF files found in the Dataset.",
    data_type=DATA_TYPE_EXPERIMENT,  # for permissions
    tags=[DATA_TYPE_EXPERIMENT, WORKFLOW_TAG_CBIOPORTAL],
    file="maf_derived_from_vcf_json.wdl",
    inputs=[
        # injected
        ACCESS_TOKEN_INPUT,
        # user
        PROJECT_DATASET_INPUT,
        json_file_input("json_document"),
    ],
))

# Analysis workflows ---------------------------------------------------------------------------------------------------

workflow_set.add_workflow(WORKFLOW_VCF2MAF, wm.WorkflowDefinition(
    type="analysis",
    name="Convert VCF to MAF files",
    description="This analysis workflow will create MAF files from every VCF file found in a dataset.",
    file="vcf2maf.wdl",
    tags=[WORKFLOW_TAG_CBIOPORTAL],
    inputs=[
        # injected
        ACCESS_TOKEN_INPUT,
        wm.WorkflowConfigInput(id="vep_cache_dir", key="vep_cache_dir"),
        DRS_URL_INPUT,
        KATSU_URL_INPUT,
        VALIDATE_SSL_INPUT,
        # user
        PROJECT_DATASET_INPUT,
    ]
))

# Export workflows -----------------------------------------------------------------------------------------------------

workflow_set.add_workflow(WORKFLOW_CBIOPORTAL, wm.WorkflowDefinition(
    type="export",
    name="cBioPortal",
    description="This workflow creates a bundle for cBioPortal ingestion.",
    tags=[WORKFLOW_TAG_CBIOPORTAL],
    file="cbioportal_export.wdl",
    inputs=[
        # injected
        DRS_URL_INPUT,
        KATSU_URL_INPUT,
        ACCESS_TOKEN_INPUT,
        VALIDATE_SSL_INPUT,
        # user
        PROJECT_DATASET_INPUT,
    ],
))

# ----------------------------------------------------------------------------------------------------------------------
