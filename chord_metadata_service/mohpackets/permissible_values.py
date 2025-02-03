"""
These lists contain the permissible values for their respective
MoH model fields and are used for validation during serialization.
"""

from chord_metadata_service.mohpackets.utils import list_to_enum

UBOOLEAN = ["Yes", "No", "Not available"]

CAUSE_OF_DEATH = ["Died of cancer", "Died of other reasons", "Not available"]

PRIMARY_SITE = [
    "Accessory sinuses",
    "Adrenal gland",
    "Anus and anal canal",
    "Base of tongue",
    "Bladder",
    "Bones, joints and articular cartilage of limbs",
    "Bones, joints and articular cartilage of other and unspecified sites",
    "Brain",
    "Breast",
    "Bronchus and lung",
    "Cervix uteri",
    "Colon",
    "Connective, subcutaneous and other soft tissues",
    "Corpus uteri",
    "Esophagus",
    "Eye and adnexa",
    "Floor of mouth",
    "Gallbladder",
    "Gum",
    "Heart, mediastinum, and pleura",
    "Hematopoietic and reticuloendothelial systems",
    "Hypopharynx",
    "Kidney",
    "Larynx",
    "Lip",
    "Liver and intrahepatic bile ducts",
    "Lymph nodes",
    "Meninges",
    "Nasal cavity and middle ear",
    "Nasopharynx",
    "Oropharynx",
    "Other and ill-defined digestive organs",
    "Other and ill-defined sites",
    "Other and ill-defined sites in lip, oral cavity and pharynx",
    "Other and ill-defined sites within respiratory system and intrathoracic organs",
    "Other and unspecified female genital organs",
    "Other and unspecified major salivary glands",
    "Other and unspecified male genital organs",
    "Other and unspecified parts of biliary tract",
    "Other and unspecified parts of mouth",
    "Other and unspecified parts of tongue",
    "Other and unspecified urinary organs",
    "Other endocrine glands and related structures",
    "Ovary",
    "Palate",
    "Pancreas",
    "Parotid gland",
    "Penis",
    "Peripheral nerves and autonomic nervous system",
    "Placenta",
    "Prostate gland",
    "Pyriform sinus",
    "Rectosigmoid junction",
    "Rectum",
    "Renal pelvis",
    "Retroperitoneum and peritoneum",
    "Skin",
    "Small intestine",
    "Spinal cord, cranial nerves, and other parts of central nervous system",
    "Stomach",
    "Testis",
    "Thymus",
    "Thyroid gland",
    "Tonsil",
    "Trachea",
    "Ureter",
    "Uterus, NOS",
    "Vagina",
    "Vulva",
    "Unknown primary site",
    "Not available"
]


LOST_TO_FOLLOWUP_REASON = [
    "Completed study",
    "Discharged to palliative care",
    "Lost contact",
    "Not available",
    "Withdrew from study",
    "Discharged from follow-up"
]

TUMOUR_STAGING_SYSTEM = [
    "AJCC cancer staging system",
    "Ann Arbor staging system",
    "Binet staging system",
    "Durie-Salmon staging system",
    "FIGO staging system",
    "International Neuroblastoma Risk Group Staging System",
    "International Neuroblastoma Staging System",
    "Lugano staging system",
    "Rai staging system",
    "Revised International staging system (R-ISS)",
    "SEER staging system",
    "St Jude staging system",
    "Not available"
]

T_CATEGORY = [
    "T0",
    "T1",
    "T1a",
    "T1a1",
    "T1a2",
    "T1a(s)",
    "T1a(m)",
    "T1b",
    "T1b1",
    "T1b2",
    "T1b(s)",
    "T1b(m)",
    "T1c",
    "T1d",
    "T1mi",
    "T2",
    "T2(s)",
    "T2(m)",
    "T2a",
    "T2a1",
    "T2a2",
    "T2b",
    "T2c",
    "T2d",
    "T3",
    "T3(s)",
    "T3(m)",
    "T3a",
    "T3b",
    "T3c",
    "T3d",
    "T3e",
    "T4",
    "T4a",
    "T4a(s)",
    "T4a(m)",
    "T4b",
    "T4b(s)",
    "T4b(m)",
    "T4c",
    "T4d",
    "T4e",
    "Ta",
    "Tis",
    "Tis(DCIS)",
    "Tis(LAMN)",
    "Tis(LCIS)",
    "Tis(Paget)",
    "Tis(Paget's)",
    "Tis pu",
    "Tis pd",
    "TX",
]

N_CATEGORY = [
    "N0",
    "N0a",
    "N0a (biopsy)",
    "N0b",
    "N0b (no biopsy)",
    "N0(i+)",
    "N0(i-)",
    "N0(mol+)",
    "N0(mol-)",
    "N1",
    "N1a",
    "N1a(sn)",
    "N1b",
    "N1c",
    "N1mi",
    "N2",
    "N2a",
    "N2b",
    "N2c",
    "N2mi",
    "N3",
    "N3a",
    "N3b",
    "N3c",
    "N4",
    "NX",
]

