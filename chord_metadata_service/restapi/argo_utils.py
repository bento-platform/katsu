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
        if "cause_of_death" in obj["extra_properties"]:
            donor["cause_of_death"] = obj["extra_properties"]["cause_of_death"]
        if "survival_time" in obj["extra_properties"]:
            donor["survival_time"] = obj["extra_properties"]["survival_time"]
        if "primary_site" in obj["extra_properties"]:
            donor["primary_site"] = obj["extra_properties"]["primary_site"]

    return donor
