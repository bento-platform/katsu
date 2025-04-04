import math
import chord_metadata_service.mohpackets.permissible_values as PERM_VAL
import copy


def add_nulls(complete_list: list, prop=0.2):
    """ Returns a list with 20% of the list as 'None' """
    list_copy = copy.deepcopy(complete_list)
    num_nulls = math.ceil(len(complete_list) * prop)
    list_copy.extend([None] * num_nulls)
    return list_copy


# add 20% nulls to all enums, remove not available from ALL enums
GENDER = PERM_VAL.GENDER + [None]
ALL_GENDER = [x for x in PERM_VAL.GENDER if x != "Not available"]
SEX_AT_BIRTH = add_nulls(PERM_VAL.SEX_AT_BIRTH)
ALL_SEX_AT_BIRTH = [x for x in PERM_VAL.SEX_AT_BIRTH if x not in ["Not available", None]]
ALL_CAUSE_OF_DEATH = [x for x in PERM_VAL.CAUSE_OF_DEATH if x != "Not available"]

BASIS_OF_DIAGNOSIS = add_nulls(PERM_VAL.BASIS_OF_DIAGNOSIS)
ALL_BASIS_OF_DIAGNOSIS = [x for x in PERM_VAL.BASIS_OF_DIAGNOSIS if x != "Not available"]
PRIMARY_DIAGNOSIS_LATERALITY = add_nulls(PERM_VAL.PRIMARY_DIAGNOSIS_LATERALITY)
ALL_PRIMARY_DIAGNOSIS_LATERALITY = [x for x in PERM_VAL.PRIMARY_DIAGNOSIS_LATERALITY if x != "Not available"]
TUMOUR_STAGING_SYSTEM = add_nulls(PERM_VAL.TUMOUR_STAGING_SYSTEM)
ALL_TUMOUR_STAGING_SYSTEM = [x for x in PERM_VAL.TUMOUR_STAGING_SYSTEM if x != "Not available"]
T_CATEGORY = add_nulls(PERM_VAL.T_CATEGORY)
N_CATEGORY = add_nulls(PERM_VAL.N_CATEGORY)
M_CATEGORY = add_nulls(PERM_VAL.M_CATEGORY)
STAGE_GROUP = add_nulls(PERM_VAL.STAGE_GROUP)
ALL_STAGE_GROUP = [x for x in PERM_VAL.STAGE_GROUP if x != "Not available"]

STORAGE = add_nulls(PERM_VAL.STORAGE)
ALL_STORAGE = [x for x in PERM_VAL.STORAGE if x != "Not available"]
SPECIMEN_PROCESSING = add_nulls(PERM_VAL.SPECIMEN_PROCESSING)
ALL_SPECIMEN_PROCESSING = [x for x in PERM_VAL.SPECIMEN_PROCESSING if x != "Not available"]
SPECIMEN_LATERALITY = add_nulls(PERM_VAL.SPECIMEN_LATERALITY)
ALL_SPECIMEN_LATERALITY = [x for x in PERM_VAL.SPECIMEN_LATERALITY if x != "Not available"]
CONFIRMED_DIAGNOSIS_TUMOUR = add_nulls(PERM_VAL.CONFIRMED_DIAGNOSIS_TUMOUR)
ALL_CONFIRMED_DIAGNOSIS_TUMOUR = [x for x in PERM_VAL.CONFIRMED_DIAGNOSIS_TUMOUR if x != "Not available"]
TUMOUR_GRADE = add_nulls(PERM_VAL.TUMOUR_GRADE)
ALL_TUMOUR_GRADE = [x for x in PERM_VAL.TUMOUR_GRADE if x != "Not available"]
TUMOUR_GRADING_SYSTEM = add_nulls(PERM_VAL.TUMOUR_GRADING_SYSTEM)
ALL_TUMOUR_GRADING_SYSTEM = [x for x in PERM_VAL.TUMOUR_GRADING_SYSTEM if x != "Not available"]
PERCENT_CELLS_RANGE = add_nulls(PERM_VAL.PERCENT_CELLS_RANGE)
ALL_PERCENT_CELLS_RANGE = [x for x in PERM_VAL.PERCENT_CELLS_RANGE if x != "Not available"]
CELLS_MEASURE_METHOD = add_nulls(PERM_VAL.CELLS_MEASURE_METHOD)
ALL_CELLS_MEASURE_METHOD = [x for x in PERM_VAL.CELLS_MEASURE_METHOD if x != "Not available"]

