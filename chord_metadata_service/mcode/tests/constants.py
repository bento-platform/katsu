VALID_INDIVIDUAL = {
    "id": "patient:1",
    "taxonomy": {
        "id": "NCBITaxon:9606",
        "label": "human"
    },
    "date_of_birth": "1960-01-01",
    "age": {
        "age": {
            "start": {
                "age": "P45Y"
            },
            "end": {
                "age": "P49Y"
            }
        }
    },
    "sex": "FEMALE",
    "active": True
}

VALID_GENETIC_VARIANT_TESTED = {
    "id": "variant_tested:01",
    "method": {
        "id": "C17003",
        "label": "Polymerase Chain Reaction"
    },
    "variant_tested_identifier": {
        "id": "360448",
        "label": "360448",
    },
    "variant_tested_hgvs_name": [
        "NC_000007.13:g.55086734A>G",
        "NC_000007.14:g.55019041A>G",
        "NM_001346897.2:c.-237A>G",
        "NM_001346898.2:c.-237A>G",
        "NM_001346899.1:c.-237A>G",
        "NM_001346941.2:c.-237A>G",
        "NM_005228.5:c.-237A>G",
        "NM_201282.2:c.-237A>G",
        "NM_201283.1:c.-237A>G",
        "NM_201284.2:c.-237A>G",
        "LRG_304t1:c.-237A>G",
        "LRG_304:g.5010A>G",
        "NG_007726.3:g.5010A>G"
    ],
    "variant_tested_description": "single nucleotide variant",
    "data_value": {
        "id": "LA6576-8",
        "label": "Positive",
    }
}

VALID_GENETIC_VARIANT_FOUND = {
    "id": "variant_found:01",
    "method": {
        "id": "C17003",
        "label": "Polymerase Chain Reaction"
    },
    "variant_found_identifier": {
        "id": "360448",
        "label": "360448",
    },
    "variant_found_hgvs_name": [
        "NC_000007.13:g.55086734A>G",
        "NC_000007.14:g.55019041A>G",
        "NM_001346897.2:c.-237A>G",
        "NM_001346898.2:c.-237A>G",
        "NM_001346899.1:c.-237A>G",
        "NM_001346941.2:c.-237A>G",
        "NM_005228.5:c.-237A>G",
        "NM_201282.2:c.-237A>G",
        "NM_201283.1:c.-237A>G",
        "NM_201284.2:c.-237A>G",
        "LRG_304t1:c.-237A>G",
        "LRG_304:g.5010A>G",
        "NG_007726.3:g.5010A>G"
    ],
    "variant_found_description": "single nucleotide variant",
    "genomic_source_class": {
        "id": "LA6684-0",
        "label": "Somatic",
    }
}


def valid_genetic_report(subject):
    return {
        "id": "genomics_report:01",
        "test_name": {
            "id": "GTR000567625.2",
            "label": "PREVENTEST",
        },
        "performing_ogranization_name": "Test organization",
        "specimen_type": {
            "id": "119342007 ",
            "label": "SAL (Saliva)",
        },
        "subject": subject,
    }


def valid_labs_vital(individual):
    return {
        "id": "labs_vital:01",
        "body_height": {
            "value": 1.70,
            "unit": "m"
        },
        "body_weight": {
            "value": 60,
            "unit": "kg"
        },
        "cbc_with_auto_differential_panel": ["Test"],
        "comprehensive_metabolic_2000": ["Test"],
        "blood_pressure_diastolic": {
            "value": 80,
            "unit": "mmHg"
        },
        "blood_pressure_systolic": {
            "value": 120,
            "unit": "mmHg"
        },
        "tumor_marker_test": {
            "code": {
                "coding": [
                    {
                        "code": "50610-5",
                        "display": "Alpha-1-Fetoprotein",
                        "system": "https://loinc.org/"
                    }
                ]
            },
            "data_value": {
                "value": 10,
                "unit": "ng/mL"
            }
        },
        "individual": individual,
    }


def valid_cancer_condition(subject):
    return {
        "id": "cancer_condition:01",
        "condition_type": "primary",
        "body_location_code": [
            {
                "id": "442083009",
                "label": "Anatomical or acquired body structure (body structure)"
            }
        ],
        "clinical_status": {
            "id": "active",
            "label": "Active"
        },
        "condition_code": {
            "id": "404087009",
            "label": "Carcinosarcoma of skin (disorder)",
        },
        "date_of_diagnosis": "2018-11-13T20:20:39+00:00",
        "histology_morphology_behavior": {
            "id": "372147008",
            "label": "Kaposi's sarcoma - category (morphologic abnormality)",
        },
        "subject": subject,
    }


def valid_tnm_staging(cancer_condition):
    return {
        "id": "tnm_staging:01",
        "tnm_type": "clinical",
        "stage_group": {
            "data_value": {
                "coding": [
                    {
                        "code": "123",
                        "display": "test",
                        "system": "https://example.com/path/resource.txt#fragment"
                    }
                ]
            }
        },
        "primary_tumor_category": {
            "data_value": {
                "coding": [
                    {
                        "code": "123",
                        "display": "test",
                        "system": "https://example.com/path/resource.txt#fragment"
                    }
                ]
            }
        },
        "regional_nodes_category": {
            "data_value": {
                "coding": [
                    {
                        "code": "123",
                        "display": "test",
                        "system": "https://example.com/path/resource.txt#fragment"
                    }
                ]
            }
        },
        "distant_metastases_category": {
            "data_value": {
                "coding": [
                    {
                        "code": "123",
                        "display": "test"
                    }
                ]
            }
        },
        "cancer_condition": cancer_condition,
    }
