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
