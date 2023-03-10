from chord_metadata_service.restapi.description_utils import ontology_class

AGE = {
    "description": "An ISO8601 duration string (e.g. P40Y10M05D for 40 years, 10 months, 5 days) representing an age "
                   "of a subject.",
    "help": "Age of a subject."
}

AGE_RANGE = {
    "description": "Age range of a subject (e.g. when a subject's age falls into a bin.)",
    "properties": {
        "start": "An ISO8601 duration string representing the start of the age range bin.",
        "end": "An ISO8601 duration string representing the end of the age range bin."
    }
}

AGE_NESTED = {
    "description": AGE["description"],
    "properties": {
        "age": AGE
    }
}

GESTATIONAL_AGE = {
    "description": ("Gestational age (or menstrual age) is the time elapsed between the first "
                    "day of the last normal menstrual period and the day of delivery."),
    "properties": {
        "weeks": "Completed weeks of gestation according to the above definition. REQUIRED.",
        "days": "RECOMMENDED, If available"
    }
}

TIME_STAMP = {
    "description": "In phenopackets we define the Timestamp as an ISO-8601 date time string."
}

TIME_INTERVAL = {
    "description": "Indicates an interval of time",
    "properties": {
        "start": TIME_STAMP,
        "end": TIME_STAMP
    }
}

TIME_ELEMENT = {
    "description": "This element intends to bundle all of the various ways of denoting time or age in phenopackets "
                   "schema.",
    "properties": {
        "gestational_age": GESTATIONAL_AGE,
        "age": AGE,
        "age_range": AGE_RANGE,
        "ontology_class": ontology_class("indicates the age of the individual as an ontology class"),
        "timestamp": TIME_STAMP,
        "interval": TIME_INTERVAL}}
