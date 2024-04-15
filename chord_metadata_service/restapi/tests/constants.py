from copy import deepcopy


INVALID_FHIR_BUNDLE_1 = {
    "resourceType": "NotBundle",
    "entry": [
        {
            "test": "required resource is not present"
        }
    ]
}

INVALID_SUBJECT_NOT_PRESENT = {
    "resourceType": "Bundle",
    "entry": [
        {
            "resource": {
                "id": "1c8d2ee3-2a7e-47f9-be16-abe4e9fa306b",
                "resourceType": "Observation",
                "status": "final",
                "code": {
                    "coding": [
                        {
                            "code": "718-7",
                            "display": "Hemoglobin [Mass/volume] in Blood",
                            "system": "http://loinc.org"
                        }
                    ],
                    "text": "Hemoglobin [Mass/volume] in Blood"
                }
            }
        }
    ]
}

VALID_INDIVIDUAL_1 = {
    "id": "ind:NA19648",
    "date_of_birth": "1993-10-04",
    "time_at_last_encounter": {
        "age": {
            "iso8601duration": "P28Y"
        }
    },
    "sex": "FEMALE",
    "karyotypic_sex": "XX",
    "taxonomy": {
        "id": "NCBITaxon:9606",
        "label": "Homo sapiens"
    },
    "extra_properties": {
        "smoking": "Passive smoker",
        "covidstatus": "Positive",
        "death_dc": "Alive",
        "mobility": "I am unable to walk about",
        "date_of_consent": "2020-08-20",
        "lab_test_result_value": 705.91
    }
}

VALID_INDIVIDUAL_2 = {
    "id": "ind:HG00096",
    "date_of_birth": "1924-03-29",
    "time_at_last_encounter": {
        "age": {
            "iso8601duration": "P97Y"
        }
    },
    "sex": "MALE",
    "karyotypic_sex": "XY",
    "taxonomy": {
        "id": "NCBITaxon:9606",
        "label": "Homo sapiens"
    },
    "extra_properties": {
        "smoking": "Not specified",
        "covidstatus": "Positive",
        "death_dc": "Alive",
        "mobility": "I have no problems in walking about",
        "date_of_consent": "2020-04-04",
        "lab_test_result_value": 581.97
    }
}

VALID_INDIVIDUAL_3 = {
    "id": "ind:HG00100",
    "date_of_birth": "1997-10-29",
    "time_at_last_encounter": {
        "age": {
            "iso8601duration": "P24Y"
        }
    },
    "sex": "FEMALE",
    "karyotypic_sex": "XX",
    "taxonomy": {
        "id": "NCBITaxon:9606",
        "label": "Homo sapiens"
    },
    "extra_properties": {
        "smoking": "Former smoker",
        "covidstatus": "Negative",
        "death_dc": "Deceased",
        "mobility": "I have moderate problems in walking about",
        "date_of_consent": "2022-01-25",
        "lab_test_result_value": 464.22
    }
}

VALID_INDIVIDUAL_4 = {
    "id": "ind:HG00103",
    "date_of_birth": "1972-06-16",
    "time_at_last_encounter": {
        "age": {
            "iso8601duration": "P49Y"
        }
    },
    "sex": "MALE",
    "karyotypic_sex": "XY",
    "taxonomy": {
        "id": "NCBITaxon:9606",
        "label": "Homo sapiens"
    },
    "extra_properties": {
        "smoking": "Not specified",
        "covidstatus": "Indeterminate",
        "death_dc": "Deceased",
        "mobility": "I have slight problems in walking about",
        "date_of_consent": "2021-03-03",
        "lab_test_result_value": 786.86
    }
}

VALID_INDIVIDUAL_5 = {
    "id": "ind:HG00104",
    "date_of_birth": "1972-06-16",
    "time_at_last_encounter": {
        "age": {
            "iso8601duration": "P49Y"
        }
    },
    "sex": "MALE",
    "karyotypic_sex": "XY",
    "taxonomy": {
        "id": "NCBITaxon:9606",
        "label": "Homo sapiens"
    },
    "extra_properties": {
        "smoking": "Not specified",
        "covidstatus": "Indeterminate",
        "death_dc": "Deceased",
        "mobility": "I have slight problems in walking about",
        "date_of_consent": "2021-03-03",
        "lab_test_result_value": 786.86
    }
}

VALID_INDIVIDUAL_6 = {
    "id": "ind:HG00105",
    "date_of_birth": "1972-06-16",
    "time_at_last_encounter": {
        "age": {
            "iso8601duration": "P49Y"
        }
    },
    "sex": "MALE",
    "karyotypic_sex": "XY",
    "taxonomy": {
        "id": "NCBITaxon:9606",
        "label": "Homo sapiens"
    },
    "extra_properties": {
        "smoking": "Not specified",
        "covidstatus": "Indeterminate",
        "death_dc": "Deceased",
        "mobility": "I have slight problems in walking about",
        "date_of_consent": "2021-03-03",
        "lab_test_result_value": 786.86
    }
}

