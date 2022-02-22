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
