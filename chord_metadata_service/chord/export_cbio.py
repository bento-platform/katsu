import logging
import csv
from typing import TextIO, Callable
from django.db.models import F

from chord_metadata_service.experiments.models import ExperimentResult

from .export_utils import ExportError

from chord_metadata_service.chord.models import Dataset
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets import models as pm

__all__ = [
    "study_export",
]

logger = logging.getLogger(__name__)

# predefined filenames recognized by cBioPortal
STUDY_FILENAME = "meta_study.txt"
SAMPLE_DATA_FILENAME = "data_clinical_sample.txt"
SAMPLE_META_FILENAME = "meta_clinical_sample.txt"
PATIENT_DATA_FILENAME = "data_clinical_patient.txt"
PATIENT_META_FILENAME = "meta_clinical_patient.txt"
MUTATION_META_FILENAME = "meta_mutation.txt"
MUTATION_DATA_FILENAME = "data_mutations_extended.txt"   # is generated during workflow from files coming from DRS
MAF_LIST_FILENAME = 'maf_list.tsv'  # Accessory file
CASE_LIST_SEQUENCED = "case_lists/case_list_sequenced.txt"  # in a subfolder


CBIO_FILES_SET = frozenset({
    STUDY_FILENAME,
    SAMPLE_DATA_FILENAME,
    SAMPLE_META_FILENAME,
    PATIENT_DATA_FILENAME,
    PATIENT_META_FILENAME,
    MUTATION_META_FILENAME,
    # MUTATION_DATA_FILENAME is not part of the files generated here
    CASE_LIST_SEQUENCED
})

PATIENT_DATATYPE = 'PATIENT'
SAMPLE_DATATYPE = 'SAMPLE'


def study_export(getPath: Callable[[str], str], dataset_id: str):
    """Export a given Project as a cBioPortal study"""
    # TODO: a Dataset is a Study (associated with a publication), not a Project!
    if Dataset.objects.count == 0:
        raise ExportError("No Dataset to export")
    dataset = Dataset.objects.get(identifier=dataset_id)
    cbio_study_id = str(dataset.identifier)

    # Export study file
    with open(getPath(STUDY_FILENAME), 'w') as file_study:
        study_export_meta(dataset, file_study)

    # Export patients.
    with open(getPath(PATIENT_DATA_FILENAME), 'w') as file_patient:
        # Note: plural in `phenopackets` is intentional (related_name property in model)
        indiv = Individual.objects.filter(phenopackets__table__ownership_record__dataset_id=dataset.identifier)
        individual_export(indiv, file_patient)

    with open(getPath(PATIENT_META_FILENAME), 'w') as file_patient_meta:
        clinical_meta_export(cbio_study_id, PATIENT_DATATYPE, file_patient_meta)

    # Export samples
    with open(getPath(SAMPLE_DATA_FILENAME), 'w') as file_sample:
        sampl = pm.Biosample.objects.filter(phenopacket__table__ownership_record__dataset_id=dataset.identifier)\
            .annotate(phenopacket_subject_id=F("phenopacket__subject"))
        sample_export(sampl, file_sample)

    with open(getPath(SAMPLE_META_FILENAME), 'w') as file_sample_meta:
        clinical_meta_export(cbio_study_id, SAMPLE_DATATYPE, file_sample_meta)

    # .maf files stored
    with open(getPath(MAF_LIST_FILENAME), 'w') as file_maf_list:
        # TODO: change to MAF format when it is added to Katsu
        exp_res = ExperimentResult.objects.filter(experiment__table__ownership_record__dataset_id=dataset.identifier)\
            .filter(file_format='VCF') \
            .annotate(biosample_id=F("experiment__biosample"))
        maf_list(exp_res, file_maf_list)

    with open(getPath(MUTATION_META_FILENAME), 'w') as file_mutation_meta:
        mutation_meta_export(cbio_study_id, file_mutation_meta)

    with open(getPath(CASE_LIST_SEQUENCED), 'w') as file_case_list:
        case_list_export(cbio_study_id, file_case_list)


def study_export_meta(dataset: Dataset, file_handle: TextIO):
    """
    Study meta data file generation
    """
    lines = dict()
    lines['type_of_cancer'] = "mixed"   # TODO: find if this information is available. !IMPORTANT! uses Oncotree codes
    lines['cancer_study_identifier'] = str(dataset.identifier)
    lines['name'] = dataset.title
    lines['description'] = dataset.description

    # optional fields
    if len(dataset.primary_publications):
        lines['citation'] = dataset.primary_publications[0]
    # pmid: unvailable
    # groups: unused for authentication
    # add_global_case_list: ?
    # tags_file: ?
    # reference_genome: ?

    for field, value in lines.items():
        file_handle.write(f"{field}: {value}\n")


