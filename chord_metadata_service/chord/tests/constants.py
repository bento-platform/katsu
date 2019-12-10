__all__ = [
    "VALID_DATA_USE_1",
    "VALID_PROJECT_1",
    "valid_dataset_1",
    "TEST_SEARCH_QUERY_1",
    "TEST_SEARCH_QUERY_2",
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


def valid_dataset_1(project_id):
    return {
        "title": "Dataset 1",
        "description": "Test Dataset",
        "data_use": VALID_DATA_USE_1,
        "project": project_id
    }


TEST_SEARCH_QUERY_1 = ["#eq", ["#resolve", "subject", "sex"], "FEMALE"]
TEST_SEARCH_QUERY_2 = ["#eq", ["#resolve", "subject", "sex"], "MALE"]
