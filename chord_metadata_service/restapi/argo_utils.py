# functions to convert mcode class to argo representation
# there is no official implemetation guide from mCODE or ARGO
# the mappings is an internal document in CanDIG


def argo_donor(obj):
    """
    Convert Individual to ARGO Donor.
    Takes Katsu patient object and converts its fields to ARGO aoccrding to the mapping.
    """

    donor = {
        "submitter_donor_id": obj["id"],
        "vital_status": obj.get("deceased", False),
        # TODO add mapping between sex and gender
        "gender": obj.get("sex", "UNKNOWN_SEX")
    }
    # check for not mapped fields in extra_properties
    if "extra_properties" in obj and obj["extra_properties"]:
        for i in ["cause_of_death", "survival_time", "primary_site"]:
            if i in obj["extra_properties"]:
                donor[i] = obj["extra_properties"][i]
    return donor


def argo_specimen(obj):
    """
    Convert GeneticSpecimen to ARGO Specimen.
    Takes Katsu genetic specimen object and converts its fields to ARGO aoccrding to the mapping.
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
