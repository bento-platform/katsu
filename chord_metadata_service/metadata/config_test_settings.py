CONFIG_FIELDS_TEST = {
    "sex": {
        "type": "string",
        "enum": [
            "Male",
            "Female"
        ],
        "title": "Sex",
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
        }
    }
}
