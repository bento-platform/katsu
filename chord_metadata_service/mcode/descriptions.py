# Most parts of this text are taken from the mCODE:Minimal Common Oncology Data Elements Data Dictionary.
# The mCODE is made available under the Creative Commons 0 "No Rights Reserved" license https://creativecommons.org/share-your-work/public-domain/cc0/

# Portions of this text copyright (c) 2019-2020 the Canadian Centre for Computational Genomics; licensed under the
# GNU Lesser General Public License version 3.


GENETIC_VARIANT_TESTED = {
    "description": "A description of an alteration in the most common DNA nucleotide sequence.",
    "properties": {
        "id": "An arbitrary identifier for the genetic variant tested.",
        "gene_studied": "A gene targeted for mutation analysis, identified in HUGO Gene Nomenclature Committee "
                        "(HGNC) notation.",
        "method": "An ontology or controlled vocabulary term to identify the method used to perform the genetic test. "
                  "Accepted value set: NCIT.",
        "variant_tested_identifier": "The variation ID assigned by HGVS, for example, 360448 is the identifier for "
                                     "NM_005228.4(EGFR):c.-237A>G (single nucleotide variant in EGFR).",
        "variant_tested_hgvs_name": "Symbolic representation of the variant used in HGVS, for example, "
                                    "NM_005228.4(EGFR):c.-237A>G for HVGS variation ID 360448.",
        "variant_tested_description": "Description of the variant.",
        "data_value": "An ontology or controlled vocabulary term to identify positive or negative value for"
                      "the mutation. Accepted value set: SNOMED CT."
    }
}


GENETIC_VARIANT_FOUND = {
    "description": "Description of single discrete variant tested.",
    "properties": {
        "id": "An arbitrary identifier for the genetic variant found.",
        "method": "An ontology or controlled vocabulary term to identify the method used to perform the genetic test. "
                  "Accepted value set: NCIT.",
        "variant_found_identifier": "The variation ID assigned by HGVS, for example, 360448 is the identifier for "
                                    "NM_005228.4(EGFR):c.-237A>G (single nucleotide variant in EGFR). "
                                    "Accepted value set: ClinVar.",
        "variant_found_hgvs_name": "Symbolic representation of the variant used in HGVS, for example, "
                                    "NM_005228.4(EGFR):c.-237A>G for HVGS variation ID 360448.",
        "variant_found_description": "Description of the variant.",
        "genomic_source_class": "An ontology or controlled vocabulary term to identify the genomic class of the "
                                "specimen being analyzed."
    }
}


GENOMICS_REPORT = {
    "description": "Genetic Analysis Summary.",
    "properties": {
        "id": "An arbitrary identifier for the genetics report.",
        "test_name": "An ontology or controlled vocabulary term to identify the laboratory test. "
                     "Accepted value sets: LOINC, GTR.",
        "performing_ogranization_name": "The name of the organization  producing the genomics report.",
        "specimen_type": "An ontology or controlled vocabulary term to identify the type of material the specimen "
                         "contains or consists of. Accepted value set: HL7 Version 2 and Specimen Type.",
        "genetic_variant_tested": "A test for a specific mutation on a particular gene.",
        "genetic_variant_found": "Records an alteration in the most common DNA nucleotide sequence.",
        "subject": "Subject (Patient) of genomics report."
    }
}


LABS_VITAL = {
    "description": "A description of tests performed on patient.",
    "properties": {
        "id": "An arbitrary identifier for the labs/vital tests.",
        "individual": "The individual who is the subject of the tests.",
        "body_height": "The patient\'s height.",
        "body_weight": "The patient\'s weight.",
        "cbc_with_auto_differential_panel": "Reference to a laboratory observation in the CBC with Auto Differential"
                                            "Panel test.",
        "comprehensive_metabolic_2000": "Reference to a laboratory observation in the CMP 2000 test.",
        "blood_pressure_diastolic": "The blood pressure after the contraction of the heart while the chambers of "
                                    "the heart refill with blood, when the pressure is lowest.",
        "blood_pressure_systolic": "The blood pressure during the contraction of the left ventricle of the heart, "
                                    "when blood pressure is at its highest.",
        "tumor_marker_test": "An ontology or controlled vocabulary term to identify tumor marker test."
    }
}


CANCER_CONDITION = {
    "description": "A description of history of primary or secondary cancer conditions.",
    "properties": {
        "id": "An arbitrary identifier for the cancer condition.",
        "condition_type": "Cancer condition type: primary or secondary.",
        "body_location_code": "Code for the body location, optionally pre-coordinating laterality or direction. "
                              "Accepted ontologies: SNOMED CT, ICD-O-3 and others.",
        "clinical_status": "A flag indicating whether the condition is active or inactive, recurring, in remission, "
                           "or resolved (as of the last update of the Condition). Accepted code system: "
                            "http://terminology.hl7.org/CodeSystem/condition-clinical",
        "condition_code": "A code describing the type of primary or secondary malignant neoplastic disease.",
        "date_of_diagnosis": "The date the disease was first clinically recognized with sufficient certainty, "
                             "regardless of whether it was fully characterized at that time.",
        "histology_morphology_behavior": "A description of the morphologic and behavioral characteristics of "
                                         "the cancer. Accepted ontologies: SNOMED CT, ICD-O-3 and others.",
        "subject": "The subject (Patient) of the study that has a cancer condition."
    }
}


TNM_STAGING = {
    "description": "A description of the cancer spread in a patient's body.",
    "properties": {
        "id": "An arbitrary identifier for the TNM staging.",
        "tnm_type": "TNM type: clinical or pathological.",
        "stage_group": "The extent of the cancer in the body, according to the TNM classification system."
                        "Accepted ontologies: SNOMED CT, AJCC and others.",
        "primary_tumor_category": "Category of the primary tumor, based on its size and extent. "
                                  "Accepted ontologies: SNOMED CT, AJCC and others.",
        "regional_nodes_category": "Category of the presence or absence of metastases in regional lymph nodes. "
                                    "Accepted ontologies: SNOMED CT, AJCC and others.",
        "distant_metastases_category": "Category describing the presence or absence of metastases in remote "
                                       "anatomical locations. Accepted ontologies: SNOMED CT, AJCC and others.",
        "cancer_condition": "Cancer condition."
    }
}


CANCER_RELATED_PROCEDURE = {
    "description": "Description of radiological treatment or surgical action addressing a cancer condition.",
    "properties": {
        "id": "An arbitrary identifier for the procedure.",
        "procedure_type": "Type of cancer related procedure: radion or surgical.",
        "code": "Code for the procedure performed.",
        "occurence_time_or_period": "The date/time that a procedure was performed.",
        "target_body_site": "The body location(s) where the procedure was performed.",
        "treatment_intent": "The purpose of a treatment.",
        "subject": "The patient who has a cancer condition."
    }
}


MEDICATION_STATEMENT = {
    "description": "Description of medication use.",
    "properties": {
        "id": "An arbitrary identifier for the medication statement.",
        "medication_code": "A code for medication. Accepted code systems: Medication Clinical Drug (RxNorm) and other.",
        "termination_reason": "A code explaining unplanned or premature termination of a course of medication. "
                              "Accepted ontologies: SNOMED CT.",
        "treatment_intent": "The purpose of a treatment. Accepted ontologies: SNOMED CT.",
        "start_date": "The start date/time of the medication.",
        "end_date": "The end date/time of the medication.",
        "date_time": "The date/time the medication was administered.",
        "subject": "Subject of medication statement."
    }
}
