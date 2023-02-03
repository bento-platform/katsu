def transform_json(json_data):
    transformed_data = []
    for primary_diagnosis in json_data["primary_diagnosis"]:
        range_start, range_end = primary_diagnosis["range"]
        for i in range(range_start, range_end + 1):
            submitter_primary_diagnosis_id = "PRIMARY_DIAGNOSIS_{}".format(i)
            for target in primary_diagnosis["targets"]:
                if "donor_id" in target:
                    submitter_donor_id = target["donor_id"][0] + str(target["range"][0])
                if "program_id" in target:
                    program_id = target["program_id"][0] + str(target["range"][0])
            transformed_data.append(
                {
                    "program_id": program_id,
                    "submitter_donor_id": submitter_donor_id,
                    "submitter_primary_diagnosis_id": submitter_primary_diagnosis_id,
                }
            )
    return transformed_data
