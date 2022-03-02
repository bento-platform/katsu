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
            "death_dc": random.choice(["Alive", "Deceased"]),
            "covidstatus": random.choice(["Positive", "Negative"]),
            "lab_test_result_value": round(random.uniform(0, 999.99), 2),
            "baseline_creatinine": round(random.uniform(30, 600), 0)
        }
    }
