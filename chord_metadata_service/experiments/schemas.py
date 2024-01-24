from pathlib import Path
from .descriptions import EXPERIMENT, EXPERIMENT_RESULT, INSTRUMENT
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS_LIST, KEY_VALUE_OBJECT
from chord_metadata_service.restapi.schema_utils import tag_ids_and_describe, get_schema_app_id, sub_schema_uri

__all__ = ["EXPERIMENT_SCHEMA", "EXPERIMENT_RESULT_SCHEMA", "INSTRUMENT_SCHEMA"]

base_uri = get_schema_app_id(Path(__file__).parent.name)

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
        "url": {
            "type": "string",
            "format": "uri",
            # only supported schemes allowed, in alphabetical order:
            "pattern": r"^(data|doi|drs|file|ftp|https?|s3)://",
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
            "enum": ["Bisulfite-Seq", "RNA-Seq", "ChIP-Seq", "WES", "WGS", "RAD-Seq", "AMPLICON", "Other"]
        },
        "library_source": {
            "type": "string",
            "enum": ["Genomic", "Genomic Single Cell", "Transcriptomic", "Transcriptomic Single Cell",
                     "Metagenomic", "Metatranscriptomic", "Synthetic", "Viral RNA", "Other"]
        },
        "library_selection": {
            "type": "string",
            "enum": ["Random", "PCR", "Random PCR", "RT-PCR", "MF", "Exome capture", "Other"]
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
