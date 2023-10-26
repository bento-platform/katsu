import os

__all__ = [
    "WORKFLOW_PHENOPACKETS_JSON",
    "WORKFLOW_EXPERIMENTS_JSON",
    "WORKFLOW_FHIR_JSON",
    "WORKFLOW_READSET",
    "WORKFLOW_READDOC",
    "WORKFLOW_MAF_DERIVED_FROM_VCF_JSON",
    "WORKFLOW_VCF2MAF",
    "WORKFLOW_CBIOPORTAL",

    "METADATA_WORKFLOWS",

    "WORKFLOWS_PATH",
]

from typing import Optional

from chord_metadata_service.chord.data_types import (
    DATA_TYPE_EXPERIMENT,
    DATA_TYPE_EXPERIMENT_RESULT,
    DATA_TYPE_PHENOPACKET,
    DATA_TYPE_READSET,
)

from .constants import FROM_CONFIG

WORKFLOW_PHENOPACKETS_JSON = "phenopackets_json"
WORKFLOW_EXPERIMENTS_JSON = "experiments_json"
WORKFLOW_FHIR_JSON = "fhir_json"
WORKFLOW_READSET = "readset"
WORKFLOW_READDOC = "readdoc"
WORKFLOW_MAF_DERIVED_FROM_VCF_JSON = "maf_derived_from_vcf_json"
WORKFLOW_VCF2MAF = "vcf2maf"
WORKFLOW_CBIOPORTAL = "cbioportal"


def json_file_input(id_: str, required: bool = True):
    return {
        "id": id_,
        "type": "file",
        "required": required,
        "extensions": [".json"]
    }


def json_file_output(id_: str, output_name: Optional[str] = None):
    return {
        "id": id_,
        "type": "file",

        # this triple {} abomination, with e.g. id_=json_document, turns into the string '{json_document}'
        # the 'output_name or' part is a bit of a hack until we move to a new ingest system which can actually read
        # Cromwell output JSON to grab the right files or something.
        "value": output_name or f"{{{id_}}}",
    }


DRS_URL_INPUT = {
    "id": "drs_url",
    "type": "string",
    "required": True,
    "value": FROM_CONFIG,
    "hidden": True,
}

KATSU_URL_INPUT = {
    "id": "katsu_url",
    "type": "string",
    "required": True,
    "value": FROM_CONFIG,
    "hidden": True,
}


