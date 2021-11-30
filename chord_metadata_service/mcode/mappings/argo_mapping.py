# title is ARGO collection of data elements
# keys are mCODE fiels, values are ARGO fields
ARGO_MAPPING = {
    "individual": {
        "title": "Donor",
        "id": "submitter_donor_id",
        "deceased": "vital_status",
        "sex": "gender"
    },
    "genetic_specimen": {
        "title": "Specimen",
        "id": "submitter_specimen_id",
        "collection_body": "specimen_tissue_source",
        "specimen_type": "specimen_type",
        "laterality": "specimen_laterality",
        "extra_properties": [
            "sample_type"
        ]
    },
    "cancer_condition": {
        "title": "PrimaryDiagnosis",
        "id": "submitter_primary_diagnosis_id",
        "condition_type": "primary",
        "body_site": "",
        "laterality": "laterality",
        "clinical_status": "",
        "code": "cancer_type_code",
        "date_of_diagnosis": "age_at_diagnosis",
        "histology_morphology_behavior": "",
        "verification_status": "",
        "extra_properties": [
            "cancer_type_additional_information",
        ]
    },
    "tnm_staging": {
        "title": "PrimaryDiagnosis",
        "id": "",
        "tnm_type": "clinical",
        "stage_group": "clinical_tumour_staging_system",
        "primary_tumor_category": "clinical_t_category",
        "regional_nodes_category": "clinical_n_category",
        "distant_metastases_category": "clinical_m_category",
        "cancer_condition": "submitter_primary_diagnosis_id",
        "extra_properties": [
            "clinical_stage_group",
        ]
    }
}