M_CATEGORY = [
    "M0",
    "M0(i+)",
    "M1",
    "M1a",
    "M1a(0)",
    "M1a(1)",
    "M1b",
    "M1b(0)",
    "M1b(1)",
    "M1c",
    "M1c(0)",
    "M1c(1)",
    "M1d",
    "M1d(0)",
    "M1d(1)",
    "M1e",
    "MX",
]

STAGE_GROUP = [
    "Stage 0",
    "Stage 0a",
    "Stage 0is",
    "Stage 1",
    "Stage 1A",
    "Stage 1B",
    "Stage A",
    "Stage B",
    "Stage C",
    "Stage I",
    "Stage IA",
    "Stage IA1",
    "Stage IA2",
    "Stage IA3",
    "Stage IAB",
    "Stage IAE",
    "Stage IAES",
    "Stage IAS",
    "Stage IB",
    "Stage IB1",
    "Stage IB2",
    "Stage IBE",
    "Stage IBES",
    "Stage IBS",
    "Stage IC",
    "Stage IE",
    "Stage IEA",
    "Stage IEB",
    "Stage IES",
    "Stage II",
    "Stage II bulky",
    "Stage IIA",
    "Stage IIA1",
    "Stage IIA2",
    "Stage IIAE",
    "Stage IIAES",
    "Stage IIAS",
    "Stage IIB",
    "Stage IIBE",
    "Stage IIBES",
    "Stage IIBS",
    "Stage IIC",
    "Stage IIE",
    "Stage IIEA",
    "Stage IIEB",
    "Stage IIES",
    "Stage III",
    "Stage IIIA",
    "Stage IIIA1",
    "Stage IIIA2",
    "Stage IIIAE",
    "Stage IIIAES",
    "Stage IIIAS",
    "Stage IIIB",
    "Stage IIIBE",
    "Stage IIIBES",
    "Stage IIIBS",
    "Stage IIIC",
    "Stage IIIC1",
    "Stage IIIC2",
    "Stage IIID",
    "Stage IIIE",
    "Stage IIIES",
    "Stage IIIS",
    "Stage IIS",
    "Stage IS",
    "Stage IV",
    "Stage IVA",
    "Stage IVA1",
    "Stage IVA2",
    "Stage IVAE",
    "Stage IVAES",
    "Stage IVAS",
    "Stage IVB",
    "Stage IVBE",
    "Stage IVBES",
    "Stage IVBS",
    "Stage IVC",
    "Stage IVE",
    "Stage IVES",
    "Stage IVS",
    "In situ",
    "Localized",
    "Regionalized",
    "Distant",
    "Stage L1",
    "Stage L2",
    "Stage M",
    "Stage Ms",
    "Stage 2A",
    "Stage 2B",
    "Stage 3",
    "Stage 4",
    "Stage 4S",
    "Occult Carcinoma",
    "Not available"
]


STORAGE = [
    "Cut slide",
    "Frozen in -70 freezer",
    "Frozen in liquid nitrogen",
    "Frozen in vapour phase",
    "Not Applicable",
    "OCT embedded",
    "Other",
    "Paraffin block",
    "RNA later frozen",
    "Not available",
]

SPECIMEN_PROCESSING = [
    "Cryopreservation in liquid nitrogen (dead tissue)",
    "Cryopreservation in dry ice (dead tissue)",
    "Cryopreservation of live cells in liquid nitrogen",
    "Cryopreservation - other",
    "Formalin fixed & paraffin embedded",
    "Formalin fixed - buffered",
    "Formalin fixed - unbuffered",
    "Fresh",
    "Other",
    "Not available",
]

SPECIMEN_LATERALITY = ["Left", "Not applicable", "Right", "Not available"]

PRIMARY_DIAGNOSIS_LATERALITY = [
    "Bilateral",
    "Left",
    "Midline",
    "Not a paired site",
    "Right",
    "Unilateral, side not specified",
    "Not available",
]

CONFIRMED_DIAGNOSIS_TUMOUR = ["Yes", "No", "Not done", "Not available"]

TUMOUR_GRADING_SYSTEM = [
    "FNCLCC grading system",
    "Four-tier grading system",
    "Gleason grade group system",
    "Grading system for GISTs",
    "Grading system for GNETs",
    "IASLC grading system",
    "ISUP grading system",
    "Nottingham grading system",
    "Nuclear grading system for DCIS",
    "Scarff-Bloom-Richardson grading system",
    "Three-tier grading system",
    "Two-tier grading system",
    "WHO grading system for CNS tumours",
    "Not available"
]

TUMOUR_GRADE = [
    "Low grade",
    "High grade",
    "GX",
    "G1",
    "G2",
    "G3",
    "G4",
    "Low",
    "High",
    "Grade 1",
    "Grade 2",
    "Grade 3",
    "Grade 4",
    "Grade I",
    "Grade II",
    "Grade III",
    "Grade IV",
    "Grade Group 1",
    "Grade Group 2",
    "Grade Group 3",
    "Grade Group 4",
    "Grade Group 5",
    "Not available",
]

