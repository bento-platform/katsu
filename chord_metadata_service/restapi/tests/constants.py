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


CONFIG_PUBLIC_TEST = {
    "overview": [
        {
            "section_title": "First Section",
            "charts": [
                {"field": "age", "chart_type": "bar"},
                {"field": "sex", "chart_type": "pie"},
            ]
        },
        {
            "section_title": "Second Section",
            "charts": [
                {"field": "date_of_consent", "chart_type": "bar"},
                {"field": "smoking", "chart_type": "bar"},
                {"field": "baseline_creatinine", "chart_type": "bar"}
            ]
        }
    ],
    "search": [
        {
            "section_title": "First Section",
            "fields": [
                "sex", "age", "smoking", "covidstatus", "death_dc",
                "lab_test_result_value", "baseline_creatinine", "date_of_consent"
            ]
        }
    ],
    "fields": {
        "sex": {
            "mapping": "individual/sex",
            "title": "Sex",
            "description": "Sex at birth",
            "datatype": "string",
            "config": {
                "enum": None
            }
        },
        "age": {
            "mapping": "individual/age_numeric",
            "title": "Age",
            "description": "Age at arrival",
            "datatype": "number",
            "config": {
                "bin_size": 10,
                "taper_left": 10,
                "taper_right": 100,
                "units": "years",
                "minimum": 0,
                "maximum": 100
            }
        },
        "smoking": {
            "mapping": "individual/extra_properties/smoking",
            "title": "Smoking",
            "description": "Smoking exposure",
            "datatype": "string",
            "config": {
                "enum": [
                    "Non-smoker",
                    "Smoker",
                    "Former smoker",
                    "Passive smoker",
                    "Not specified"
                ]
            }
        },
        "covidstatus": {
            "mapping": "individual/extra_properties/covidstatus",
            "title": "Covid status",
            "description": "Covid status",
            "datatype": "string",
            "config": {
                "enum": [
                    "Positive",
                    "Negative",
                    "Indeterminate"
                ]
            }
        },
        "death_dc": {
            "mapping": "individual/extra_properties/death_dc",
            "title": "Death",
            "description": "Death status",
            "datatype": "string",
            "config": {
                "enum": [
                    "Alive",
                    "Deceased"
                ]
            }
        },
        "lab_test_result_value": {
            "mapping": "individual/extra_properties/lab_test_result_value",
            "title": "Lab Test Result",
            "description": "This acts as a placeholder for numeric values",
            "datatype": "number",
            "config": {
                "bin_size": 50,
                "taper_left": 50,
                "taper_right": 800,
                "minimum": 0,
                "maximum": 1000,
                "units": "mg/L"
            }
        },
        "baseline_creatinine": {
            "mapping": "individual/extra_properties/baseline_creatinine",
            "title": "Creatinine",
            "description": "Baseline Creatinine",
            "datatype": "number",
            "config": {
                "bin_size": 50,
                "taper_left": 50,
                "taper_right": 200,
                "minimum": 30,
                "maximum": 600,
                "units": "mg/L"
            }
        },
        "date_of_consent": {
            "mapping": "individual/extra_properties/date_of_consent",
            "title": "Verbal consent date",
            "description": "Date of initial verbal consent(participant, legal representative or tutor), yyyy-mm-dd",
            "datatype": "date",
            "config": {
                "bin_by": "month"
            }
        }
    },
    "rules": {
        "count_threshold": 5,
        "max_query_parameters": 2
    }
}

CONFIG_PUBLIC_TEST_SEARCH_SEX_ONLY = deepcopy(CONFIG_PUBLIC_TEST)
CONFIG_PUBLIC_TEST_SEARCH_SEX_ONLY["search"][0]["fields"] = ["sex"]

CONFIG_PUBLIC_TEST_SEARCH_UNSET_FIELDS = deepcopy(CONFIG_PUBLIC_TEST)
CONFIG_PUBLIC_TEST_SEARCH_UNSET_FIELDS["fields"].update([
    ("unset_date",
     {
        "mapping": "individual/extra_properties/unset_date",
        "title": "Some date",
        "description": "Some date",
        "datatype": "date",
        "config": {
            "bin_by": "month"
        }
     }),
    ("unset_numeric",
     {
        "mapping": "individual/extra_properties/unset_numeric",
        "title": "Some measure",
        "description": "Some measure",
        "datatype": "number",
        "config": {
            "bin_size": 50,
            "taper_left": 50,
            "taper_right": 500,
            "minimum": 0,
            "maximum": 600,
            "units": "mg/L"
        }
     }),
    ("unset_category",
     {
        "mapping": "individual/extra_properties/unset_category",
        "title": "Some things",
        "description": "Some things",
        "datatype": "string",
        "config": {
            "enum": None
        }
     })
])