VALID_INDIVIDUAL_7 = {
    "id": "ind:HG00106",
    "date_of_birth": "1972-06-16",
    "time_at_last_encounter": {
        "age": {
            "iso8601duration": "P49Y"
        }
    },
    "sex": "MALE",
    "karyotypic_sex": "XY",
    "taxonomy": {
        "id": "NCBITaxon:9606",
        "label": "Homo sapiens"
    },
    "extra_properties": {
        "smoking": "Not specified",
        "covidstatus": "Indeterminate",
        "death_dc": "Deceased",
        "mobility": "I have slight problems in walking about",
        "date_of_consent": "2021-03-03",
        "lab_test_result_value": 786.86
    }
}
VALID_INDIVIDUAL_8 = {
    "id": "ind:HG00107",
    "date_of_birth": "1972-06-16",
    "time_at_last_encounter": {
        "age": {
            "iso8601duration": "P49Y"
        }
    },
    "sex": "MALE",
    "karyotypic_sex": "XY",
    "taxonomy": {
        "id": "NCBITaxon:9606",
        "label": "Homo sapiens"
    },
    "extra_properties": {
        "smoking": "Not specified",
        "covidstatus": "Indeterminate",
        "death_dc": "Deceased",
        "mobility": "I have slight problems in walking about",
        "date_of_consent": "2021-03-03",
        "lab_test_result_value": 786.86
    }
}


VALID_INDIVIDUALS = [
    VALID_INDIVIDUAL_1,
    VALID_INDIVIDUAL_2,
    VALID_INDIVIDUAL_3,
    VALID_INDIVIDUAL_4,
    VALID_INDIVIDUAL_5,
    VALID_INDIVIDUAL_6,
    VALID_INDIVIDUAL_7,
    VALID_INDIVIDUAL_8,
]

VALID_PHENOPACKET_1 = {
    "id": "8670db4d-77ad-4bee-b38c-599453510c6a",
    "subject": {
        "id": "patient:1",
        "date_of_birth": "1967-01-01T00:00:00Z",
        "sex": "MALE",
        "time_at_last_encounter": {
            "age": {
                "iso8601duration": "P45Y",
            }
        },
        "extra_properties": {
            "education": "Bachelor's Degree"
        }
    },
    "meta_data": {
        "phenopacket_schema_version": "2.0",
        "created": "2023-09-12T00:25:54.662Z",
        "created_by": "David Lougheed",
        "submitted_by": "David Lougheed",
    }
}

VALID_PHENOPACKET_2 = {
    "id": "ae8fbf37-2029-4e07-87c2-f3fecb3c1f89",
    "subject": {
        "id": "patient:2",
        "date_of_birth": "1967-01-01T00:00:00Z",
        "sex": "MALE",
        "time_at_last_encounter": {
            "age": {
                "iso8601duration": "P45Y",
            }
        },
        "extra_properties": {
            "education": "Bachelor's Degree"
        }
    },
    "meta_data": {
        "phenopacket_schema_version": "2.0",
        "created": "2023-09-12T00:25:54.662Z",
        "created_by": "David Lougheed",
        "submitted_by": "David Lougheed",
    }
}

VALID_PHENOPACKET_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "katsu:phenopackets",
    "type": "object",
    "properties": {
        "phenopacket": {
            "$id": "katsu:phenopackets:phenopacket",
            "type": "object",
            "properties": {
                "biosamples": {
                    "type": "array",
                    "items": {
                        "$id": "katsu:phenopackets:biosample",
                        "type": "object",
                        "properties": {
                            "original_biosample_extra_prop": {"type": "string"}
                        }
                    }
                },
                "extra_properties": {
                    "type": "object",
                    "properties": {
                        "original_pheno_extra_prop": {"type": "string"}
                    }
                }
            }
        }
    }
}

VALID_EXTRA_PROPERTIES_EXTENSIONS = {
    "phenopacket": {
        "schema_type": "PHENOPACKET",
        "required": True,
        "json_schema": {
            "type": "object",
            "properties": {
                "new_pheno_prop": {"type": "string"}
            },
        }
    },
    "biosample": {
        "schema_type": "BIOSAMPLE",
        "required": False,
        "json_schema": {
            "type": "object",
            "properties": {
                "new_biosample_prop": {"type": "string"}
            }
        }
    }
}

extra_properties_with_list = {
    "smoking": "Former smoker",
    "covidstatus": "Positive",
    "death_dc": "Alive",
    "mobility": "I have slight problems in walking about",
    "date_of_consent": "2021-03-03",
    "lab_test_result_value": 699.86,
    "baseline_creatinine": [100, 120]
}

extra_properties_with_dict = {
    "smoking": "Former smoker",
    "covidstatus": "Positive",
    "death_dc": "Alive",
    "mobility": "I have slight problems in walking about",
    "date_of_consent": "2021-03-03",
    "lab_test_result_value": 699.86,
    "baseline_creatinine": {
        "test_key_1": 120,
        "test_key_2": "test_value_2"
    }
}


INDIVIDUALS_NOT_ACCEPTED_DATA_TYPES_LIST = [
    {**item, "extra_properties": extra_properties_with_list} for item in deepcopy(VALID_INDIVIDUALS)
]

INDIVIDUALS_NOT_ACCEPTED_DATA_TYPES_DICT = [
    {**item, "extra_properties": extra_properties_with_dict} for item in deepcopy(VALID_INDIVIDUALS)
]