PERCENT_CELLS_RANGE = ["0-19%", "20-50%", "51-100%", "Not available"]

CELLS_MEASURE_METHOD = [
    "Genomics",
    "Image analysis",
    "Pathology estimate by percent nuclei",
    "Other",
    "Not available",
]

GENDER = ["Man", "Woman", "Non-binary", "Other", "Prefer not to disclose", "Not available"]

SEX_AT_BIRTH = ["Male", "Female", "Other", "Not available"]

SPECIMEN_TISSUE_SOURCE = [
    "Abdominal fluid",
    "Amniotic fluid",
    "Arterial blood",
    "Bile",
    "Blood derived - bone marrow",
    "Blood derived - peripheral blood",
    "Bone marrow fluid",
    "Bone marrow derived mononuclear cells",
    "Buccal cell",
    "Buffy coat",
    "Cerebrospinal fluid",
    "Cervical mucus",
    "Convalescent plasma",
    "Cord blood",
    "Duodenal fluid",
    "Female genital fluid",
    "Fetal blood",
    "Hydrocele fluid",
    "Male genital fluid",
    "Other",
    "Pancreatic fluid",
    "Pericardial effusion",
    "Pleural fluid",
    "Renal cyst fluid",
    "Saliva",
    "Seminal fluid",
    "Serum",
    "Solid tissue",
    "Sputum",
    "Synovial fluid",
    "Urine",
    "Venous blood",
    "Vitreous fluid",
    "Whole blood",
    "Wound",
]

SPECIMEN_TYPE = [
    "Cell line - derived from normal",
    "Cell line - derived from primary tumour",
    "Cell line - derived from metastatic tumour",
    "Cell line - derived from xenograft tumour",
    "Metastatic tumour - additional metastatic",
    "Metastatic tumour - metastasis local to lymph node",
    "Metastatic tumour - metastasis to distant location",
    "Metastatic tumour",
    "Normal - tissue adjacent to primary tumour",
    "Normal",
    "Primary tumour - additional new primary",
    "Primary tumour - adjacent to normal",
    "Primary tumour",
    "Recurrent tumour",
    "Tumour - unknown if derived from primary or metastatic tumour",
    "Xenograft - derived from primary tumour",
    "Xenograft - derived from metastatic tumour",
    "Xenograft - derived from tumour cell line",
]


SAMPLE_TYPE = [
    "Amplified DNA",
    "ctDNA",
    "Other DNA enrichments",
    "Other RNA fractions",
    "polyA+ RNA",
    "Protein",
    "rRNA-depleted RNA",
    "Total DNA",
    "Total RNA",
]

BASIS_OF_DIAGNOSIS = [
    "Clinical investigation",
    "Clinical",
    "Cytology",
    "Death certificate only",
    "Histology of a metastasis",
    "Histology of a primary tumour",
    "Specific tumour markers",
    "Not available",
]

LYMPH_NODE_STATUS = [
    "Cannot be determined",
    "No",
    "No lymph nodes found in resected specimen",
    "Not applicable",
    "Yes",
]

LYMPH_NODE_METHOD = [
    "Imaging",
    "Lymph node dissection/pathological exam",
    "Physical palpation of patient",
]

TREATMENT_TYPE = [
    "Bone marrow transplant",
    "Systemic therapy",
    "No treatment",
    "Targeted molecular therapy",
    "Photodynamic therapy",
    "Radiation therapy",
    "Stem cell transplant",
    "Surgery",
    "Other",
]

TREATMENT_SETTING = [
    "Adjuvant",
    "Advanced/Metastatic",
    "Neoadjuvant",
    "Conditioning",
    "Induction",
    "Locally advanced",
    "Maintenance",
    "Mobilization",
    "Preventative",
    "Radiosensitization",
    "Salvage",
]

TREATMENT_INTENT = [
    "Curative",
    "Palliative",
    "Supportive",
    "Diagnostic",
    "Preventive",
    "Guidance",
    "Screening",
    "Forensic",
    "Not available"
]

TREATMENT_RESPONSE_METHOD = [
    "RECIST 1.1",
    "iRECIST",
    "Cheson CLL 2012 Oncology Response Criteria",
    "Response Assessment in Neuro-Oncology (RANO)",
    "AML Response Criteria",
    "Physician Assessed Response Criteria",
    "Blazer score",
    "Not available",
]

TREATMENT_RESPONSE = [
    "Complete response",
    "Partial response",
    "Progressive disease",
    "Stable disease",
    "Immune complete response (iCR)",
    "Immune partial response (iPR)",
    "Immune uncomfirmed progressive disease (iUPD)",
    "Immune confirmed progressive disease (iCPD)",
    "Immune stable disease (iSD)",
    "Complete remission",
    "Partial remission",
    "Minor response",
    "Complete remission without measurable residual disease (CR MRD-)",
    "Complete remission with incomplete hematologic recovery (CRi)",
    "Morphologic leukemia-free state",
    "Primary refractory disease",
    "Hematologic relapse (after CR MRD-, CR, CRi)",
    "Molecular relapse (after CR MRD-)",
    "Physician assessed complete response",
    "Physician assessed partial response",
    "Physician assessed stable disease",
    "No evidence of disease (NED)",
    "Minor response",
    "Major response",
    "Complete response",
    "Not available",
]

