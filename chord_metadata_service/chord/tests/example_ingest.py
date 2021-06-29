import json
import os


__all__ = ["EXAMPLE_INGEST_PHENOPACKET", "EXAMPLE_INGEST_OUTPUTS",
           "EXAMPLE_INGEST_EXPERIMENT", "EXAMPLE_INGEST_OUTPUTS_EXPERIMENT"]

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