SPECIMEN_TISSUE_SOURCE = add_nulls(PERM_VAL.SPECIMEN_TISSUE_SOURCE)
ALL_SPECIMEN_TISSUE_SOURCE = [x for x in PERM_VAL.SPECIMEN_TISSUE_SOURCE if x != "Not available"]
SPECIMEN_TYPE = add_nulls(PERM_VAL.SPECIMEN_TYPE)
ALL_SPECIMEN_TYPE = [x for x in PERM_VAL.SPECIMEN_TYPE if x != "Not available"]
SAMPLE_TYPE = add_nulls(PERM_VAL.SAMPLE_TYPE)
ALL_SAMPLE_TYPE = [x for x in PERM_VAL.SAMPLE_TYPE if x != "Not available"]
TUMOUR_DESIGNATION = add_nulls(PERM_VAL.TUMOUR_DESIGNATION)
ALL_TUMOUR_DESIGNATION = [x for x in PERM_VAL.TUMOUR_DESIGNATION if x != "Not available"]

TREATMENT_TYPE = add_nulls(PERM_VAL.TREATMENT_TYPE)

# remove typed treatments, they get added if there is a specific treatment linked
TREATMENT_TYPE_FOR_ALL = [
    "Bone marrow transplant",
    "No treatment",
    "Targeted molecular therapy",
    "Photodynamic therapy",
    "Stem cell transplant",
]
TREATMENT_INTENT = add_nulls(PERM_VAL.TREATMENT_INTENT)
ALL_TREATMENT_INTENT = [x for x in PERM_VAL.TREATMENT_INTENT if x != "Not available"]
TREATMENT_RESPONSE_METHOD = add_nulls(PERM_VAL.TREATMENT_RESPONSE_METHOD)
ALL_TREATMENT_RESPONSE_METHOD = [x for x in PERM_VAL.TREATMENT_RESPONSE_METHOD if x != "Not available"]
TREATMENT_RESPONSE = add_nulls(PERM_VAL.TREATMENT_RESPONSE)
ALL_TREATMENT_RESPONSE = [x for x in PERM_VAL.TREATMENT_RESPONSE if x != "Not available"]
TREATMENT_STATUS = add_nulls(PERM_VAL.TREATMENT_STATUS)
ALL_TREATMENT_STATUS = [x for x in PERM_VAL.TREATMENT_STATUS if x != "Not available"]

DOSAGE_UNITS = add_nulls(PERM_VAL.DOSAGE_UNITS)
ALL_DOSAGE_UNITS = [x for x in PERM_VAL.DOSAGE_UNITS if x != "Not available"]

RADIATION_THERAPY_MODALITY = add_nulls(PERM_VAL.RADIATION_THERAPY_MODALITY)
ALL_RADIATION_THERAPY_MODALITY = [x for x in PERM_VAL.RADIATION_THERAPY_MODALITY if x != "Not available"]
RADIATION_ANATOMICAL_SITE = add_nulls(PERM_VAL.RADIATION_ANATOMICAL_SITE)
ALL_RADIATION_ANATOMICAL_SITE = [x for x in PERM_VAL.RADIATION_ANATOMICAL_SITE if x != "Not available"]
THERAPY_TYPE = add_nulls(PERM_VAL.THERAPY_TYPE)
ALL_THERAPY_TYPE = [x for x in PERM_VAL.THERAPY_TYPE if x != "Not available"]

