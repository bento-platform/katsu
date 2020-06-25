from .mcode_profiles import *

MCODE_PROFILES_MAPPING = {
    "patient": {
        "profile": MCODE_PATIENT,
        "properties_profile": {
            "comorbid_condition": MCODE_COMORBID_CONDITION,
            "ecog_performance_status": MCODE_ECOG_PERFORMANCE_STATUS,
            "karnofsky": MCODE_KARNOFSKY
        }
    },
    "genetic_specimen": {
        "profile": MCODE_GENETIC_SPECIMEN,
        "properties_profile": {
            "laterality": MCODE_LATERALITY
        }
    },
    "cancer_genetic_variant": {
        "profile": MCODE_CANCER_GENETIC_VARIANT
    },
    "genomic_region_studied": {
        "profile": MCODE_GENOMIC_REGION_STUDIED
    },
    "genomics_report": {
        "profile": MCODE_GENOMICS_REPORT
    },
    "labs_vital": {
        "profile": MCODE_TUMOR_MARKER
    },
    "cancer_condition": {
        "profile": {
            "primary": MCODE_PRIMARY_CANCER_CONDITION,
            "secondary": MCODE_SECONDARY_CANCER_CONDITION
        },
        "properties_profile": {
            "histology_morphology_behavior": MCODE_HISTOLOGY_MORPHOLOGY_BEHAVIOR
        }
    },
    "tnm_staging": {
        "properties_profile": {
            "stage_group": {
                "clinical": MCODE_TNM_CLINICAL_STAGE_GROUP,
                "pathologic": MCODE_TNM_PATHOLOGIC_STAGE_GROUP
            },
            "primary_tumor_category": {
                "clinical": MCODE_TNM_CLINICAL_PRIMARY_TUMOR_CATEGORY,
                "pathologic": MCODE_TNM_PATHOLOGIC_PRIMARY_TUMOR_CATEGORY
            },
            "regional_nodes_category": {
                "clinical": MCODE_TNM_CLINICAL_REGIONAL_NODES_CATEGORY,
                "pathologic": MCODE_TNM_PATHOLOGIC_REGIONAL_NODES_CATEGORY
            },
            "distant_metastases_category": {
                "clinical": MCODE_TNM_CLINICAL_DISTANT_METASTASES_CATEGORY,
                "pathologic": MCODE_TNM_PATHOLOGIC_DISTANT_METASTASES_CATEGORY
            }
        }
    },
    "cancer_related_procedure": {
        "profile": {
            "radiation": MCODE_CANCER_RELATED_RADIATION_PROCEDURE,
            "surgical": MCODE_CANCER_RELATED_SURGICAL_PROCEDURE
        }
    },
    "medication_statement": {
        "profile": MCODE_MEDICATION_STATEMENT,
        "properties_profile": {
            "termination_reason": MCODE_TERMINATION_REASON,
            "treatment_intent": MCODE_TREATMENT_INTENT
        }
    },
    "mcodepacket": {
        "properties_profile": {
            "cancer_disease_status": MCODE_CANCER_DISEASE_STATUS
        }
    }
}
