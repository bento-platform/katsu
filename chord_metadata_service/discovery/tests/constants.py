from bento_lib.discovery.models.config import DiscoveryConfig
from copy import deepcopy

DISCOVERY_CONFIG_TEST_DICT = {
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
                {"field": "diagnostic_markers", "chart_type": "pie"},
                {"field": "measurement_tumor_length", "chart_type": "bar"},
                {"field": "tissues", "chart_type": "pie"}
            ]
        }
    ],
    "search": [
        {
            "section_title": "First Section",
            "fields": ["sex", "age", "tissues", "extraction_protocol"]
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
        "tissues": {
            "mapping": "biosample/sampled_tissue/label",
            "mapping_for_search_filter": "individual/biosamples/sampled_tissue/label",
            "title": "Tissue",
            "description": "Tissue from which the biosample was extracted",
            "datatype": "string",
            "config": {
                "enum": None
            }
        },
        "diagnostic_markers": {
            "mapping": "individual/phenopackets/biosamples/diagnostic_markers",
            "group_by": "label",
            "title": "Diagnostic Markers",
            "description": "Markers used for diagnosis",
            "datatype": "string",
            "config": {
                "enum": None
            }
        },
        "measurement_tumor_length": {
            "mapping": "individual/phenopackets/measurements",
            "group_by": "assay/id",
            "group_by_value": "NCIT:C200479",
            "value_mapping": "value/quantity/value",
            "title": "Tumor lengths",
            "description": "measured tumor lengths in millimeters",
            "datatype": "number",
            "config": {
                "minimum": 0,
                "maximum": 200,
                "bin_size": 20,
                "taper_left": 0,
                "taper_right": 200,
                "units": "mm"
            }
        },
        "extraction_protocol": {
            "mapping": "experiment/extraction_protocol",
            "mapping_for_search_filter": "individual/biosamples/experiment/extraction_protocol",
            "title": "Experiment Extraction Protocol",
            "description": "experiment extraction protocol",
            "datatype": "string",
            "config": {
                "enum": ["NGS"]
            },
        },
    },
    "rules": {
        "count_threshold": 5,
        "max_query_parameters": 2
    }
}

DISCOVERY_CONFIG_TEST: DiscoveryConfig = DiscoveryConfig.model_validate(DISCOVERY_CONFIG_TEST_DICT)

DISCOVERY_CONFIG_EXTRA_PROPERTIES_DICT: dict = deepcopy(DISCOVERY_CONFIG_TEST_DICT)
DISCOVERY_CONFIG_EXTRA_PROPERTIES_DICT["fields"].update({
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
            "bins": [200, 300, 500, 1000, 1500, 2000],
            "minimum": 0,
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
    },
})
DISCOVERY_CONFIG_EXTRA_PROPERTIES_DICT["search"][0]["fields"].extend(
    ["smoking", "covidstatus", "death_dc", "lab_test_result_value", "baseline_creatinine", "date_of_consent"]
)
DISCOVERY_CONFIG_EXTRA_PROPERTIES_DICT["overview"].extend([
    {
        "section_title": "Dataset individual exta properties specific Section",
        "charts": [
            {"field": "date_of_consent", "chart_type": "bar"},
            {"field": "smoking", "chart_type": "bar"},
            {"field": "baseline_creatinine", "chart_type": "bar"},
        ]
    },
    {
        "section_title": "Lab test results section",
        "charts": [
            {"field": "lab_test_result_value", "chart_type": "bar"},
        ]
    },
])

DISCOVERY_CONFIG_EXTRA_PROPERTIES: DiscoveryConfig = DiscoveryConfig.model_validate(
    DISCOVERY_CONFIG_EXTRA_PROPERTIES_DICT
)

CONFIG_PUBLIC_TEST_SEARCH_SEX_ONLY_DICT: dict = deepcopy(DISCOVERY_CONFIG_TEST_DICT)
CONFIG_PUBLIC_TEST_SEARCH_SEX_ONLY_DICT["search"][0]["fields"] = ["sex"]
CONFIG_PUBLIC_TEST_SEARCH_SEX_ONLY: DiscoveryConfig = DiscoveryConfig.model_validate(
    CONFIG_PUBLIC_TEST_SEARCH_SEX_ONLY_DICT
)

CONFIG_PUBLIC_TEST_SEARCH_UNSET_FIELDS_DICT: dict = deepcopy(DISCOVERY_CONFIG_TEST_DICT)
CONFIG_PUBLIC_TEST_SEARCH_UNSET_FIELDS_DICT["fields"].update([
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
CONFIG_PUBLIC_TEST_SEARCH_UNSET_FIELDS: DiscoveryConfig = DiscoveryConfig.model_validate(
    CONFIG_PUBLIC_TEST_SEARCH_UNSET_FIELDS_DICT
)