SURGERY_LOCATION = add_nulls(PERM_VAL.SURGERY_LOCATION)
ALL_SURGERY_LOCATION = [x for x in PERM_VAL.SURGERY_LOCATION if x != "Not available"]
SURGERY_REFERENCE_DATABASE = add_nulls(PERM_VAL.SURGERY_REFERENCE_DATABASE)
ALL_SURGERY_REFERENCE_DATABASE = [x for x in PERM_VAL.SURGERY_REFERENCE_DATABASE if x != "Not availabe"]
TUMOUR_FOCALITY = add_nulls(PERM_VAL.TUMOUR_FOCALITY)
ALL_TUMOUR_FOCALITY = [x for x in PERM_VAL.TUMOUR_FOCALITY if x != "Not available"]
TUMOUR_CLASSIFICATION = add_nulls(PERM_VAL.TUMOUR_CLASSIFICATION)
ALL_TUMOUR_CLASSIFICATION = [x for x in PERM_VAL.TUMOUR_CLASSIFICATION if x != "Not available"]
LYMPHOVACULAR_INVASION = add_nulls(PERM_VAL.LYMPHOVACULAR_INVASION)
ALL_LYMPHOVACULAR_INVASION = [x for x in PERM_VAL.LYMPHOVACULAR_INVASION if x != "Not available"]
PERINEURAL_INVASION = add_nulls(PERM_VAL.PERINEURAL_INVASION)
ALL_PERINEURAL_INVASION = [x for x in PERM_VAL.PERINEURAL_INVASION]
MARGIN_TYPES = add_nulls(PERM_VAL.MARGIN_TYPES)
ALL_MARGIN_TYPES = [x for x in PERM_VAL.MARGIN_TYPES if x != "Not available"]

ER_PR_HPV_STATUS = add_nulls(PERM_VAL.ER_PR_HPV_STATUS)
ALL_ER_PR_HPV_STATUS = [x for x in PERM_VAL.ER_PR_HPV_STATUS if x != "Not available"]
HER2_STATUS = add_nulls(PERM_VAL.HER2_STATUS)
ALL_HER2_STATUS = [x for x in PERM_VAL.HER2_STATUS if x != "Not available"]

UBOOLEAN = add_nulls(PERM_VAL.UBOOLEAN)
ALL_UBOOLEAN = [x for x in PERM_VAL.UBOOLEAN if x != "Not available"]

MALIGNANCY_LATERALITY = add_nulls(PERM_VAL.MALIGNANCY_LATERALITY)
ALL_MALIGNANCY_LATERALITY = [x for x in PERM_VAL.MALIGNANCY_LATERALITY if x != "Not available"]

DISEASE_STATUS_FOLLOWUP = add_nulls(PERM_VAL.DISEASE_STATUS_FOLLOWUP)
ALL_DISEASE_STATUS_FOLLOWUP = [x for x in PERM_VAL.DISEASE_STATUS_FOLLOWUP if x != "Not available"]
PROGRESSION_STATUS_METHOD = add_nulls(PERM_VAL.PROGRESSION_STATUS_METHOD)
ALL_PROGRESSION_STATUS_METHOD = [x for x in PERM_VAL.PROGRESSION_STATUS_METHOD if x != "Not available"]

ALL_SMOKING_STATUS = [x for x in PERM_VAL.SMOKING_STATUS if x != "Not available"]

# Restricted values for synthetic data generation

PRIMARY_SITE = ["Breast",
                "Bronchus and lung",
                "Colon",
                "Skin",
                None]

# ICD disease codes, not all are correct but will match regex in model
c_codes = ['C' + str(x).rjust(2, '0') for x in list(range(0, 97))]
d_codes = ['D' + str(x).rjust(2, '0') for x in list(range(0, 9)) + list(range(37, 48))]
CANCER_CODES = c_codes + d_codes + [None]
CANCER_CODES.extend([None] * math.floor(len(CANCER_CODES) * .2))
# some codes from diseases of the circulatory system, diseases of the blood
NON_CANCER_CODES = ['D' + str(x) for x in list(range(50, 89)) + list(range(37, 48))] + \
                   ['I' + str(x).rjust(2, '0') for x in list(range(0, 99))]
CANCER_CODES.extend([None] * math.floor(len(NON_CANCER_CODES) * .2))

ALL_CODES = CANCER_CODES + NON_CANCER_CODES

