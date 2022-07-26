import json
import os


__all__ = ["EXAMPLE_INGEST_PHENOPACKET", "EXAMPLE_INGEST_OUTPUTS",
           "EXAMPLE_INGEST_EXPERIMENT", "EXAMPLE_INGEST_OUTPUTS_EXPERIMENT",
           "EXAMPLE_INGEST_INVALID_EXPERIMENT", "EXAMPLE_INGEST_INVALID_PHENOPACKET",
           "EXAMPLE_INGEST_MULTIPLE_PHENOPACKETS", "EXAMPLE_INGEST_MULTIPLE_OUTPUTS"]

with open(os.path.join(os.path.dirname(__file__), "example_phenopacket.json"), "r") as pf:
    EXAMPLE_INGEST_PHENOPACKET = json.load(pf)

EXAMPLE_INGEST_OUTPUTS = {
    "json_document": os.path.join(os.path.dirname(__file__), "example_phenopacket.json"),
}


with open(os.path.join(os.path.dirname(__file__), "example_experiment.json"), "r") as exp:
    EXAMPLE_INGEST_EXPERIMENT = json.load(exp)

EXAMPLE_INGEST_OUTPUTS_EXPERIMENT = {
    "json_document": os.path.join(os.path.dirname(__file__), "example_experiment.json"),
}


with open(os.path.join(os.path.dirname(__file__), "example_invalid_experiment.json"), "r") as pf:
    EXAMPLE_INGEST_INVALID_EXPERIMENT = json.load(pf)


with open(os.path.join(os.path.dirname(__file__), "example_invalid_phenopacket.json"), "r") as pf:
    EXAMPLE_INGEST_INVALID_PHENOPACKET = json.load(pf)


with open(os.path.join(os.path.dirname(__file__), "example_multiple_phenopackets.json"), "r") as pf:
    EXAMPLE_INGEST_MULTIPLE_PHENOPACKETS = json.load(pf)

EXAMPLE_INGEST_MULTIPLE_OUTPUTS = {
    "json_document": os.path.join(os.path.dirname(__file__), "example_multiple_phenopackets.json"),
}