def clinical_meta_export(study_id: str, datatype: str, file_handle: TextIO):
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


def individual_export(results, file_handle: TextIO):
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


def sample_export(results, file_handle: TextIO):
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
    - SAMPLE_TYPE, TUMOR_TISSUE_SITE, TUMOR_TYPE can have the following values
        (are displayed with a distinct color in the timelines):
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

        # sample.inidividual may be null: use Phenopacket model Subject field
        # instead if available or skip.
        subject_id = None
        if sample.individual is not None:
            subject_id = sample.individual
        elif sample.phenopacket_subject_id is not None:
            subject_id = sample.phenopacket_subject_id
        else:
            continue

        sample_obj = {
            'individual_id': subject_id,
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


def maf_list(results, file_handle: TextIO):
    """
    List of maf files/biosample ids associated with this dataset.

    The biosample IDs are added to the maf file before it is catenated to the
    other maf files for cbioportal ingestion.
    """

    experiments = []
    for experiment in results:
        experiments.append((experiment.filename, experiment.biosample_id))

    csv_writer = csv.writer(file_handle, delimiter='\t')
    csv_writer.writerows(experiments)


def mutation_meta_export(study_id: str, file_handle: TextIO):
    """
    Mutation data, metadata file generation

    specifications:
    cancer_study_identifier: same value as specified in study meta file
    genetic_alteration_type: MUTATION_EXTENDED
    datatype: MAF
    stable_id: mutations
    show_profile_in_analysis_tab: true
    profile_name: A name for the mutation data, e.g., "Mutations".
    profile_description: A description of the mutation data, e.g., "Mutation data from whole exome sequencing.".
    data_filename: your data file
    gene_panel (optional): gene panel stable id. See Gene panels for mutation data.
    swissprot_identifier (optional): accession or name, indicating the type of identifier in the SWISSPROT column
    variant_classification_filter (optional): List of Variant_Classifications values to be filtered out.
    namespaces (optional): Comma-delimited list of namespaces to import.
    """
    lines = dict()
    lines['cancer_study_identifier'] = study_id
    lines['genetic_alteration_type'] = 'MUTATION_EXTENDED'
    lines['datatype'] = 'MAF'
    lines['stable_id'] = 'mutations'
    lines['show_profile_in_analysis_tab'] = 'true'
    lines['profile_name'] = 'Mutations'
    lines['profile_description'] = 'Mutation data from whole exome sequencing'  # TODO: extract from experiments
    lines['data_filename'] = MUTATION_DATA_FILENAME

    for field, value in lines.items():
        file_handle.write(f"{field}: {value}\n")


def case_list_export(study_id: str, file_handle: TextIO):
    """
    Case list. For now, sequenced data only.

    Specifications:
    cancer_study_identifier: same value as specified in study meta file
    stable_id: it must contain the cancer_study_identifier followed by an underscore.
        Typically, after this a relevant suffix, e.g., _custom, is added.
        There are some naming rules to follow if you want the case list to be
        selected automatically in the query UI base on the selected sample
        profiles. See subsection below.
    case_list_name: A name for the patient list, e.g., "All Tumors".
    case_list_description: A description of the patient list, e.g.,
        "All tumor samples (825 samples).".
    case_list_ids: A tab-delimited list of sample ids from the dataset.
    case_list_category: Optional alternative way of linking your case list to a
        specific molecular profile. E.g. setting this to all_cases_with_cna_data
        will signal to the portal that this is the list of samples to be associated
        with CNA data in some of the analysis.
    """
    lines = dict()
    lines['cancer_study_identifier'] = study_id
    lines['stable_id'] = f'{study_id}_sequenced'
    lines['case_list_name'] = 'All samples'
    lines['case_list_description'] = 'All samples'
    # case_list_ids will be added as part of the workflow for now. When Katsu is
    # reliably holding the information about which mafs files are actually
    # available from DRS for a given experiment, the list of cases ids could be
    # built entirely here

    for field, value in lines.items():
        file_handle.write(f"{field}: {value}\n")


class CbioportalClinicalHeaderGenerator():
    """
    Generates cBioPortal data files headers based on field names from katsu models.
    """

    fields_mapping = {}

    def __init__(self, mappings={}):
        self.fields_mapping = mappings

    def make_header(self, fields: list):
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

    cbio_header = CbioportalClinicalHeaderGenerator(fields_mapping)
    return cbio_header.make_header(fields)


def biosample_to_sample_header(fields: list):
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

    cbio_header = CbioportalClinicalHeaderGenerator(fields_mapping)
    return cbio_header.make_header(fields)