SMOKER_TOBACCO_TYPE = [
    "Chewing Tobacco",
    "Cigar",
    "Cigarettes",
    "Electronic cigarettes",
    "Pipe",
    "Roll-ups",
    "Snuff",
    "Not available",
    "Waterpipe",
]

# Systemic Therapy Drugs
CHEMO_DRUGS = {
    "Methotrexate": {"RxNorm": "6851",
                     "PubChem": "126941",
                     "NCI Thesaurus": "C642"},
    "Fludarabine": {"RxNorm": "24698",
                    "PubChem": "657237",
                    "NCI Thesaurus": "C1094"},
    "Carboplatin": {"RxNorm": "40048",
                    "PubChem": "426756",
                    "NCI Thesaurus": "C1282"},
    "Idarubicin": {"RxNorm": "5650",
                   "PubChem": "42890",
                   "NCI Thesaurus": "C562"},
    "Paclitaxel": {"RxNorm": "56946",
                   "PubChem": "36314",
                   "NCI Thesaurus": "C1411"}
}

IMMUNO_DRUGS = {
    "Atezolizumab": {"RxNorm": "1792776",
                     "PubChem": "469690927",
                     "NCI Thesaurus": "C106250"},
    "Durvalumab": {"RxNorm": "1919503",
                   "PubChem": "481101604",
                   "NCI Thesaurus": "C103194"},
    "Nivolumab": {"RxNorm": "1597876",
                  "PubChem": "469753496",
                  "NCI Thesaurus": "C68814"},
    "Pembrolizumab": {"RxNorm": "1547545",
                      "PubChem": "469691028",
                      "NCI Thesaurus": "C106432"},
    "Ipilimumab": {"RxNorm": "1094833",
                   "PubChem": "472634117",
                   "NCI Thesaurus": "C2654"},
}

HORMONE_DRUGS = {
    "Tamoxifen": {"RxNorm": "10324",
                  "PubChem": "2733526",
                  "NCI Thesaurus": "C62078"},
    "Fluoxymesterone": {"RxNorm": "4494",
                        "PubChem": "6446",
                        "NCI Thesaurus": "C507"},
    "Diethylstilbestrol": {"RxNorm": "3390",
                           "PubChem": "448537",
                           "NCI Thesaurus": "C433"},
    "Buserelin": {"RxNorm": "1825",
                  "PubChem": "50225",
                  "NCI Thesaurus": "C320"},
    "Degarelix": {"RxNorm": "475230",
                  "PubChem": "16136245",
                  "NCI Thesaurus": "C48385"}
}

SURGERY_TYPE = {
    "Biopsy": {"NCIt": "C15189",
               "SNOMED": "86273004",
               "UMLS": "C0005558"},
    "Bypass Gastrojejunostomy": {"NCIt": "C51758",
                                 "SNOMED": "49245001",
                                 "UMLS": "C0399839"},
    "Exploratory laparotomy": {"NCIt": "C51779",
                               "SNOMED": "74770008",
                               "UMLS": "C0085704"},
    "Total Mastectomy": {"NCIt": "C15281"},
    "Mastectomy with excision of regional lymph nodes": {"SNOMED": "66398006"},
    "Radical prostatectomy": {"NCIt": "C15399",
                              "SNOMED": "26294005",
                              "UMLS": "C0194810"},
    "Total gastrectomy": {"NCIt": "C185240",
                          "SNOMED": "26452005",
                          "UMLS": "C1304782"}
}

RISS_DURIE_STAGES = ["Stage I",
                     "Stage II",
                     "Stage III"]

LUGANO_STAGES = ["Stage I",
                 "Stage IA",
                 "Stage IB",
                 "Stage IE",
                 "Stage II",
                 "Stage II bulky",
                 "Stage IIE",
                 "Stage IIA",
                 "Stage IIB",
                 "Stage III",
                 "Stage IIIA1",
                 "Stage IV"]

ST_JUDE = ["Stage I",
           "Stage II",
           "Stage III",
           "Stage IV"]

