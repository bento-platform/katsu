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
    "age": {
        "age": "P28Y"
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
    "age": {
        "age": "P97Y"
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
    "age": {
        "age": "P24Y"
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
    "age": {
        "age": "P49Y"
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
    "age": {
        "age": "P49Y"
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
    "age": {
        "age": "P49Y"
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
    "age": {
        "age": "P49Y"
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
    "age": {
        "age": "P49Y"
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

VALID_INDIVIDUALS = [VALID_INDIVIDUAL_1, VALID_INDIVIDUAL_2, VALID_INDIVIDUAL_3, VALID_INDIVIDUAL_4,
                     VALID_INDIVIDUAL_5, VALID_INDIVIDUAL_6, VALID_INDIVIDUAL_7, VALID_INDIVIDUAL_8]


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


CONFIG_FIELDS_TEST = {
    "sex": {
        "type": "string",
        "enum": [
            "Male",
            "Female"
        ],
        "title": "Sex"
    },
    "age": {
        "type": "number",
        "title": "Age",
        "bin_size": 10
    },
    "extra_properties": {
        "smoking": {
            "type": "string",
            "enum": [
                "Non-smoker",
                "Smoker",
                "Former smoker",
                "Passive smoker",
                "Not specified"
            ],
            "title": "Smoking"
        },
        "covidstatus": {
            "type": "string",
            "enum": [
                "Positive",
                "Negative",
                "Indeterminate"
            ],
            "title": "Covidstatus"
        },
        "death_dc": {
            "type": "string",
            "enum": [
                "Alive",
                "Deceased"
            ],
            "title": "Death"
        },
        "lab_test_result_value": {
            "type": "number",
            "title": "Lab test result",
            "minimum": 0,
            "maximum": 999.99
        },
        "baseline_creatinine": {
            "type": "number",
            "title": "Baseline creatinine"
        },
        "date_of_consent": {
            "type": "string",
            "format": "date",
            "title": "Date of consent"
        }
    }
}

CONFIG_FIELDS_TEST_NO_EXTRA_PROPERTIES = {
    "sex": {
        "type": "string",
        "enum": [
            "Male",
            "Female"
        ],
        "title": "Sex",
        "bin_size": 10
    }
}