METADATA_WORKFLOWS = {
    "ingestion": {
        WORKFLOW_PHENOPACKETS_JSON: {
            "name": "Bento Phenopackets-Compatible JSON",
            "description": "This ingestion workflow will validate and import a Phenopackets schema-compatible "
                           "JSON document.",
            "data_type": DATA_TYPE_PHENOPACKET,
            "file": "phenopackets_json.wdl",
            "inputs": [KATSU_URL_INPUT, json_file_input("json_document")],
            "outputs": [],
        },
        WORKFLOW_EXPERIMENTS_JSON: {
            "name": "Bento Experiments JSON",
            "description": "This ingestion workflow will validate and import a Bento Experiments schema-compatible "
                           "JSON document.",
            "data_type": DATA_TYPE_EXPERIMENT,
            "file": "experiments_json.wdl",
            "inputs": [KATSU_URL_INPUT, json_file_input("json_document")],
            "outputs": []
        },
        WORKFLOW_FHIR_JSON: {
            "name": "FHIR Resources JSON",
            "description": "This ingestion workflow will validate and import a FHIR schema-compatible "
                           "JSON document, and convert it to the Bento metadata service's internal Phenopackets-based "
                           "data model.",
            "data_type": DATA_TYPE_PHENOPACKET,
            "file": "fhir_json.wdl",
            "inputs": [
                KATSU_URL_INPUT,
                json_file_input("patients"),
                json_file_input("observations", required=False),
                json_file_input("conditions", required=False),
                json_file_input("specimens", required=False),
                {
                    "id": "created_by",
                    "required": False,
                    "type": "string"
                },

            ],
            "outputs": [
                json_file_output("patients", "patients.json"),
                json_file_output("observations", "observations.json"),
                json_file_output("conditions", "conditions.json"),
                json_file_output("specimens", "specimens.json"),
                {
                    "id": "created_by",
                    "type": "string",
                    "value": "{created_by}"
                },

            ]
        },
        WORKFLOW_READSET: {
            "name": "Readset",
            "description": "This workflow will copy readset files over to DRS.",
            "data_type": DATA_TYPE_READSET,
            "file": "readset.wdl",
            "inputs": [
                {
                    "id": "readset_files",
                    "type": "file[]",
                    "required": True,
                    "extensions": [".cram", ".bam", ".bigWig", ".bigBed", ".bw", ".bb"]
                }
            ],
            "outputs": [
                {
                    "id": "readset_files",
                    "type": "file[]",
                    "map_from_input": "readset_files",
                    "value": "{}"
                }
            ]
        },
        WORKFLOW_READDOC: {
            "name": "Document",
            "description": "XThis workflow will send document files to the specified ingestion service.",
            "data_type": DATA_TYPE_EXPERIMENT_RESULT,
            "file": "readdoc.wdl",
            "inputs": [
                {
                    "id": "readdoc_files",
                    "type": "file[]",
                    "required": True,
                    "extensions": [".pdf", ".csv", ".tsv", ".txt", ".doc", ".docx", ".xls", ".xlsx",
                                   ".jpeg", ".jpg", ".png", ".gif", ".md", ".mp3", ".m4a", ".mp4"]
                },
                DRS_URL_INPUT,
            ],
            "outputs": [
                {
                    "id": "readdoc_files_out",
                    "type": "file",
                    "value": "{readdoc_files_out}"
                },
            ],

        },
        WORKFLOW_MAF_DERIVED_FROM_VCF_JSON: {
            "name": "MAF files derived from VCF files as a JSON",
            "description": "This ingestion workflow will add to the current experiment results "
                           "MAF files that were generated from VCF files found in the Dataset. ",
            "data_type": DATA_TYPE_EXPERIMENT_RESULT,
            "file": "maf_derived_from_vcf_json.wdl",
            "inputs": [json_file_input("json_document")],
            "outputs": [json_file_output("json_document", "ingest.json")],
        },
    },
    "analysis": {
        WORKFLOW_VCF2MAF: {
            "name": "Convert VCF to MAF files",
            "description": "This analysis workflow will create MAF files from every VCF file found in a dataset.",
            "data_type": None,
            "file": "vcf2maf.wdl",
            "auth": [
                {
                    "id": "one_time_token_metadata_ingest",
                    "type": "ott",
                    "scope": "/api/metadata/private/ingest/",
                },
                {
                    "id": "temp_token_drs",
                    "type": "tt",
                    "scope": "/api/drs/",
                },
            ],
            "inputs": [
                {
                    "id": "dataset_id",
                    "type": "string",
                    "required": True,
                },
                {
                    "id": "dataset_name",
                    "type": "string",
                    "required": True,
                },
                {
                    "id": "chord_url",
                    "type": "string",
                    "required": True,
                    "value": FROM_CONFIG,
                    "hidden": True,
                },
                {
                    "id": "vep_cache_dir",
                    "type": "string",
                    "required": True,
                    "value": FROM_CONFIG,
                    "hidden": True,
                },
                DRS_URL_INPUT,
                KATSU_URL_INPUT,
            ],
            "outputs": [
                {
                    "id": "maf_files",
                    "type": "file[]",
                    "value": "glob('*.maf')",
                },
            ],
        }
    },
    "export": {
        WORKFLOW_CBIOPORTAL: {
            "name": "cBioPortal",
            "description": "This workflow creates a bundle for cBioPortal ingestion.",
            "data_type": None,
            "file": "cbioportal_export.wdl",
            "inputs": [
                {
                    "id": "dataset_id",
                    "type": "string",
                    "required": True,
                },
                DRS_URL_INPUT,
                KATSU_URL_INPUT,
            ],
            "outputs": [
                {
                    "id": "cbioportal_archive",
                    "type": "file",
                    "map_from_input": "dataset_id",
                    "value": "{}.tar",
                }
            ]
        }
    }
}

# Tag all workflows with their action (ingestion/analysis/export)
for action, workflows in METADATA_WORKFLOWS.items():
    for wf in workflows.values():
        wf["action"] = action

WORKFLOWS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "wdls")
