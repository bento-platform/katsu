import uuid
import random

VALID_INDIVIDUAL = {
    "id": "patient:1",
    "taxonomy": {
        "id": "NCBITaxon:9606",
        "label": "human"
    },
    "date_of_birth": "1960-01-01",
    "age": {
        "start": {
            "age": "P45Y"
        },
        "end": {
            "age": "P49Y"
        }
    },
    "sex": "FEMALE",
    "active": True
}

INVALID_INDIVIDUAL = {
    "id": "patient:1",
    "taxonomy": {
        "id": "NCBITaxon:9606"
    },
    "date_of_birth": "1960-01-01",
    "age": {
        "start": {
            "age": "P45Y"
        },
        "end": {
            "age": "P49Y"
        }
    },
    "sex": "FEM",
    "active": True
}

VALID_INDIVIDUAL_2 = {
    "id": "patient:2",
    "taxonomy": {
        "id": "NCBITaxon:9606",
        "label": "human"
    },
    "date_of_birth": "1967-01-01",
    "age": {
        "age": "P55Y"
    },
    "sex": "MALE",
    "active": True
}


def generate_valid_individual():
    return {
        "id": str(uuid.uuid4()),
        "taxonomy": {
            "id": "NCBITaxon:9606",
            "label": "human"
        },
        "age": {
            "age": f"P{str(random.randrange(16, 89))}Y"
        },
        "sex": random.choice(["MALE", "FEMALE", "UNKNOWN_SEX", "OTHER_SEX"]),
        "extra_properties": {
            "smoking": random.choice(["Non-smoker", "Smoker", "Former smoker", "Passive smoker", "Not specified"]),
            "death": random.choice(["Alive", "Deceased"]),
            "test_result": random.choice(["Positive", "Negative"])
        }
    }
