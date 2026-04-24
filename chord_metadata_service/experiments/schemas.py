from django.conf import settings
from referencing import Registry, Resource
from .descriptions import EXPERIMENT, EXPERIMENT_RESULT, INSTRUMENT
from chord_metadata_service.restapi.constants import MODEL_ID_PATTERN
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS, EXTRA_PROPERTIES_SCHEMA
from chord_metadata_service.restapi.schema_utils import tag_ids_and_describe, sub_schema_uri

__all__ = [
    "experiment_base_uri",
    "experiment_resource",
    "experiment_registry",
    "experiment_resolver",
    "DATA_FILE_OR_RECORD_URL_SCHEMA",
    "EXPERIMENT_RESULT_FILE_INDEX_SCHEMA",
    "EXPERIMENT_RESULT_FILE_INDEX_LIST_SCHEMA",
    "EXPERIMENT_SCHEMA",
    "EXPERIMENT_RESULT_SCHEMA",
    "INSTRUMENT_SCHEMA",
]

experiment_base_uri = f"{settings.SCHEMAS_BASE_URL}/experiment"

DATA_FILE_OR_RECORD_URL_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": sub_schema_uri(experiment_base_uri, "data_file_or_record_url"),
    "title": "Data file or record URL",
    "description": "A URL of a particular scheme, pointing to a data file OR a DRS record which itself points to a "
                   "data file.",
    "type": "string",
    "format": "uri",
    # only supported schemes allowed, in alphabetical order:
    "pattern": r"^(data|doi|drs|file|ftp|https?|s3)://",
}

EXPERIMENT_RESULT_FILE_INDEX_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": sub_schema_uri(experiment_base_uri, "experiment_result_file_index"),
    "title": "Experiment result file index schema",
    "description": "Schema for describing an object representing an index of an experiment result file.",
    "type": "object",
    "properties": {
        "url": DATA_FILE_OR_RECORD_URL_SCHEMA,
        "format": {
            "type": "string",
            "enum": [
                "BAI",  # BAM index files ( http://samtools.github.io/hts-specs/SAMv1.pdf "BAI" )
                "BGZF",  # BGZip index files (often .gzi)
                "CRAI",  # CRAM index files ( https://samtools.github.io/hts-specs/CRAMv3.pdf "CRAM index" )
                "CSI",  # See http://samtools.github.io/hts-specs/CSIv1.pdf
                "TABIX",  # See https://samtools.github.io/hts-specs/tabix.pdf
                "TRIBBLE",
            ],
        }
    },
    "required": ["url", "format"],
}
EXPERIMENT_RESULT_FILE_INDEX_LIST_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": sub_schema_uri(experiment_base_uri, "experiment_result_file_index_list"),
    "title": "Experiment result file index list schema",
    "description": "Schema for describing a list of object representing an indices of an experiment result file.",
    "type": "array",
    "items": EXPERIMENT_RESULT_FILE_INDEX_SCHEMA,
}

EXPERIMENT_RESULT_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": sub_schema_uri(experiment_base_uri, "experiment_result"),
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
        "url": DATA_FILE_OR_RECORD_URL_SCHEMA,
        "indices": EXPERIMENT_RESULT_FILE_INDEX_LIST_SCHEMA,
        "storage_uri": {
            "type": "string",
            "format": "uri",  # e.g., a file URI or an S3 uri
        },
        "storage_server": {
            "type": "string",
            # should be formatted as a fully-qualified domain name
            # contextual use:
            #   - for a file URI, this SHOULD be the server it's located on.
            #   - for an S3 URI, this SHOULD be the S3 host (to allow specific regions, or alternate hosts like SD4H)
            # for other uses, this may be specified or excluded as desired.
        },
        "genome_assembly_id": {
            "type": "string",
        },
        "file_format": {
            "type": "string",
            "enum": ["SAM", "BAM", "CRAM", "VCF", "BCF", "MAF", "GVCF", "BigWig", "BigBed", "FASTA", "FASTQ", "TAB",
                     "SRA", "SRF", "SFF", "GFF", "PDF", "CSV", "TSV", "JPEG", "PNG", "GIF", "HTML", "MARKDOWN",
                     "MP3", "M4A", "MP4", "DOCX", "XLS", "XLSX", "UNKNOWN", "OTHER"]
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
        "extra_properties": EXTRA_PROPERTIES_SCHEMA,
    }
}, EXPERIMENT_RESULT)


