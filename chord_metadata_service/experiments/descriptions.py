# Portions of this text (c) International Human Epigenome Consortium (https://github.com/IHEC)
# Licensed under the Apache License 2.0

from chord_metadata_service.restapi.description_utils import EXTRA_PROPERTIES, ontology_class


EXPERIMENT = {
    "description": "Experiment related metadata.",
    "properties": {
        "id": "An arbitrary identifier for the experiment.",

        "reference_registry_id": "The IHEC EpiRR ID for this dataset, only for IHEC Reference Epigenome datasets. "
                                 "Otherwise leave empty.",
        "qc_flags": {
            "description": "Any quality control observations can be noted here. This field can be omitted if empty",
            "items": "A quality control observation.",
        },
        "experiment_type": "(Controlled Vocabulary) The assay target (e.g. ‘DNA Methylation’, ‘mRNA-Seq’, ‘smRNA-Seq’, "
                           "'Histone H3K4me1').",
        "experiment_ontology": {
            "description": "Links to experiment ontology information (e.g. via the OBI ontology.)",
            "items": ontology_class("describing the experiment"),
        },
        "molecule_ontology": {
            "description": "Links to molecule ontology information (e.g. via the SO ontology.)",
            "items": ontology_class("describing a molecular property"),
        },
        "molecule": "(Controlled Vocabulary) The type of molecule that was extracted from the biological material."
                    "Include one of the following: total RNA, polyA RNA, cytoplasmic RNA, nuclear RNA, small RNA, "
                    "genomic DNA, protein, or other.",
        "library_strategy": "(Controlled Vocabulary) The assay used. These are defined within the SRA metadata "
                            "specifications with a controlled vocabulary (e.g. ‘Bisulfite-Seq’, ‘RNA-Seq’, ‘ChIP-Seq’)."
                            " For a complete list, see https://www.ebi.ac.uk/ena/submit/reads-library-strategy.",
        "extraction_protocol": "The protocol used to isolate the extract material.",
        "file_location": "The location of the file that contains the analysis of sequencing data.",
        "biosample": "Biosample on which this experiment was done.",

        **EXTRA_PROPERTIES
    }
}

EXPERIMENT_RESULT = {
    "description": "Experiment result metadata.",
    "properties": {
        "identifier": "An arbitrary identifier for an experiment result.",
        "description": "Description of an experiment result.",
        "filename": "The name of the file containing the result.",
        "file_format": "(Controlled Vocabulary) File format.",
        "creation_date": "The date when the experiment result file was created.",
        **EXTRA_PROPERTIES
    }
}
