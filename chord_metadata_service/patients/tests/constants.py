from typing import Tuple, Optional
import uuid
import random
from datetime import date, timedelta
import isodate


def generate_date_in_range(lower_year: int, upper_year: int):
    # generates a random date contained between lower_year and upper_year
    lower_date = date(lower_year, 1, 1)
    upper_date = date(upper_year, 1, 1)
    delta = upper_date - lower_date
    random_day_in_range = random.randint(1, delta.days)
    new_date = lower_date + timedelta(days=random_day_in_range)
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
        "age_range": {
            "start" : {
                "iso8601duration": "P45Y"
            },
            "end": {
                "iso8601duration": "P49Y"
            }
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


CSV_HEADER = "Id,Sex,Date of birth,Taxonomy,Karyotypic sex,Age,Diseases,Created,Updated"
INDIVIDUAL_1_CSV = "patient:1,FEMALE,1960-01-01,human,UNKNOWN_KARYOTYPE,P45Y - P49Y,,--IGNORE--,--IGNORE--"
INDIVIDUAL_2_CSV = "patient:2,MALE,1967-01-01,human,UNKNOWN_KARYOTYPE,P50Y,,--IGNORE--,--IGNORE--"


def generate_valid_individual(age=None, age_range=None, gen_random_age: Optional[Tuple[int, int]]=None,
                              date_of_consent_range: Tuple[int, int] = (2020, 2023)):
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
            "date_of_consent": generate_date_in_range(date_of_consent_range[0], date_of_consent_range[1]),
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
