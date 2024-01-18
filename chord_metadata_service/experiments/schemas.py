from pathlib import Path
from .descriptions import EXPERIMENT, EXPERIMENT_RESULT, INSTRUMENT
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS_LIST, KEY_VALUE_OBJECT
from chord_metadata_service.restapi.schema_utils import tag_ids_and_describe, get_schema_app_id, sub_schema_uri
from chord_metadata_service.ontologies import read_xsd_simple_type_values, SRA_EXPERIMENT_FILE_NAME

__all__ = ["EXPERIMENT_SCHEMA", "EXPERIMENT_RESULT_SCHEMA", "INSTRUMENT_SCHEMA"]


base_uri = get_schema_app_id(Path(__file__).parent.name)

# Experiment library strategy options are read from the EBI xsd file
LIBRARY_STRATEGIES = read_xsd_simple_type_values(
    SRA_EXPERIMENT_FILE_NAME,
    "typeLibraryStrategy",
)


# Experiment library selection options are read from the EBI xsd file
LIBRARY_SELECTION = read_xsd_simple_type_values(
    SRA_EXPERIMENT_FILE_NAME,
    "typeLibrarySelection",
)


EXPERIMENT_RESULT_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": sub_schema_uri(base_uri, "experiment_result"),
    "title": "Experiment result schema",
    "description": "Schema for describing information about analysis of sequencing data in a file format.",
    "type": "object",
    "properties": {
        "identifier": {
            "type": "string"
        },
        "description": {
            "type": "string"
        },
        "filename": {
            "type": "string"
        },
        "genome_assembly_id": {
            "type": "string",
        },
        "file_format": {
            "type": "string",
            "enum": ["SAM", "BAM", "CRAM", "BAI", "CRAI", "VCF", "BCF", "MAF", "GVCF", "BigWig", "BigBed", "FASTA",
                     "FASTQ", "TAB", "SRA", "SRF", "SFF", "GFF", "TABIX", "PDF", "CSV", "TSV", "JPEG", "PNG", "GIF",
                     "MARKDOWN", "MP3", "M4A", "MP4", "DOCX", "XLS", "XLSX", "UNKNOWN", "OTHER"]
        },
        "data_output_type": {
            "type": "string",
            "enum": ["Raw data", "Derived data"]
        },
        "usage": {
            "type": "string"
        },
        "creation_date": {
            "type": "string"
        },
        "created_by": {
            "type": "string"
        },
        "extra_properties": KEY_VALUE_OBJECT,
    }
}, EXPERIMENT_RESULT)


INSTRUMENT_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": sub_schema_uri(base_uri, "instrument"),
    "title": "Instrument schema",
    "description": "Schema for describing an instrument used for a sequencing experiment.",
    "type": "object",
    "properties": {
        "identifier": {
            "type": "string"
        },
        "platform": {
            "type": "string"
        },
        "description": {
            "type": "string"
        },
        "model": {
            "type": "string"
        },
        "extra_properties": KEY_VALUE_OBJECT,
    }
}, INSTRUMENT)


EXPERIMENT_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": sub_schema_uri(base_uri, "experiment"),
    "title": "Experiment schema",
    "description": "Schema for describing an experiment.",
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "study_type": {
            "type": "string",
            "enum": ["Genomics", "Epigenomics", "Metagenomics", "Transcriptomics",
                     "Serology", "Metabolomics", "Proteomics", "Other"]
        },
        "experiment_type": {
            "type": "string",
            "enum": ["DNA Methylation", "mRNA-Seq", "smRNA-Seq", "RNA-Seq", "WES",
                     "WGS", "Genotyping", "Proteomic profiling",
                     "Neutralizing antibody titers", "Metabolite profiling",
                     "Antibody measurement", "Viral WGS", "Other"]
        },
        "experiment_ontology": ONTOLOGY_CLASS_LIST,
        "molecule": {
            "type": "string",
            "enum": ["total RNA", "polyA RNA", "cytoplasmic RNA", "nuclear RNA",
                     "small RNA", "genomic DNA", "protein", "Other"]
        },
        "molecule_ontology": ONTOLOGY_CLASS_LIST,
        "library_strategy": {
            "type": "string",
            "enum": LIBRARY_STRATEGIES
        },
        "library_source": {
            "type": "string",
            "enum": ["Genomic", "Genomic Single Cell", "Transcriptomic", "Transcriptomic Single Cell",
                     "Metagenomic", "Metatranscriptomic", "Synthetic", "Viral RNA", "Other"]
        },
        "library_selection": {
            "type": "string",
            "enum": LIBRARY_SELECTION
        },
        "library_layout": {
            "type": "string",
            "enum": ["Single", "Paired"]
        },
        "extraction_protocol": {
            "type": "string"
        },
        "reference_registry_id": {
            "type": "string"
        },
        "qc_flags": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "extra_properties": KEY_VALUE_OBJECT,
        "biosample": {
            "type": "string"
        },
        "experiment_results": {
            "type": "array",
            "items": EXPERIMENT_RESULT_SCHEMA
        },
        "instrument": INSTRUMENT_SCHEMA
    },
    "required": ["id", "experiment_type"]
}, EXPERIMENT)


EXPERIMENT_WORKFLOW_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "katsu:experiments:experiment_workflow_schema",
    "title": "Experiment workflow schema",
    "description": "Schema that describes the shape \
        of an experiment workflow ingestion",
    "type": "object",
    "properties": {
        "experiments": {
            "type": "array",
            "items": {"type": "object"},
            "minItems": 1,
        },
        "resources": {
            "type": "array",
            "items": {"type": "object"},
        }
    },
    "required": ["experiments"]
}

"""
Dictionary of schema changes for warnings.
"""
EXPERIMENT_SCHEMA_CHANGES = {
    "4.1.0": {
        "properties": {
            "library_strategy": [
                    ("WES", "WXS"),
                    ("Other", "OTHER"),
            ],
            "library_selection": [
                    ("Random", "RANDOM"),
                    ("Random PCR", "RANDOM PCR"),
                    ("Exome capture", "Hybrid Selection"),
                    ("Other", "other"),
            ]
        }
    }
}
