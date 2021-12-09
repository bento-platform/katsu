# functions to convert mcode class to argo representation
# there is no official implemetation guide from mCODE or ARGO
# the mappings is an internal document in CanDIG


def argo_administrative_gender(value):
    """ Converts Phenopackets sex values to mCODE administrative gender values. """
    if value in ["MALE", "FEMALE"]:
        return value.title()
    elif value in ["OTHER_SEX", "UNKNOWN_SEX"]:
        return value.split("_")[0].title()
    else:
        raise ValueError("The value is not supported.")


def argo_donor(obj):
    """
    Convert Individual to ARGO Donor.
    Takes Katsu patient object and converts its fields to ARGO according to the mapping.
    """

    donor = {
        "submitter_donor_id": obj["id"],
        "vital_status": obj.get("deceased", False),
        "gender": argo_administrative_gender(obj.get("sex", "UNKNOWN_SEX"))
    }
    # check for not mapped fields in extra_properties
    if "extra_properties" in obj and obj["extra_properties"]:
        for i in ["cause_of_death", "survival_time", "primary_site"]:
            if i in obj["extra_properties"]:
                donor[i] = obj["extra_properties"][i]
    return donor


def argo_specimen(obj):
    """
    Convert Genetic Specimen to ARGO Specimen.
    Takes Katsu genetic specimen object and converts its fields to ARGO according to the mapping.
    """
    specimen = {
        "submitter_specimen_id": obj["id"],
        "specimen_type": obj["specimen_type"]
    }
    for argo_field, mcode_field in zip(
            ("specimen_tissue_source", "specimen_laterality"),
            ("collection_body", "laterality")
    ):
        if mcode_field in obj:
            specimen[argo_field] = obj[mcode_field]
    return specimen


def argo_primary_diagnosis(obj):
    """
    Convert Cancer Condition to ARGO Primary Diagnosis.
    Takes Katsu cancer condition object and converts its fields to ARGO according to the mapping.
    """
    primary_diagnosis = {
        "submitter_primary_diagnosis_id": obj["id"],
        "cancer_type_code": obj["code"]
    }
    if "tnm_staging" in obj and obj["tnm_staging"]:
        for item in obj["tnm_staging"]:
            # tnm_staging clinical is mapped to PrimaryDiagnosis fields
            if item["tnm_type"] == "clinical":
                for mcode_field, argo_field in zip(
                        ["stage_group", "primary_tumor_category",
                         "regional_nodes_category", "distant_metastases_category"],
                        ["clinical_stage_group", "clinical_t_category",
                         "clinical_n_category", "clinical_m_category"]
                ):
                    if mcode_field in item and item[mcode_field]:
                        if argo_field in primary_diagnosis and primary_diagnosis[argo_field]:
                            primary_diagnosis[argo_field].append(item[mcode_field]["data_value"])
                        else:
                            primary_diagnosis[argo_field] = [item[mcode_field]["data_value"]]

            # tnm_staging pathologic is mapped to Specimen fields
            elif item["tnm_type"] == "pathologic":
                # need to instanciate a local specimen object here
                primary_diagnosis["specimen"] = {}
                for mcode_field, argo_field in zip(
                        ["stage_group", "primary_tumor_category",
                         "regional_nodes_category", "distant_metastases_category"],
                        ["pathological_stage_group", "pathological_t_category",
                         "pathological_n_category", "clinical_m_category"]
                ):
                    if argo_field in primary_diagnosis["specimen"] and primary_diagnosis["specimen"][argo_field]:
                        primary_diagnosis["specimen"][argo_field].append(item[mcode_field]["data_value"])
                    else:
                        primary_diagnosis["specimen"][argo_field] = [item[mcode_field]["data_value"]]

    # check for not mapped fields in extra_properties
    if "extra_properties" in obj and obj["extra_properties"]:
        for i in ["age_at_diagnosis", "lymph_nodes_examined_status",
                  "number_lymph_nodes_positive", "clinical_tumour_staging_system"]:
            if i in obj["extra_properties"]:
                primary_diagnosis[i] = obj["extra_properties"][i]

    return primary_diagnosis


# a dict to map mCODE procedure type to ARGO treatment types
PROCEDUR_TYPE_TO_TREATMENT_TYPE = {
    "radiation": "Radiation therapy",
    "surgical": "Surgery"
}


def argo_treatment(obj):
    """
    Convert Cancer Related Procedure to ARGO Treatment.
    Takes Katsu cancer related procedure object and converts its fields to ARGO according to the mapping.
    """
    treatment = {
        "submitter_treatment_id": obj["id"],
        "treatment_type": PROCEDUR_TYPE_TO_TREATMENT_TYPE[obj["procedure_type"]]
    }
    if "treatment_intent" in obj and obj["treatment_intent"]:
        treatment["treatment_intent"] = obj["treatment_intent"]
    # only radiation treatment fields
    if obj["procedure_type"] == "radiation":
        for mcode_field, argo_field in zip(
                ["code", "body_site"],
                ["radiation_therapy_modality", "anatomical_site_irradiated"]
        ):
            if mcode_field in obj and obj[mcode_field]:
                treatment[argo_field] = obj[mcode_field]
    return treatment


def argo_therapy(obj):
    """
    Convert Medication statement to ARGO Immunotherapy, Chemotherapy, Hormone Therapy.
    Takes Katsu medication statement object and converts its fields to ARGO according to the mapping.
    """
    therapy = {
        "submitter_treatment_id": obj["id"],
        "drug_rxnormcui": obj["medication_code"]
    }
    return therapy


def argo_composition_object(obj):
    """
    Returns all Mcodepacket related objects converted to their ARGO element according to the mapping.
    """
    composition_object = {
        "donor": argo_donor(obj["subject"]),
        "primary_diagnoses": [argo_primary_diagnosis(cc) for cc in obj["cancer_condition"]],
        "treatments": [argo_treatment(crp) for crp in obj["cancer_related_procedures"]],
        # the name doesn't look nice but there is no therapy type field in mcode
        "immunotherapies_chemotherapies_hormone_therapies": [argo_therapy(ms) for ms in obj["medication_statement"]]
    }
    return composition_object