TREATMENT_STATUS = [
    "Treatment completed as prescribed",
    "Treatment incomplete due to technical or organizational problems",
    "Treatment incomplete because patient died",
    "Patient choice (stopped or interrupted treatment)",
    "Physician decision (stopped or interrupted treatment)",
    "Treatment stopped due to lack of efficacy (disease progression)",
    "Treatment stopped due to acute toxicity",
    "Treatment ongoing",
    "Other",
    "Not available",
]

DRUG_REFERENCE_DB = [
    "RxNorm",
    "PubChem",
    "NCI Thesaurus",
]

DOSAGE_UNITS = [
    "mg/m2",
    "IU/m2",
    "IU/kg",
    "ug/m2",
    "g/m2",
    "mg/kg",
    "mg",
    "Not available",
]

RADIATION_THERAPY_MODALITY = [
    "Megavoltage radiation therapy using photons (procedure)",
    "Radiopharmaceutical",
    "Teleradiotherapy using electrons (procedure)",
    "Teleradiotherapy protons (procedure)",
    "Teleradiotherapy neutrons (procedure)",
    "Brachytherapy (procedure)",
    "Other",
    "Not available"
]

RADIATION_ANATOMICAL_SITE = [
    "LEFT ABDOMEN",
    "WHOLE ABDOMEN",
    "RIGHT ABDOMEN",
    "LOWER ABDOMEN",
    "LEFT LOWER ABDOMEN",
    "RIGHT LOWER ABDOMEN",
    "UPPER ABDOMEN",
    "LEFT UPPER ABDOMEN",
    "RIGHT UPPER ABDOMEN",
    "LEFT ADRENAL",
    "RIGHT ADRENAL",
    "BILATERAL ANKLE",
    "LEFT ANKLE",
    "RIGHT ANKLE",
    "BILATERAL ANTRUM (BULL'S EYE)",
    "LEFT ANTRUM",
    "RIGHT ANTRUM",
    "ANUS",
    "LOWER LEFT ARM",
    "LOWER RIGHT ARM",
    "BILATERAL ARMS",
    "LEFT ARM",
    "RIGHT ARM",
    "UPPER LEFT ARM",
    "UPPER RIGHT ARM",
    "LEFT AXILLA",
    "RIGHT AXILLA",
    "SKIN OR SOFT TISSUE OF BACK",
    "BILE DUCT",
    "BLADDER",
    "LOWER BODY",
    "MIDDLE BODY",
    "UPPER BODY",
    "WHOLE BODY",
    "BOOST - AREA PREVIOUSLY TREATED",
    "BRAIN",
    "LEFT BREAST BOOST",
    "RIGHT BREAST BOOST",
    "BILATERAL BREAST",
    "LEFT BREAST",
    "RIGHT BREAST",
    "BILATERAL BREASTS WITH NODES",
    "LEFT BREAST WITH NODES",
    "RIGHT BREAST WITH NODES",
    "BILATERAL BUTTOCKS",
    "LEFT BUTTOCK",
    "RIGHT BUTTOCK",
    "INNER CANTHUS",
    "OUTER CANTHUS",
    "CERVIX",
    "BILATERAL CHEST LUNG & AREA INVOLVE",
    "LEFT CHEST",
    "RIGHT CHEST",
    "CHIN",
    "LEFT CHEEK",
    "RIGHT CHEEK",
    "BILATERAL CHEST WALL (W/O BREAST)",
    "LEFT CHEST WALL",
    "RIGHT CHEST WALL",
    "BILATERAL CLAVICLE",
    "LEFT CLAVICLE",
    "RIGHT CLAVICLE",
    "COCCYX",
    "COLON",
    "WHOLE C.N.S. (MEDULLA TECHINQUE)",
    "CSF SPINE (MEDULL TECH 2 DIFF MACHI",
    "LEFT CHESTWALL BOOST",
    "RIGHT CHESTWALL BOOST",
    "BILATERAL CHESTWALL WITH NODES",
    "LEFT CHESTWALL WITH NODES",
    "RIGHT CHESTWALL WITH NODES",
    "LEFT EAR",
    "RIGHT EAR",
    "EPIGASTRIUM",
    "LOWER ESOPHAGUS",
    "MIDDLE ESOPHAGUS",
    "UPPER ESOPHAGUS",
    "ENTIRE ESOPHAGUS",
    "ETHMOID SINUS",
    "BILATERAL EYES",
    "LEFT EYE",
    "RIGHT EYE",
    "BILATERAL FACE",
    "LEFT FACE",
    "RIGHT FACE",
    "LEFT FALLOPIAN TUBES",
    "RIGHT FALLOPIAN TUBES",
    "BILATERAL FEMUR",
    "LEFT FEMUR",
    "RIGHT FEMUR",
    "LEFT FIBULA",
    "RIGHT FIBULA",
    "FINGER (INCLUDING THUMBS)",
    "FLOOR OF MOUTH (BOOSTS)",
    "BILATERAL FEET",
    "LEFT FOOT",
    "RIGHT FOOT",
    "FOREHEAD",
    "POSTERIOR FOSSA",
    "GALL BLADDER",
    "GINGIVA",
    "BILATERAL HAND",
    "LEFT HAND",
    "RIGHT HAND",
    "HEAD",
    "BILATERAL HEEL",
    "LEFT HEEL",
    "RIGHT HEEL",
    "LEFT HEMIMANTLE",
    "RIGHT HEMIMANTLE",
    "HEART",
    "BILATERAL HIP",
    "LEFT HIP",
    "RIGHT HIP",
    "LEFT HUMERUS",
    "RIGHT HUMERUS",
    "HYPOPHARYNX",
    "BILATERAL INTERNAL MAMMARY CHAIN",
    "BILATERAL INGUINAL NODES",
    "LEFT INGUINAL NODES",
    "RIGHT INGUINAL NODES",
    "INVERTED 'Y' (DOG-LEG,HOCKEY-STICK)",
    "LEFT KIDNEY",
    "RIGHT KIDNEY",
    "BILATERAL KNEE",
    "LEFT KNEE",
    "RIGHT KNEE",
    "BILATERAL LACRIMAL GLAND",
    "LEFT LACRIMAL GLAND",
    "RIGHT LACRIMAL GLAND",
    "LARYGOPHARYNX",
    "LARYNX",
    "BILATERAL LEG",
    "LEFT LEG",
    "RIGHT LEG",
    "LOWER BILATERAL LEG",
    "LOWER LEFT LEG",
    "LOWER RIGHT LEG",
    "UPPER BILATERAL LEG",
    "UPPER LEFT LEG",
    "UPPER RIGHT LEG",
    "BOTH EYELID(S)",
    "LEFT EYELID",
    "RIGHT EYELID",
    "BOTH LIP(S)",
    "LOWER LIP",
    "UPPER LIP",
    "LIVER",
    "BILATERAL LUNG",
    "LEFT LUNG",
    "RIGHT LUNG",
    "BILATERAL MANDIBLE",
    "LEFT MANDIBLE",
    "RIGHT MANDIBLE",
    "MANTLE",
    "BILATERAL MAXILLA",
    "LEFT MAXILLA",
    "RIGHT MAXILLA",
    "MEDIASTINUM",
    "MULTIPLE SKIN",
    "NASAL FOSSA",
    "NASOPHARYNX",
    "BILATERAL NECK INCLUDES NODES",
    "LEFT NECK INCLUDES NODES",
    "RIGHT NECK INCLUDES NODES",
    "NECK - SKIN",
    "NOSE",
    "ORAL CAVITY / BUCCAL MUCOSA",
    "BILATERAL ORBIT",
    "LEFT ORBIT",
    "RIGHT ORBIT",
    "OROPHARYNX",
    "BILATERAL OVARY",
    "LEFT OVARY",
    "RIGHT OVARY",
    "HARD PALATE",
    "SOFT PALATE",
    "PALATE UNSPECIFIED",
    "PANCREAS",
    "PARA-AORTIC NODES",
    "LEFT PAROTID",
    "RIGHT PAROTID",
    "BILATERAL PELVIS",
    "LEFT PELVIS",
    "RIGHT PELVIS",
    "PENIS",
    "PERINEUM",
    "PITUITARY",
    "LEFT PLEURA (AS IN MESOTHELIOMA)",
    "RIGHT PLEURA",
    "PROSTATE",
    "PUBIS",
    "PYRIFORM FOSSA (SINUSES)",
    "LEFT RADIUS",
    "RIGHT RADIUS",
    "RECTUM (INCLUDES SIGMOID)",
    "LEFT RIBS",
    "RIGHT RIBS",
    "SACRUM",
    "LEFT SALIVARY GLAND",
    "RIGHT SALIVARY GLAND",
    "BILATERAL SCAPULA",
    "LEFT SCAPULA",
    "RIGHT SCAPULA",
    "BILATERAL SUPRACLAVICULAR NODES",
    "LEFT SUPRACLAVICULAR NODES",
    "RIGHT SUPRACLAVICULAR NODES",
    "BILATERAL SCALP",
    "LEFT SCALP",
    "RIGHT SCALP",
    "SCROTUM",
    "BILATERAL SHOULDER",
    "LEFT SHOULDER",
    "RIGHT SHOULDER",
    "WHOLE BODY - SKIN",
    "SKULL",
    "CERVICAL & THORACIC SPINE",
    "SPHENOID SINUS",
    "CERVICAL SPINE",
    "LUMBAR SPINE",
    "THORACIC SPINE",
    "WHOLE SPINE",
    "SPLEEN",
    "LUMBO-SACRAL SPINE",
    "THORACIC & LUMBAR SPINE",
    "STERNUM",
    "STOMACH",
    "SUBMANDIBULAR GLANDS",
    "LEFT TEMPLE",
    "RIGHT TEMPLE",
    "BILATERAL TESTIS",
    "LEFT TESTIS",
    "RIGHT TESTIS",
    "THYROID",
    "LEFT TIBIA",
    "RIGHT TIBIA",
    "LEFT TOES",
    "RIGHT TOES",
    "TONGUE",
    "TONSIL",
    "TRACHEA",
    "LEFT ULNA",
    "RIGHT ULNA",
    "LEFT URETER",
    "RIGHT URETER",
    "URETHRA",
    "UTERUS",
    "UVULA",
    "VAGINA",
    "VULVA",
    "ABDOMEN",
    "BODY",
    "CHEST",
    "HEAD",
    "LOWER LIMB",
    "NECK",
    "OTHER",
    "PELVIS",
    "SKIN",
    "SPINE",
    "UPPER LIMB",
    "Not available",
]


