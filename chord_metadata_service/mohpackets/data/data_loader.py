import json
import os
import sys
from collections import OrderedDict

import django
from django.db import transaction

# Add your Django project's root directory to the Python path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
)  # This assumes your script is in the data directory

# Set the DJANGO_SETTINGS_MODULE to your project's settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
# Initialize Django
django.setup()
from chord_metadata_service.mohpackets.models import (  # noqa: E402
    Biomarker,
    Chemotherapy,
    Comorbidity,
    Donor,
    Exposure,
    FollowUp,
    HormoneTherapy,
    Immunotherapy,
    PrimaryDiagnosis,
    Program,
    Radiation,
    SampleRegistration,
    Specimen,
    Surgery,
    Treatment,
)


def ingest_data(path):
    # Install tqdm if needed
    try:
        from tqdm import tqdm
    except ImportError:
        import subprocess

        subprocess.check_call(["pip", "install", "tqdm"])
        from tqdm import tqdm

    script_dir = os.path.dirname(__file__)
    synthetic_data_folder = os.path.join(script_dir, f"{path}/synthetic_data")
    file_mapping = OrderedDict(
        [
            (Donor, "Donor.json"),
            (PrimaryDiagnosis, "PrimaryDiagnosis.json"),
            (Specimen, "Specimen.json"),
            (SampleRegistration, "SampleRegistration.json"),
            (Treatment, "Treatment.json"),
            (Chemotherapy, "Chemotherapy.json"),
            (HormoneTherapy, "HormoneTherapy.json"),
            (Radiation, "Radiation.json"),
            (Immunotherapy, "Immunotherapy.json"),
            (Surgery, "Surgery.json"),
            (FollowUp, "FollowUp.json"),
            (Biomarker, "Biomarker.json"),
            (Comorbidity, "Comorbidity.json"),
            (Exposure, "Exposure.json"),
        ]
    )
    program_file_path = f"{synthetic_data_folder}/Program.json"
    with open(program_file_path, "r") as json_file:
        program_data = json.load(json_file)

    # Iterate through the data and create model instances
    with transaction.atomic():
        for program in program_data:
            program_instance = Program(**program)
            program_instance.save()

    for model, filename in file_mapping.items():
        # Read the JSON file
        file_path = f"{synthetic_data_folder}/{filename}"
        with open(file_path, "r") as json_file:
            data = json.load(json_file)

        # Iterate through the data and create model instances
        with transaction.atomic():
            for item in tqdm(
                data,
                desc=f"{filename}",
                bar_format="{desc}: {percentage:3.0f}% {n_fmt}/{total_fmt}",
            ):
                item["program_id_id"] = item.pop("program_id", None)
                model_instance = model(**item)
                model_instance.save()


def main():
    print("Select an option:")
    print("1. Load small dataset")
    print("2. Load medium dataset")
    print("3. Load large dataset")
    print("4. Exit")

    choice = int(input("Enter your choice [1-4]: "))

    if choice == 1:
        path = "small_dataset"
    elif choice == 2:
        path = "medium_dataset"
    elif choice == 3:
        path = "large_dataset"
    elif choice == 4:
        print("Exiting...")
        exit()
    else:
        print("Invalid option. Please try again.")
        return

    ingest_data(path)


if __name__ == "__main__":
    main()
