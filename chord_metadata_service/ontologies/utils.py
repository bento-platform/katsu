import xmltodict


def readXsdSimpleTypeValues(xsd_file_path: str, type_name: str):
    """Reads an XML Schema Definition (XSD) file and returns a type's values.
    The XSD file is parsed using xmltodict following this spec:
    https://www.xml.com/pub/a/2006/05/31/converting-between-xml-and-json.html
    """
    sra_file = open(xsd_file_path).read()
    sra_experiment_data = xmltodict.parse(sra_file, namespaces={'xs': None})
    simple_types = {sp["@name"]: sp for sp in sra_experiment_data["schema"]["simpleType"]}
    target_type = simple_types[type_name]
    values = [val['@value'] for val in target_type['restriction']['enumeration']]
    return values