IMMUNOTHERAPY_TYPE = [
    "Cell-based",
    "Immune checkpoint inhibitors",
    "Monoclonal antibodies other than immune checkpoint inhibitors",
    "Other immunomodulatory substances",
]

SURGERY_TYPE = [
    "Ablation",
    "Axillary Clearance",
    "Axillary lymph nodes sampling",
    "Bilateral complete salpingo-oophorectomy",
    "Biopsy",
    "Bypass Gastrojejunostomy",
    "Cholecystectomy",
    "Cholecystojejunostomy",
    "Completion Gastrectomy",
    "Debridement of pancreatic and peripancreatic necrosis",
    "Distal subtotal pancreatectomy",
    "Drainage of abscess",
    "Duodenal preserving pancreatic head resection",
    "Endoscopic biopsy",
    "Endoscopic brushings of gastrointestinal tract",
    "Enucleation",
    "Esophageal bypass surgery/jejunostomy only",
    "Exploratory laparotomy",
    "Fine needle aspiration biopsy",
    "Gastric Antrectomy",
    "Glossectomy",
    "Hepatojejunostomy",
    "Hysterectomy",
    "Incision of thorax",
    "Ivor Lewis subtotal esophagectomy",
    "Laparotomy",
    "Left thoracoabdominal incision",
    "Lobectomy",
    "Mammoplasty",
    "Mastectomy",
    "McKeown esophagectomy",
    "Merendino procedure",
    "Minimally invasive esophagectomy",
    "Omentectomy",
    "Ovariectomy",
    "Pancreaticoduodenectomy (Whipple procedure)",
    "Pancreaticojejunostomy, side-to-side anastomosis",
    "Partial pancreatectomy",
    "Pneumonectomy",
    "Prostatectomy",
    "Proximal subtotal gastrectomy",
    "Pylorus-sparing Whipple operation",
    "Radical pancreaticoduodenectomy",
    "Radical prostatectomy",
    "Reexcision",
    "Segmentectomy",
    "Sentinal Lymph Node Biopsy",
    "Spleen preserving distal pancreatectomy",
    "Splenectomy",
    "Total gastrectomy",
    "Total gastrectomy with extended lymphadenectomy",
    "Total pancreatectomy",
    "Transhiatal esophagectomy",
    "Triple bypass of pancreas",
    "Tumor Debulking",
    "Wedge/localised gastric resection",
    "Wide Local Excision",
]

