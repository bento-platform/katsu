# About

This folder contains synthetic data for **MoH models**.

The **schemas** contains the blueprints to generate the data.

The **synthetic_data** folder contains the generated data.

The **fixtures** contains the mock data in Django format (converted from synthetic data).
## How to use

To generate synthetic data, you need to create a [Mockaroo](https://www.mockaroo.com/) account and use the blueprints in the schemas folder ("RESTORE FROM BACKUP...").

Then, generate the data and download it as a JSON file.

To convert the JSON file to Django fixtures, use the following command from the root folder:

```
python chord_metadata_service/mohpackets/data/convert.py
```

To load the fixtures into local database, you can use the following command from the root folder:
```
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Program.json chord_metadata_service/mohpackets/data/fixtures/Donor.json chord_metadata_service/mohpackets/data/fixtures/PrimaryDiagnosis.json chord_metadata_service/mohpackets/data/fixtures/Specimen.json chord_metadata_service/mohpackets/data/fixtures/SampleRegistration.json chord_metadata_service/mohpackets/data/fixtures/Treatment.json chord_metadata_service/mohpackets/data/fixtures/Chemotherapy.json chord_metadata_service/mohpackets/data/fixtures/HormoneTherapy.json chord_metadata_service/mohpackets/data/fixtures/Radiation.json chord_metadata_service/mohpackets/data/fixtures/Immunotherapy.json chord_metadata_service/mohpackets/data/fixtures/Surgery.json chord_metadata_service/mohpackets/data/fixtures/FollowUp.json chord_metadata_service/mohpackets/data/fixtures/Biomarker.json chord_metadata_service/mohpackets/data/fixtures/Comorbidity.json
```

or you can do it one by one in this order:
```
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Program.json 
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Donor.json 
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/PrimaryDiagnosis.json
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Specimen.json
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/SampleRegistration.json
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Treatment.json
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Chemotherapy.json
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/HormoneTherapy.json
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Radiation.json
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Immunotherapy.json
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Surgery.json
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/FollowUp.json
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Biomarker.json 
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Comorbidity.json
```

*Note:* To clean up data (this will **delete everything** in the database, not just MoH data)

```
python manage.py flush
```

## Small dataset data:
 - 2 Programs
 - 10 Donors (6 program_1, 4 program_2)
 - 15 PrimaryDiagnosis (donor_1_2 have 3, donor_3_4 has 2, donor_5_to_10 have 1)
 - 20 Specimen (primary_diagnosis_1_2 have 3, primary_diagnosis_3_4 have 2, primary_diagnosis_5_to_15 have 1)
 - 25 SampleRegistration (specimen_1_2 has 3, specimen_3_4 have 2, specimen_5_to_20 have 1)
 - 20 Treatment (primary_diagnosis_1_2 have 3, primary_diagnosis_3_4 have 2, primary_diagnosis_5_to_15 have 1)
 - 7 Chemotherapy (treatment_1 has 3, treatment_2 has 2, treatment_3_4 has 1)
 - 7 HormoneTherapy (treatment_5 has 3, treatment_6 has 2, treatment_7_8 has 1)
 - 7 Radiation (treatment_9 has 3, treatment_10 has 2, treatment_11_12 has 1)
 - 7 Immunotherapy (treatment_13 has 3, treatment_14 has 2, treatment_15_16 has 1)
 - 7 Surgery (treatment_17 has 3, treatment_18 has 2, treatment_19_20 has 1)
 - 25 FollowUp (treatment_1_2 have 3, treatment_3_4 have 2, treatment_5_to_20 have 1)
 - 30 Biomarker (follow_up_1_2 have 3, follow_up_3_4 have 2, follow_up_5_to_25 have 1)
 - 15 Comorbidity (donor_1_2 have 3, donor_3_4 has 2, donor_5_to_10 have 1)

Question:
 - Should program and donor be linked to each other? (e.g donor_1 only go with program_1). If this is true, then we should put the program FK in donor only.
 - Similarly, should primary_diagnosis be linked to donor? (e.g primary_diagnosis_1 only go with donor_1 and program_1). If this is true, then we should put the donor FK in primary_diagnosis only.
 - Same for the rest of the models.