ANN_ARBOR = ["Stage I",
             "Stage II",
             "Stage III",
             "Stage IV",
             "Stage IA",
             "Stage IIA",
             "Stage IIIA",
             "Stage IVA",
             "Stage IB",
             "Stage IIB",
             "Stage IIIB",
             "Stage IVB",
             "Stage IE",
             "Stage IIE",
             "Stage IIIE",
             "Stage IVE",
             "Stage IS",
             "Stage IIS",
             "Stage IIIS",
             "Stage IVS"
             ]

FIGO_STAGING = [
    "Stage IA",
    "Stage IA1",
    "Stage IA2",
    "Stage IB",
    "Stage IB1",
    "Stage IB2",
    "Stage IIA",
    "Stage IAB",
    "Stage IIIA",
    "Stage IIIB",
    "Stage IVA",
    "Stage IVB"
]

BINET_STAGING = [
    "Stage A",
    "Stage B",
    "Stage C"
]

RAI_STAGING = [
    "Stage 0",
    "Stage I",
    "Stage II",
    "Stage III",
    "Stage IV"
]

STAGE_GROUP_KEY = {
    "Ann Arbor staging system": ANN_ARBOR,
    "Binet staging system": BINET_STAGING,
    "Durie-Salmon staging system": RISS_DURIE_STAGES,
    "FIGO staging system": FIGO_STAGING,
    "Lugano staging system": LUGANO_STAGES,
    "Rai staging system": RAI_STAGING,
    "Revised International staging system(R-ISS)": RISS_DURIE_STAGES,
    "St Jude staging system": ST_JUDE
}

