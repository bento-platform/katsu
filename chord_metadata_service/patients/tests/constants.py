from typing import Tuple, Optional
import uuid
import random
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import isodate


def generate_random_date(years_from: int, years_to: int):
    # generates random date in the format YYYY-MM-DD, e.g. 2020-01-01
    start_date = date.today() - relativedelta(years=years_from)
    end_date = date.today() - relativedelta(years=years_to)
    delta = end_date - start_date
    random_number = random.randint(1, delta.days)
    new_date = start_date + timedelta(days=random_number)
    return new_date.strftime('%Y-%m-%d')


VITAL_STATUS_DECEASED = {
    "status": "DECEASED",
    "time_of_death": {
        "timestamp": "2020-03-28T00:00:00Z"
    },
    "cause_of_death": {
        "id": "MONDO:0100096",
        "label": "COVID-19"
    },
    "survival_time_in_days": 20
}

VITAL_STATUS_ALIVE = {
    "status": "ALIVE"
}

VALID_INDIVIDUAL = {
    "id": "patient:1",
    "taxonomy": {
        "id": "NCBITaxon:9606",
        "label": "human"
    },
    "date_of_birth": "1960-01-01",
    "time_at_last_encounter": {
        "age": {
            "iso8601duration": "P49Y"
        }
    },
    "sex": "FEMALE",
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
    "time_at_last_encounter": {
        "age": {
            "iso8601duration": "P50Y"
        }
    },
    "sex": "MALE",
}

CSV_HEADER = "Id,Sex,Date of birth,Taxonomy,Karyotypic sex,Race,Ethnicity,Diseases,Created,Updated"
INDIVIDUAL_1_CSV = "patient:1,FEMALE,1960-01-01,human,UNKNOWN_KARYOTYPE,,,,--IGNORE--,--IGNORE--"
INDIVIDUAL_2_CSV = "patient:2,MALE,1967-01-01,human,UNKNOWN_KARYOTYPE,,,,--IGNORE--,--IGNORE--"


def generate_valid_individual(age=None, age_range=None, gen_random_age: Optional[Tuple[int, int]] = None):
    if age and age_range:
        raise ValueError("Cannot use 'age' and 'age_range' simultaneously for Individual.time_at_last_encounter.")
    individual = {
        "id": str(uuid.uuid4()),
        "taxonomy": {
            "id": "NCBITaxon:9606",
            "label": "human"
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

    if age:
        individual["time_at_last_encounter"] = {"age": age}
    if age_range:
        individual["time_at_last_encounter"] = {"age_range": age_range}
    if gen_random_age:
        min_age, max_age = gen_random_age
        years = random.randrange(min_age, max_age)
        individual["time_at_last_encounter"] = {
            "age": isodate.duration_isoformat(isodate.Duration(years=years)),
        }
    return individual
