from chord_metadata_service.restapi.description_utils import EXTRA_PROPERTIES, ontology_class


# TODO: This is part of another app
INDIVIDUAL = {
    "description": "A subject of a phenopacket, representing either a human (typically) or another organism.",
    "properties": {
        # Phenopackets / shared
        "id": "A unique researcher-specified identifier for an individual.",
        "alternate_ids": {
            "description": "A list of alternative identifiers for an individual.",
            "items": "One of possibly many alternative identifiers for an individual."
        },
        "date_of_birth": "A timestamp representing an individual's date of birth; either exactly or imprecisely.",
        "age": None,  # TODO: Age or AgeRange
        "sex": "The phenotypic sex of an individual, as would be determined by a midwife or physician at birth.",
        "karyotypic_sex": "The karyotypic sex of an individual.",
        "taxonomy": ontology_class("specified when more than one organism may be studied. It is advised that codes"
                                   "from the NCBI Taxonomy resource are used, e.g. NCBITaxon:9606 for humans"),

        # FHIR-specific
        "active": "Whether a patient's record is in active use.",
        "deceased": "Whether a patient is deceased.",

        # mCode-specific
        "race": "A code for a person's race (mCode).",
        "ethnicity": "A code for a person's ethnicity (mCode).",
        "comorbid_condition": "One or more conditions that occur with primary condition.",
        "ecog_performance_status": "Value representing the Eastern Cooperative Oncology Group performance status.",
        "karnofsky": "Value representing the Karnofsky Performance status.",

        **EXTRA_PROPERTIES
    }
}
