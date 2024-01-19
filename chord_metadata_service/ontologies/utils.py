import os
from typing import List
import xmltodict
from pathlib import Path

XSD_ONTOLOGIES_PATH = Path("chord_metadata_service/ontologies/xsd/")
SRA_EXPERIMENT_FILE_NAME = "SRA.experiment.xsd.xml"


def read_xsd_simple_type_values(xsd_file_name: str, type_name: str) -> List[str]:
    """Reads an XML Schema Definition (XSD) file and returns a type's values.
    The XSD file is parsed using xmltodict following this spec:
    https://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html
    """
    xsd_file_path = os.path.join(XSD_ONTOLOGIES_PATH, xsd_file_name)
    with open(xsd_file_path, "r") as file:
        xsd_file = file.read()

    xsd_data = xmltodict.parse(xsd_file, namespaces={"xs": None})
    simple_types = {sp["@name"]: sp for sp in xsd_data["schema"]["simpleType"]}
    target_type = simple_types[type_name]
    values = [val["@value"] for val in target_type["restriction"]["enumeration"]]
    return values