INSTRUMENT_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": sub_schema_uri(experiment_base_uri, "instrument"),
    "title": "Instrument schema",
    "description": "Schema for describing an instrument used for a sequencing experiment.",
    "type": "object",
    "properties": {
        "identifier": {
            "type": "string"
        },
        "device": {
            "type": "string"
        },
        "device_ontology": ONTOLOGY_CLASS,
        "description": {
            "type": "string"
        },
        "extra_properties": EXTRA_PROPERTIES_SCHEMA,
    }
}, INSTRUMENT)


EXPERIMENT_SCHEMA = tag_ids_and_describe({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": experiment_base_uri,
    "title": "Experiment schema",
    "description": "Schema for describing an experiment.",
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "pattern": MODEL_ID_PATTERN,
        },
        "study_type": {
            "type": "string",
            "enum": ["Genomics", "Epigenomics", "Metagenomics", "Transcriptomics",
                     "Serology", "Metabolomics", "Proteomics",
                     "3D Genomics", "Multi-Omics", "Other"]
        },
        "experiment_type": {
            "type": "string",
            # experiment_type values are aligned with NCBI SRA, ENCODE, and common omics conventions.
            "enum": [
                # Genomics
                "WGS", "WES", "Genotyping", "Viral WGS", "DNA metabarcoding",
                # Transcriptomics
                "mRNA-Seq", "RNA-Seq", "smRNA-Seq", "miRNA-Seq", "scRNA-Seq", "snRNA-Seq",
                # Epigenomics
                "DNA Methylation", "WGBS", "ChIP-Seq", "CUT&RUN", "CUT&Tag", "ATAC-Seq", "scATAC-Seq",
                # 3D Genomics
                "Hi-C", "scChIC-seq",
                # Multi-Omics
                "Multiome",
                # Other omics
                "Proteomic profiling", "Neutralizing antibody titers", "Metabolite profiling",
                "Antibody measurement", "Other",
            ]
        },
        "experiment_ontology": ONTOLOGY_CLASS,
        "molecule": {
            "type": "string",
            "enum": ["total RNA", "polyA RNA", "cytoplasmic RNA", "nuclear RNA",
                     "small RNA", "genomic DNA", "protein", "chromatin", "Other"]
        },
        "molecule_ontology": ONTOLOGY_CLASS,
        "library_strategy": {
            "type": "string",
            "enum": ["WGS", "WES", "RNA-Seq", "Bisulfite-Seq", "ChIP-Seq", "ATAC-Seq",
                     "Hi-C", "RAD-Seq", "ddRAD-Seq", "GT-Seq", "AMPLICON", "GBS", "Other"]
        },
        "library_source": {
            "type": "string",
            "enum": ["Genomic", "Genomic Single Cell", "Transcriptomic", "Transcriptomic Single Cell",
                     "Metagenomic", "Metatranscriptomic", "Environmental DNA", "Environmental RNA",
                     "Synthetic", "Viral RNA", "Other"]
        },
        "library_selection": {
            "type": "string",
            "enum": ["Random", "PCR", "Random PCR", "RT-PCR", "MF", "Exome capture",
                     "ChIP", "PolyA", "Restriction Digest", "Other"]
        },
        "library_layout": {
            "type": "string",
            "enum": ["Single", "Paired"]
        },
        "library_id": {
            "type": "string",
            "pattern": MODEL_ID_PATTERN,
        },
        "library_description": {
            "type": "string",
            "description": "Details about library construction."
        },
        "library_extract_id": {
            "type": "string"
        },
        "insert_size": {
            "type": "integer",
            "description": "Insert size (integer)."
        },
        "description": {
            "type": "string",
            "description": "Experimental design description."
        },
        "protocol_url": {
            "type": "string",
            "format": "uri",
            "description": "URL to the protocol."
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
        "extra_properties": EXTRA_PROPERTIES_SCHEMA,
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
}, EXPERIMENT, override_children=True)

# URI referencing
experiment_resource = Resource.from_contents(EXPERIMENT_SCHEMA)
experiment_registry = Registry().with_resource(uri=experiment_base_uri, resource=experiment_resource)
experiment_resolver = experiment_registry.resolver(base_uri=experiment_base_uri)
