import json
import os
import sys


__all__ = ["EXAMPLE_INGEST_PHENOPACKET", "EXAMPLE_INGEST_OUTPUTS"]

current_dir = os.path.join(os.path.dirname(sys.path[0]), os.path.dirname(__file__))

with open(os.path.join(current_dir, "example_phenopacket.json"), "r") as pf:
    EXAMPLE_INGEST_PHENOPACKET = json.load(pf)

EXAMPLE_INGEST_OUTPUTS = {
    "json_document": os.path.join(os.path.dirname(__file__), "example_phenopacket.json"),
}