SURGERY_LOCATION = ["Local recurrence", "Metastatic", "Primary"]
SURGERY_REFERENCE_DATABASE = ["SNOMED", "NCIt", "UMLS", "CCI"]

TUMOUR_FOCALITY = [
    "Cannot be assessed",
    "Multifocal",
    "Not applicable",
    "Unifocal",
    "Not available",
]

TUMOUR_CLASSIFICATION = ["Not applicable", "RX", "R0", "R1", "R2", "Not available"]

MARGIN_TYPES = [
    "Circumferential resection margin",
    "Common bile duct margin",
    "Distal margin",
    "Not applicable",
    "Proximal margin",
    "Not available",
]

LYMPHOVACULAR_INVASION = [
    "Absent",
    "Both lymphatic and small vessel and venous (large vessel) invasion",
    "Lymphatic and small vessel invasion only",
    "Not applicable",
    "Present",
    "Venous (large vessel) invasion only",
    "Not available",
]

PERINEURAL_INVASION = [
    "Absent",
    "Cannot be assessed",
    "Not applicable",
    "Present",
    "Not available",
]

DISEASE_STATUS_FOLLOWUP = [
    "Complete remission",
    "Distant progression",
    "Loco-regional progression",
    "No evidence of disease",
    "Partial remission",
    "Progression not otherwise specified",
    "Relapse or recurrence",
    "Stable",
    "Not available",
]

RELAPSE_TYPE = [
    "Distant recurrence/metastasis",
    "Local recurrence",
    "Local recurrence and distant metastasis",
    "Progression",
    "Biochemical progression",
    "Not available",
]

PROGRESSION_STATUS_METHOD = [
    "Imaging (procedure)",
    "Histopathology test (procedure)",
    "Assessment of symptom control (procedure)",
    "Physical examination procedure (procedure)",
    "Tumor marker measurement (procedure)",
    "Laboratory data interpretation (procedure)",
]

