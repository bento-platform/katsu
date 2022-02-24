"""Katsu models fields to cBioportal fields declarations

This module contains utilities to generate cBioPortal data files headers 
based on field names from katsu models.
"""

def individual_to_patient_header(fields: list):
    """
    Maps a list of Individual field names to a 5 rows header
    suitable for cBioPortal data_clinical_patient.txt file.
    """

    # predefined mappings from Individual keys to cBioPortal field properties
    fields_mapping = {
        'id': ('Patient Identifier', 'Patient Identifier', 'STRING', '1', 'PATIENT_ID'),
        'sex': ('Sex', 'Sex', 'STRING', '1', 'SEX'),
    }

    field_properties = []
    for field in fields:
        if field in fields_mapping:
            field_properties.append(fields_mapping[field])
        else:
            fieldname = field.replace('_', ' ').capitalize()
            prop = (
                fieldname,  # display name
                fieldname,  # description
                'STRING',   # type !!!TODO: TYPE DETECTION!!!
                '1',        # priority (note: string here for use in join())
                field.upper()   # DB suitable identifier
            )
            field_properties.append(prop)

    # Transpose list of properties tuples per field to tuples of
    # field properties per property.
    rows = list(zip(*field_properties))

    # The 4 first rows are considered meta datas, prefixed by '#'.
    # The 5th row (DB field names) is a canonical TSV header.
    cbio_header = [
        '#' + '\t'.join(rows[0]),
        '#' + '\t'.join(rows[1]),
        '#' + '\t'.join(rows[2]),
        '#' + '\t'.join(rows[3]),
        '\t'.join(rows[4])
    ]

    return cbio_header
