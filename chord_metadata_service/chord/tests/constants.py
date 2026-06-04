from chord_metadata_service.restapi.models import SchemaType

__all__ = [
    "VALID_DATA_USE_1",
    "VALID_PROJECT_1",
    "VALID_PROJECT_2",
    "VALID_DATASET_PRIMARY_CONTACT",
    "valid_dataset",
    "PROJECT_JSON_SCHEMA_MISSING_PROJECT",
    "valid_project_json_schema",
    "valid_phenotypic_feature",
    "TEST_SEARCH_QUERY_1",
    "TEST_SEARCH_QUERY_2",
    "TEST_SEARCH_QUERY_3",
    "TEST_SEARCH_QUERY_4",
    "TEST_SEARCH_QUERY_5",
    "TEST_SEARCH_QUERY_6",
    "TEST_SEARCH_QUERY_7",
    "TEST_SEARCH_QUERY_8",
    "TEST_SEARCH_QUERY_9",
    "TEST_SEARCH_QUERY_10",
]

VALID_DATA_USE_1 = {
    "consent_code": {
        "primary_category": {"code": "GRU"},
        "secondary_categories": [
            {"code": "GSO"},
            {"code": "RU"}
        ]
    },
    "data_use_requirements": [
        {"code": "COL"},
        {"code": "MOR"},
        {"code": "US"}
    ]
}

VALID_PROJECT_1 = {
    "title": "Project 1",
    "description": "Some description",
}

VALID_PROJECT_2 = {
    "title": "Project 2",
    "description": "Some description too",
}

DEFAULT_PROJECT_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "string_prop": {"type": "string"},
        "bool_prop": {"type": "boolean"},
        "obj_prop": {"type": "object"}
    }
}


VALID_DATASET_PRIMARY_CONTACT = {"type": "person", "name": "Test Contact", "roles": []}


def valid_dataset(project_id, title="Dataset 1", **kwargs):
    return {
        "schema_version": "1.0",
        "title": title,
        "description": "Test Dataset",
        "primary_contact": VALID_DATASET_PRIMARY_CONTACT,
        "project": str(project_id),
        **kwargs,
    }


PROJECT_JSON_SCHEMA_MISSING_PROJECT = {
    "required": False,
    "schema_type": SchemaType.PHENOPACKET,
    "json_schema": DEFAULT_PROJECT_JSON_SCHEMA,
}


def valid_project_json_schema(project_id: str,
                              schema_type=SchemaType.PHENOPACKET,
                              required: bool = False,
                              json_schema: dict = DEFAULT_PROJECT_JSON_SCHEMA):
    return {
        "project": project_id,
        "required": required,
        "schema_type": schema_type,
        "json_schema": json_schema
    }


def valid_phenotypic_feature(biosample=None, phenopacket=None):
    return dict(
        description='This is a test phenotypic feature',
        pftype={
            "id": "HP:0000520",
            "label": "Proptosis"
        },
        biosample=biosample,
        phenopacket=phenopacket
    )


TEST_SEARCH_QUERY_1 = ["#eq", ["#resolve", "subject", "sex"], "FEMALE"]
TEST_SEARCH_QUERY_2 = ["#eq", ["#resolve", "subject", "sex"], "MALE"]
TEST_SEARCH_QUERY_3 = ["#eq", ["#resolve", "phenotypic_features", "[item]", "type", "label"], "Proptosis"]
TEST_SEARCH_QUERY_4 = ["#eq", ["#resolve", "biosamples", "[item]", "sampled_tissue", "label"],
                       "wall of urinary bladder"]
TEST_SEARCH_QUERY_5 = ["#ico", ["#resolve", "phenotypic_features", "[item]", "type", "label"], "proptosis"]
TEST_SEARCH_QUERY_6 = ["#ico", ["#resolve", "biosamples", "[item]", "sampled_tissue", "label"],
                       "URINARY BLADDER"]
TEST_SEARCH_QUERY_7 = ["#eq", ["#resolve", "experiment_results", "[item]", "file_format"], "VCF"]
TEST_SEARCH_QUERY_8 = ["#eq", ["#resolve", "experiment_type"], "DNA Methylation"]
TEST_SEARCH_QUERY_9 = ["#eq", ["#resolve", "subject", "id"], "patient:1"]
TEST_SEARCH_QUERY_10 = ["#in", ["#resolve", "biosamples", "[item]", "id"],
                        ["#list", "biosample_id:1", "biosample_id:2"]]