MALIGNANCY_LATERALITY = [
    "Bilateral",
    "Left",
    "Midline",
    "Not applicable",
    "Right",
    "Unilateral, Side not specified",
    "Not available",
]

ER_PR_HPV_STATUS = [
    "Cannot be determined",
    "Negative",
    "Not applicable",
    "Positive",
    "Not available",
]

HER2_STATUS = [
    "Cannot be determined",
    "Equivocal",
    "Positive",
    "Negative",
    "Not applicable",
    "Not available",
]

HPV_STRAIN = [
    "HPV16",
    "HPV18",
    "HPV31",
    "HPV33",
    "HPV35",
    "HPV39",
    "HPV45",
    "HPV51",
    "HPV52",
    "HPV56",
    "HPV58",
    "HPV59",
    "HPV66",
    "HPV68",
    "HPV73",
]

SMOKING_STATUS = [
    "Current reformed smoker for <= 15 years",
    "Current reformed smoker for > 15 years",
    "Current reformed smoker, duration not specified",
    "Current smoker",
    "Lifelong non-smoker (<100 cigarettes smoked in lifetime)",
    "Not applicable",
    "Not available",
]

TOBACCO_TYPE = [
    "Chewing Tobacco",
    "Cigar",
    "Cigarettes",
    "Electronic cigarettes",
    "Not applicable",
    "Pipe",
    "Roll-ups",
    "Snuff",
    "Not available",
    "Waterpipe",
]
TUMOUR_DESIGNATION = ["Normal", "Tumour"]
THERAPY_TYPE = ["External", "Internal", "Not available"]
SYSTEMIC_THERAPY_TYPE = ["Chemotherapy", "Hormone therapy", "Immunotherapy"]

# ID format
# Examples: 90234, BLD_donor_89, AML-90
ID_REGEX = r"^[A-Za-z0-9\-\._]{1,64}$"

# Date format
# A date, or partial date (e.g. just year or year + month) as used in
# human communication. The format is YYYY, YYYY-MM, or YYYY-MM-DD,
# e.g. 2018, 1973-06, or 1905-08-23. There SHALL be no time zone.
DATE_REGEX = r"^([0-9]([0-9]([0-9][1-9]|[1-9]0)|[1-9]00)|[1-9]000)(-(0[1-9]|1[0-2])(-(0[1-9]|[1-2][0-9]|3[0-1]))?)?"  # noqa: E501

# ICD-O-3 morphology codes
# Examples: 8260/3, 9691/36
MORPHOLOGY_REGEX = r"^[8,9]{1}[0-9]{3}/[0,1,2,3,6,9]{1}[1-9]{0,1}$|^Not available$"

# ICD-O-3 topography codes
# Examples: C50.1, C18
TOPOGRAPHY_REGEX = r"^[C][0-9]{2}(.[0-9]{1})?$|^Not available$"

# WHO ICD-10 codes
# Examples: E10, C50.1, I11, M06
COMORBIDITY_REGEX = r"^[A-Z][0-9]{2}(.[0-9]{1,3}[A-Z]{0,1})?$|^Not available$"