TOPOGRAPHY_CODES = [
    "C00.0",
    "C00.1",
    "C00.2",
    "C00.3",
    "C00.4",
    "C00.5",
    "C00.6",
    "C00.8",
    "C01.9",
    "C02.0",
    "C02.1",
    "C02.2",
    "C02.3",
    "C02.4",
    "C02.8",
    "C02.9",
    "C03.0",
    "C03.1",
    "C03.9",
    "C04.0",
    "C04.1",
    "C04.8",
    "C04.9",
    "C05.0",
    "C05.1",
    "C05.2",
    "C05.8",
    "C05.9",
    "C06.0",
    "C06.1",
    "C06.2",
    "C06.8",
    "C06.9",
    "C07.9",
    "C08.0",
    "C08.1",
    "C08.8",
    "C08.9",
    "C09.0",
    "C09.1",
    "C09.8",
    "C09.9",
    "C10.0",
    "C10.1",
    "C10.2",
    "C10.3",
    "C10.4",
    "C10.8",
    "C10.9",
    "C11.0",
    "C11.1",
    "C11.2",
    "C11.3",
    "C11.8",
    "C11.9",
    "C12.9",
    "C13.0",
    "C13.1",
    "C13.2",
    "C13.8",
    "C13.9",
    "C14.0",
    "C14.2",
    "C14.8",
    "C15.0",
    "C15.1",
    "C15.2",
    "C15.3",
    "C15.4",
    "C15.5",
    "C15.8",
    "C15.9",
    "C16.0",
    "C16.1",
    "C16.2",
    "C16.3",
    "C16.4",
    "C16.5",
    "C16.6",
    "C16.8",
    "C16.9",
    "C17.0",
    "C17.1",
    "C17.2",
    "C17.3",
    "C17.8",
    "C17.9",
    "C18.0",
    "C18.1",
    "C18.2",
    "C18.3",
    "C18.4",
    "C18.5",
    "C18.6",
    "C18.7",
    "C18.8",
    "C18.9",
    "C19.9",
    "C20.9",
    "C21.0",
    "C21.1",
    "C21.2",
    "C21.8",
    "C22.0",
    "C22.1",
    "C23.9",
    "C24.0",
    "C24.1",
    "C24.8",
    "C24.9",
    "C25.0",
    "C25.1",
    "C25.2",
    "C25.3",
    "C25.4",
    "C25.7",
    "C25.8",
    "C25.9",
    "C26.0",
    "C26.8",
    "C26.9",
    "C30.0",
    "C30.1",
    "C31.0",
    "C31.1",
    "C31.2",
    "C31.3",
    "C31.8",
    "C31.9",
    "C32.0",
    "C32.1",
    "C32.2",
    "C32.3",
    "C32.8",
    "C32.9",
    "C33.9",
    "C34.0",
    "C34.1",
    "C34.2",
    "C34.3",
    "C34.8",
    "C34.9",
    "C37.9",
    "C38.0",
    "C38.1",
    "C38.2",
    "C38.3",
    "C38.4",
    "C38.8",
    "C39.0",
    "C39.8",
    "C39.9",
    "C40.0",
    "C40.1",
    "C40.3",
    "C40.8",
    "C40.9",
    "C41.0",
    "C41.1",
    "C41.2",
    "C41.3",
    "C41.4",
    "C41.8",
    "C41.9",
    "C42.0",
    "C42.1",
    "C42.2",
    "C42.3",
    "C42.4",
    "C44.0",
    "C44.1",
    "C44.2",
    "C44.3",
    "C44.4",
    "C44.5",
    "C44.6",
    "C44.7",
    "C47.0",
    "C47.1",
    "C47.2",
    "C47.3",
    "C47.4",
    "C47.5",
    "C47.6",
    "C47.8",
    "C47.9",
    "C48.0",
    "C48.1",
    "C48.2",
    "C48.8",
    "C49.0",
    "C49.1",
    "C49.2",
    "C49.3",
    "C49.4",
    "C49.5",
    "C49.6",
    "C49.8",
    "C49.9",
    "C50.0",
    "C50.1",
    "C50.2",
    "C50.3",
    "C50.4",
    "C50.5",
    "C50.6",
    "C50.8",
    "C50.9",
    "C51.0",
    "C51.1",
    "C51.2",
    "C51.8",
    "C51.9",
    "C52.9",
    "C53.0",
    "C53.1",
    "C53.8",
    "C53.9",
    "C54.0",
    "C54.1",
    "C54.2",
    "C54.3",
    "C54.8",
    "C54.9",
    "C55.9",
    "C56.9",
    "C57.0",
    "C57.1",
    "C57.2",
    "C57.3",
    "C57.4",
    "C57.7",
    "C57.8",
    "C57.9",
    "C60.0",
    "C60.1",
    "C60.2",
    "C60.8",
    "C60.9",
    "C61.9",
    "C62.0",
    "C62.1",
    "C62.9",
    "C63.0",
    "C63.1",
    "C63.2",
    "C63.7",
    "C63.8",
    "C63.9",
    "C64.9",
    "C65.9",
    "C66.9",
    "C67.0",
    "C67.1",
    "C67.2",
    "C67.4",
    "C67.6",
    "C67.7",
    "C67.8",
    "C67.9",
    "C68.0",
    "C68.1",
    "C68.8",
    "C68.9",
    "C69.0",
    "C69.1",
    "C69.2",
    "C69.3",
    "C69.4",
    "C69.5",
    "C69.6",
    "C69.8",
    "C69.9",
    "C70.0",
    "C70.1",
    "C70.9",
    "C71.0",
    "C71.1",
    "C71.2",
    "C71.3",
    "C71.4",
    "C71.5",
    "C71.6",
    "C71.7",
    "C71.8",
    "C71.9",
    "C72.0",
    "C72.1",
    "C72.2",
    "C72.3",
    "C72.4",
    "C72.5",
    "C72.8",
    "C72.9",
    "C73.9",
    "C74.0",
    "C74.1",
    "C74.9",
    "C75.0",
    "C75.1",
    "C75.2",
    "C75.3",
    "C75.4",
    "C75.5",
    "C75.8",
    "C75.9",
    "C76.0",
    "C76.1",
    "C76.2",
    "C76.3",
    "C76.4",
    "C76.5",
    "C76.7",
    "C76.8",
    "C77.0",
    "C77.1",
    "C77.2",
    "C77.3",
    "C77.4",
    "C77.5",
    "C77.8",
    "C77.9",
    "C80.9",
    None
]

ALL_TOPOGRAPHY_CODES = [x for x in TOPOGRAPHY_CODES if x is not None]
