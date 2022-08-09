import uuid
import random
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


def generate_random_date(years_from: int, years_to: int):
    # generates random date in the format YYYY-MM-DD, e.g. 2020-01-01
    start_date = date.today() - relativedelta(years=years_from)
    end_date = date.today() - relativedelta(years=years_to)
    delta = end_date - start_date
    random_number = random.randint(1, delta.days)
    new_date = start_date + timedelta(days=random_number)
    return new_date.strftime('%Y-%m-%d')


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

CSV_HEADER = "Id,Sex,Date of birth,Taxonomy,Karyotypic sex,Race,Ethnicity,Age,Diseases,Created,Updated"
INDIVIDUAL_1_CSV = "patient:1,FEMALE,1960-01-01,human,UNKNOWN_KARYOTYPE,,,P45Y - P49Y,,--IGNORE--,--IGNORE--"
INDIVIDUAL_2_CSV = "patient:2,MALE,1967-01-01,human,UNKNOWN_KARYOTYPE,,,P55Y,,--IGNORE--,--IGNORE--"


def generate_valid_individual():
    return {
        "id": str(uuid.uuid4()),
        "taxonomy": {
            "id": "NCBITaxon:9606",
            "label": "human"
        },
        "age": {
            "age": f"P{str(random.randrange(16, 89))}Y{str(random.randrange(1, 12))}M{str(random.randrange(1, 31))}D"
        },
        "sex": random.choice(["MALE", "FEMALE", "UNKNOWN_SEX", "OTHER_SEX"]),
        "extra_properties": {
            "smoking": random.choice(["Non-smoker", "Smoker", "Former smoker", "Passive smoker", "Not specified"]),
            "death_dc": random.choice(["Alive", "Deceased"]),
            "covidstatus": random.choice(["Positive", "Negative"]),
            "lab_test_result_value": round(random.uniform(0, 999.99), 2),
            "baseline_creatinine": round(random.uniform(30, 600), 0),
            "date_of_consent": generate_random_date(3, 0)
        }
    }