CauseOfDeathEnum = list_to_enum("CauseOfDeathEnum", CAUSE_OF_DEATH)
PrimarySiteEnum = list_to_enum("PrimarySiteEnum", PRIMARY_SITE)
uBooleanEnum = list_to_enum("uBooleanEnum", UBOOLEAN)
LostToFollowupReasonEnum = list_to_enum(
    "LostToFollowupReasonEnum", LOST_TO_FOLLOWUP_REASON
)
TumourStagingSystemEnum = list_to_enum("TumourStagingSystemEnum", TUMOUR_STAGING_SYSTEM)
TCategoryEnum = list_to_enum("TCategoryEnum", T_CATEGORY)
NCategoryEnum = list_to_enum("NCategoryEnum", N_CATEGORY)
MCategoryEnum = list_to_enum("MCategoryEnum", M_CATEGORY)
StageGroupEnum = list_to_enum("StageGroupEnum", STAGE_GROUP)
StorageEnum = list_to_enum("StorageEnum", STORAGE)
SpecimenProcessingEnum = list_to_enum("SpecimenProcessingEnum", SPECIMEN_PROCESSING)
SpecimenLateralityEnum = list_to_enum("SpecimenLateralityEnum", SPECIMEN_LATERALITY)
PrimaryDiagnosisLateralityEnum = list_to_enum(
    "PrimaryDiagnosisLateralityEnum", PRIMARY_DIAGNOSIS_LATERALITY
)
ConfirmedDiagnosisTumourEnum = list_to_enum(
    "ConfirmedDiagnosisTumourEnum", CONFIRMED_DIAGNOSIS_TUMOUR
)
TumourGradingSystemEnum = list_to_enum("TumourGradingSystemEnum", TUMOUR_GRADING_SYSTEM)
TumourGradeEnum = list_to_enum("TumourGradeEnum", TUMOUR_GRADE)
PercentCellsRangeEnum = list_to_enum("PercentCellsRangeEnum", PERCENT_CELLS_RANGE)
CellsMeasureMethodEnum = list_to_enum("CellsMeasureMethodEnum", CELLS_MEASURE_METHOD)
GenderEnum = list_to_enum("GenderEnum", GENDER)
SexAtBirthEnum = list_to_enum("SexAtBirthEnum", SEX_AT_BIRTH)
SpecimenTissueSourceEnum = list_to_enum(
    "SpecimenTissueSourceEnum", SPECIMEN_TISSUE_SOURCE
)
SpecimenTypeEnum = list_to_enum("SpecimenTypeEnum", SPECIMEN_TYPE)
SampleTypeEnum = list_to_enum("SampleTypeEnum", SAMPLE_TYPE)
BasisOfDiagnosisEnum = list_to_enum("BasisOfDiagnosisEnum", BASIS_OF_DIAGNOSIS)
LymphNodeStatusEnum = list_to_enum("LymphNodeStatusEnum", LYMPH_NODE_STATUS)
LymphNodeMethodEnum = list_to_enum("LymphNodeMethodEnum", LYMPH_NODE_METHOD)
TreatmentTypeEnum = list_to_enum("TreatmentTypeEnum", TREATMENT_TYPE)
TreatmentSettingEnum = list_to_enum("TreatmentSettingEnum", TREATMENT_SETTING)
TreatmentIntentEnum = list_to_enum("TreatmentIntentEnum", TREATMENT_INTENT)
TreatmentResponseMethodEnum = list_to_enum(
    "TreatmentResponseMethodEnum", TREATMENT_RESPONSE_METHOD
)
TreatmentResponseEnum = list_to_enum("TreatmentResponseEnum", TREATMENT_RESPONSE)
TreatmentStatusEnum = list_to_enum("TreatmentStatusEnum", TREATMENT_STATUS)
DrugReferenceDbEnum = list_to_enum("DrugReferenceDbEnum", DRUG_REFERENCE_DB)
DosageUnitsEnum = list_to_enum("DosageUnitsEnum", DOSAGE_UNITS)
RadiationTherapyModalityEnum = list_to_enum(
    "RadiationTherapyModalityEnum", RADIATION_THERAPY_MODALITY
)
RadiationAnatomicalSiteEnum = list_to_enum(
    "RadiationAnatomicalSiteEnum", RADIATION_ANATOMICAL_SITE
)
ImmunotherapyTypeEnum = list_to_enum("ImmunotherapyTypeEnum", IMMUNOTHERAPY_TYPE)
SurgeryTypeEnum = list_to_enum("SurgeryTypeEnum", SURGERY_TYPE)
SurgeryReferenceDatabaseEnum = list_to_enum(
    "SurgeryReferenceDatabaseEnum", SURGERY_REFERENCE_DATABASE
)
SurgeryLocationEnum = list_to_enum("SurgeryLocationEnum", SURGERY_LOCATION)
TumourFocalityEnum = list_to_enum("TumourFocalityEnum", TUMOUR_FOCALITY)
TumourClassificationEnum = list_to_enum(
    "TumourClassificationEnum", TUMOUR_CLASSIFICATION
)
MarginTypesEnum = list_to_enum("MarginTypesEnum", MARGIN_TYPES)
LymphovascularInvasionEnum = list_to_enum(
    "LymphovascularInvasionEnum", LYMPHOVACULAR_INVASION
)
PerineuralInvasionEnum = list_to_enum("PerineuralInvasionEnum", PERINEURAL_INVASION)
DiseaseStatusFollowupEnum = list_to_enum(
    "DiseaseStatusFollowupEnum", DISEASE_STATUS_FOLLOWUP
)
RelapseTypeEnum = list_to_enum("RelapseTypeEnum", RELAPSE_TYPE)
ProgressionStatusMethodEnum = list_to_enum(
    "ProgressionStatusMethodEnum", PROGRESSION_STATUS_METHOD
)
MalignancyLateralityEnum = list_to_enum(
    "MalignancyLateralityEnum", MALIGNANCY_LATERALITY
)
ErPrHpvStatusEnum = list_to_enum("ErPrHpvStatusEnum", ER_PR_HPV_STATUS)
Her2StatusEnum = list_to_enum("Her2StatusEnum", HER2_STATUS)
HpvStrainEnum = list_to_enum("HpvStrainEnum", HPV_STRAIN)
SmokingStatusEnum = list_to_enum("SmokingStatusEnum", SMOKING_STATUS)
TobaccoTypeEnum = list_to_enum("TobaccoTypeEnum", TOBACCO_TYPE)
TumourDesginationEnum = list_to_enum("TumourDesginationEnum", TUMOUR_DESIGNATION)
TherapyTypeEnum = list_to_enum("TherapyTypeEnum", THERAPY_TYPE)
SystemicTherapyTypeEnum = list_to_enum("SystemicTherapyTypeEnum", SYSTEMIC_THERAPY_TYPE)
