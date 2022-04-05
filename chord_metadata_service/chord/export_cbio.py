import logging
import csv
from typing import TextIO

from .export_utils import ExportFileContext, ExportError

from chord_metadata_service.chord.models import Dataset
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets import models as pm

__all__ = [
    "StudyExport",
]

logger = logging.getLogger(__name__)

# predefined filenames recognized by cBioPortal
STUDY_FILENAME        = "meta_study.txt"
SAMPLE_DATA_FILENAME  = "data_clinical_sample.txt"
SAMPLE_META_FILENAME  = "meta_clinical_sample.txt"
PATIENT_DATA_FILENAME = "data_clinical_patient.txt"
PATIENT_META_FILENAME = "meta_clinical_patient.txt"

PATIENT_DATATYPE = 'PATIENT'
SAMPLE_DATATYPE  = 'SAMPLE'


def StudyExport (tmp_path: str, dataset_id: str):
    """Export a given Project as a cBioPortal study"""
    #TODO: a Dataset is a Study (associated with a publication), not a Project!
    if Dataset.objects.count == 0:
        raise ExportError("No Dataset to export")
    dataset = Dataset.objects.get(identifier=dataset_id)
    cbio_study_id = str(dataset.identifier)

    # create a context wrapping a tmp folder for export
    with ExportFileContext(tmp_path, cbio_study_id) as file_export:

        # Export study file
        with open(file_export.getPath(STUDY_FILENAME), 'w') as file_study:
            StudyExportMeta(dataset, file_study)

        # export patients.
        with open(file_export.getPath(PATIENT_DATA_FILENAME), 'w') as file_patient:
            # Note: plural in `phenopackets` is intentional (related_name property in model)
            indiv = Individual.objects.filter(phenopackets__table__ownership_record__dataset_id=dataset.identifier)
            IndividualExport(indiv, file_patient)

        with open(file_export.getPath(PATIENT_META_FILENAME), 'w') as file_patient_meta:
            ClinicalMetaExport(cbio_study_id, PATIENT_DATATYPE, file_patient_meta)

        # export samples
        with open(file_export.getPath(SAMPLE_DATA_FILENAME), 'w') as file_sample:
            sampl = pm.Biosample.objects.filter(phenopacket__table__ownership_record__dataset_id=dataset.identifier)
            SampleExport(sampl, file_sample)

        with open(file_export.getPath(SAMPLE_META_FILENAME), 'w') as file_sample_meta:
            ClinicalMetaExport(cbio_study_id, SAMPLE_DATATYPE, file_sample_meta)




def StudyExportMeta (dataset: Dataset, file_handle: TextIO):
    """
    Study meta data file generation
    """
    lines = dict()
    lines['type_of_cancer']          = "mixed"   #TODO: find if this information is available. !IMPORTANT! uses Oncotree codes
    lines['cancer_study_identifier'] = str(dataset.identifier)
    lines['name']                    = dataset.title
    lines['description']             = dataset.description

    # optional fields
    if len(dataset.primary_publications):
        lines['citation']           = dataset.primary_publications[0]
    # pmid: unvailable
    # groups: unused for authentication
    # add_global_case_list: ?
    # tags_file: ?
    # reference_genome: ?

    for field, value in lines.items():
        file_handle.write(f"{field}: {value}\n")


def ClinicalMetaExport (study_id: str, datatype: str, file_handle: TextIO):
    """
    Clinical Metadata files generation (samples or patients)
    """
    lines = dict()
    lines['cancer_study_identifier'] = study_id
    lines['genetic_alteration_type'] = 'CLINICAL'
    if datatype == SAMPLE_DATATYPE:
        lines['datatype'] = 'SAMPLE_ATTRIBUTES'
        lines['data_filename'] = SAMPLE_DATA_FILENAME
    else:
        lines['datatype'] = 'PATIENT_ATTRIBUTES'
        lines['data_filename'] = PATIENT_DATA_FILENAME

    for field, value in lines.items():
        file_handle.write(f"{field}: {value}\n")


