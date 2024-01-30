import logging
import csv
from typing import Callable, TextIO
import re

from django.db.models import F

from .utils import ExportError

from chord_metadata_service.chord.models import Dataset
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets import models as pm
from chord_metadata_service.experiments.models import ExperimentResult

__all__ = [
    "STUDY_FILENAME",
    "SAMPLE_DATA_FILENAME",
    "SAMPLE_META_FILENAME",
    "PATIENT_DATA_FILENAME",
    "PATIENT_META_FILENAME",
    "MUTATION_META_FILENAME",
    "MUTATION_DATA_FILENAME",
    "MAF_LIST_FILENAME",
    "CASE_LIST_SEQUENCED",
    "CBIO_FILES_SET",

    "PATIENT_DATATYPE",
    "SAMPLE_DATATYPE",

    "REGEXP_INVALID_FOR_ID",

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
MAF_LIST_FILENAME = "maf_list.txt"  # Accessory file
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

PATIENT_DATATYPE = "PATIENT"
SAMPLE_DATATYPE = "SAMPLE"

# [     List
#   ^   not in...
#   a-z lowercase letter
#   A-Z uppercase
#   0-9 digit
#   _   underscore
#   \.  dot
#   \-  hyphen
# ]     Closing list
REGEXP_INVALID_FOR_ID = re.compile(r"[^a-zA-Z0-9_\.\-]")


def study_export(get_path: Callable[[str], str], dataset_id: str):
    """Export a given Project as a cBioPortal study"""
    # TODO: a Dataset is a Study (associated with a publication), not a Project!

    try:
        dataset = Dataset.objects.get(identifier=dataset_id)
    except Dataset.DoesNotExist:
        raise ExportError(f"no dataset exists with ID {dataset_id}")

    cbio_study_id = str(dataset.identifier)

    # Export study file
    with open(get_path(STUDY_FILENAME), "w", newline="\n") as file_study:
        study_export_meta(dataset, file_study)

    # Export patients.
    with open(get_path(PATIENT_DATA_FILENAME), "w", newline="\n") as file_patient:
        # Note: plural in `phenopackets` is intentional (related_name property in model)
        indiv = Individual.objects.filter(phenopackets__dataset_id=dataset.identifier)
        individual_export(indiv, file_patient)

    with open(get_path(PATIENT_META_FILENAME), "w", newline="\n") as file_patient_meta:
        clinical_meta_export(cbio_study_id, PATIENT_DATATYPE, file_patient_meta)

    # Export samples
    with open(get_path(SAMPLE_DATA_FILENAME), "w", newline="\n") as file_sample:
        sampl = pm.Biosample.objects.filter(phenopacket__dataset_id=dataset.identifier)
        sample_export(sampl, file_sample)

    with open(get_path(SAMPLE_META_FILENAME), "w", newline="\n") as file_sample_meta:
        clinical_meta_export(cbio_study_id, SAMPLE_DATATYPE, file_sample_meta)

    # .maf files stored
    with open(get_path(MAF_LIST_FILENAME), "w", newline="\n") as file_maf_list, \
         open(get_path(CASE_LIST_SEQUENCED), "w", newline="\n") as file_case_list:
        exp_res = (
            ExperimentResult.objects
            .filter(experiment__dataset_id=dataset.identifier, file_format="MAF")
            .annotate(biosample_id=F("experiment__biosample"))
        )

        maf_list(exp_res, file_maf_list)
        case_list_export(cbio_study_id, exp_res, file_case_list)

    with open(get_path(MUTATION_META_FILENAME), 'w', newline='\n') as file_mutation_meta:
        mutation_meta_export(cbio_study_id, file_mutation_meta)


def write_dict_in_cbioportal_format(lines: dict, file_handle: TextIO) -> None:
    for field, value in lines.items():
        file_handle.write(f"{field}: {value}\n")


def study_export_meta(dataset: Dataset, file_handle: TextIO) -> None:
    """
    Study meta data file generation
    """

    lines: dict[str, str] = {
        "type_of_cancer": "mixed",  # TODO: find if this information is available. !IMPORTANT! uses Oncotree codes
        "cancer_study_identifier": str(dataset.identifier),
        "name": dataset.title,
        "description": dataset.description,

        # pmid: unavailable
        # groups: unused for authentication

        "add_global_case_list": "true",  # otherwise causes an error at validation
        # tags_file: ?
        # reference_genome: ?  TODO
    }

    # optional fields
    if dataset.primary_publications:
        lines["citation"] = dataset.primary_publications[0]

    write_dict_in_cbioportal_format(lines, file_handle)


def clinical_meta_export(study_id: str, datatype: str, file_handle: TextIO):
    """
    Clinical Metadata files generation (samples or patients)
    """

    lines: dict[str, str] = {
        "cancer_study_identifier": study_id,
        "genetic_alteration_type": "CLINICAL",
    }

    if datatype == SAMPLE_DATATYPE:
        lines["datatype"] = "SAMPLE_ATTRIBUTES"
        lines["data_filename"] = SAMPLE_DATA_FILENAME
    else:
        lines["datatype"] = "PATIENT_ATTRIBUTES"
        lines["data_filename"] = PATIENT_DATA_FILENAME

    write_dict_in_cbioportal_format(lines, file_handle)


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

    individuals = [{
        'id': sanitize_id(individual.id),
        'sex': individual.sex,
    } for individual in results]

    columns = list(individuals[0].keys())
    headers = individual_to_patient_header(columns)

    file_handle.writelines([f"{line}\n" for line in headers])
    dict_writer = csv.DictWriter(file_handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
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
        if sample.individual is None:
            continue

        subject_id = sample.individual

        sample_obj = {
            "individual_id": sanitize_id(subject_id),
            "id": sanitize_id(sample.id)
        }
        if sample.sampled_tissue:
            sample_obj["tissue_label"] = sample.sampled_tissue.get("label", "")

        samples.append(sample_obj)

    columns = list(samples[0].keys())
    headers = biosample_to_sample_header(columns)

    file_handle.writelines([f"{line}\n" for line in headers])
    dict_writer = csv.DictWriter(file_handle, fieldnames=columns, delimiter="\t", lineterminator="\n")
    dict_writer.writerows(samples)


def maf_list(results, file_handle: TextIO):
    """
    List of maf files associated with this dataset.
    """
    maf_uri = [experiment.extra_properties["uri"] + "\n" for experiment in results]
    file_handle.writelines(maf_uri)


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

    write_dict_in_cbioportal_format({
        "cancer_study_identifier": study_id,
        "genetic_alteration_type": "MUTATION_EXTENDED",
        "datatype": "MAF",
        "stable_id": "mutations",
        "show_profile_in_analysis_tab": "true",
        "profile_name": "Mutations",
        "profile_description": "Mutation data from whole exome sequencing",
        "data_filename": MUTATION_DATA_FILENAME,
        "swissprot_identifier": "name",
    }, file_handle)


def case_list_export(study_id: str, results, file_handle: TextIO):
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

    write_dict_in_cbioportal_format({
        "cancer_study_identifier": study_id,
        "stable_id": f"{study_id}_sequenced",
        "case_list_name": "All samples",
        "case_list_description": "All samples",
        "case_list_ids": "\t".join(sanitize_id(exp_res.biosample_id) for exp_res in results),
    }, file_handle)


class CbioportalClinicalHeaderGenerator:
    """
    Generates cBioPortal data files headers based on field names from katsu models.
    """

    fields_mapping = {}

    def __init__(self, mappings: dict | None = None):
        self.fields_mapping = mappings or {}

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
                fieldname = field.replace("_", " ").capitalize()
                prop = (
                    fieldname,  # display name
                    fieldname,  # description
                    "STRING",  # type !!!TODO: TYPE DETECTION!!!
                    "1",  # priority (note: string here for use in join())
                    field.upper()   # DB suitable identifier
                )
                field_properties.append(prop)

        # Transpose list of properties tuples per field to tuples of
        # field properties per property.
        rows = list(zip(*field_properties))

        # The 4 first rows are considered meta datas, prefixed by '#'.
        # The 5th row (DB field names) is a canonical TSV header.
        cbio_header = [
            "#" + "\t".join(rows[0]),
            "#" + "\t".join(rows[1]),
            "#" + "\t".join(rows[2]),
            "#" + "\t".join(rows[3]),
            "\t".join(rows[4])
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


def sanitize_id(id_: str):
    """Ensure IDs are compatible with cBioPortal specifications

    IDs must contain alphanumeric characters, dot, hyphen or underscore
    """
    id_ = str(id_)    # force casting to string
    if REGEXP_INVALID_FOR_ID.search(id_) is None:
        return id_

    return REGEXP_INVALID_FOR_ID.sub("_", id_)
