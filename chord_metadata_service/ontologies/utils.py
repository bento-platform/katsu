from typing import List
import xmltodict


def read_xsd_simple_type_values(xsd_file_path: str, type_name: str) -> List[str]:
    """Reads an XML Schema Definition (XSD) file and returns a type's values.
    The XSD file is parsed using xmltodict following this spec:
    https://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html
    """
    with open(xsd_file_path, 'r') as file:
        xsd_file = file.read()
    xsd_data = xmltodict.parse(xsd_file, namespaces={'xs': None})
    simple_types = {sp["@name"]: sp for sp in xsd_data["schema"]["simpleType"]}
    target_type = simple_types[type_name]
    values = [val['@value'] for val in target_type['restriction']['enumeration']]
    return values