def IndividualExport(results, file_handle: TextIO):
    """
    Renders Individuals as a clinical_patient text file suitable for
    importing by cBioPortal.

    cBioPortal Patients fields specs:
    ---------------------------------
    Required:
    - PATIENT_ID
    Special columns:
    - OS_STATUS, OS_MONTHS overall survivall. Status can be 1:DECEASED, 0:LIVING
    - DFS_STATUS, DFS_MONTHS disease free
    - PATIENT_DISPLAY_NAME
    - GENDER or SEX
    - AGE
    - TUMOR_SITE
    """

    individuals = []
    for individual in results:
        ind_obj = {
            'id': individual.id,
            'sex': individual.sex,
        }
        individuals.append(ind_obj)

    columns = individuals[0].keys()
    headers = individual_to_patient_header(columns)

    file_handle.writelines([line + '\n' for line in headers])
    dict_writer = csv.DictWriter(file_handle, fieldnames=columns, delimiter='\t')
    dict_writer.writerows(individuals)


def SampleExport (results, file_handle: TextIO):
    """
    Renders Biosamples as a clinical_sample text file suitable for
    importing by cBioPortal.

    cBioPortal Sample fields specs:
    ---------------------------------
    Required:
    - PATIENT_ID
    - SAMPLE_ID

    Special columns:
    - For pan-cancer summary statistics tab:
        - CANCER_TYPE as an Oncotree code
        - CANCER_TYPE_DETAILED
    - SAMPLE_DISPLAY_NAME
    - SAMPLE_CLASS
    - METASTATIC_SITE / PRIMARY_SITE overrides the patients level attribute TUMOR_SITE
    - SAMPLE_TYPE, TUMOR_TISSUE_SITE, TUMOR_TYPE can have the following values (are displayed with a distinct color in the timelines):
        - "recurrence", "recurred", "progression"
        - "metastatic", "metastasis"
        - "primary" or any other value
    - KNOWN_MOLECULAR_CLASSIFIER
    - GLEASON_SCORE (prostate cancer)
    - HISTOLOGY
    - TUMOR_STAGE_2009
    - TUMOR_GRADE
    - ETS_RAF_SPINK1_STATUS
    - TMPRSS2_ERG_FUSION_STATUS
    - ERG_FUSION_ACGH
    - SERUM_PSA
    - DRIVER_MUTATIONS
    """

    samples = []
    for sample in results:
        sample_obj = {
            'individual_id': sample.individual.id,
            'id': sample.id
        }
        if sample.sampled_tissue:
            sample_obj['tissue_label'] = sample.sampled_tissue.get('label', '')

        samples.append(sample_obj)

    columns = samples[0].keys()
    headers = biosample_to_sample_header(columns)

    file_handle.writelines([line + '\n' for line in headers])
    dict_writer = csv.DictWriter(file_handle, fieldnames=columns, delimiter='\t')
    dict_writer.writerows(samples)


class cbioportal_clinical_header_generator ():
    """
    Generates cBioPortal data files headers based on field names from katsu models.
    """

    fields_mapping = {}

    def __init__(self, mappings = {}):
        self.fields_mapping = mappings

    def make_header (self, fields: list):
        """
        Maps a list of field names to a 5 rows header
        suitable for cBioPortal clinical data files.
        """

        field_properties = []
        for field in fields:
            if field in self.fields_mapping:
                field_properties.append(self.fields_mapping[field])
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



def individual_to_patient_header (fields: list):
    """
    Maps a list of Individual field names to a 5 rows header
    suitable for cBioPortal data_clinical_patient.txt file.
    """

    # predefined mappings from Individual keys to cBioPortal field properties
    fields_mapping = {
        'id': ('Patient Identifier', 'Patient Identifier', 'STRING', '1', 'PATIENT_ID'),
        'sex': ('Sex', 'Sex', 'STRING', '1', 'SEX'),
    }

    cbio_header = cbioportal_clinical_header_generator(fields_mapping);
    return cbio_header.make_header(fields)

def biosample_to_sample_header (fields: list):
    """
    Maps a list of biosamples field names to a 5 rows header
    suitable for cBioPortal data_sample_patient.txt file.
    """

    # predefined mappings from Samples keys to cBioPortal field properties
    fields_mapping = {
        'individual_id': ('Patient Identifier', 'Patient Identifier', 'STRING', '1', 'PATIENT_ID'),
        'id': ('Sample Identifier', 'Sample Identifier', 'STRING', '1', 'SAMPLE_ID'),
        'tissue_label': ('Sampled Tissue', 'Sampled Tissue', 'STRING', '1', 'TISSUE_LABEL')
    }

    cbio_header = cbioportal_clinical_header_generator(fields_mapping);
    return cbio_header.make_header(fields)
