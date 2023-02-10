import json
import os

from django.core.management import call_command


def convert_to_fixtures():
    """
    Convert synthetic data to Django fixtures.
    The data should been assigned foreign keys already.
    """
    # Get the absolute path to the synthetic data folder
    script_dir = os.path.dirname(__file__)
    synthetic_data_folder = os.path.join(script_dir, "small_dataset/synthetic_data")
    fixtures_folder = os.path.join(script_dir, "small_dataset/fixtures")

    # Create the fixtures folder if it doesn't already exist
    os.makedirs(fixtures_folder, exist_ok=True)

    # Get all the JSON file names in the synthetic data folder
    json_file_names = [
        file for file in os.listdir(synthetic_data_folder) if file.endswith(".json")
    ]

    # Convert each JSON file to a Django fixture
    for json_file_name in json_file_names:
        print(f"Processing {json_file_name}...")
        model_name = json_file_name.split(".")[0].lower()
        fixtures = []

        with open(os.path.join(synthetic_data_folder, json_file_name)) as json_file:
            raw_data = json.load(json_file)

            for data_item in raw_data:
                fixture = {"model": "mohpackets." + model_name, "fields": data_item}
                fixtures.append(fixture)

        with open(os.path.join(fixtures_folder, json_file_name), "w") as fixtures_file:
            json.dump(fixtures, fixtures_file, indent=4)

    print("\nSuccess! Converted files to fixtures and saved to folder fixtures.")


def set_foreign_keys():
    """
    Set foreign keys for synthetic data.
    """
    # Get the absolute path to the synthetic data folder
    script_dir = os.path.dirname(__file__)
    relationships_file = os.path.join(
        script_dir, "small_dataset/template/relationships.json"
    )
    no_relationships_data_folder = os.path.join(
        script_dir, "small_dataset/no_relationships_data"
    )
    synthetic_data_folder = os.path.join(script_dir, "small_dataset/synthetic_data")

    # Create the folder if it doesn't already exist
    os.makedirs(synthetic_data_folder, exist_ok=True)

    file_names = {
        "programs": "Program.json",
        "donors": "Donor.json",
        "primary_diagnoses": "PrimaryDiagnosis.json",
        "specimens": "Specimen.json",
        "sample_registrations": "SampleRegistration.json",
        "treatments": "Treatment.json",
        "chemotherapies": "Chemotherapy.json",
        "hormone_therapies": "HormoneTherapy.json",
        "radiations": "Radiation.json",
        "immunotherapies": "Immunotherapy.json",
        "surgeries": "Surgery.json",
        "follow_ups": "FollowUp.json",
        "biomarkers": "Biomarker.json",
        "comorbidities": "Comorbidity.json",
    }

    with open(relationships_file, "r") as f:
        relationships = json.load(f)

    for model, filename in file_names.items():
        input_path = f"{no_relationships_data_folder}/{filename}"
        output_path = f"{synthetic_data_folder}/{filename}"

        try:
            relationship = relationships[model]
        except KeyError as e:
            print(f"KeyError: {e}")
            break

        with open(input_path, "r") as f:
            data_without_relationships = json.load(f)

        print(f"Processing {filename}...")
        data_with_keys = replace_values(data_without_relationships, relationship)

        with open(output_path, "w") as f:
            json.dump(data_with_keys, f, indent=4)
    print("\nSuccess! Set foreign keys and saved to folder synthetic_data.")


def replace_values(input_data, transformation_rules):
    """
    Replace values in input data using transformation rules.

    Inputs:
        - `input_data`: a list of dictionaries
        - `transformation_rules`:  a list of dictionaries, each defining a rule

    Each rule consists of:
        - `range`: tuple of two integers, specifying range of items to apply the rule to.
        - `targets`: list of dictionaries, each defining a field to be updated.

    Each target consists of:
        - `field_name`: name of field to update.
        - `field_value`: new value of the field.
        - `range`: tuple of two integers, specifying the range of numbers to add to field_value.

    The function updates specified fields by combining field_value (e.g. "DONOR_") with a string
    representation of the target index (e.g. "1"). Target index is calculated by adding
    current item index to target_start, if result is greater than target_end, it's wrapped around.

    Here an example of input data:
    {
        "submitter_donor_id": "DONOR_{REPLACE_ME}",
        "submitter_primary_diagnosis_id": "PRIMARY_DIAGNOSIS_1",
    }

    and transformation rules:
    {
        "range": [1, 3],
        "targets": [
            {
            "range": [1, 1],
            "field_name": "submitter_donor_id",
            "field_value": "DONOR_"
            }
        ]
    }

    and the result:
    {
        "submitter_donor_id": "DONOR_1",
        "submitter_primary_diagnosis_id": "PRIMARY_DIAGNOSIS_1",
    }
    """
    for rule in transformation_rules:
        item_start, item_end = rule["range"]
        target_fields = rule["targets"]

        # loop through each item in the range
        for item_index_offset in range(item_end - item_start + 1):
            item_index = item_start + item_index_offset - 1

            for target_field in target_fields:
                field_name = target_field["field_name"]
                field_value = target_field["field_value"]
                target_start, target_end = target_field["range"]

                # compute the target index
                target_index = target_start + item_index_offset

                # wrap around the target index if it's out of range
                if target_index > target_end:
                    target_index = target_start + (
                        item_index_offset % (target_end - target_start + 1)
                    )

                # replace the value in the input data
                input_data[item_index][field_name] = field_value + str(target_index)
    return input_data


def main():
    print("Select an option:")
    print("1. Set Foreign Keys")
    print("2. Convert to Django fixtures")
    print("3. Exit")

    choice = int(input("Enter your choice [1-3]: "))

    if choice == 1:
        set_foreign_keys()
    elif choice == 2:
        convert_to_fixtures()
    elif choice == 3:
        exit()
    else:
        print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
